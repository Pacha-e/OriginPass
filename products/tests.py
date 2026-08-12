"""Invariants of the product tables created in Sprint 1.

The views that exercise these belong to later sprints; the rules are in place
from now, which is what DBR12 asks for on the revocation side.
"""

import hashlib

from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, transaction
from django.test import TestCase, override_settings

from accounts.models import User
from audit.integrity import GENESIS
from audit.models import Action, AuditEntry
from companies.models import Company, CompanyStatus, CompanyType, VerificationTrack

from .models import CustodyTransfer, Product, ProductStatus, ProductType


def make_approved_company(email="weaver@tuchin.co", company_type=CompanyType.COMMERCIAL):
    owner = User.objects.create_user(email, "Vueltiao-2026")
    is_commercial = company_type == CompanyType.COMMERCIAL
    return Company.objects.create(
        owner=owner,
        legal_name="Artesanias La Bonga SAS",
        company_type=company_type,
        verification_track=(
            VerificationTrack.CHAMBER_OF_COMMERCE
            if is_commercial
            else VerificationTrack.ARTISAN_REVIEW
        ),
        registry_code="NIT-900123456-7" if is_commercial else "",
        description="Crafts from Cordoba.",
        location="Monteria, Cordoba",
        status=CompanyStatus.APPROVED,
        status_reason="",
    )


def make_product(company, **overrides):
    fields = {
        "product_type": ProductType.COMMERCIAL_ORIGINAL,
        "name": "Sombrero vueltiao 21 vueltas",
        "description": "Hand woven.",
        "category": "Headwear",
        "origin": "Tuchin, Cordoba",
    }
    fields.update(overrides)
    return Product.objects.create(company=company, **fields)


class RevocationReasonTests(TestCase):
    """DBR12 - Require a reason on negative decisions (product side)."""

    def setUp(self):
        self.company = make_approved_company()
        self.admin = User.objects.create_superuser("admin@originpass.co", "Admin-Pass-2026")
        self.product = make_product(self.company)

    def test_a_revocation_without_a_reason_is_refused(self):
        with self.assertRaises(ValueError):
            self.product.revoke(actor=self.admin, reason="  ")

        self.product.refresh_from_db()
        self.assertEqual(self.product.status, ProductStatus.ACTIVE)

    def test_the_database_refuses_a_revoked_product_with_no_reason(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Product.objects.filter(pk=self.product.pk).update(
                status=ProductStatus.REVOKED, revocation_reason=""
            )

    def test_the_reason_is_kept_with_the_decision(self):
        self.product.revoke(actor=self.admin, reason="Reported as a counterfeit.")

        self.product.refresh_from_db()
        self.assertEqual(self.product.status, ProductStatus.REVOKED)
        self.assertEqual(self.product.revocation_reason, "Reported as a counterfeit.")

    def test_revocation_is_final(self):
        self.product.revoke(actor=self.admin, reason="Reported as a counterfeit.")

        with self.assertRaises(ValueError):
            self.product.revoke(actor=self.admin, reason="Reported again.")


class PassportCodeTests(TestCase):
    """A code that cannot be derived from another code."""

    def setUp(self):
        self.company = make_approved_company()

    def test_each_product_gets_its_own_code(self):
        first = make_product(self.company)
        second = make_product(self.company)

        self.assertNotEqual(first.passport_code, second.passport_code)
        self.assertGreaterEqual(len(first.passport_code), 24)

    def test_the_code_is_unique_across_the_table(self):
        first = make_product(self.company)

        with self.assertRaises(IntegrityError), transaction.atomic():
            make_product(self.company, passport_code=first.passport_code)


class IntegrityHashTests(TestCase):
    """The identifying fields are signed, so later tampering is detectable."""

    def setUp(self):
        self.company = make_approved_company()

    def test_the_signature_is_written_on_registration(self):
        product = make_product(self.company)

        self.assertEqual(len(product.integrity_hash), 64)
        self.assertTrue(product.is_intact)

    def test_a_change_written_behind_the_model_is_detectable(self):
        product = make_product(self.company)

        Product.objects.filter(pk=product.pk).update(name="A different product")
        product.refresh_from_db()

        self.assertFalse(product.is_intact)

    def test_an_attacker_holding_the_database_cannot_repair_the_signature(self):
        """The case a plain hash over these columns would not survive.

        Someone able to write to the table knows every input the signature
        covers, so with an unkeyed hash they could edit the row and recompute a
        matching value. The key is not in the database, so they cannot.
        """
        product = make_product(self.company)

        forged_columns = "|".join(
            [
                product.passport_code,
                str(product.company_id),
                product.product_type,
                "Sombrero de imitacion",
                "Sombreros",
                "Bogota",
            ]
        )
        recomputed_without_the_key = hashlib.sha256(forged_columns.encode()).hexdigest()

        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE products_product "
                "SET name = %s, origin = %s, integrity_hash = %s WHERE id = %s",
                ["Sombrero de imitacion", "Bogota", recomputed_without_the_key, product.pk],
            )

        product.refresh_from_db()
        self.assertEqual(product.name, "Sombrero de imitacion")
        self.assertFalse(product.is_intact)

    def test_the_signature_does_not_verify_under_another_key(self):
        product = make_product(self.company)

        with override_settings(SECRET_KEY="a-different-secret-key-entirely"):
            self.assertFalse(product.is_intact)

        self.assertTrue(product.is_intact)


