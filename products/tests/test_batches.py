"""Handing many products over at once, as one batch with its own QR and code."""

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from products.batches import (
    PERSON_BATCH_LIMIT,
    batch_code_args,
    cancel_batch,
    create_batch,
    receive_batch,
)
from products.handover import handover_code
from products.models import BatchState, CustodyTransfer, Product, TransferBatchItem
from test_support.factories import make_approved_company, make_product, make_user


def code_for(batch):
    return handover_code(*batch_code_args(batch), timezone.now())


def give(products, to):
    for product in products:
        CustodyTransfer.record_handover(product, actor=to, to_holder=to)


class BatchRulesTests(TestCase):
    def setUp(self):
        self.company = make_approved_company()
        self.maker = self.company.owner
        self.receiver = make_user("tienda@correo.co")

    def _products(self, count):
        return [make_product(self.company, name=f"Sombrero {index}") for index in range(count)]

    def test_person_limited_to_five(self):
        person = make_user("ana@correo.co")
        products = self._products(PERSON_BATCH_LIMIT + 1)
        give(products, person)

        with self.assertRaises(ValidationError):
            create_batch(person, products)
        batch = create_batch(person, products[:PERSON_BATCH_LIMIT])
        self.assertEqual(batch.items.count(), 5)

    def test_company_unlimited(self):
        batch = create_batch(self.maker, self._products(30))
        self.assertEqual(batch.items.count(), 30)

    def test_only_products_the_owner_holds(self):
        stranger = make_user("otro@correo.co")
        with self.assertRaises(ValidationError):
            create_batch(stranger, self._products(2))

    def test_receive_moves_all_and_closes_batch(self):
        products = self._products(3)
        batch = create_batch(self.maker, products)

        receive_batch(batch, self.receiver, code_for(batch), timezone.now())

        for product in products:
            self.assertEqual(Product.objects.get(pk=product.pk).current_holder, self.receiver)
            self.assertEqual(CustodyTransfer.verify_chain(product), (True, None))
        batch.refresh_from_db()
        self.assertEqual(batch.state, BatchState.HANDED)
        self.assertFalse(batch.items.filter(is_open=True).exists())

    def test_revoked_piece_in_batch_fails_whole_batch_and_names_it(self):
        products = self._products(3)
        batch = create_batch(self.maker, products)
        products[1].revoke(actor=self.maker, reason="Se perdió.")

        with self.assertRaisesMessage(ValidationError, products[1].name):
            receive_batch(batch, self.receiver, code_for(batch), timezone.now())

        for product in products:
            self.assertEqual(Product.objects.get(pk=product.pk).current_holder, self.maker)
        batch.refresh_from_db()
        self.assertEqual(batch.state, BatchState.OPEN)

    def test_piece_cannot_be_in_two_open_batches(self):
        products = self._products(2)
        create_batch(self.maker, products)

        with self.assertRaises(ValidationError):
            create_batch(self.maker, products[:1])
        with self.assertRaises(IntegrityError), transaction.atomic():
            batch = create_batch(self.maker, self._products(1))
            TransferBatchItem.objects.create(batch=batch, product=products[0], is_open=True)

    def test_batch_code_dies_when_handed(self):
        batch = create_batch(self.maker, self._products(2))
        code = code_for(batch)
        receive_batch(batch, self.receiver, code, timezone.now())

        with self.assertRaises(ValidationError):
            receive_batch(batch, make_user("tarde@correo.co"), code, timezone.now())

    def test_wrong_code_moves_nothing(self):
        products = self._products(2)
        batch = create_batch(self.maker, products)
        right = code_for(batch)
        wrong = "000000" if right != "000000" else "111111"

        with self.assertRaises(ValidationError):
            receive_batch(batch, self.receiver, wrong, timezone.now())
        self.assertEqual(Product.objects.get(pk=products[0].pk).current_holder, self.maker)

    def test_cancel_frees_the_products(self):
        products = self._products(2)
        batch = create_batch(self.maker, products)

        cancel_batch(batch, self.maker)

        create_batch(self.maker, products)

    def test_batch_not_shown_on_public_page(self):
        products = self._products(2)
        batch = create_batch(self.maker, products)

        response = self.client.get(reverse("verification:verify", args=[products[0].passport_code]))

        self.assertNotContains(response, batch.public_code)


class BatchScreensTests(TestCase):
    def setUp(self):
        self.company = make_approved_company()
        self.maker = self.company.owner
        self.products = [make_product(self.company, name="Sombrero vueltiao") for _ in range(4)]

    def test_owner_builds_a_batch_from_chosen_products(self):
        self.client.force_login(self.maker)
        response = self.client.post(
            reverse("products:batch_new"), {"product": [p.pk for p in self.products[:3]]}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.maker.batches.get().items.count(), 3)

    def test_owner_sees_the_code_and_others_get_404(self):
        batch = create_batch(self.maker, self.products)
        url = reverse("products:batch_handover", args=[batch.public_code])
        self.client.force_login(self.maker)
        code = code_for(batch)
        self.assertContains(self.client.get(url), f"{code[:3]} {code[3:]}")

        self.client.force_login(make_user("otro@correo.co"))
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_receiver_sees_the_list_and_receives_with_the_code(self):
        batch = create_batch(self.maker, self.products)
        receiver = make_user("tienda@correo.co")
        self.client.force_login(receiver)
        url = reverse("products:batch_receive", args=[batch.public_code])

        page = self.client.get(url)
        self.assertContains(page, "4 × Sombrero vueltiao")

        response = self.client.post(url, {"code": code_for(batch)})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Product.objects.held_by(receiver).count(), 4)
