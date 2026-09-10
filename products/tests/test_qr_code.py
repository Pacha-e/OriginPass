"""FR22 - A downloadable PNG encoding the public verification address."""

import io

import qrcode
from django.test import TestCase
from django.urls import reverse

from test_support.factories import OWNER_PASSWORD, make_approved_company, make_product


class QrCodeTests(TestCase):
    def setUp(self):
        self.company = make_approved_company(email="weaver@tuchin.co")
        self.product = make_product(self.company)
        self.client.login(email="weaver@tuchin.co", password=OWNER_PASSWORD)
        self.url = reverse("products:qr_download", args=[self.product.pk])

    def test_the_response_is_a_png_offered_as_a_download(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/png")
        self.assertIn("attachment", response["Content-Disposition"])
        self.assertTrue(response.content.startswith(b"\x89PNG\r\n\x1a\n"))

    def test_the_image_encodes_the_verification_address(self):
        """Compared against the image the address produces, so no decoder is needed."""
        response = self.client.get(self.url)

        address = "http://testserver" + reverse(
            "verification:verify", args=[self.product.passport_code]
        )
        expected = io.BytesIO()
        qrcode.make(address).save(expected, format="PNG")

        self.assertEqual(response.content, expected.getvalue())

    def test_a_company_cannot_download_the_qr_of_another(self):
        make_approved_company(email="otro@barranquilla.co")
        self.client.login(email="otro@barranquilla.co", password=OWNER_PASSWORD)

        self.assertEqual(self.client.get(self.url).status_code, 404)
