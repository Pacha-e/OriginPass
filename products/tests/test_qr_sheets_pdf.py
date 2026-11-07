"""The printable QR sheets: the owner's picker, the PDF of Letter pages and the export command."""

# ---- External imports ----
import re
import tempfile
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

# ---- Internal imports ----
from test_support.factories import make_admin, make_approved_company, make_product, make_user

# ---- Private helpers ----


def _pdf_page_count(data):
    """Pillow cannot open a PDF, so the pages are counted in the file itself."""
    return len(re.findall(rb"/Type\s*/Page(?!s)", data))


# ---- Public API ----


class PrintQrTests(TestCase):
    def setUp(self):
        self.owner = make_user(email="maker@tuchin.co")
        self.company = make_approved_company(owner=self.owner)
        self.client.force_login(self.owner)
        self.url = reverse("products:print_qr")

    def test_thirteen_passports_make_two_pages(self):
        ids = [make_product(company=self.company, name=f"Producto {n}").pk for n in range(13)]

        response = self.client.post(self.url, {"product": ids})

        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertEqual(
            response["Content-Disposition"], 'attachment; filename="originpass-qr.pdf"'
        )
        self.assertEqual(_pdf_page_count(response.content), 2)

    def test_foreign_product_ids_refused(self):
        foreign = make_product(
            company=make_approved_company(owner=make_user(email="other@tuchin.co"))
        )
        own = make_product(company=self.company)

        mixed = self.client.post(self.url, {"product": [own.pk, foreign.pk]})

        self.assertEqual(mixed["Content-Type"], "application/pdf")
        self.assertEqual(_pdf_page_count(mixed.content), 1)

        only_foreign = self.client.post(self.url, {"product": [foreign.pk]})

        self.assertEqual(only_foreign.status_code, 200)
        self.assertTrue(only_foreign["Content-Type"].startswith("text/html"))

    def test_an_impossible_id_is_ignored_not_an_error(self):
        own = make_product(company=self.company)

        response = self.client.post(self.url, {"product": ["9" * 40, own.pk]})

        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertEqual(_pdf_page_count(response.content), 1)

    def test_get_lists_products_grouped_by_line(self):
        bag = make_product(company=self.company, name="Mochila wayuu")
        bag_twin = make_product(company=self.company, line=bag.line, name="Mochila wayuu")
        hat = make_product(company=self.company, name="Sombrero vueltiao")
        revoked = make_product(company=self.company, name="Sombrero retirado")
        revoked.revoke(actor=make_admin(), reason="Counterfeit reports")

        response = self.client.get(self.url)

        groups = response.context["groups"]
        self.assertEqual(
            [line.name for line, _products in groups],
            ["Mochila wayuu", "Sombrero vueltiao"],
        )
        self.assertEqual(
            sorted(product.pk for product in groups[0][1]), sorted([bag.pk, bag_twin.pk])
        )
        self.assertEqual([product.pk for product in groups[1][1]], [hat.pk])
        self.assertContains(response, f'name="product" value="{hat.pk}"')
        self.assertNotContains(response, f'name="product" value="{revoked.pk}"')


class ExportCommandStillWritesSheetsTests(TestCase):
    def test_command_still_writes_png_sheets(self):
        product = make_product(company=make_approved_company(owner=make_user()))

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            call_command(
                "export_passport_qr",
                "--base-url",
                "http://54.12.34.56",
                "--output",
                str(output),
                stdout=StringIO(),
            )

            self.assertTrue((output / f"qr-{product.passport_code}.png").is_file())
            self.assertTrue((output / "hoja-qr-1.png").is_file())
