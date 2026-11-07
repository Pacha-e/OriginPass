"""The receive page can read a product QR with the camera, and ships what that needs.

The camera only works on HTTPS, so the reader is offered only where the browser
allows it; on plain HTTP the page keeps the typed field.
"""

# ---- External imports ----
from django.contrib.staticfiles import finders
from django.test import TestCase
from django.urls import reverse

# ---- Internal imports ----
from test_support.factories import make_product, make_user


# ---- Public API ----
class ClaimScannerTests(TestCase):
    def setUp(self):
        self.client.force_login(make_user(email="buyer@example.com"))
        self.response = self.client.get(reverse("products:receive_start"))

    def test_the_page_offers_the_camera_reader_hidden_until_the_browser_allows_it(self):
        self.assertContains(self.response, "data-scanner-start")
        self.assertContains(self.response, "data-scanner-field")

    def test_the_page_loads_the_reader_and_its_script(self):
        self.assertContains(self.response, "vendor/jsqr/jsQR.js")
        self.assertContains(self.response, "js/passport-scanner.js")

    def test_the_page_accepts_a_photo_of_the_qr_that_is_read_in_the_browser(self):
        self.assertContains(self.response, 'type="file"')
        self.assertContains(self.response, 'accept="image/*"')
        self.assertContains(self.response, "data-scanner-photo")

    def test_the_shipped_files_exist(self):
        self.assertIsNotNone(finders.find("vendor/jsqr/jsQR.js"))
        self.assertIsNotNone(finders.find("js/passport-scanner.js"))


class ReceiveStartTests(TestCase):
    def setUp(self):
        self.client.force_login(make_user(email="buyer@example.com"))
        self.product = make_product()

    def test_a_typed_code_leads_to_the_product(self):
        response = self.client.get(
            reverse("products:receive_start"), {"code": self.product.passport_code}
        )
        self.assertRedirects(
            response,
            reverse("products:receive", args=[self.product.passport_code]),
            fetch_redirect_response=False,
        )

    def test_the_whole_address_read_from_the_qr_also_works(self):
        address = "https://originpass.example/v/" + self.product.passport_code + "/"
        response = self.client.get(reverse("products:receive_start"), {"code": address})
        self.assertEqual(
            response["Location"], reverse("products:receive", args=[self.product.passport_code])
        )

    def test_an_unknown_code_is_explained(self):
        response = self.client.get(reverse("products:receive_start"), {"code": "no-existe"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ningún producto tiene ese código")
