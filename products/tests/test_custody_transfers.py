"""Custody transfers through the views: FR35 to FR40, FR54 and FR55.

Each test below that names a defect was written to fail against the code that
had it: a claim that reported success without moving the product, an admin
revocation that ended on a missing page, a receiver told their product had been
revoked when they accepted it, and offers made by an account that no longer
held the product.
"""

from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse

from products.models import CustodyTransfer, TransferState
from test_support.factories import (
    ADMIN_PASSWORD,
    OWNER_PASSWORD,
    make_admin,
    make_company,
    make_product,
    make_user,
)


def logged_in(user, password=OWNER_PASSWORD):
    client = Client()
    assert client.login(email=user.email, password=password)
    return client


class TransferFlowTests(TestCase):
    def setUp(self):
        self.owner = make_user(email="maker@tuchin.co")
        self.buyer = make_user(email="buyer@example.com")
        self.company = make_company(owner=self.owner, status="APPROVED")
        self.product = make_product(company=self.company)
        self.seller_client = logged_in(self.owner)
        self.buyer_client = logged_in(self.buyer)

    def _offer(self, client=None, to=None, note="Sold in Montería"):
        return (client or self.seller_client).post(
            reverse("products:transfer_initiate", args=[self.product.pk]),
            {"to_holder_email": (to or self.buyer).email, "note": note},
        )

    # FR35, FR54

    def test_current_holder_offers_a_transfer(self):
        response = self._offer()
        self.assertRedirects(response, reverse("products:custody"))
        transfer = self.product.custody_transfers.get()
        self.assertEqual(transfer.state, TransferState.INITIATED)
        self.assertEqual(transfer.to_holder, self.buyer)
        self.assertEqual(transfer.note, "Sold in Montería")

    def test_the_receiver_is_emailed_when_a_transfer_is_offered(self):
        self._offer()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.buyer.email])
        self.assertIn(self.product.name, mail.outbox[0].body)

    def test_the_transfer_code_is_shown_to_the_seller_only(self):
        self._offer()
        code = str(self.product.custody_transfers.get().transfer_code)
        self.assertContains(self.seller_client.get(reverse("products:custody")), code)
        self.assertNotContains(self.buyer_client.get(reverse("products:custody")), code)
        self.assertNotIn(code, mail.outbox[0].body)

    # FR38, FR39

    def test_a_non_holder_is_refused_with_the_reason(self):
        stranger = make_user(email="stranger@example.com")
        response = self._offer(client=logged_in(stranger))
        self.assertContains(response, "Solo quien tiene el producto ahora", status_code=403)
        self.assertFalse(CustodyTransfer.objects.exists())

    def test_the_maker_cannot_offer_a_piece_it_no_longer_holds(self):
        """Defect: the company could still offer a product it had handed over."""
        self._offer()
        self.product.custody_transfers.get().accept(actor=self.buyer)
        stranger = make_user(email="stranger@example.com")
        response = self._offer(to=stranger)
        self.assertEqual(response.status_code, 403)
        self.assertFalse(CustodyTransfer.objects.filter(state=TransferState.INITIATED).exists())

    def test_the_new_holder_can_pass_it_on(self):
        """A distributor or a buyer holds products too, without a company."""
        self._offer()
        self.product.custody_transfers.get().accept(actor=self.buyer)
        third = make_user(email="third@example.com")
        response = self._offer(client=self.buyer_client, to=third)
        self.assertRedirects(response, reverse("products:custody"))
        self.assertTrue(
            CustodyTransfer.objects.filter(
                from_holder=self.buyer, to_holder=third, state=TransferState.INITIATED
            ).exists()
        )

    def test_only_one_offer_is_open_at_a_time(self):
        """Defect: two open offers could both be accepted, and the product sold twice."""
        self._offer()
        response = self._offer(to=make_user(email="second@example.com"))
        self.assertContains(response, "ya tiene una entrega pendiente")
        self.assertEqual(CustodyTransfer.objects.filter(state=TransferState.INITIATED).count(), 1)

    def test_a_revoked_product_cannot_be_transferred(self):
        self.product.revoke(actor=self.owner, reason="Recalled.")
        response = self.seller_client.get(
            reverse("products:transfer_initiate", args=[self.product.pk])
        )
        self.assertContains(response, "producto anulado no se puede entregar", status_code=403)

    # FR36, FR37

    def test_receiver_can_accept(self):
        self._offer()
        transfer = self.product.custody_transfers.get()
        response = self.buyer_client.post(
            reverse("products:transfer_respond", args=[transfer.pk]), {"action": "accept"}
        )
        self.assertRedirects(response, reverse("products:custody"))
        transfer.refresh_from_db()
        self.assertEqual(transfer.state, TransferState.ACCEPTED)
        self.assertEqual(self.product.current_holder, self.buyer)

    def test_accepting_sends_no_revocation_notice(self):
        """Defect: accepting a transfer emailed the holder that it had been revoked."""
        self._offer()
        mail.outbox.clear()
        transfer = self.product.custody_transfers.get()
        self.buyer_client.post(
            reverse("products:transfer_respond", args=[transfer.pk]), {"action": "accept"}
        )
        self.assertEqual(mail.outbox, [])

    def test_receiver_can_decline(self):
        self._offer()
        transfer = self.product.custody_transfers.get()
        self.buyer_client.post(
            reverse("products:transfer_respond", args=[transfer.pk]), {"action": "decline"}
        )
        transfer.refresh_from_db()
        self.assertEqual(transfer.state, TransferState.DECLINED)
        self.assertEqual(self.product.current_holder, self.owner)

    def test_a_resolved_transfer_is_not_answered_again(self):
        self._offer()
        transfer = self.product.custody_transfers.get()
        transfer.accept(actor=self.buyer)
        response = self.buyer_client.post(
            reverse("products:transfer_respond", args=[transfer.pk]), {"action": "decline"}
        )
        self.assertRedirects(response, reverse("products:custody"))
        transfer.refresh_from_db()
        self.assertEqual(transfer.state, TransferState.ACCEPTED)

    def test_the_sender_cannot_answer_their_own_offer(self):
        self._offer()
        transfer = self.product.custody_transfers.get()
        response = self.seller_client.get(reverse("products:transfer_respond", args=[transfer.pk]))
        self.assertEqual(response.status_code, 404)

    # FR40

    def _claim(self, client, transfer_code):
        return client.post(
            reverse("products:transfer_claim"),
            {"passport_code": self.product.passport_code, "transfer_code": transfer_code},
        )

    def test_the_buyer_claims_with_both_codes_and_becomes_the_holder(self):
        """Defect: the claim reported success and left the product where it was."""
        self._offer()
        transfer = self.product.custody_transfers.get()
        response = self._claim(self.buyer_client, str(transfer.transfer_code))
        self.assertRedirects(response, reverse("products:custody"))
        self.assertEqual(self.product.current_holder, self.buyer)
        ok, problem = CustodyTransfer.verify_chain(self.product)
        self.assertTrue(ok, problem)

    def test_codes_read_over_a_shoulder_move_nothing(self):
        self._offer()
        transfer = self.product.custody_transfers.get()
        thief = make_user(email="thief@example.com")
        response = self._claim(logged_in(thief), str(transfer.transfer_code))
        self.assertContains(response, "Ninguna entrega pendiente para tu cuenta")
        transfer.refresh_from_db()
        self.assertEqual(transfer.state, TransferState.INITIATED)
        self.assertEqual(self.product.current_holder, self.owner)

    def test_a_wrong_transfer_code_is_refused(self):
        self._offer()
        response = self._claim(self.buyer_client, "00000000-0000-0000-0000-000000000000")
        self.assertContains(response, "Ninguna entrega pendiente para tu cuenta")


class RevocationNoticeTests(TestCase):
    def setUp(self):
        self.owner = make_user(email="maker@tuchin.co")
        self.holder = make_user(email="holder@example.com")
        self.product = make_product(company=make_company(owner=self.owner, status="APPROVED"))
        CustodyTransfer.objects.create(
            product=self.product, from_holder=self.owner, to_holder=self.holder
        ).accept(actor=self.holder)

    def test_the_holder_is_told_when_the_company_revokes(self):
        logged_in(self.owner).post(
            reverse("products:product_revoke", args=[self.product.pk]),
            {"reason": "Recalled for a defect."},
        )
        self.assertEqual(mail.outbox[-1].to, [self.holder.email])
        self.assertIn("Recalled for a defect.", mail.outbox[-1].body)

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
