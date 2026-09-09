"""The invariants of the company table itself: DBR01, DBR12 and the type rules.

These assert what holds however the row was written, so several of them go behind
the model with `update()` to check that the database refuses the row on its own.
"""

from django.db import IntegrityError, transaction
from django.test import TestCase

from companies.models import Company, CompanyStatus, CompanyType, VerificationTrack
from testing.factories import make_admin, make_company, make_user


class CompanyRecordTests(TestCase):
    """DBR01 - Store the company record."""

    #: Every field the Domain Model wiki page lists for Company.
    DOMAIN_MODEL_FIELDS = {
        "owner",
        "legal_name",
        "company_type",
        "verification_track",
        "status",
        "description",
        "location",
        "website",
        "logo",
        "registry_code",
        "status_reason",
        "submitted_at",
        "status_changed_at",
    }

    def test_the_model_holds_every_field_listed_in_the_domain_model(self):
        declared = {field.name for field in Company._meta.get_fields()}

        self.assertTrue(self.DOMAIN_MODEL_FIELDS.issubset(declared))

    def test_the_submission_timestamp_is_set_on_creation(self):
        company = make_company()

        self.assertIsNotNone(company.submitted_at)

    def test_the_status_change_timestamp_is_updated_on_every_status_change(self):
        admin = make_admin()
        company = make_company()
        before = company.status_changed_at

        company.approve(actor=admin)
        after_approval = company.status_changed_at
        company.suspend(actor=admin, reason="Counterfeit reports.")
        after_suspension = company.status_changed_at

        self.assertGreater(after_approval, before)
        self.assertGreater(after_suspension, after_approval)

    def test_one_company_per_account(self):
        owner = make_user()
        make_company(owner)

        with self.assertRaises(IntegrityError), transaction.atomic():
            make_company(owner, legal_name="Second SAS")


class ReasonRequiredTests(TestCase):
    """DBR12 - Require a reason on negative decisions (company side)."""

    def setUp(self):
        self.admin = make_admin()
        self.company = make_company()

    def test_a_rejection_without_a_reason_is_refused(self):
        with self.assertRaises(ValueError):
            self.company.reject(actor=self.admin, reason="")

        self.company.refresh_from_db()
        self.assertEqual(self.company.status, CompanyStatus.PENDING)

    def test_a_suspension_without_a_reason_is_refused(self):
        self.company.approve(actor=self.admin)

        with self.assertRaises(ValueError):
            self.company.suspend(actor=self.admin, reason="   ")

        self.company.refresh_from_db()
        self.assertEqual(self.company.status, CompanyStatus.APPROVED)

    def test_the_database_refuses_a_negative_status_with_no_reason(self):
        """The rule is not left to the application layer alone."""
        with self.assertRaises(IntegrityError), transaction.atomic():
            Company.objects.filter(pk=self.company.pk).update(
                status=CompanyStatus.REJECTED, status_reason=""
            )

    def test_the_reason_is_kept_with_the_decision(self):
        self.company.reject(actor=self.admin, reason="Registry code not found.")

        self.company.refresh_from_db()
        self.assertEqual(self.company.status_reason, "Registry code not found.")


class VerificationTrackConstraintTests(TestCase):
    """The company type and its verification track have to agree."""

    def test_the_database_refuses_a_commercial_company_on_the_artisan_track(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            make_company(
                company_type=CompanyType.COMMERCIAL,
                verification_track=VerificationTrack.ARTISAN_REVIEW,
            )

    def test_the_database_refuses_a_commercial_company_with_no_registry_code(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            make_company(registry_code="")
