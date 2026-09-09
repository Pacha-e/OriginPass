"""DBR10 - The lookup is served by the index on the passport code.

Where an issue states a time bound, the test measures the lookup and asserts it.
"""

from django.test import TestCase
from django.urls import reverse

from products.models import Product
from testing.factories import make_product
from testing.timing import measure

#: Enough rows that a sequential scan would show against an index lookup.
FILLER_ROWS = 200


class PassportLookupTests(TestCase):
    def test_the_passport_code_is_indexed(self):
        field = Product._meta.get_field("passport_code")

        self.assertTrue(field.db_index)
        self.assertTrue(field.unique)

    def test_the_lookup_completes_well_inside_the_bound(self):
        product = make_product()
        for number in range(FILLER_ROWS):
            make_product(product.company, name=f"Filler {number}", category="Filler")

        _, seconds = measure(lambda: Product.objects.get(passport_code=product.passport_code))

        self.assertLess(seconds, 0.2, f"the lookup took {seconds * 1000:.1f}ms")


class LookupFormTests(TestCase):
    """Typing a code by hand, for a QR that will not scan."""

    def test_the_form_is_reachable_without_an_account(self):
        self.assertEqual(self.client.get(reverse("verification:lookup")).status_code, 200)

    def test_a_submitted_code_goes_to_its_verdict(self):
        response = self.client.get(reverse("verification:lookup"), {"code": "abc123"})

        self.assertRedirects(
            response,
            reverse("verification:verify", args=["abc123"]),
            fetch_redirect_response=False,
        )
