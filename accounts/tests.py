"""Acceptance criteria of the Sprint 1 authentication issues.

Each test class names the issue it covers. Where an issue states a time bound,
the test measures the response and asserts it.
"""

import time

from django.test import TestCase
from django.urls import reverse

from .forms import AUTHENTICATION_ERROR
from .models import Role, User


def elapsed(call):
    """Run `call` and return (result, seconds)."""
    started = time.perf_counter()
    result = call()
    return result, time.perf_counter() - started


class CreateAccountTests(TestCase):
    """FR01 - Create an account."""

    def test_visitor_creates_an_account(self):
        response, seconds = elapsed(
            lambda: self.client.post(
                reverse("accounts:register"),
                {
                    "email": "weaver@tuchin.co",
                    "password1": "Vueltiao-2026",
                    "password2": "Vueltiao-2026",
                },
            )
        )

        self.assertRedirects(response, reverse("accounts:login"))
        self.assertTrue(User.objects.filter(email="weaver@tuchin.co").exists())
        self.assertLess(seconds, 3, "The result must be confirmed within 3 seconds.")

    def test_the_new_account_can_log_in_immediately_afterwards(self):
        self.client.post(
            reverse("accounts:register"),
            {
                "email": "weaver@tuchin.co",
                "password1": "Vueltiao-2026",
                "password2": "Vueltiao-2026",
            },
        )

        logged_in = self.client.login(email="weaver@tuchin.co", password="Vueltiao-2026")

        self.assertTrue(logged_in)

    def test_a_new_account_starts_as_a_holder(self):
        self.client.post(
            reverse("accounts:register"),
            {
                "email": "weaver@tuchin.co",
                "password1": "Vueltiao-2026",
                "password2": "Vueltiao-2026",
            },
        )

        self.assertEqual(User.objects.get(email="weaver@tuchin.co").role, Role.HOLDER)


class DuplicateEmailTests(TestCase):
    """FR02 - Reject registration with an email already in use."""

    def setUp(self):
        User.objects.create_user("weaver@tuchin.co", "Vueltiao-2026")

    def test_the_message_states_that_the_address_is_in_use(self):
        response, seconds = elapsed(
            lambda: self.client.post(
                reverse("accounts:register"),
                {
                    "email": "weaver@tuchin.co",
                    "password1": "Another-Pass-2026",
                    "password2": "Another-Pass-2026",
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This email address is already in use.")
        self.assertLess(seconds, 2, "The message must be shown within 2 seconds.")

    def test_no_second_account_is_created(self):
        self.client.post(
            reverse("accounts:register"),
            {
                "email": "weaver@tuchin.co",
                "password1": "Another-Pass-2026",
                "password2": "Another-Pass-2026",
            },
        )

        self.assertEqual(User.objects.filter(email="weaver@tuchin.co").count(), 1)

    def test_the_cause_is_attached_to_the_email_field(self):
        """UR08: the message belongs beside the field that caused the refusal."""
        response = self.client.post(
            reverse("accounts:register"),
            {
                "email": "weaver@tuchin.co",
                "password1": "Another-Pass-2026",
                "password2": "Another-Pass-2026",
            },
        )

        self.assertIn("email", response.context["form"].errors)
        self.assertContains(response, "field-row--invalid")


class LoginTests(TestCase):
    """FR03 - Log in with email and password."""

    def setUp(self):
        User.objects.create_user("weaver@tuchin.co", "Vueltiao-2026")

    def test_valid_credentials_grant_access(self):
        response, seconds = elapsed(
            lambda: self.client.post(
                reverse("accounts:login"),
                {"email": "weaver@tuchin.co", "password": "Vueltiao-2026"},
            )
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertLess(seconds, 3, "Access must be granted within 3 seconds.")

    def test_the_session_is_kept_across_page_navigations(self):
        self.client.post(
            reverse("accounts:login"),
            {"email": "weaver@tuchin.co", "password": "Vueltiao-2026"},
        )

        first = self.client.get(reverse("companies:application_create"))
        second = self.client.get(reverse("companies:application_create"))

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertTrue(second.wsgi_request.user.is_authenticated)


class UniformAuthenticationErrorTests(TestCase):
    """FR04 - Show a uniform authentication error."""

    def setUp(self):
        User.objects.create_user("weaver@tuchin.co", "Vueltiao-2026")

    def _errors_for(self, email, password):
        response = self.client.post(
            reverse("accounts:login"), {"email": email, "password": password}
        )
        return response, response.context["form"].errors

    def test_an_unknown_address_and_a_wrong_password_produce_the_same_message(self):
        _, unknown_address = self._errors_for("nobody@tuchin.co", "Vueltiao-2026")
        _, wrong_password = self._errors_for("weaver@tuchin.co", "not-the-password")

        self.assertEqual(unknown_address, wrong_password)
        self.assertEqual(unknown_address["__all__"], [AUTHENTICATION_ERROR])

    def test_the_message_identifies_neither_field_as_the_failing_one(self):
        _, errors = self._errors_for("weaver@tuchin.co", "not-the-password")

        self.assertNotIn("email", errors)
        self.assertNotIn("password", errors)
        self.assertNotIn("email", AUTHENTICATION_ERROR.lower().replace("email address", ""))

    def test_the_message_is_shown_within_two_seconds(self):
        response, seconds = elapsed(
            lambda: self.client.post(
                reverse("accounts:login"),
                {"email": "weaver@tuchin.co", "password": "not-the-password"},
            )
        )

        self.assertContains(response, AUTHENTICATION_ERROR)
        self.assertLess(seconds, 2)


class LogoutTests(TestCase):
    """FR05 - Log out and end the session."""

    def setUp(self):
        User.objects.create_user("weaver@tuchin.co", "Vueltiao-2026")
        self.client.login(email="weaver@tuchin.co", password="Vueltiao-2026")

    def test_the_session_ends(self):
        response, seconds = elapsed(lambda: self.client.post(reverse("accounts:logout")))

        self.assertRedirects(response, reverse("home"))
        self.assertLess(seconds, 2, "The session must end within 2 seconds.")

    def test_a_protected_page_opened_afterwards_redirects_to_the_login_page(self):
        self.client.post(reverse("accounts:logout"))

        protected = reverse("companies:application_create")
        response = self.client.get(protected)

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)


class PasswordStorageTests(TestCase):
    """DBR11 - Store passwords as salted hashes."""

    def test_the_password_is_stored_as_a_one_way_hash(self):
        user = User.objects.create_user("weaver@tuchin.co", "Vueltiao-2026")

        self.assertNotEqual(user.password, "Vueltiao-2026")
        self.assertNotIn("Vueltiao-2026", user.password)
        self.assertTrue(user.password.startswith("pbkdf2_sha256$"))
        self.assertTrue(user.check_password("Vueltiao-2026"))

    def test_the_salt_is_unique_to_the_record(self):
        first = User.objects.create_user("one@tuchin.co", "Vueltiao-2026")
        second = User.objects.create_user("two@tuchin.co", "Vueltiao-2026")

        # Same password, different stored value: the salt differs per record.
        self.assertNotEqual(first.password, second.password)

    def test_no_plain_text_password_reaches_the_database(self):
        self.client.post(
            reverse("accounts:register"),
            {
                "email": "weaver@tuchin.co",
                "password1": "Vueltiao-2026",
                "password2": "Vueltiao-2026",
            },
        )

        stored = User.objects.values_list("password", flat=True)

        self.assertFalse(any("Vueltiao-2026" in value for value in stored))
