"""The chain of custody: who may hand a product on, and what shows when the chain is edited."""

from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, transaction
from django.test import TestCase

from audit.integrity import GENESIS
from audit.models import Action, AuditEntry
from products.models import CustodyTransfer
from test_support.factories import make_admin, make_approved_company, make_product, make_user


class CustodyChainTests(TestCase):
    """Only the current holder transfers, and a revoked product transfers to nobody."""

    def setUp(self):
        self.company = make_approved_company()
        self.admin = make_admin()
        self.product = make_product(self.company)
        self.buyer = make_user("buyer@example.co")

    def _hand_to(self, holder, from_holder=None):
        return CustodyTransfer.objects.create(
            product=self.product,
            from_holder=from_holder or self.company.owner,
            to_holder=holder,
        )

    def test_the_first_holder_is_the_owner_of_the_registering_company(self):
        self.assertEqual(self.product.current_holder, self.company.owner)

    def test_an_accepted_transfer_moves_the_holder(self):
        self._hand_to(self.buyer).accept()

        self.assertEqual(self.product.current_holder, self.buyer)

    def test_only_the_current_holder_can_transfer(self):
        stranger = make_user("stranger@example.co")
        transfer = CustodyTransfer(product=self.product, from_holder=stranger, to_holder=self.buyer)

        with self.assertRaises(ValidationError):
            transfer.clean()

    def test_a_revoked_product_accepts_no_transfer(self):
        self.product.revoke(actor=self.admin, reason="Reported as a counterfeit.")
        transfer = CustodyTransfer(
            product=self.product, from_holder=self.company.owner, to_holder=self.buyer
        )

        with self.assertRaises(ValidationError):
            transfer.clean()

    def test_a_resolved_transfer_cannot_be_rewritten(self):
        transfer = self._hand_to(self.buyer)
        transfer.accept()

        transfer.note = "Rewritten after the fact"
        with self.assertRaises(ValueError):
            transfer.save()

    def test_the_database_refuses_a_transfer_that_changes_nothing(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            self._hand_to(self.company.owner)


class CustodyChainIntegrityTests(TestCase):
    """One chain per product, and what shows when someone edits it with SQL."""

    def setUp(self):
        self.company = make_approved_company()
        self.product = make_product(self.company)
        self.first = make_user("first@example.co")
        self.second = make_user("second@example.co")

        step_one = CustodyTransfer.objects.create(
            product=self.product, from_holder=self.company.owner, to_holder=self.first
        )
        step_one.accept()
        step_two = CustodyTransfer.objects.create(
            product=self.product, from_holder=self.first, to_holder=self.second
        )
        step_two.accept()

    def _transfers(self):
        return CustodyTransfer.objects.filter(product=self.product).order_by("id")

    def test_an_untouched_chain_verifies(self):
        ok, problem = CustodyTransfer.verify_chain(self.product)

        self.assertTrue(ok, problem)

    def test_each_handover_links_to_the_one_before_it(self):
        transfers = list(self._transfers())

        self.assertEqual(transfers[0].previous_hash, GENESIS)
        self.assertEqual(transfers[1].previous_hash, transfers[0].entry_hash)

    def test_rewriting_a_handover_with_raw_sql_is_detected(self):
        target = self._transfers().first()

        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE products_custodytransfer SET to_holder_id = %s WHERE id = %s",
                [self.second.pk, target.pk],
            )

        ok, problem = CustodyTransfer.verify_chain(self.product)
        self.assertFalse(ok)
        self.assertIn("altered since it was written", problem)

    def test_removing_a_handover_from_the_middle_is_detected(self):
        target = self._transfers().first()

        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM products_custodytransfer WHERE id = %s", [target.pk])

        ok, problem = CustodyTransfer.verify_chain(self.product)
        self.assertFalse(ok)
        self.assertIn("removed or reordered", problem)

    def test_resolving_a_transfer_is_written_into_the_audit_trail(self):
        """The state is outside the row's signature, so it is evidenced there."""
        actions = set(AuditEntry.objects.values_list("action", flat=True))

        self.assertIn(Action.CUSTODY_ACCEPTED, actions)

        ok, problem = AuditEntry.verify_chain()
        self.assertTrue(ok, problem)
