"""FR22 - A downloadable PNG encoding the public verification address."""

# ---- External imports ----
import io

from django.test import TestCase
from django.urls import reverse

# ---- Internal imports ----
from products.qr import passport_qr_image
from test_support.factories import OWNER_PASSWORD, make_approved_company, make_product


# ---- Public API ----
class QrCodeTests(TestCase):
    def setUp(self):
        self.company = make_approved_company(email="weaver@tuchin.co")
        self.product = make_product(self.company)
        self.client.login(email="weaver@tuchin.co", password=OWNER_PASSWORD)
        self.url = reverse("products:qr_download", args=[self.product.pk])

    def test_a_company_cannot_download_the_qr_of_another(self):
        make_approved_company(email="otro@barranquilla.co")
        self.client.login(email="otro@barranquilla.co", password=OWNER_PASSWORD)

        self.assertEqual(self.client.get(self.url).status_code, 404)

    def test_the_image_is_the_passport_code_with_the_mark(self):
        """Compared against the image the shared builder makes for the same address."""
        response = self.client.get(self.url)

        address = "http://testserver" + reverse(
            "verification:verify", args=[self.product.passport_code]
        )
        expected = io.BytesIO()
        passport_qr_image(address).save(expected, format="PNG")

        self.assertEqual(response.content, expected.getvalue())

    def test_the_response_is_a_png_offered_as_a_download(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/png")
        self.assertIn("attachment", response["Content-Disposition"])
        self.assertTrue(response.content.startswith(b"\x89PNG\r\n\x1a\n"))
