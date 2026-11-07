"""Custody through the views: revocation notices (FR55) and the retired offer pages.

Each test below that names a defect was written to fail against the code that
had it: a claim that reported success without moving the product, an admin
revocation that ended on a missing page, a receiver told their product had been
revoked when they accepted it, and offers made by an account that no longer
held the product.
"""

# ---- External imports ----
from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse

# ---- Internal imports ----
from products.models import CustodyTransfer
from test_support.factories import (
    ADMIN_PASSWORD,
    OWNER_PASSWORD,
    make_admin,
    make_company,
    make_product,
    make_user,
)


class RevocationNoticeTests(TestCase):
    def setUp(self):
        self.owner = make_user(email="maker@tuchin.co")
        self.holder = make_user(email="holder@example.com")
        self.product = make_product(company=make_company(owner=self.owner, status="APPROVED"))
        CustodyTransfer.objects.create(
            product=self.product, from_holder=self.owner, to_holder=self.holder
        ).accept(actor=self.holder)

    def test_an_admin_revocation_lands_on_the_public_page(self):
        """Defect: the administrator's revocation ended on a missing page."""
        admin = make_admin()
        response = logged_in(admin, ADMIN_PASSWORD).post(
            reverse("products:admin_revoke", args=[self.product.pk]),
            {"reason": "Fraud confirmed."},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Anulado")
        self.assertContains(response, "Fraud confirmed.")
        self.assertEqual(mail.outbox[-1].to, [self.holder.email])

    def test_the_holder_is_told_when_the_company_revokes(self):
        logged_in(self.owner).post(
            reverse("products:product_revoke", args=[self.product.pk]),
            {"reason": "Recalled for a defect."},
        )
        self.assertEqual(mail.outbox[-1].to, [self.holder.email])
        self.assertIn("Recalled for a defect.", mail.outbox[-1].body)


class RetiredOfferRoutesTests(TestCase):
    """The offer answered later with a long code is gone: products change hands
    in person with the rotating code (products.handover_views)."""

    def test_the_old_offer_pages_no_longer_exist(self):
        client = logged_in(make_user(email="buyer@example.com"))
        for path in (
            "/products/custody/claim/",
            "/products/1/transfer/",
            "/products/custody/1/answer/",
        ):
            with self.subTest(path=path):
                self.assertEqual(client.get(path).status_code, 404)


# ---- Public API ----
def logged_in(user, password=OWNER_PASSWORD):
    client = Client()
    assert client.login(email=user.email, password=password)
    return client
