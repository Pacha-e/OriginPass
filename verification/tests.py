"""The public verification page, one or more tests per acceptance criterion.

The tests that matter most here are the ones about what the page does *not* do:
it does not ask for a session, it does not load a script, and it does not tell
one kind of unmatched code from another.
"""

import time

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from companies.models import Company, CompanyStatus, CompanyType, VerificationTrack
from products.models import Product, ProductType

from .models import ScanEvent, Verdict

PASSWORD = "Vueltiao-2026"


def as_the_page_writes_it(moment):
    """The same date the `date:"j F Y"` filter renders, in the project's time zone."""
    local = timezone.localtime(moment)
    return f"{local.day} {local:%B} {local.year}"


def make_product(**overrides):
    owner = User.objects.create_user("weaver@tuchin.co", PASSWORD)
    company = Company.objects.create(
        owner=owner,
        legal_name="Artesanias La Bonga SAS",
        company_type=CompanyType.COMMERCIAL,
        verification_track=VerificationTrack.CHAMBER_OF_COMMERCE,
        registry_code="NIT-900123456-7",
        description="Crafts from Cordoba.",
        location="Monteria, Cordoba",
        status=CompanyStatus.APPROVED,
    )
    fields = {
        "product_type": ProductType.COMMERCIAL_ORIGINAL,
        "name": "Sombrero vueltiao 21 vueltas",
        "description": "Hand woven over three weeks.",
        "category": "Headwear",
        "origin": "Tuchin, Cordoba",
    }
    fields.update(overrides)
    return Product.objects.create(company=company, **fields)


class OpenWithoutAnAccountTests(TestCase):
    """FR28: any visitor opens the verification page without authenticating."""

    def test_the_page_is_served_to_a_visitor_with_no_session(self):
        product = make_product()

        response = self.client.get(reverse("verification:verify", args=[product.passport_code]))

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Location", response)

    def test_the_verdict_is_reached_in_one_request_from_the_scanned_address(self):
        """UR02: scanning is the first interaction and the verdict is the answer."""
        product = make_product()

        response = self.client.get(
            reverse("verification:verify", args=[product.passport_code]), follow=True
        )

        self.assertEqual(len(response.redirect_chain), 0)
        self.assertContains(response, "Genuine")


class GenuineVerdictTests(TestCase):
    """FR29: the verdict Genuine, with the product and the verified company."""

    def setUp(self):
        self.product = make_product()
        self.url = reverse("verification:verify", args=[self.product.passport_code])

    def test_the_verdict_is_genuine(self):
        response = self.client.get(self.url)

        self.assertContains(response, "Genuine")
        self.assertEqual(response.context["verdict"], Verdict.GENUINE)

    def test_the_product_and_the_company_are_shown(self):
        response = self.client.get(self.url)

        self.assertContains(response, "Sombrero vueltiao 21 vueltas")
        self.assertContains(response, "Tuchin, Cordoba")
        self.assertContains(response, "Artesanias La Bonga SAS")
        self.assertContains(response, "Chamber of Commerce")

    def test_the_page_answers_within_three_seconds(self):
        started = time.perf_counter()
        self.client.get(self.url)
        elapsed = time.perf_counter() - started

        self.assertLess(elapsed, 3.0, f"the verification page took {elapsed:.3f}s")


class RevokedVerdictTests(TestCase):
    """FR30: the verdict Revoked, with the date the product was withdrawn."""

    def setUp(self):
        self.admin = User.objects.create_superuser("admin@originpass.co", "Admin-Pass-2026")
        self.product = make_product()
        self.product.revoke(actor=self.admin, reason="Reported as a copy.")
        self.url = reverse("verification:verify", args=[self.product.passport_code])

    def test_the_verdict_is_revoked(self):
        response = self.client.get(self.url)

        self.assertContains(response, "Revoked")
        self.assertEqual(response.context["verdict"], Verdict.REVOKED)

    def test_the_date_of_the_revocation_is_shown(self):
        self.product.refresh_from_db()
        response = self.client.get(self.url)

        self.assertContains(response, as_the_page_writes_it(self.product.updated_at))

    def test_a_revoked_passport_does_not_read_as_genuine(self):
        response = self.client.get(self.url)
        self.assertNotContains(response, "Genuine")


