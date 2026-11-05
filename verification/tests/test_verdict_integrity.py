"""The public verdict must not trust a row whose signature no longer matches (FR28-FR31).

The status a passport shows is part of what the signature covers. A row changed
directly in the database, say from REVOKED back to ACTIVE, must not read as
GENUINE, and must not be trusted for any other verdict either.
"""

# ---- External imports ----
from django.test import TestCase
from django.urls import reverse

# ---- Internal imports ----
from products.models import Product, ProductStatus
from test_support.factories import make_admin, make_company, make_product, make_user
from verification.models import Verdict


# ---- Public API ----
class VerdictIntegrityTests(TestCase):
    def setUp(self):
        owner = make_user(email="maker@tuchin.co")
        self.product = make_product(company=make_company(owner=owner, status="APPROVED"))
        self.admin = make_admin()

    def _verdict(self):
        response = self.client.get(
            reverse("verification:verify", args=[self.product.passport_code])
        )
        return response.context["verdict"]

    def test_a_revoked_passport_reads_revoked(self):
        self.product.revoke(actor=self.admin, reason="Counterfeit reports")

        self.assertEqual(self._verdict(), Verdict.REVOKED)

    def test_a_revoked_passport_is_still_intact_after_the_revocation(self):
        self.product.revoke(actor=self.admin, reason="Counterfeit reports")

        self.product.refresh_from_db()
        self.assertTrue(self.product.is_intact)

    def test_a_status_changed_directly_in_the_database_is_not_genuine(self):
        self.product.revoke(actor=self.admin, reason="Counterfeit reports")
        Product.objects.filter(pk=self.product.pk).update(status=ProductStatus.ACTIVE)

        self.assertEqual(self._verdict(), Verdict.ALTERED)

    def test_an_identifying_field_changed_directly_in_the_database_is_altered(self):
        Product.objects.filter(pk=self.product.pk).update(name="Forged name")

        self.assertEqual(self._verdict(), Verdict.ALTERED)
