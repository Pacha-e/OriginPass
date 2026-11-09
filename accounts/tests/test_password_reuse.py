"""A new password must differ from the current one.

Someone resets or changes a password because they forgot it or because it may
be known to someone else. In the second case keeping the same one undoes the
change, so the reset and the signed-in change both refuse it.
"""

# ---- External imports ----
import re

from django.core import mail
from django.test import TestCase
from django.urls import reverse

# ---- Internal imports ----
from test_support.factories import OWNER_PASSWORD, make_user

REFUSAL = "Elige una contraseña distinta de la que tenías."


# ---- Public API ----
class PasswordReuseTests(TestCase):
    def setUp(self):
        self.user = make_user(email="holder@example.com")

    def _reset_form_url(self):
        self.client.post(reverse("accounts:password_reset"), {"email": self.user.email})
        link = re.search(r"https?://\S+", mail.outbox[0].body).group(0)
        return self.client.get(link, follow=True).redirect_chain[-1][0]

    def test_the_reset_refuses_the_current_password(self):
        response = self.client.post(
            self._reset_form_url(),
            {"new_password1": OWNER_PASSWORD, "new_password2": OWNER_PASSWORD},
            HTTP_ACCEPT_LANGUAGE="es",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, REFUSAL)

    def test_the_signed_in_change_refuses_the_current_password(self):
        self.client.login(email=self.user.email, password=OWNER_PASSWORD)
        response = self.client.post(
            reverse("accounts:password_change"),
            {
                "old_password": OWNER_PASSWORD,
                "new_password1": OWNER_PASSWORD,
                "new_password2": OWNER_PASSWORD,
            },
            HTTP_ACCEPT_LANGUAGE="es",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, REFUSAL)

    def test_a_different_password_is_still_accepted(self):
        response = self.client.post(
            self._reset_form_url(),
            {"new_password1": "Otra-Clave-Segura-77", "new_password2": "Otra-Clave-Segura-77"},
        )
        self.assertRedirects(response, reverse("accounts:password_reset_complete"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("Otra-Clave-Segura-77"))
