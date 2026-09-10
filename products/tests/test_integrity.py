"""The identifying fields of a passport are signed, so later tampering is detectable."""

import hashlib

from django.db import connection
from django.test import TestCase, override_settings

from products.models import Product
from test_support.factories import make_approved_company, make_product


class IntegrityHashTests(TestCase):
    def setUp(self):
        self.company = make_approved_company()

    def test_the_signature_is_written_on_registration(self):
        product = make_product(self.company)

        self.assertEqual(len(product.integrity_hash), 64)
        self.assertTrue(product.is_intact)

    def test_registering_a_passport_writes_the_row_once(self):
        """The signature is computed before the write, not patched in afterwards.

        Every field it covers is known before the row reaches the database, so
        a second UPDATE per registration buys nothing.
        """
        with self.assertNumQueries(1):
            make_product(self.company)

    def test_changing_one_column_carries_the_signature_with_it(self):
        """An edit through `update_fields` must not leave the row looking tampered with."""
        product = make_product(self.company)

        product.name = "Sombrero vueltiao 27 vueltas"
        product.save(update_fields=["name"])

        product.refresh_from_db()
        self.assertEqual(product.name, "Sombrero vueltiao 27 vueltas")
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
