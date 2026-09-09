"""Acceptance criteria of FR03, FR04 and FR05: starting and ending a session.

Where an issue states a time bound, the test measures the response and asserts it.
"""

from django.test import TestCase
from django.urls import reverse

from accounts import forms
from testing.factories import make_user
from testing.timing import measure

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
