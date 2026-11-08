"""Handing a product to a person without an account, by their email address."""

import re
from datetime import timedelta
from unittest import mock

from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from products.models import CustodyTransfer
from test_support.factories import OWNER_PASSWORD, make_product, make_user

ANA = "ana@correo.co"


class HandoverByEmailTests(TestCase):
    def setUp(self):
        self.product = make_product()
        self.maker = self.product.company.owner
        self.client.force_login(self.maker)
        self.url = reverse("products:handover_email", args=[self.product.pk])

    def _hand_to(self, email, confirm=None):
        return self.client.post(self.url, {"email": email, "email_again": confirm or email})

    def _link(self):
        return re.search(r"https?://\S+/reclamar/\S+/", mail.outbox[-1].body).group(0)

    def test_mismatched_emails_refused(self):
        response = self._hand_to(ANA, "anna@correo.co")

        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.product.custody_transfers.exists())
        self.assertEqual(mail.outbox, [])

    def test_email_sent_with_link(self):
        self._hand_to(ANA)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [ANA])
        self.assertIn(self.product.name, mail.outbox[0].body)
        self.assertIn("/reclamar/", mail.outbox[0].body)
        self.assertEqual(self.product.holder_email, ANA)
        self.assertIsNone(self.product.current_holder)

    def test_claim_with_matching_account_moves_to_account(self):
        self._hand_to(ANA)
        link = self._link()
        ana = make_user(ANA)
        self.client.force_login(ana)

        self.client.post(link)

        self.assertEqual(self.product.current_holder, ana)
        last = self.product.custody_transfers.order_by("-id").first()
        self.assertEqual((last.from_email, last.to_holder), (ANA, ana))
        self.assertEqual(CustodyTransfer.verify_chain(self.product), (True, None))

    def test_registering_same_email_without_link_does_not_claim(self):
        self._hand_to(ANA)
        self.client.logout()

        self.client.post(
            reverse("accounts:register"),
            {
                "email": ANA,
                "password1": OWNER_PASSWORD,
                "password2": OWNER_PASSWORD,
                "kind": "person",
            },
        )

        self.assertIsNone(self.product.current_holder)
        self.assertEqual(self.product.holder_email, ANA)

    def test_logged_in_as_other_account_cannot_claim(self):
        self._hand_to(ANA)
        link = self._link()
        self.client.force_login(make_user("otra@correo.co"))

        response = self.client.post(link)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, ANA)
        self.assertEqual(self.product.holder_email, ANA)

    def test_expired_token_after_30_days(self):
        self._hand_to(ANA)
        link = self._link()
        ana = make_user(ANA)
        self.client.force_login(ana)

        later = timezone.now() + timedelta(days=31)
        with mock.patch("django.core.signing.time.time", return_value=later.timestamp()):
            response = self.client.post(link)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.product.holder_email, ANA)

    def test_correction_kills_old_link(self):
        self._hand_to("ana@corre.co")
        old_link = self._link()

        self.client.post(
            reverse("products:correct_email", args=[self.product.pk]),
            {"email": ANA, "email_again": ANA},
        )
        new_link = self._link()
        self.assertNotEqual(old_link, new_link)
        self.assertEqual(self.product.holder_email, ANA)

        self.client.force_login(make_user("ana@corre.co"))
        self.client.post(old_link)
        self.assertEqual(self.product.holder_email, ANA)

    def test_only_the_giver_can_correct_or_resend(self):
        self._hand_to(ANA)
        self.client.force_login(make_user("otra@correo.co"))

        for name in ("products:correct_email", "products:resend_email"):
            with self.subTest(name=name):
                response = self.client.post(
                    reverse(name, args=[self.product.pk]),
                    {"email": "x@y.co", "email_again": "x@y.co"},
                )
                self.assertEqual(response.status_code, 404)

    def test_resend_sends_the_same_possession_again(self):
        self._hand_to(ANA)

        self.client.post(reverse("products:resend_email", args=[self.product.pk]))

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[1].to, [ANA])

    def test_public_page_shows_una_persona_not_email(self):
        self._hand_to(ANA)
        self.client.logout()

        response = self.client.get(
            reverse("verification:verify", args=[self.product.passport_code])
        )

        self.assertNotContains(response, ANA)
        self.assertContains(response, "Una persona")


class PendingEmailHandoversTests(TestCase):
    def test_custody_lists_products_waiting_for_their_email(self):
        product = make_product()
        maker = product.company.owner
        self.client.force_login(maker)
        self.client.post(
            reverse("products:handover_email", args=[product.pk]),
            {"email": ANA, "email_again": ANA},
        )

        response = self.client.get(reverse("products:custody"))

        self.assertContains(response, ANA)
        self.assertContains(response, reverse("products:correct_email", args=[product.pk]))
        self.assertContains(response, reverse("products:resend_email", args=[product.pk]))

    def test_handover_screen_offers_the_email_way(self):
        product = make_product()
        self.client.force_login(product.company.owner)
        response = self.client.get(reverse("products:handover", args=[product.pk]))
        self.assertContains(response, reverse("products:handover_email", args=[product.pk]))
