"""Acceptance criteria of FR24, FR25 and FR26: a company's own passports.

Where an issue states a time bound, the test measures the response and asserts it.
"""

from django.test import TestCase
from django.urls import reverse

from products.models import ProductStatus
from test_support.factories import OWNER_PASSWORD, make_admin, make_approved_company, make_product
from test_support.timing import measure

VALID_PRODUCT = {
    "name": "Sombrero vueltiao 21 vueltas",
    "description": "Hand woven over three weeks.",
    "category": "Headwear",
    "origin": "Tuchin, Cordoba",
}


class ProductListTests(TestCase):
    """FR24 list filtered by status, FR25 search by name, category or code."""

    def setUp(self):
        self.company = make_approved_company(email="weaver@tuchin.co")
        self.hat = make_product(self.company, name="Sombrero vueltiao", category="Headwear")
        self.basket = make_product(
            self.company,
            name="Canasto de iraca",
            description="Woven palm.",
            category="Basketry",
            origin="Usiacuri, Atlantico",
            status=ProductStatus.REVOKED,
            revocation_reason="Reported as a copy.",
        )
        self.client.login(email="weaver@tuchin.co", password=OWNER_PASSWORD)

    def test_the_list_shows_the_products_of_this_company(self):
        response = self.client.get(reverse("products:product_list"))

        self.assertContains(response, "Sombrero vueltiao")
        self.assertContains(response, "Canasto de iraca")

    def test_the_list_hides_the_products_of_another_company(self):
        other = make_approved_company(email="otro@barranquilla.co")
        make_product(other, name="Mochila arhuaca", category="Bags", origin="Nabusimake, Cesar")

        response = self.client.get(reverse("products:product_list"))

        self.assertNotContains(response, "Mochila arhuaca")

    def test_the_list_filters_by_status(self):
        response = self.client.get(reverse("products:product_list"), {"status": "REVOKED"})

        self.assertContains(response, "Canasto de iraca")
        self.assertNotContains(response, "Sombrero vueltiao")

    def test_the_search_matches_a_name(self):
        response = self.client.get(reverse("products:product_list"), {"q": "vueltiao"})

        self.assertContains(response, "Sombrero vueltiao")
        self.assertNotContains(response, "Canasto de iraca")

    def test_the_search_matches_a_category(self):
        response = self.client.get(reverse("products:product_list"), {"q": "Basketry"})

        self.assertContains(response, "Canasto de iraca")
        self.assertNotContains(response, "Sombrero vueltiao")

    def test_the_search_matches_a_passport_code(self):
        response = self.client.get(reverse("products:product_list"), {"q": self.hat.passport_code})

        self.assertContains(response, "Sombrero vueltiao")
        self.assertNotContains(response, "Canasto de iraca")

    def test_the_list_answers_within_three_seconds(self):
        """FR24 states the bound, so it is measured rather than assumed."""
        _, seconds = measure(lambda: self.client.get(reverse("products:product_list")))

        self.assertLess(seconds, 3.0, f"the list took {seconds:.3f}s")


class ProductEditTests(TestCase):
    """FR26: the descriptive fields change, the passport code does not."""

    def setUp(self):
        self.company = make_approved_company(email="weaver@tuchin.co")
        self.product = make_product(self.company, **VALID_PRODUCT)
        self.client.login(email="weaver@tuchin.co", password=OWNER_PASSWORD)

    def test_editing_changes_the_description_and_keeps_the_code(self):
        original_code = self.product.passport_code

        self.client.post(
            reverse("products:product_edit", args=[self.product.pk]),
            {**VALID_PRODUCT, "description": "Hand woven over four weeks."},
        )

        self.product.refresh_from_db()
        self.assertEqual(self.product.description, "Hand woven over four weeks.")
        self.assertEqual(self.product.passport_code, original_code)

    def test_a_revoked_passport_is_not_edited(self):
        self.product.revoke(actor=make_admin(), reason="Reported as a copy.")

        response = self.client.get(reverse("products:product_edit", args=[self.product.pk]))

        self.assertEqual(response.status_code, 403)

    def test_a_suspended_company_is_refused_rather_than_crashed_into(self):
        """Suspension is the one way a passport outlives its company's approval.

        A company is only approved when it registers a passport, and the only
        transition out of approved is suspension, so this is the single state
        in which an owner can open the edit page for a passport its company may
        no longer act on. The refusal has to be stated, because the alternative
        is the model's own rule reaching a form that has no field to attach it
        to.
        """
        self.company.suspend(actor=make_admin(), reason="Under investigation.")

        response = self.client.post(
            reverse("products:product_edit", args=[self.product.pk]),
            {**VALID_PRODUCT, "description": "Rewritten while suspended."},
        )

        self.assertEqual(response.status_code, 403)
        self.product.refresh_from_db()
        self.assertEqual(self.product.description, VALID_PRODUCT["description"])

    def test_a_company_cannot_edit_the_product_of_another(self):
        make_approved_company(email="otro@barranquilla.co")
        self.client.login(email="otro@barranquilla.co", password=OWNER_PASSWORD)

        response = self.client.get(reverse("products:product_edit", args=[self.product.pk]))

        self.assertEqual(response.status_code, 404)
