"""Invariants of the passport itself: its code, its revocation and its type.

These hold however the row was written, so the ones the database can express are
also checked from behind the model with `update()`.
"""

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase

from companies.models import CompanyType
from products.models import Product, ProductStatus, ProductType
from test_support.factories import make_admin, make_approved_company, make_product


class ProductRecordTests(TestCase):
    """DBR02 - Store the product record."""

    #: Every field the Domain Model wiki page lists for Product.
    DOMAIN_MODEL_FIELDS = {
        "company",
        "passport_code",
        "product_type",
        "status",
        "name",
        "description",
        "category",
        "origin",
        "image",
        "integrity_hash",
        "revocation_reason",
        "registered_at",
        "updated_at",
    }

    def test_the_model_holds_every_field_listed_in_the_domain_model(self):
        declared = {field.name for field in Product._meta.get_fields()}

        self.assertTrue(self.DOMAIN_MODEL_FIELDS.issubset(declared))

    def test_the_registration_timestamp_is_set_on_creation(self):
        self.assertIsNotNone(make_product().registered_at)


class ProductBelongsToACompanyTests(TestCase):
    """DBR04 - Enforce the product to company reference."""

    def test_every_product_names_the_company_that_issued_it(self):
        company = make_approved_company()

        self.assertEqual(make_product(company).company, company)

    def test_a_company_with_passports_cannot_be_deleted(self):
        """The reference is PROTECT: deleting the issuer would orphan its passports."""
        product = make_product()

        with self.assertRaises(ProtectedError), transaction.atomic():
            product.company.delete()

        self.assertTrue(Product.objects.filter(pk=product.pk).exists())


class RevocationReasonTests(TestCase):
    """DBR12 - Require a reason on negative decisions (product side)."""

    def setUp(self):
        self.admin = make_admin()
        self.product = make_product()

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
    """FR21 - A code that cannot be derived from another code."""

    def setUp(self):
        self.company = make_approved_company()

    def test_each_product_gets_its_own_code(self):
        first = make_product(self.company)
        second = make_product(self.company)

        self.assertNotEqual(first.passport_code, second.passport_code)
        self.assertGreaterEqual(len(first.passport_code), 24)

    def test_the_code_is_unique_across_the_table(self):
        """DBR03 - Enforce passport code uniqueness."""
        first = make_product(self.company)

        with self.assertRaises(IntegrityError), transaction.atomic():
            make_product(self.company, passport_code=first.passport_code)


class ProductTypeMatchesCompanyTests(TestCase):
    """FR23 - A commercial company issues commercial originals, an artisan issues artisan pieces."""

    def setUp(self):
        self.artisan_company = make_approved_company(company_type=CompanyType.ARTISAN)

    def _unsaved(self, product_type):
        return Product(
            company=self.artisan_company,
            product_type=product_type,
            name="Sombrero vueltiao",
            description="Hand woven.",
            category="Headwear",
            origin="Tuchin, Cordoba",
        )

    def test_an_artisan_company_cannot_issue_a_commercial_original(self):
        with self.assertRaises(ValidationError):
            self._unsaved(ProductType.COMMERCIAL_ORIGINAL).clean()

    def test_a_matching_type_is_accepted(self):
        self._unsaved(ProductType.ARTISAN).clean()
