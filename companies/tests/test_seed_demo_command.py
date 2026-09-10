"""The demo dataset used for the deliverable walkthrough.

It is also what is shown when someone asks to see the data, so it has to cover
what the current sprint built rather than only what the first one did.
"""

from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

from companies.models import Company, CompanyStatus
from products.models import PRODUCT_TYPE_BY_COMPANY_TYPE, Product, ProductStatus
from verification.models import ScanEvent


class SeedDemoCommandTests(TestCase):
    @override_settings(DEBUG=True)
    def test_it_creates_one_company_in_each_status(self):
        call_command("seed_demo", stdout=StringIO())

        statuses = set(Company.objects.values_list("status", flat=True))

        self.assertEqual(statuses, {value for value, _ in CompanyStatus.choices})

    @override_settings(DEBUG=True)
    def test_running_it_twice_creates_nothing_new(self):
        call_command("seed_demo", stdout=StringIO())
        before = Company.objects.count()

        call_command("seed_demo", stdout=StringIO())

        self.assertEqual(Company.objects.count(), before)

    @override_settings(DEBUG=False)
    def test_it_refuses_to_run_with_debug_off(self):
        """Every account it creates shares one known password."""
        with self.assertRaises(CommandError):
            call_command("seed_demo", stdout=StringIO())

        self.assertFalse(Company.objects.exists())


@override_settings(DEBUG=True)
class SeedDemoPassportsTests(TestCase):
    """The dataset covers Sprint 2, not only Sprint 1."""

    def setUp(self):
        call_command("seed_demo", stdout=StringIO())

    def test_it_issues_passports(self):
        self.assertGreater(Product.objects.count(), 0)

    def test_every_passport_belongs_to_an_approved_company(self):
        statuses = {product.company.status for product in Product.objects.select_related("company")}

        self.assertEqual(statuses, {CompanyStatus.APPROVED})

    def test_every_passport_type_matches_its_company(self):
        """FR23 holds for seeded rows too, which is where a crossed pair would hide."""
        for product in Product.objects.select_related("company"):
            with self.subTest(product=product.name):
                expected = PRODUCT_TYPE_BY_COMPANY_TYPE[product.company.company_type]
                self.assertEqual(product.product_type, expected)

    def test_it_includes_a_revoked_passport_so_that_verdict_can_be_shown(self):
        revoked = Product.objects.filter(status=ProductStatus.REVOKED)

        self.assertTrue(revoked.exists())
        self.assertTrue(all(product.revocation_reason for product in revoked))

    def test_it_records_a_history_of_verifications(self):
        self.assertGreater(ScanEvent.objects.count(), 0)

    def test_running_it_twice_issues_nothing_new(self):
        before = Product.objects.count()

        call_command("seed_demo", stdout=StringIO())

        self.assertEqual(Product.objects.count(), before)
