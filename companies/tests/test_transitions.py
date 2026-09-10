"""A status change is only made from a status it can be made from.

Without this, an administrator posting straight to the approve address could
approve a company that had been rejected or suspended, with no record of the
decision in between. The rule lives on the model because the review view is not
its only caller: the demo command and the tests change status too.
"""

from django.test import TestCase
from django.urls import reverse

from audit.models import Action, AuditEntry
from companies.models import Company, CompanyStatus, TransitionNotAllowed
from test_support.factories import make_admin, make_company, make_user


class ApprovalTransitionTests(TestCase):
    def setUp(self):
        self.admin = make_admin()
        self.company = make_company()

    def test_a_pending_application_can_be_approved(self):
        self.company.approve(actor=self.admin)

        self.assertEqual(self.company.status, CompanyStatus.APPROVED)

    def test_an_approved_company_is_not_approved_again(self):
        self.company.approve(actor=self.admin)

        with self.assertRaises(TransitionNotAllowed):
            self.company.approve(actor=self.admin)

    def test_a_rejected_application_is_not_approved_without_being_resubmitted(self):
        self.company.reject(actor=self.admin, reason="Registry code not found.")

        with self.assertRaises(TransitionNotAllowed):
            self.company.approve(actor=self.admin)

    def test_a_suspended_company_is_reactivated_rather_than_approved(self):
        self.company.approve(actor=self.admin)
        self.company.suspend(actor=self.admin, reason="Counterfeit reports.")

        with self.assertRaises(TransitionNotAllowed):
            self.company.approve(actor=self.admin)

        self.company.reactivate(actor=self.admin)
        self.assertEqual(self.company.status, CompanyStatus.APPROVED)

    def test_a_pending_company_cannot_be_suspended(self):
        with self.assertRaises(TransitionNotAllowed):
            self.company.suspend(actor=self.admin, reason="Counterfeit reports.")

    def test_an_approved_company_cannot_be_rejected(self):
        self.company.approve(actor=self.admin)

        with self.assertRaises(TransitionNotAllowed):
            self.company.reject(actor=self.admin, reason="Changed my mind.")


class TwoAdministratorsDecidingAtOnceTests(TestCase):
    """The refusal has to read the stored status, not the one in hand.

    Two administrators can hold the same application open. Each request loads
    its own copy, and the copy the second one holds still says pending after
    the first has decided. If the guard trusts that copy, both decisions go
    through: the trail records two contradictory decisions on one application
    and the status is whichever write landed last.
    """

    def setUp(self):
        self.admin = make_admin()
        self.company = make_company()

    def _two_copies(self):
        return (
            Company.objects.get(pk=self.company.pk),
            Company.objects.get(pk=self.company.pk),
        )

    def test_a_rejection_is_refused_once_the_other_copy_has_approved(self):
        approving, rejecting = self._two_copies()

        approving.approve(actor=self.admin)

        with self.assertRaises(TransitionNotAllowed):
            rejecting.reject(actor=self.admin, reason="Registry code not found.")

        self.company.refresh_from_db()
        self.assertEqual(self.company.status, CompanyStatus.APPROVED)

    def test_the_refused_decision_leaves_nothing_in_the_trail(self):
        approving, rejecting = self._two_copies()

        approving.approve(actor=self.admin)
        with self.assertRaises(TransitionNotAllowed):
            rejecting.reject(actor=self.admin, reason="Registry code not found.")

        self.assertEqual(
            AuditEntry.objects.filter(action=Action.COMPANY_REJECTED).count(),
            0,
            "A decision that was refused must not be recorded as taken.",
        )

    def test_a_second_approval_is_refused_as_well(self):
        first, second = self._two_copies()

        first.approve(actor=self.admin)

        with self.assertRaises(TransitionNotAllowed):
            second.approve(actor=self.admin)

        self.assertEqual(
            AuditEntry.objects.filter(action=Action.COMPANY_APPROVED).count(),
            1,
            "One application approved once leaves one entry in the trail.",
        )


class ReviewViewRefusesTheTransitionTests(TestCase):
    """The view reports the refusal instead of failing with a server error."""

    def setUp(self):
        self.admin = make_admin()
        self.company = make_company()
        self.client.force_login(self.admin)

    def test_posting_an_approval_for_a_rejected_company_changes_nothing(self):
        self.company.reject(actor=self.admin, reason="Registry code not found.")

        response = self.client.post(
            reverse("companies:review_approve", args=[self.company.pk]), follow=True
        )

        self.company.refresh_from_db()
        self.assertEqual(self.company.status, CompanyStatus.REJECTED)
        self.assertContains(response, "no puede quedar aprobada")

    def test_posting_a_rejection_for_an_approved_company_changes_nothing(self):
        self.company.approve(actor=self.admin)

        response = self.client.post(
            reverse("companies:review_reject", args=[self.company.pk]),
            {"reason": "Changed my mind."},
            follow=True,
        )

        self.company.refresh_from_db()
        self.assertEqual(self.company.status, CompanyStatus.APPROVED)
        self.assertContains(response, "no puede quedar rechazada")

    def test_the_decision_is_not_offered_once_it_has_been_taken(self):
        self.company.approve(actor=self.admin)

        response = self.client.get(reverse("companies:review_detail", args=[self.company.pk]))

        # Asserted on the form targets rather than the button copy, which is
        # translated and would make this pass for the wrong reason.
        self.assertNotContains(
            response, reverse("companies:review_approve", args=[self.company.pk])
        )
        self.assertNotContains(response, reverse("companies:review_reject", args=[self.company.pk]))


class OwnedByTests(TestCase):
    """One account owns at most one company, so the lookup answers with the record."""

    def test_it_returns_the_company_of_its_owner(self):
        owner = make_user()
        company = make_company(owner)

        self.assertEqual(Company.objects.owned_by(owner), company)

    def test_it_returns_nothing_for_an_account_that_has_not_applied(self):
        self.assertIsNone(Company.objects.owned_by(make_user("nobody@tuchin.co")))
