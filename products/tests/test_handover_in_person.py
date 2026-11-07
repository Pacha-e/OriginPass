"""Handing a piece over in person: the holder shows the code, the receiver types it."""

import threading

from django.db import connection
from django.test import Client, TestCase, TransactionTestCase
from django.urls import reverse
from django.utils import timezone

from products.handover import handover_code, product_code_args
from products.models import CustodyTransfer, TransferState
from test_support.factories import OWNER_PASSWORD, make_product, make_user


def code_for(product):
    return handover_code(*product_code_args(product), timezone.now())


class HandoverTests(TestCase):
    def setUp(self):
        self.product = make_product()
        self.maker = self.product.company.owner
        self.buyer = make_user("comprador@correo.co")
        self.receive_url = reverse("products:receive", args=[self.product.passport_code])

    def _receive(self, client, code):
        return client.post(self.receive_url, {"code": code})

    def test_holder_sees_code_and_others_get_404(self):
        self.client.force_login(self.maker)
        page = self.client.get(reverse("products:handover", args=[self.product.pk]))
        code = code_for(self.product)
        self.assertContains(page, f"{code[:3]} {code[3:]}")
        data = self.client.get(reverse("products:handover_code", args=[self.product.pk])).json()
        self.assertEqual(data["code"], code_for(self.product))
        self.assertTrue(1 <= data["seconds_left"] <= 120)

        self.client.force_login(self.buyer)
        self.assertEqual(
            self.client.get(reverse("products:handover", args=[self.product.pk])).status_code, 404
        )
        response = self.client.get(reverse("products:handover_code", args=[self.product.pk]))
        self.assertEqual(response.status_code, 404)

    def test_code_json_is_never_cached(self):
        self.client.force_login(self.maker)
        response = self.client.get(reverse("products:handover_code", args=[self.product.pk]))
        self.assertIn("no-store", response["Cache-Control"])

    def test_receive_with_right_code_moves_the_piece(self):
        self.client.force_login(self.buyer)
        response = self._receive(self.client, code_for(self.product))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.product.current_holder, self.buyer)
        transfer = self.product.custody_transfers.get()
        self.assertEqual(transfer.state, TransferState.ACCEPTED)
        self.assertEqual(transfer.from_holder, self.maker)
        self.assertEqual(CustodyTransfer.verify_chain(self.product), (True, None))

    def test_wrong_code_counts_a_failure_and_says_so(self):
        self.client.force_login(self.buyer)
        right = code_for(self.product)
        wrong = "000000" if right != "000000" else "111111"

        response = self._receive(self.client, wrong)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "no sirve")
        self.assertEqual(self.product.current_holder, self.maker)

    def test_code_is_dead_right_after_handover(self):
        code = code_for(self.product)
        self.client.force_login(self.buyer)
        self._receive(self.client, code)

        other = Client()
        other.force_login(make_user("otro@correo.co"))
        response = other.post(self.receive_url, {"code": code})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.product.current_holder, self.buyer)

    def test_double_submit_does_not_add_a_second_row(self):
        code = code_for(self.product)
        self.client.force_login(self.buyer)
        self._receive(self.client, code)

        response = self._receive(self.client, code)

        self.assertEqual(self.product.custody_transfers.count(), 1)
        self.assertContains(self.client.get(response["Location"]), "Ya es tuyo")

    def test_revoked_piece_cannot_be_received(self):
        code = code_for(self.product)
        self.product.revoke(actor=self.maker, reason="Se perdió.")
        self.client.force_login(self.buyer)

        response = self._receive(self.client, code)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.product.custody_transfers.exists())

    def test_receive_page_shows_photo_name_maker_holder(self):
        self.client.force_login(self.buyer)
        response = self.client.get(self.receive_url)

        self.assertContains(response, self.product.name)
        self.assertContains(response, self.product.company.legal_name)
        self.assertContains(response, 'name="code"')

    def test_receive_needs_an_account(self):
        response = self.client.get(self.receive_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response["Location"])

    def test_genuine_verdict_offers_to_receive(self):
        response = self.client.get(
            reverse("verification:verify", args=[self.product.passport_code])
        )
        self.assertContains(response, self.receive_url)


class ConcurrentReceiveTests(TransactionTestCase):
    """Two people type the same code at once; the product has one holder after."""

    def test_concurrent_receivers_only_one_wins(self):
        product = make_product()
        code = code_for(product)
        url = reverse("products:receive", args=[product.passport_code])
        receivers = [make_user(f"r{index}@correo.co") for index in range(2)]
        barrier = threading.Barrier(2)

        def receive(user):
            client = Client()
            client.login(email=user.email, password=OWNER_PASSWORD)
            barrier.wait()
            client.post(url, {"code": code})
            connection.close()

        threads = [threading.Thread(target=receive, args=[user]) for user in receivers]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        self.assertEqual(product.custody_transfers.count(), 1)
        self.assertIn(product.current_holder, receivers)
