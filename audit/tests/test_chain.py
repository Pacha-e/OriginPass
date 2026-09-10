"""What happens when someone goes around the model and writes SQL.

The guard on `save()` is Python. Raw SQL never calls it, so these are the cases
that matter: the chain is what makes them visible.
"""

from datetime import timedelta

from django.conf import settings
from django.db import IntegrityError, connection, transaction
from django.test import TestCase, override_settings
from django.utils import timezone

from audit.integrity import sign
from audit.models import Action, AuditEntry
from test_support.factories import (
    make_admin,
    make_approved_company,
    make_company,
    make_product,
    make_user,
)


class ChainTests(TestCase):
    def setUp(self):
        self.admin = make_admin()
        self.owner = make_user()
        self.company = make_company(self.owner)

        self.company.approve(actor=self.admin)
        self.company.suspend(actor=self.admin, reason="Counterfeit reports.")
        self.company.reactivate(actor=self.admin)

    def _oldest(self):
        return AuditEntry.objects.order_by("id").first()

    def test_an_untouched_trail_verifies(self):
        ok, problem = AuditEntry.verify_chain()

        self.assertTrue(ok, problem)
        self.assertIsNone(problem)

    def test_every_entry_is_signed(self):
        for entry in AuditEntry.objects.all():
            self.assertEqual(len(entry.entry_hash), 64)
            self.assertTrue(entry.is_intact)

    def test_rewriting_an_entry_with_raw_sql_is_detected(self):
        target = self._oldest()

        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE audit_auditentry SET reason = %s WHERE id = %s",
                ["Rewritten after the fact", target.pk],
            )

        ok, problem = AuditEntry.verify_chain()
        self.assertFalse(ok)
        self.assertIn("altered since it was written", problem)
        self.assertIn(str(target.pk), problem)

    def test_deleting_an_entry_with_raw_sql_is_detected(self):
        target = AuditEntry.objects.order_by("id")[1]

        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM audit_auditentry WHERE id = %s", [target.pk])

        ok, problem = AuditEntry.verify_chain()
        self.assertFalse(ok)
        self.assertIn("removed or reordered", problem)

    def test_changing_the_recorded_actor_is_detected(self):
        target = self._oldest()

        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE audit_auditentry SET actor_id = %s WHERE id = %s",
                [self.owner.pk, target.pk],
            )

        ok, _ = AuditEntry.verify_chain()

        self.assertFalse(ok)

    def test_backdating_an_entry_is_detected(self):
        target = self._oldest()

        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE audit_auditentry SET created_at = %s WHERE id = %s",
                [timezone.now() - timedelta(days=365), target.pk],
            )

        ok, _ = AuditEntry.verify_chain()

        self.assertFalse(ok)

    def test_a_forged_entry_appended_with_raw_sql_is_detected(self):
        """The attacker knows the scheme but not the key."""
        last = AuditEntry.objects.order_by("-id").first()

        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO audit_auditentry "
                "(actor_id, action, target_type, target_id, reason, created_at,"
                " previous_hash, entry_hash) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                [
                    self.admin.pk,
                    Action.COMPANY_APPROVED,
                    "Company",
                    self.company.pk,
                    "Approval that never happened",
                    timezone.now(),
                    last.entry_hash,
                    sign("something", "the attacker", "cannot know"),
                ],
            )

        ok, problem = AuditEntry.verify_chain()
        self.assertFalse(ok)
        self.assertIn("altered since it was written", problem)

    def test_the_database_refuses_a_second_entry_linked_to_the_same_predecessor(self):
        """The fork the lock in `record` cannot prevent on an empty table.

        Two writers racing to append the first entry of a new database both
        read GENESIS and both link to it, because there is no row to lock. The
        chain is linear, so the database rejects the second one.
        """
        existing = self._oldest()

        with self.assertRaises(IntegrityError), transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO audit_auditentry "
                    "(actor_id, action, target_type, target_id, reason, created_at,"
                    " previous_hash, entry_hash) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    [
                        self.admin.pk,
                        Action.COMPANY_APPROVED,
                        "companies.Company",
                        self.company.pk,
                        "A second entry claiming the same predecessor",
                        timezone.now(),
                        existing.previous_hash,
                        sign("a", "forged", "entry"),
                    ],
                )

    def test_a_signature_made_with_another_key_does_not_pass(self):
        entry = self._oldest()

        with override_settings(SECRET_KEY="a-different-secret-key-entirely"):
            self.assertFalse(entry.is_intact)

        self.assertTrue(entry.is_intact)


class KeyRotationTests(TestCase):
    """Rotating the signing key must not make every existing record look forged.

    The two cases have to stay apart. A record signed with a key that is being
    retired is a record this system wrote and still stands behind; a record
    signed with a key it never used is a forgery. Collapsing them would drown a
    real alteration in a report that flags everything.
    """

    def setUp(self):
        self.admin = make_admin()
        self.owner = make_user()
        self.company = make_company(self.owner)
        self.company.approve(actor=self.admin)
        self.product = make_product(make_approved_company(email="otro@monteria.co"))

    def test_an_entry_signed_with_a_retired_key_still_verifies(self):
        entry = AuditEntry.objects.order_by("id").first()

        with override_settings(
            SECRET_KEY="the-key-rotated-in",
            SECRET_KEY_FALLBACKS=[settings.SECRET_KEY],
        ):
            self.assertTrue(entry.is_intact)

    def test_the_whole_trail_still_verifies_after_a_rotation(self):
        with override_settings(
            SECRET_KEY="the-key-rotated-in",
            SECRET_KEY_FALLBACKS=[settings.SECRET_KEY],
        ):
            ok, problem = AuditEntry.verify_chain()

        self.assertTrue(ok, problem)

    def test_a_product_signed_with_a_retired_key_still_verifies(self):
        with override_settings(
            SECRET_KEY="the-key-rotated-in",
            SECRET_KEY_FALLBACKS=[settings.SECRET_KEY],
        ):
            self.product.refresh_from_db()
            self.assertTrue(self.product.is_intact)

    def test_a_key_that_was_never_ours_is_still_refused(self):
        entry = AuditEntry.objects.order_by("id").first()

        with override_settings(
            SECRET_KEY="the-key-rotated-in",
            SECRET_KEY_FALLBACKS=["a-key-this-system-never-used"],
        ):
            self.assertFalse(entry.is_intact)

    def test_a_record_altered_under_the_retired_key_is_still_caught(self):
        """The fallback accepts an old signature, not an old row that changed."""
        entry = AuditEntry.objects.order_by("id").first()

        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE audit_auditentry SET reason = %s WHERE id = %s",
                ["Rewritten during the rotation window", entry.pk],
            )

        with override_settings(
            SECRET_KEY="the-key-rotated-in",
            SECRET_KEY_FALLBACKS=[settings.SECRET_KEY],
        ):
            ok, problem = AuditEntry.verify_chain()

        self.assertFalse(ok)
        self.assertIn("altered since it was written", problem)
