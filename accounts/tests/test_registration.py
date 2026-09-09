"""Acceptance criteria of FR01 and FR02, creating an account.

Where an issue states a time bound, the test measures the response and asserts it.
"""

from django.test import TestCase
from django.urls import reverse

from accounts.models import Role, User
from testing.factories import make_user
from testing.timing import measure

EMAIL = "weaver@tuchin.co"
PASSWORD = "Vueltiao-2026"

NEW_ACCOUNT = {"email": EMAIL, "password1": PASSWORD, "password2": PASSWORD}
SAME_ADDRESS_ANOTHER_PASSWORD = {
    "email": EMAIL,
    "password1": "Another-Pass-2026",
    "password2": "Another-Pass-2026",
}


class CreateAccountTests(TestCase):
    """FR01 - Create an account."""

    def test_visitor_creates_an_account(self):
        response, seconds = measure(
            lambda: self.client.post(reverse("accounts:register"), NEW_ACCOUNT)
        )

        self.assertRedirects(response, reverse("accounts:login"))
        self.assertTrue(User.objects.filter(email=EMAIL).exists())
        self.assertLess(seconds, 3, "The result must be confirmed within 3 seconds.")

    def test_the_new_account_can_log_in_immediately_afterwards(self):
        self.client.post(reverse("accounts:register"), NEW_ACCOUNT)

        logged_in = self.client.login(email=EMAIL, password=PASSWORD)

        self.assertTrue(logged_in)

    def test_a_new_account_starts_as_a_holder(self):
        self.client.post(reverse("accounts:register"), NEW_ACCOUNT)

        self.assertEqual(User.objects.get(email=EMAIL).role, Role.HOLDER)


class DuplicateEmailTests(TestCase):
    """FR02 - Reject registration with an email already in use."""

    def setUp(self):
        make_user(EMAIL)

    def test_the_message_states_that_the_address_is_in_use(self):
        response, seconds = measure(
            lambda: self.client.post(reverse("accounts:register"), SAME_ADDRESS_ANOTHER_PASSWORD)
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Este correo ya está en uso.")
        self.assertLess(seconds, 2, "The message must be shown within 2 seconds.")

    def test_no_second_account_is_created(self):
        self.client.post(reverse("accounts:register"), SAME_ADDRESS_ANOTHER_PASSWORD)

        self.assertEqual(User.objects.filter(email=EMAIL).count(), 1)

    def test_the_cause_is_attached_to_the_email_field(self):
        """UR08: the message belongs beside the field that caused the refusal."""
        response = self.client.post(reverse("accounts:register"), SAME_ADDRESS_ANOTHER_PASSWORD)

        self.assertIn("email", response.context["form"].errors)
        self.assertContains(response, "field-row--invalid")
