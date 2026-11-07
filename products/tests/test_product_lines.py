"""A product is registered once as a line; each passport belongs to its line."""

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TestCase, TransactionTestCase

from audit.integrity import sign
from audit.models import Action, AuditEntry
from companies.models import CompanyStatus
from products.models import PRODUCT_TYPE_BY_COMPANY_TYPE, Product, ProductLine
from test_support.factories import make_approved_company, make_company, make_product

BEFORE = [("products", "0008_resign_products_with_status")]
AFTER = [("products", "0011_product_line_required")]


class ExistingProductsMigrationTests(TransactionTestCase):
    """Run against the real migrations, from before lines existed to after."""

    def setUp(self):
        executor = MigrationExecutor(connection)
        executor.migrate(BEFORE)
        old_apps = executor.loader.project_state(BEFORE).apps
        Company = old_apps.get_model("companies", "Company")
        OldProduct = old_apps.get_model("products", "Product")

        company = make_approved_company()
        old_company = Company.objects.get(pk=company.pk)
        for name in ("Sombrero vueltiao 21 vueltas", "Mochila wayuu"):
            product = OldProduct(
                company=old_company,
                product_type="ARTISAN",
                name=name,
                description="Hecho a mano.",
                category="Artesanía",
                origin="Tuchín, Córdoba",
                status="ACTIVE",
            )
            product.integrity_hash = sign(
                product.passport_code,
                product.company_id,
                product.product_type,
                product.name,
                product.category,
                product.origin,
                product.status,
            )
            product.save()

        executor = MigrationExecutor(connection)
        executor.loader.build_graph()
        executor.migrate(AFTER)

    def tearDown(self):
        MigrationExecutor(connection).migrate(
            MigrationExecutor(connection).loader.graph.leaf_nodes()
        )

    def test_every_existing_product_gets_its_own_line(self):
        products = list(Product.objects.order_by("name"))
        self.assertEqual(ProductLine.objects.count(), 2)
        for product in products:
            self.assertEqual(product.line.name, product.name)
            self.assertEqual(product.line.company_id, product.company_id)
            self.assertTrue(product.is_intact)


def make_line(company=None, **overrides):
    company = company or make_approved_company()
    fields = {
        "product_type": PRODUCT_TYPE_BY_COMPANY_TYPE[company.company_type],
        "name": "Sombrero vueltiao 24 vueltas",
        "description": "Tejido en caña flecha.",
        "category": "Sombreros",
        "origin": "Tuchín, Córdoba",
    }
    fields.update(overrides)
    return ProductLine.objects.create(company=company, **fields)


class IssuePassportsTests(TestCase):
    def test_issue_twenty_passports_copies_the_line(self):
        line = make_line()

        passports = line.issue_passports(20, actor=line.company.owner)

        self.assertEqual(len(passports), 20)
        self.assertEqual(len({passport.passport_code for passport in passports}), 20)
        for passport in passports:
            passport.refresh_from_db()
            self.assertEqual(passport.line_id, line.pk)
            self.assertEqual(passport.name, line.name)
            self.assertEqual(passport.origin, line.origin)
            self.assertTrue(passport.is_intact)
        self.assertEqual(AuditEntry.objects.filter(action=Action.PRODUCT_REGISTERED).count(), 20)

    def test_issue_rejects_zero_and_201(self):
        line = make_line()
        for count in (0, 201):
            with self.assertRaises(ValueError):
                line.issue_passports(count, actor=line.company.owner)
        self.assertFalse(line.passports.exists())

    def test_issue_refused_for_unapproved_company(self):
        line = make_line(make_company(status=CompanyStatus.SUSPENDED))
        with self.assertRaises(ValueError):
            line.issue_passports(1, actor=line.company.owner)

    def test_editing_line_does_not_alter_issued_passports(self):
        line = make_line()
        [passport] = line.issue_passports(1, actor=line.company.owner)

        line.name = "Sombrero vueltiao 27 vueltas"
        line.save()

        passport.refresh_from_db()
        self.assertEqual(passport.name, "Sombrero vueltiao 24 vueltas")
        self.assertTrue(passport.is_intact)


class LineOfNewProductTests(TestCase):
    def test_product_saved_without_a_line_gets_one_of_its_own(self):
        product = make_product()
        self.assertEqual(product.line.name, product.name)
        self.assertEqual(product.line.origin, product.origin)
        self.assertTrue(product.is_intact)

    def test_line_is_not_part_of_the_passport_signature(self):
        product = make_product()
        self.assertEqual(
            product.signed_parts(),
            (
                product.passport_code,
                product.company_id,
                product.product_type,
                product.name,
                product.category,
                product.origin,
                product.status,
            ),
        )
