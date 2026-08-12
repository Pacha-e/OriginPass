"""Invariants of the product tables created in Sprint 1.

The views that exercise these belong to later sprints; the rules are in place
from now, which is what DBR12 asks for on the revocation side.
"""

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from accounts.models import User
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
    """The identifying fields are hashed, so later tampering is detectable."""

    def setUp(self):
        self.company = make_approved_company()

    def test_the_hash_is_written_on_registration(self):
        product = make_product(self.company)

        self.assertEqual(len(product.integrity_hash), 64)
        self.assertTrue(product.is_intact)

    def test_a_change_written_behind_the_model_is_detectable(self):
        product = make_product(self.company)

        Product.objects.filter(pk=product.pk).update(name="A different product")
        product.refresh_from_db()

        self.assertFalse(product.is_intact)


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
