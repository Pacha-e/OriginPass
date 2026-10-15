"""FR06: a registered user asks for a reset link by email."""

import re

from django.core import mail
from django.test import TestCase
from django.urls import reverse

from test_support.factories import make_user


class PasswordResetTests(TestCase):
    def setUp(self):
        self.user = make_user(email="holder@example.com")

    def _ask(self, email):
        return self.client.post(reverse("accounts:password_reset"), {"email": email})

    def test_a_registered_address_receives_a_working_link(self):
        response = self._ask(self.user.email)
        self.assertRedirects(response, reverse("accounts:password_reset_done"))
        self.assertEqual(mail.outbox[0].to, [self.user.email])
        link = re.search(r"https?://\S+", mail.outbox[0].body).group(0)

        page = self.client.get(link, follow=True)
        self.assertContains(page, "Elige una contraseña nueva")
        response = self.client.post(
            page.redirect_chain[-1][0] if page.redirect_chain else link,
            {"new_password1": "Otra-Clave-Segura-77", "new_password2": "Otra-Clave-Segura-77"},
        )
        self.assertRedirects(response, reverse("accounts:password_reset_complete"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("Otra-Clave-Segura-77"))

    def test_an_unknown_address_gets_the_same_answer_and_no_email(self):
        """The page must not tell a live address from an unknown one."""
        response = self._ask("nobody@example.com")
        self.assertRedirects(response, reverse("accounts:password_reset_done"))
        self.assertEqual(mail.outbox, [])

    def test_a_used_link_stops_working(self):
        self._ask(self.user.email)
        link = re.search(r"https?://\S+", mail.outbox[0].body).group(0)
        page = self.client.get(link, follow=True)
        target = page.redirect_chain[-1][0]
        self.client.post(
            target,
            {"new_password1": "Otra-Clave-Segura-77", "new_password2": "Otra-Clave-Segura-77"},
        )
        again = self.client.get(link, follow=True)
        self.assertContains(again, "Este enlace ya no funciona")

    def test_the_login_page_links_to_the_reset(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertContains(response, reverse("accounts:password_reset"))
