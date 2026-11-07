"""A product is registered once as a line; each passport belongs to its line."""

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TestCase, TransactionTestCase

from audit.integrity import sign
from products.models import Product, ProductLine
from test_support.factories import make_approved_company, make_product

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
