"""Acceptance criteria of FR28 to FR31 and UR02, UR03, UR06: the three verdicts.

The tests that matter most here are the ones about what the page does *not* do:
it does not ask for a session, it does not load a script, and it does not tell
one kind of unmatched code from another.

The copy asserted below is Spanish because that is what a visitor reads (UR04).
The source strings stay English; `locale/es` is what turns them.
"""

from django.template.defaultfilters import date as render_date
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from test_support.factories import make_admin, make_product
from test_support.timing import measure
from verification.models import Verdict


def as_the_page_writes_it(moment):
    """The date exactly as the page renders it.

    Two steps, and leaving out either one produces a test that fails at some
    hours of the day and not others:

    - Localtime, because the template engine converts an aware datetime to the
      project's time zone before any filter sees it. Formatting the UTC value
      instead is off by a day for the five hours either side of midnight
      in Bogota.
    - The template's own filter rather than strftime, whose month names come
      from the process locale and say "September" where the page says
      "septiembre".
    """
    return render_date(timezone.localtime(moment), "j F Y")


def verdict_url(product):
    return reverse("verification:verify", args=[product.passport_code])


class OpenWithoutAnAccountTests(TestCase):
    """FR28: any visitor opens the verification page without authenticating."""

    def test_the_page_is_served_to_a_visitor_with_no_session(self):
        product = make_product()

        response = self.client.get(verdict_url(product))

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Location", response)

    def test_the_verdict_is_reached_in_one_request_from_the_scanned_address(self):
        """UR02: scanning is the first interaction and the verdict is the answer."""
        product = make_product()

        response = self.client.get(verdict_url(product), follow=True)

        self.assertEqual(len(response.redirect_chain), 0)
        self.assertContains(response, "Auténtico")


class GenuineVerdictTests(TestCase):
    """FR29: the verdict Genuine, with the product and the verified company."""

    def setUp(self):
        self.product = make_product()
        self.url = verdict_url(self.product)

    def test_the_verdict_is_genuine(self):
        response = self.client.get(self.url)

        self.assertContains(response, "Auténtico")
        self.assertEqual(response.context["verdict"], Verdict.GENUINE)

    def test_the_product_and_the_company_are_shown(self):
        response = self.client.get(self.url)

        self.assertContains(response, "Sombrero vueltiao 21 vueltas")
        self.assertContains(response, "Tuchin, Cordoba")
        self.assertContains(response, "Artesanias La Bonga SAS")
        self.assertContains(response, "Cámara de Comercio")

    def test_the_page_answers_within_three_seconds(self):
        """UR06 states the bound, so it is measured rather than assumed."""
        _, seconds = measure(lambda: self.client.get(self.url))

        self.assertLess(seconds, 3.0, f"the verification page took {seconds:.3f}s")


class RevokedVerdictTests(TestCase):
    """FR30: the verdict Revoked, with the date the product was withdrawn."""

    def setUp(self):
        self.product = make_product()
        self.product.revoke(actor=make_admin(), reason="Reported as a copy.")
        self.url = verdict_url(self.product)

    def test_the_verdict_is_revoked(self):
        response = self.client.get(self.url)

        self.assertContains(response, "Revocado")
        self.assertEqual(response.context["verdict"], Verdict.REVOKED)

    def test_the_date_of_the_revocation_is_shown(self):
        self.product.refresh_from_db()

        response = self.client.get(self.url)

        self.assertContains(response, as_the_page_writes_it(self.product.updated_at))

    def test_a_revoked_passport_does_not_read_as_genuine(self):
        response = self.client.get(self.url)

        self.assertNotContains(response, "Auténtico")


class NotFoundVerdictTests(TestCase):
    """FR31: one message for every unmatched code, whatever the reason."""

    def test_an_unknown_code_returns_not_found(self):
        response = self.client.get(reverse("verification:verify", args=["nothing-here"]))

        self.assertContains(response, "No encontrado")
        self.assertEqual(response.context["verdict"], Verdict.NOT_FOUND)

    def test_two_different_unmatched_codes_get_the_same_message(self):
        """Telling one kind of miss from another would leak which codes are live."""
        first = self.client.get(reverse("verification:verify", args=["aaaaaaaaaaaa"]))
        second = self.client.get(reverse("verification:verify", args=["bbbbbbbbbbbb"]))

        def message(response):
            body = str(response.content)
            return response.context["verdict"], body.replace("aaaaaaaaaaaa", "CODE").replace(
                "bbbbbbbbbbbb", "CODE"
            )

        self.assertEqual(message(first), message(second))

    def test_no_product_is_offered(self):
        response = self.client.get(reverse("verification:verify", args=["nothing-here"]))

        self.assertIsNone(response.context["product"])


class VerdictPresentationTests(TestCase):
    """UR03 the verdict in words, UR06 the weight of the page."""

    def setUp(self):
        self.url = verdict_url(make_product())

    def test_the_verdict_is_stated_in_text_and_not_only_in_colour(self):
        body = self.client.get(self.url).content.decode()

        self.assertIn("Auténtico", body)
        self.assertIn("verdict--genuine", body)

    def test_the_page_loads_no_script(self):
        """UR06: the 3G budget is met by not spending it. No script, one stylesheet."""
        body = self.client.get(self.url).content.decode()

        self.assertNotIn("<script", body)
        self.assertEqual(body.count('<link rel="stylesheet"'), 1)

    def test_no_template_syntax_reaches_the_visitor(self):
        """Caught a comment being served as text; see pages.tests.test_template_hygiene."""
        body = self.client.get(self.url).content.decode()

        self.assertNotIn("{#", body)
        self.assertNotIn("{%", body)
