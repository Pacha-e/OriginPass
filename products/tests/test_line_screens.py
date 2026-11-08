"""The artisan screens: products are lines in cards, and a line issues its passports.

The list shows one card per line with its counts; the line page holds the form that
issues passports and the link to print their QR codes. The register and custody
pages carry no tables and no technical words.
"""

# ---- External imports ----
from django.test import TestCase
from django.urls import reverse

# ---- Internal imports ----
from products.models import CustodyTransfer, Product
from test_support.factories import OWNER_PASSWORD, make_approved_company, make_product

# ---- Constants ----

#: The words the artisan screens must not use; the same list as the vocabulary test.
TECHNICAL_WORDS = ("criptogr", "custodia", "traspas", "revoc", "pieza")


class LineScreensTests(TestCase):
    def setUp(self):
        self.company = make_approved_company(email="weaver@tuchin.co")
        self.owner = self.company.owner
        self.client.login(email="weaver@tuchin.co", password=OWNER_PASSWORD)
        self.passport = make_product(self.company, name="Sombrero vueltiao 21 vueltas")
        self.line = self.passport.line

    def test_list_shows_lines_with_counts(self):
        self.line.issue_passports(2, self.owner)
        CustodyTransfer.record_handover(
            Product.objects.filter(line=self.line).first(),
            actor=self.owner,
            to_email="comprador@example.co",
        )

        response = self.client.get(reverse("products:product_list"))

        self.assertContains(response, "Pasaportes: 3 · Ya entregados: 1")
        self.assertContains(response, reverse("products:line_detail", args=[self.line.pk]), count=1)
        self.assertNotContains(response, "<table")

    def test_issue_form_creates_n(self):
        response = self.client.post(
            reverse("products:line_issue", args=[self.line.pk]), {"count": 5}
        )

        self.assertRedirects(response, reverse("products:line_detail", args=[self.line.pk]))
        self.assertEqual(self.line.passports.count(), 6)
        line_page = self.client.get(reverse("products:line_detail", args=[self.line.pk]))
        self.assertContains(line_page, f"{reverse('products:print_qr')}?line={self.line.pk}")

    def test_issue_rejects_out_of_range(self):
        for count in (0, 201):
            with self.subTest(count=count):
                self.client.post(
                    reverse("products:line_issue", args=[self.line.pk]), {"count": count}
                )

                self.assertEqual(self.line.passports.count(), 1)

    def test_line_of_another_company_is_404(self):
        other = make_approved_company(email="otro@barranquilla.co")
        other_line = make_product(other).line

        detail = self.client.get(reverse("products:line_detail", args=[other_line.pk]))
        issue = self.client.post(reverse("products:line_issue", args=[other_line.pk]), {"count": 3})

        self.assertEqual(detail.status_code, 404)
        self.assertEqual(issue.status_code, 404)
        self.assertEqual(other_line.passports.count(), 1)

    def test_origin_prefilled_from_company(self):
        response = self.client.get(reverse("products:product_create"))

        self.assertContains(response, f'value="{self.company.location}"')

    def test_print_qr_preselects_the_line(self):
        other_passport = make_product(self.company, name="Canasto de iraca")

        response = self.client.get(reverse("products:print_qr"), {"line": self.line.pk})

        self.assertContains(response, f'value="{self.passport.pk}" checked')
        self.assertNotContains(response, f'value="{other_passport.pk}" checked')

    def test_no_technical_words_on_product_pages(self):
        pages = (
            reverse("products:product_list"),
            reverse("products:line_detail", args=[self.line.pk]),
            reverse("products:product_create"),
            reverse("products:custody"),
        )
        for url in pages:
            with self.subTest(url=url):
                body = self.client.get(url, HTTP_ACCEPT_LANGUAGE="es").content.decode().lower()
                for word in TECHNICAL_WORDS:
                    self.assertNotIn(word, body)

    def test_custody_has_no_table(self):
        response = self.client.get(reverse("products:custody"))

        self.assertNotContains(response, "<table")
