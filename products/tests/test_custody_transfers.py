"""Custody transfers (FR35-FR40)."""

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from products.models import ProductStatus, TransferState
from test_support.factories import OWNER_PASSWORD, make_company, make_product, make_user


class TransferFlowTests(TestCase):
    def setUp(self):
        self.owner = make_user(email="maker@tuchin.co")
        self.buyer = make_user(email="buyer@example.com")
        self.company = make_company(owner=self.owner, status="APPROVED")
        self.product = make_product(company=self.company)
        self.seller_client = Client(enforce_csrf_checks=True)
        assert self.seller_client.login(email=self.owner.email, password=OWNER_PASSWORD)
        self.buyer_client = Client(enforce_csrf_checks=True)
        assert self.buyer_client.login(email=self.buyer.email, password=OWNER_PASSWORD)

    def _initiate(self):
        url = reverse("products:transfer_initiate", args=[self.product.pk])
        self.seller_client.get(url)
        csrf = self.seller_client.cookies["csrftoken"].value
        return self.seller_client.post(
            url,
            {
                "to_holder_email": self.buyer.email,
                "note": "Sold in Montería",
                "csrfmiddlewaretoken": csrf,
            },
        )

    def test_current_holder_offers_a_transfer(self):
        response = self._initiate()
        self.assertEqual(response.status_code, 302)
        transfer = self.product.custody_transfers.get()
        self.assertEqual(transfer.state, TransferState.INITIATED)
        self.assertEqual(transfer.from_holder, self.owner)
        self.assertEqual(transfer.to_holder, self.buyer)
        self.assertEqual(transfer.note, "Sold in Montería")
        # The transfer code the seller shares in person.
        self.assertIsNotNone(transfer.transfer_code)

    def test_a_non_holder_cannot_offer_a_transfer(self):
        stranger = make_user(email="stranger@example.com")
        stranger_client = Client(enforce_csrf_checks=True)
        assert stranger_client.login(email=stranger.email, password=OWNER_PASSWORD)
        url = reverse("products:transfer_initiate", args=[self.product.pk])
        stranger_client.get(url)
        csrf = stranger_client.cookies["csrftoken"].value
        response = stranger_client.post(
            url,
            {"to_holder_email": self.buyer.email, "csrfmiddlewaretoken": csrf},
        )
        # 404 because the company-owner lookup breaks: the seller is not
        # the owner of this product's company.
        self.assertEqual(response.status_code, 404)

    def test_receiver_can_accept(self):
        self._initiate()
        transfer = self.product.custody_transfers.get()
        url = reverse("products:transfer_respond", args=[transfer.pk])
        self.buyer_client.get(url)
        csrf = self.buyer_client.cookies["csrftoken"].value
        response = self.buyer_client.post(
            url, {"action": "accept", "csrfmiddlewaretoken": csrf}
        )
        self.assertEqual(response.status_code, 302)
        transfer.refresh_from_db()
        self.assertEqual(transfer.state, TransferState.ACCEPTED)
        self.assertIsNotNone(transfer.resolved_at)

    def test_receiver_can_decline(self):
        self._initiate()
        transfer = self.product.custody_transfers.get()
        url = reverse("products:transfer_respond", args=[transfer.pk])
        self.buyer_client.get(url)
        csrf = self.buyer_client.cookies["csrftoken"].value
        response = self.buyer_client.post(
            url, {"action": "decline", "csrfmiddlewaretoken": csrf}
        )
        self.assertEqual(response.status_code, 302)
        transfer.refresh_from_db()
        self.assertEqual(transfer.state, TransferState.DECLINED)

    def test_a_resolved_transfer_cannot_be_answered_again(self):
        self._initiate()
        transfer = self.product.custody_transfers.get()
        transfer.accept(actor=self.buyer)
        url = reverse("products:transfer_respond", args=[transfer.pk])
        response = self.buyer_client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_a_stranger_cannot_answer(self):
        self._initiate()
        transfer = self.product.custody_transfers.get()
        url = reverse("products:transfer_respond", args=[transfer.pk])
        response = self.seller_client.get(url)
        # The seller cannot accept or decline their own offer.
        self.assertEqual(response.status_code, 404)

    def test_buyer_claims_with_passport_and_transfer_code(self):
        self._initiate()
        transfer = self.product.custody_transfers.get()
        claimer = make_user(email="claimer@example.com")
        claimer_client = Client(enforce_csrf_checks=True)
        assert claimer_client.login(email=claimer.email, password=OWNER_PASSWORD)
        url = reverse("products:transfer_claim")
        claimer_client.get(url)
        csrf = claimer_client.cookies["csrftoken"].value
        response = claimer_client.post(
            url,
            {
                "passport_code": self.product.passport_code,
                "transfer_code": str(transfer.transfer_code),
                "csrfmiddlewaretoken": csrf,
            },
        )
        self.assertEqual(response.status_code, 302)
        transfer.refresh_from_db()
        self.assertEqual(transfer.state, TransferState.ACCEPTED)

    def test_a_wrong_transfer_code_is_refused(self):
        self._initiate()
        claimer = make_user(email="claimer2@example.com")
        claimer_client = Client(enforce_csrf_checks=True)
        assert claimer_client.login(email=claimer.email, password=OWNER_PASSWORD)
        url = reverse("products:transfer_claim")
        claimer_client.get(url)
        csrf = claimer_client.cookies["csrftoken"].value
        response = claimer_client.post(
            url,
            {
                "passport_code": self.product.passport_code,
                "transfer_code": "00000000-0000-0000-0000-000000000000",
                "csrfmiddlewaretoken": csrf,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No pending transfer matches those codes")

    def test_a_revoked_product_cannot_be_transferred(self):
        self.product.revoke(actor=self.owner, reason="Recalled.")
        url = reverse("products:transfer_initiate", args=[self.product.pk])
        response = self.seller_client.get(url)
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "revoked product", status_code=403)
