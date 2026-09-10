"""Acceptance criteria of FR03, FR04 and FR05: starting and ending a session.

Where an issue states a time bound, the test measures the response and asserts it.
"""

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from accounts import forms
from test_support.factories import make_user
from test_support.timing import measure

#: Resolved once, here, because the form holds it as a lazy translation and the
#: assertions below compare it against text that has already been rendered.
AUTHENTICATION_ERROR = str(forms.AUTHENTICATION_ERROR)

EMAIL = "weaver@tuchin.co"
PASSWORD = "Vueltiao-2026"
WRONG_PASSWORD = "not-the-password"


class LoginTests(TestCase):
    """FR03 - Log in with email and password."""

    def setUp(self):
        make_user(EMAIL)

    def test_valid_credentials_grant_access(self):
        response, seconds = measure(
            lambda: self.client.post(
                reverse("accounts:login"), {"email": EMAIL, "password": PASSWORD}
            )
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertLess(seconds, 3, "Access must be granted within 3 seconds.")

    def test_the_session_is_kept_across_page_navigations(self):
        self.client.post(reverse("accounts:login"), {"email": EMAIL, "password": PASSWORD})

        first = self.client.get(reverse("companies:application_create"))
        second = self.client.get(reverse("companies:application_create"))

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertTrue(second.wsgi_request.user.is_authenticated)


class LoginDestinationTests(TestCase):
    """Where a login lands, when the link that led to it named a destination.

    The address is supplied by whoever wrote the link, so it is treated as
    input rather than as instruction: this page hands a freshly authenticated
    user straight to it, and a page on another site is exactly what a login
    form pretending to be this one would ask for.
    """

    def setUp(self):
        make_user(EMAIL)

    def _log_in_asking_for(self, destination):
        return self.client.post(
            reverse("accounts:login"),
            {"email": EMAIL, "password": PASSWORD, "next": destination},
        )

    def test_a_path_on_this_site_is_honoured(self):
        wanted = reverse("products:product_list")

        response = self._log_in_asking_for(wanted)

        self.assertEqual(response.url, wanted)

    def test_an_address_on_another_site_is_discarded(self):
        response = self._log_in_asking_for("https://originpass.example.net/steal")

        self.assertEqual(response.url, reverse(settings.LOGIN_REDIRECT_URL))

    def test_a_scheme_relative_address_is_discarded(self):
        # Reads as a path and is not one: the browser keeps the current scheme
        # and replaces the host.
        response = self._log_in_asking_for("//originpass.example.net/steal")

        self.assertEqual(response.url, reverse(settings.LOGIN_REDIRECT_URL))

    def test_no_destination_lands_on_the_account_page(self):
        response = self.client.post(
            reverse("accounts:login"), {"email": EMAIL, "password": PASSWORD}
        )

        self.assertEqual(response.url, reverse(settings.LOGIN_REDIRECT_URL))


class UniformAuthenticationErrorTests(TestCase):
    """FR04 - Show a uniform authentication error."""

    def setUp(self):
        make_user(EMAIL)

    def _errors_for(self, email, password):
        response = self.client.post(
            reverse("accounts:login"), {"email": email, "password": password}
        )
        return response, response.context["form"].errors

    def test_an_unknown_address_and_a_wrong_password_produce_the_same_message(self):
        _, unknown_address = self._errors_for("nobody@tuchin.co", PASSWORD)
        _, wrong_password = self._errors_for(EMAIL, WRONG_PASSWORD)

        self.assertEqual(unknown_address, wrong_password)
        self.assertEqual(unknown_address["__all__"], [AUTHENTICATION_ERROR])

    def test_the_message_identifies_neither_field_as_the_failing_one(self):
        _, errors = self._errors_for(EMAIL, WRONG_PASSWORD)

        self.assertNotIn("email", errors)
        self.assertNotIn("password", errors)
        self.assertNotIn("email", AUTHENTICATION_ERROR.lower().replace("email address", ""))

    def test_the_message_is_shown_within_two_seconds(self):
        response, seconds = measure(
            lambda: self.client.post(
                reverse("accounts:login"), {"email": EMAIL, "password": WRONG_PASSWORD}
            )
        )

        self.assertContains(response, AUTHENTICATION_ERROR)
        self.assertLess(seconds, 2)


class LogoutTests(TestCase):
    """FR05 - Log out and end the session."""

    def setUp(self):
        make_user(EMAIL)
        self.client.login(email=EMAIL, password=PASSWORD)

    def test_the_session_ends(self):
        response, seconds = measure(lambda: self.client.post(reverse("accounts:logout")))

        self.assertRedirects(response, reverse("pages:home"))
        self.assertLess(seconds, 2, "The session must end within 2 seconds.")

    def test_a_protected_page_opened_afterwards_redirects_to_the_login_page(self):
        self.client.post(reverse("accounts:logout"))

        response = self.client.get(reverse("companies:application_create"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)
