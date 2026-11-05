"""A signed-in account can change its own password, and the session survives the change.

Demonstration accounts are created with a shared password and need to be
changed once the site is online, so this has to work without the reset email.
"""

# ---- External imports ----
from django.test import Client, TestCase
from django.urls import reverse

# ---- Internal imports ----
from test_support.factories import OWNER_PASSWORD, make_user

NEW_PASSWORD = "A-brand-new-passphrase-2026"


# ---- Public API ----
class PasswordChangeTests(TestCase):
    def setUp(self):
        self.user = make_user(email="holder@example.com")
        self.url = reverse("accounts:password_change")

    def _change(self, old=OWNER_PASSWORD, new1=NEW_PASSWORD, new2=NEW_PASSWORD):
        return self.client.post(
            self.url,
            {"old_password": old, "new_password1": new1, "new_password2": new2},
        )

    def test_anonymous_visitors_are_sent_to_log_in(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response["Location"])

    def test_the_password_changes_with_the_current_one(self):
        self.client.force_login(self.user)

        response = self._change()

        self.assertRedirects(response, reverse("accounts:password_change_done"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(NEW_PASSWORD))
        self.assertFalse(self.user.check_password(OWNER_PASSWORD))

    def test_the_session_stays_signed_in_after_the_change(self):
        self.client.force_login(self.user)

        self._change()

        response = self.client.get(reverse("accounts:password_change_done"))
        self.assertEqual(response.status_code, 200)

    def test_a_wrong_current_password_changes_nothing(self):
        self.client.force_login(self.user)

        response = self._change(old="not-the-current-one")

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(OWNER_PASSWORD))

    def test_the_two_new_passwords_must_match(self):
        self.client.force_login(self.user)

        response = self._change(new2="A-different-passphrase-2026")

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(OWNER_PASSWORD))

    def test_the_new_password_can_log_in_afterwards(self):
        self.client.force_login(self.user)
        self._change()

        other = Client()
        self.assertTrue(other.login(username="holder@example.com", password=NEW_PASSWORD))
