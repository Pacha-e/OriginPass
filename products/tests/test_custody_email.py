"""Custody can rest on an email address, and the old chains survive the change."""

from django.db import IntegrityError, connection, transaction
from django.db.migrations.executor import MigrationExecutor
from django.test import TestCase, TransactionTestCase
from django.utils import timezone

from audit.integrity import GENESIS, sign
from audit.models import Action, AuditEntry
from products.models import CustodyTransfer, Product, TransferState
from test_support.factories import make_product, make_user

BEFORE_EMAIL = [("products", "0011_product_line_required")]
AFTER_RESIGN = [("products", "0013_resign_custody_with_email")]
AFTER_CLOSE = [("products", "0014_close_open_offers")]
CLOSING_REASON = "Cerrada al cambiar el sistema de entregas"


class EmailHolderTests(TestCase):
    def setUp(self):
        self.product = make_product()
        self.maker = self.product.company.owner

    def test_transfer_to_email_leaves_no_account_holder(self):
        CustodyTransfer.objects.create(
            product=self.product,
            from_holder=self.maker,
            to_email="ana@correo.co",
            state=TransferState.ACCEPTED,
            resolved_at=timezone.now(),
        )

        self.assertIsNone(self.product.current_holder)
        self.assertEqual(self.product.holder_email, "ana@correo.co")
        self.assertFalse(Product.objects.held_by(self.maker).exists())
        self.assertEqual(CustodyTransfer.verify_chain(self.product), (True, None))

    def test_check_refuses_both_receivers(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            CustodyTransfer.objects.create(
                product=self.product,
                from_holder=self.maker,
                to_holder=make_user("otra@correo.co"),
                to_email="ana@correo.co",
            )

    def test_check_refuses_no_sender(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            CustodyTransfer.objects.create(product=self.product, to_email="ana@correo.co")


class MigrationTests(TransactionTestCase):
    """Old chains, signed without the email columns, are signed again."""

    def setUp(self):
        self.executor = MigrationExecutor(connection)
        self.executor.migrate(BEFORE_EMAIL)
        apps = self.executor.loader.project_state(BEFORE_EMAIL).apps
        self.OldTransfer = apps.get_model("products", "CustodyTransfer")

        product = make_product()
        self.product_id = product.pk
        maker = product.company.owner
        buyer = make_user("comprador@correo.co")
        # One accepted handover and one open offer back, signed the old way.
        self.accepted_id = self._old_row(maker.pk, buyer.pk, TransferState.ACCEPTED, GENESIS)
        accepted = self.OldTransfer.objects.get(pk=self.accepted_id)
        self.open_id = self._old_row(
            buyer.pk, maker.pk, TransferState.INITIATED, accepted.entry_hash
        )

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())

    def _old_row(self, from_id, to_id, state, previous):
        created = timezone.now()
        row = self.OldTransfer(
            product_id=self.product_id,
            from_holder_id=from_id,
            to_holder_id=to_id,
            state=state,
            note="",
            created_at=created,
            resolved_at=created if state == TransferState.ACCEPTED else None,
            previous_hash=previous,
        )
        row.entry_hash = sign(previous, self.product_id, from_id, to_id, "", created.isoformat())
        row.save()
        return row.pk

    def _migrate(self, target):
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()
        executor.migrate(target)

    def test_old_chains_verify_after_resign(self):
        self._migrate(AFTER_RESIGN)

        product = Product.objects.get(pk=self.product_id)
        self.assertEqual(CustodyTransfer.verify_chain(product), (True, None))

    def test_open_offers_are_declined_with_note(self):
        self._migrate(AFTER_CLOSE)

        offer = CustodyTransfer.objects.get(pk=self.open_id)
        self.assertEqual(offer.state, TransferState.DECLINED)
        self.assertIsNotNone(offer.resolved_at)
        entry = AuditEntry.objects.get(action=Action.CUSTODY_DECLINED, target_id=self.open_id)
        self.assertEqual(entry.reason, CLOSING_REASON)
        self.assertEqual(AuditEntry.verify_chain(), (True, None))
        product = Product.objects.get(pk=self.product_id)
        self.assertEqual(CustodyTransfer.verify_chain(product), (True, None))
