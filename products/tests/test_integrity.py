"""The identifying fields of a passport are signed, so later tampering is detectable."""

import hashlib

from django.db import connection
from django.test import TestCase, override_settings

from products.models import Product
from testing.factories import make_approved_company, make_product


class IntegrityHashTests(TestCase):
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
