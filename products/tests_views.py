"""The Sprint 2 product views, one or more tests per acceptance criterion.

The invariants these views rest on are tested in `tests.py`, which was written
in Sprint 1. What is tested here is the behaviour a person can see: who may
register a passport, what the refusal says, what the list shows, and that the
QR image encodes the address it claims to.
"""

import io
import time

import qrcode
from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from audit.models import Action, AuditEntry
from companies.models import Company, CompanyStatus, CompanyType, VerificationTrack

from .forms import ProductForm
from .models import Product, ProductStatus, ProductType

PASSWORD = "Vueltiao-2026"


def make_company(email, status=CompanyStatus.APPROVED, company_type=CompanyType.COMMERCIAL):
    owner = User.objects.create_user(email, PASSWORD)
    is_commercial = company_type == CompanyType.COMMERCIAL
    return Company.objects.create(
        owner=owner,
        legal_name="Artesanias La Bonga SAS",
        company_type=company_type,
        verification_track=(
            VerificationTrack.CHAMBER_OF_COMMERCE
            if is_commercial
            else VerificationTrack.ARTISAN_REVIEW
        ),
        registry_code="NIT-900123456-7" if is_commercial else "",
        description="Crafts from Cordoba.",
        location="Monteria, Cordoba",
        status=status,
        status_reason="Not enough evidence." if status != CompanyStatus.APPROVED else "",
    )


VALID_PRODUCT = {
    "name": "Sombrero vueltiao 21 vueltas",
    "description": "Hand woven over three weeks.",
    "category": "Headwear",
    "origin": "Tuchin, Cordoba",
}


class ProductRegistrationTests(TestCase):
    """FR19 register a product, FR20 refuse an unapproved company, FR21, FR23."""

    def setUp(self):
        self.company = make_company("weaver@tuchin.co")
        self.client.login(email="weaver@tuchin.co", password=PASSWORD)

    def test_an_approved_company_registers_a_product(self):
        response = self.client.post(reverse("products:product_create"), VALID_PRODUCT)

        product = Product.objects.get(name=VALID_PRODUCT["name"])
        self.assertRedirects(response, reverse("products:product_detail", args=[product.pk]))
        self.assertEqual(product.company, self.company)
        self.assertEqual(product.origin, "Tuchin, Cordoba")
        self.assertEqual(product.status, ProductStatus.ACTIVE)

    def test_registration_generates_a_passport_code(self):
        """FR21: the code is issued by the system, never supplied by the form."""
        self.client.post(reverse("products:product_create"), VALID_PRODUCT)
        product = Product.objects.get(name=VALID_PRODUCT["name"])

        self.assertTrue(product.passport_code)
        self.assertNotIn("passport_code", ProductForm().fields)

    def test_the_product_type_follows_the_company_type(self):
        """FR23: a commercial company issues commercial originals."""
        self.client.post(reverse("products:product_create"), VALID_PRODUCT)
        product = Product.objects.get(name=VALID_PRODUCT["name"])

        self.assertEqual(product.product_type, ProductType.COMMERCIAL_ORIGINAL)
        self.assertNotIn("product_type", ProductForm().fields)

    def test_an_artisan_company_issues_artisan_pieces(self):
        make_company("taller@tuchin.co", company_type=CompanyType.ARTISAN)
        self.client.login(email="taller@tuchin.co", password=PASSWORD)

        self.client.post(reverse("products:product_create"), VALID_PRODUCT)
        product = Product.objects.get(company__owner__email="taller@tuchin.co")

        self.assertEqual(product.product_type, ProductType.ARTISAN)

    def test_registration_is_written_into_the_audit_trail(self):
        self.client.post(reverse("products:product_create"), VALID_PRODUCT)
        product = Product.objects.get(name=VALID_PRODUCT["name"])

        entry = AuditEntry.objects.get(target_type="Product", target_id=product.pk)
        self.assertEqual(entry.action, Action.PRODUCT_REGISTERED)
        self.assertEqual(entry.actor, self.company.owner)

    def test_registration_keeps_to_five_required_fields(self):
        """UR10: at most five fields are marked as required."""
        required = [name for name, field in ProductForm().fields.items() if field.required]
        self.assertLessEqual(len(required), 5, f"required fields: {required}")

    def test_the_form_refuses_a_product_with_no_origin(self):
        response = self.client.post(
            reverse("products:product_create"), {**VALID_PRODUCT, "origin": "   "}
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Product.objects.exists())

    def test_an_anonymous_visitor_cannot_register(self):
        self.client.logout()
        response = self.client.get(reverse("products:product_create"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)


class RegistrationRefusalTests(TestCase):
    """FR20: a company that is not Approved is refused, and told why."""

    def _attempt(self, status):
        make_company(f"{status.lower()}@tuchin.co", status=status)
        self.client.login(email=f"{status.lower()}@tuchin.co", password=PASSWORD)
        return self.client.post(reverse("products:product_create"), VALID_PRODUCT)

    def test_a_pending_company_is_refused_with_the_reason(self):
        response = self._attempt(CompanyStatus.PENDING)

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "still being reviewed", status_code=403)
        self.assertFalse(Product.objects.exists())

    def test_a_rejected_company_is_refused_with_the_reason(self):
        response = self._attempt(CompanyStatus.REJECTED)

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "rejected", status_code=403)
        self.assertFalse(Product.objects.exists())

    def test_a_suspended_company_is_refused_with_the_reason(self):
        response = self._attempt(CompanyStatus.SUSPENDED)

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "suspended", status_code=403)
        self.assertFalse(Product.objects.exists())