class NotFoundVerdictTests(TestCase):
    """FR31: one message for every unmatched code, whatever the reason."""

    def test_an_unknown_code_returns_not_found(self):
        response = self.client.get(reverse("verification:verify", args=["nothing-here"]))

        self.assertContains(response, "Not found")
        self.assertEqual(response.context["verdict"], Verdict.NOT_FOUND)

    def test_two_different_unmatched_codes_get_the_same_message(self):
        """Telling one kind of miss from another would leak which codes are live."""
        first = self.client.get(reverse("verification:verify", args=["aaaaaaaaaaaa"]))
        second = self.client.get(reverse("verification:verify", args=["bbbbbbbbbbbb"]))

        def message(response):
            return response.context["verdict"], str(response.content).replace(
                "aaaaaaaaaaaa", "CODE"
            ).replace("bbbbbbbbbbbb", "CODE")

        self.assertEqual(message(first), message(second))

    def test_no_product_is_offered(self):
        response = self.client.get(reverse("verification:verify", args=["nothing-here"]))
        self.assertIsNone(response.context["product"])


class VerdictPresentationTests(TestCase):
    """UR03 the verdict in words, UR06 the weight of the page."""

    def setUp(self):
        self.product = make_product()
        self.url = reverse("verification:verify", args=[self.product.passport_code])

    def test_the_verdict_is_stated_in_text_and_not_only_in_colour(self):
        response = self.client.get(self.url)
        body = response.content.decode()

        self.assertIn("Genuine", body)
        self.assertIn("verdict--genuine", body)

    def test_the_page_loads_no_script(self):
        """UR06: the 3G budget is met by not spending it. No script, one stylesheet."""
        body = self.client.get(self.url).content.decode()

        self.assertNotIn("<script", body)
        self.assertEqual(body.count('<link rel="stylesheet"'), 1)

    def test_no_template_syntax_reaches_the_visitor(self):
        """Caught a comment being served as text; see config.tests."""
        body = self.client.get(self.url).content.decode()

        self.assertNotIn("{#", body)
        self.assertNotIn("{%", body)


class ScanEventTests(TestCase):
    """Every visit is recorded, including the ones that matched nothing."""

    def test_a_genuine_verification_writes_a_scan_event(self):
        product = make_product()

        self.client.get(reverse("verification:verify", args=[product.passport_code]))

        event = ScanEvent.objects.get()
        self.assertEqual(event.product, product)
        self.assertEqual(event.verdict, Verdict.GENUINE)

    def test_an_unmatched_code_is_recorded_with_no_product(self):
        self.client.get(reverse("verification:verify", args=["nothing-here"]))

        event = ScanEvent.objects.get()
        self.assertIsNone(event.product)
        self.assertEqual(event.verdict, Verdict.NOT_FOUND)

    def test_the_device_category_is_taken_from_the_browser(self):
        product = make_product()

        self.client.get(
            reverse("verification:verify", args=[product.passport_code]),
            HTTP_USER_AGENT="Mozilla/5.0 (Linux; Android 14) Mobile Safari/537.36",
        )

        self.assertEqual(ScanEvent.objects.get().device_category, "MOBILE")

    def test_every_visit_is_recorded_separately(self):
        product = make_product()
        url = reverse("verification:verify", args=[product.passport_code])

        self.client.get(url)
        self.client.get(url)

        self.assertEqual(ScanEvent.objects.count(), 2)


class PassportLookupTests(TestCase):
    """DBR10: the lookup is served by the index on the passport code."""

    def test_the_passport_code_is_indexed(self):
        field = Product._meta.get_field("passport_code")

        self.assertTrue(field.db_index)
        self.assertTrue(field.unique)

    def test_the_lookup_completes_well_inside_the_bound(self):
        product = make_product()
        for number in range(200):
            Product.objects.create(
                company=product.company,
                product_type=ProductType.COMMERCIAL_ORIGINAL,
                name=f"Filler {number}",
                description="Filler.",
                category="Filler",
                origin="Filler",
            )

        started = time.perf_counter()
        Product.objects.get(passport_code=product.passport_code)
        elapsed = time.perf_counter() - started

        self.assertLess(elapsed, 0.2, f"the lookup took {elapsed * 1000:.1f}ms")


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
