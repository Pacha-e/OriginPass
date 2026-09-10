"""Acceptance criteria of FR19, FR20, FR21, FR23 and UR10: issuing a passport.

What is tested here is the behaviour a person can see: who may issue a passport
and what the refusal says. The invariants underneath are in `test_passport_record`.
"""

from django.test import TestCase
from django.urls import reverse

from audit.models import Action, AuditEntry
from companies.models import CompanyStatus, CompanyType
from products.forms import ProductForm
from products.models import Product, ProductStatus, ProductType
from test_support.factories import OWNER_PASSWORD, make_approved_company, make_company

VALID_PRODUCT = {
    "name": "Sombrero vueltiao 21 vueltas",
    "description": "Hand woven over three weeks.",
    "category": "Headwear",
    "origin": "Tuchin, Cordoba",
}


class ProductRegistrationTests(TestCase):
    """FR19 register a product, FR21 generate its code, FR23 match the type."""

    def setUp(self):
        self.company = make_approved_company(email="weaver@tuchin.co")
        self.client.login(email="weaver@tuchin.co", password=OWNER_PASSWORD)

    def test_an_approved_company_registers_a_product(self):
        response = self.client.post(reverse("products:product_create"), VALID_PRODUCT)

        product = Product.objects.get(name=VALID_PRODUCT["name"])
        self.assertRedirects(response, reverse("products:product_detail", args=[product.pk]))
        self.assertEqual(product.company, self.company)
        self.assertEqual(product.origin, "Tuchin, Cordoba")
        self.assertEqual(product.status, ProductStatus.ACTIVE)

    def test_registration_generates_a_passport_code(self):
        self.client.post(reverse("products:product_create"), VALID_PRODUCT)

        product = Product.objects.get(name=VALID_PRODUCT["name"])
        self.assertGreaterEqual(len(product.passport_code), 24)

    def test_the_product_type_follows_the_company_type(self):
        self.client.post(reverse("products:product_create"), VALID_PRODUCT)

        product = Product.objects.get(name=VALID_PRODUCT["name"])
        self.assertEqual(product.product_type, ProductType.COMMERCIAL_ORIGINAL)

    def test_an_artisan_company_issues_artisan_pieces(self):
        make_approved_company(email="taller@tuchin.co", company_type=CompanyType.ARTISAN)
        self.client.login(email="taller@tuchin.co", password=OWNER_PASSWORD)

        self.client.post(reverse("products:product_create"), VALID_PRODUCT)

        product = Product.objects.get(name=VALID_PRODUCT["name"])
        self.assertEqual(product.product_type, ProductType.ARTISAN)

    def test_registration_is_written_into_the_audit_trail(self):
        self.client.post(reverse("products:product_create"), VALID_PRODUCT)
        product = Product.objects.get(name=VALID_PRODUCT["name"])

        entry = AuditEntry.objects.get(target_type=Product._meta.label, target_id=product.pk)
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
        email = f"{status.lower()}@tuchin.co"
        make_company(email=email, status=status)
        self.client.login(email=email, password=OWNER_PASSWORD)
        return self.client.post(reverse("products:product_create"), VALID_PRODUCT)

    def test_a_pending_company_is_refused_with_the_reason(self):
        response = self._attempt(CompanyStatus.PENDING)

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "todavía está en revisión", status_code=403)
        self.assertFalse(Product.objects.exists())

    def test_a_rejected_company_is_refused_with_the_reason(self):
        response = self._attempt(CompanyStatus.REJECTED)

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "fue rechazada", status_code=403)
        self.assertFalse(Product.objects.exists())

    def test_a_suspended_company_is_refused_with_the_reason(self):
        response = self._attempt(CompanyStatus.SUSPENDED)

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "está suspendida", status_code=403)
        self.assertFalse(Product.objects.exists())