class ProductListTests(TestCase):
    """FR24 list filtered by status, FR25 search by name, category or code."""

    def setUp(self):
        self.company = make_company("weaver@tuchin.co")
        self.hat = Product.objects.create(
            company=self.company,
            product_type=ProductType.COMMERCIAL_ORIGINAL,
            name="Sombrero vueltiao",
            description="Hand woven.",
            category="Headwear",
            origin="Tuchin, Cordoba",
        )
        self.basket = Product.objects.create(
            company=self.company,
            product_type=ProductType.COMMERCIAL_ORIGINAL,
            name="Canasto de iraca",
            description="Woven palm.",
            category="Basketry",
            origin="Usiacuri, Atlantico",
            status=ProductStatus.REVOKED,
            revocation_reason="Reported as a copy.",
        )
        self.client.login(email="weaver@tuchin.co", password=PASSWORD)

    def test_the_list_shows_the_products_of_this_company(self):
        response = self.client.get(reverse("products:product_list"))

        self.assertContains(response, "Sombrero vueltiao")
        self.assertContains(response, "Canasto de iraca")

    def test_the_list_hides_the_products_of_another_company(self):
        other = make_company("otro@barranquilla.co")
        Product.objects.create(
            company=other,
            product_type=ProductType.COMMERCIAL_ORIGINAL,
            name="Mochila arhuaca",
            description="Not mine.",
            category="Bags",
            origin="Nabusimake, Cesar",
        )

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
        started = time.perf_counter()
        self.client.get(reverse("products:product_list"))
        elapsed = time.perf_counter() - started

        self.assertLess(elapsed, 3.0, f"the list took {elapsed:.3f}s")


class ProductEditTests(TestCase):
    """FR26: the descriptive fields change, the passport code does not."""

    def setUp(self):
        self.company = make_company("weaver@tuchin.co")
        self.product = Product.objects.create(
            company=self.company,
            product_type=ProductType.COMMERCIAL_ORIGINAL,
            **VALID_PRODUCT,
        )
        self.client.login(email="weaver@tuchin.co", password=PASSWORD)

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
        admin = User.objects.create_superuser("admin@originpass.co", "Admin-Pass-2026")
        self.product.revoke(actor=admin, reason="Reported as a copy.")

        response = self.client.get(reverse("products:product_edit", args=[self.product.pk]))
        self.assertEqual(response.status_code, 403)

    def test_a_company_cannot_edit_the_product_of_another(self):
        make_company("otro@barranquilla.co")
        self.client.login(email="otro@barranquilla.co", password=PASSWORD)

        response = self.client.get(reverse("products:product_edit", args=[self.product.pk]))
        self.assertEqual(response.status_code, 404)


class QrCodeTests(TestCase):
    """FR22: a downloadable PNG encoding the public verification address."""

    def setUp(self):
        self.company = make_company("weaver@tuchin.co")
        self.product = Product.objects.create(
            company=self.company,
            product_type=ProductType.COMMERCIAL_ORIGINAL,
            **VALID_PRODUCT,
        )
        self.client.login(email="weaver@tuchin.co", password=PASSWORD)
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
        make_company("otro@barranquilla.co")
        self.client.login(email="otro@barranquilla.co", password=PASSWORD)

        self.assertEqual(self.client.get(self.url).status_code, 404)