class ProductTypeMatchesCompanyTests(TestCase):
    """A commercial company issues commercial originals, an artisan issues artisan pieces."""

    def test_an_artisan_company_cannot_issue_a_commercial_original(self):
        company = make_approved_company(company_type=CompanyType.ARTISAN)
        product = Product(
            company=company,
            product_type=ProductType.COMMERCIAL_ORIGINAL,
            name="Sombrero vueltiao",
            description="Hand woven.",
            category="Headwear",
            origin="Tuchin, Cordoba",
        )

        with self.assertRaises(ValidationError):
            product.clean()

    def test_a_matching_type_is_accepted(self):
        company = make_approved_company(company_type=CompanyType.ARTISAN)
        product = Product(
            company=company,
            product_type=ProductType.ARTISAN,
            name="Sombrero vueltiao",
            description="Hand woven.",
            category="Headwear",
            origin="Tuchin, Cordoba",
        )

        product.clean()


class CustodyChainTests(TestCase):
    """Only the current holder transfers, and a revoked product transfers to nobody."""

    def setUp(self):
        self.company = make_approved_company()
        self.admin = User.objects.create_superuser("admin@originpass.co", "Admin-Pass-2026")
        self.product = make_product(self.company)
        self.buyer = User.objects.create_user("buyer@example.co", "Buyer-Pass-2026")

    def test_the_first_holder_is_the_owner_of_the_registering_company(self):
        self.assertEqual(self.product.current_holder, self.company.owner)

    def test_an_accepted_transfer_moves_the_holder(self):
        transfer = CustodyTransfer.objects.create(
            product=self.product,
            from_holder=self.company.owner,
            to_holder=self.buyer,
        )
        transfer.accept()

        self.assertEqual(self.product.current_holder, self.buyer)

    def test_only_the_current_holder_can_transfer(self):
        stranger = User.objects.create_user("stranger@example.co", "Stranger-Pass-2026")
        transfer = CustodyTransfer(product=self.product, from_holder=stranger, to_holder=self.buyer)

        with self.assertRaises(ValidationError):
            transfer.clean()

    def test_a_revoked_product_accepts_no_transfer(self):
        self.product.revoke(actor=self.admin, reason="Reported as a counterfeit.")
        transfer = CustodyTransfer(
            product=self.product, from_holder=self.company.owner, to_holder=self.buyer
        )

        with self.assertRaises(ValidationError):
            transfer.clean()

    def test_a_resolved_transfer_cannot_be_rewritten(self):
        transfer = CustodyTransfer.objects.create(
            product=self.product,
            from_holder=self.company.owner,
            to_holder=self.buyer,
        )
        transfer.accept()

        transfer.note = "Rewritten after the fact"
        with self.assertRaises(ValueError):
            transfer.save()

    def test_the_database_refuses_a_transfer_that_changes_nothing(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            CustodyTransfer.objects.create(
                product=self.product,
                from_holder=self.company.owner,
                to_holder=self.company.owner,
            )


class CustodyChainIntegrityTests(TestCase):
    """One chain per product, and what shows when someone edits it with SQL."""

    def setUp(self):
        self.company = make_approved_company()
        self.product = make_product(self.company)
        self.first = User.objects.create_user("first@example.co", "First-Pass-2026")
        self.second = User.objects.create_user("second@example.co", "Second-Pass-2026")

        step_one = CustodyTransfer.objects.create(
            product=self.product, from_holder=self.company.owner, to_holder=self.first
        )
        step_one.accept()
        step_two = CustodyTransfer.objects.create(
            product=self.product, from_holder=self.first, to_holder=self.second
        )
        step_two.accept()

    def test_an_untouched_chain_verifies(self):
        ok, problem = CustodyTransfer.verify_chain(self.product)

        self.assertTrue(ok, problem)

    def test_each_handover_links_to_the_one_before_it(self):
        transfers = list(CustodyTransfer.objects.filter(product=self.product).order_by("id"))

        self.assertEqual(transfers[0].previous_hash, GENESIS)
        self.assertEqual(transfers[1].previous_hash, transfers[0].entry_hash)

    def test_rewriting_a_handover_with_raw_sql_is_detected(self):
        target = CustodyTransfer.objects.filter(product=self.product).order_by("id").first()

        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE products_custodytransfer SET to_holder_id = %s WHERE id = %s",
                [self.second.pk, target.pk],
            )

        ok, problem = CustodyTransfer.verify_chain(self.product)
        self.assertFalse(ok)
        self.assertIn("altered since it was written", problem)

    def test_removing_a_handover_from_the_middle_is_detected(self):
        target = CustodyTransfer.objects.filter(product=self.product).order_by("id").first()

        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM products_custodytransfer WHERE id = %s", [target.pk])

        ok, problem = CustodyTransfer.verify_chain(self.product)
        self.assertFalse(ok)
        self.assertIn("removed or reordered", problem)

    def test_resolving_a_transfer_is_written_into_the_audit_trail(self):
        """The state is outside the row's signature, so it is evidenced there."""
        actions = set(AuditEntry.objects.values_list("action", flat=True))

        self.assertIn(Action.CUSTODY_ACCEPTED, actions)

        ok, problem = AuditEntry.verify_chain()
        self.assertTrue(ok, problem)
