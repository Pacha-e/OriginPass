"""Every status change appends an entry, and no entry is edited afterwards."""

from django.test import TestCase

from audit.models import Action, AuditEntry
from test_support.factories import make_admin, make_company


class AuditTrailTests(TestCase):
    def setUp(self):
        self.admin = make_admin()
        self.company = make_company()

    def test_an_approval_is_recorded(self):
        self.company.approve(actor=self.admin)

        entry = AuditEntry.objects.get(target_type="Company", target_id=self.company.pk)
        self.assertEqual(entry.action, Action.COMPANY_APPROVED)
        self.assertEqual(entry.actor, self.admin)

    def test_a_rejection_records_its_reason(self):
        self.company.reject(actor=self.admin, reason="Registry code not found.")

        entry = AuditEntry.objects.first()
        self.assertEqual(entry.action, Action.COMPANY_REJECTED)
        self.assertEqual(entry.reason, "Registry code not found.")

    def test_every_transition_appends_rather_than_replaces(self):
        self.company.approve(actor=self.admin)
        self.company.suspend(actor=self.admin, reason="Counterfeit reports.")
        self.company.reactivate(actor=self.admin)

        actions = list(AuditEntry.objects.order_by("id").values_list("action", flat=True))

        self.assertEqual(
            actions,
            [Action.COMPANY_APPROVED, Action.COMPANY_SUSPENDED, Action.COMPANY_REACTIVATED],
        )

    def test_an_entry_cannot_be_edited(self):
        self.company.approve(actor=self.admin)
        entry = AuditEntry.objects.first()

        entry.reason = "Rewritten after the fact"
        with self.assertRaises(ValueError):
            entry.save()
