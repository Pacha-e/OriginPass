"""An edit must not undo a revocation made while the form was open.

ProductForm saved every field, including the status the form loaded. A
revocation made in between would be overwritten, with the reason kept but the
passport back to ACTIVE.
"""

# ---- External imports ----
from django.test import TestCase

# ---- Internal imports ----
from products.forms import ProductForm
from products.models import Product, ProductStatus
from test_support.factories import make_admin, make_company, make_product, make_user


# ---- Public API ----
class StaleProductEditTests(TestCase):
    def setUp(self):
        owner = make_user(email="maker@tuchin.co")
        self.product = make_product(company=make_company(owner=owner, status="APPROVED"))
        self.admin = make_admin()

    def test_a_revocation_made_during_the_edit_survives_the_save(self):
        loaded = Product.objects.get(pk=self.product.pk)
        other = Product.objects.get(pk=self.product.pk)
        other.revoke(actor=self.admin, reason="Counterfeit reports")

        form = ProductForm(
            data={
                "name": "Sombrero vueltiao 21 vueltas, edicion",
                "description": "Hand woven over three weeks.",
                "category": "Headwear",
                "origin": "Tuchin, Cordoba",
            },
            instance=loaded,
        )
        self.assertTrue(form.is_valid(), form.errors)
        form.save()

        self.product.refresh_from_db()
        self.assertEqual(self.product.status, ProductStatus.REVOKED)
        self.assertEqual(self.product.revocation_reason, "Counterfeit reports")
        self.assertEqual(self.product.name, "Sombrero vueltiao 21 vueltas, edicion")
