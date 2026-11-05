"""FR22 extension: a downloadable photo of the product with its passport QR on it.

The owner gets the photograph with the code in one corner, ready to post or print.
A passport without a photograph still gets a card: the code on white.
"""

# ---- External imports ----
import io
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

# ---- Internal imports ----
from test_support.factories import OWNER_PASSWORD, make_approved_company, make_product


def _photo_bytes(size=(800, 600)):
    buffer = io.BytesIO()
    Image.new("RGB", size, (200, 120, 60)).save(buffer, format="JPEG")
    return buffer.getvalue()


# ---- Public API ----
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class QrCardTests(TestCase):
    def setUp(self):
        self.company = make_approved_company(email="weaver@tuchin.co")
        self.client.login(email="weaver@tuchin.co", password=OWNER_PASSWORD)

    def _card(self, product):
        return self.client.get(reverse("products:qr_card_download", args=[product.pk]))

    def test_the_card_is_the_photograph_with_the_code_on_it(self):
        product = make_product(self.company)
        product.image.save("bolso.jpg", SimpleUploadedFile("bolso.jpg", _photo_bytes()))

        response = self._card(product)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/png")
        card = Image.open(io.BytesIO(response.content))
        self.assertEqual(card.size, (800, 600))

    def test_a_passport_without_a_photograph_still_gets_a_card(self):
        product = make_product(self.company)

        response = self._card(product)

        self.assertEqual(response.status_code, 200)
        card = Image.open(io.BytesIO(response.content))
        self.assertEqual(card.size[0], card.size[1])

    def test_a_company_cannot_download_the_card_of_another(self):
        other = make_approved_company(email="otro@barranquilla.co")
        product = make_product(other)

        self.assertEqual(self._card(product).status_code, 404)
