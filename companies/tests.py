"""Acceptance criteria of the Sprint 1 company issues.

Each test class names the issue it covers. Where an issue states a time bound,
the test measures the response and asserts it.
"""

import time

from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from accounts.models import Role, User

from .models import Company, CompanyStatus, CompanyType, VerificationTrack

COMMERCIAL_APPLICATION = {
    "legal_name": "Artesanias La Bonga SAS",
    "company_type": CompanyType.COMMERCIAL,
    "verification_track": VerificationTrack.CHAMBER_OF_COMMERCE,
    "registry_code": "NIT-900123456-7",
    "description": "Distributor of certified crafts from Cordoba.",
    "location": "Monteria, Cordoba",
    "website": "https://labonga.co",
}

ARTISAN_APPLICATION = {
    "legal_name": "Taller Tuchin",
    "company_type": CompanyType.ARTISAN,
    "verification_track": "",
    "registry_code": "",
    "description": "Family workshop weaving sombrero vueltiao.",
    "location": "Tuchin, Cordoba",
    "website": "",
}


def elapsed(call):
    started = time.perf_counter()
    result = call()
    return result, time.perf_counter() - started


def make_owner(email="weaver@tuchin.co"):
    return User.objects.create_user(email, "Vueltiao-2026")


def make_admin(email="admin@originpass.co"):
    return User.objects.create_superuser(email, "Admin-Pass-2026")


def make_company(owner, **overrides):
    fields = {
        "legal_name": "Artesanias La Bonga SAS",
        "company_type": CompanyType.COMMERCIAL,
        "verification_track": VerificationTrack.CHAMBER_OF_COMMERCE,
        "registry_code": "NIT-900123456-7",
        "description": "Distributor of certified crafts.",
        "location": "Monteria, Cordoba",
        "status": CompanyStatus.PENDING,
    }
    fields.update(overrides)
    return Company.objects.create(owner=owner, **fields)


class SubmitApplicationTests(TestCase):
    """FR07 - Submit a company application."""

    def setUp(self):
        self.owner = make_owner()
        self.client.force_login(self.owner)

    def test_the_form_captures_every_required_detail(self):
        response = self.client.get(reverse("companies:application_create"))

        for field in ["legal_name", "company_type", "description", "location", "website"]:
            self.assertIn(field, response.context["form"].fields)

    def test_the_record_is_stored_with_status_pending(self):
        response, seconds = elapsed(
            lambda: self.client.post(
                reverse("companies:application_create"), COMMERCIAL_APPLICATION
            )
        )

        company = Company.objects.get(owner=self.owner)
        self.assertRedirects(response, reverse("companies:application_detail"))
        self.assertEqual(company.status, CompanyStatus.PENDING)
        self.assertEqual(company.legal_name, "Artesanias La Bonga SAS")
        self.assertLess(seconds, 3, "The confirmation must be shown within 3 seconds.")

    def test_submitting_makes_the_user_a_company(self):
        self.client.post(reverse("companies:application_create"), COMMERCIAL_APPLICATION)

        self.owner.refresh_from_db()
        self.assertEqual(self.owner.role, Role.COMPANY)


class CommercialRegistryCodeTests(TestCase):
    """FR08 - Require a registry code from commercial companies."""

    def setUp(self):
        self.owner = make_owner()
        self.client.force_login(self.owner)

    def test_a_commercial_application_without_a_code_is_refused(self):
        payload = COMMERCIAL_APPLICATION | {"registry_code": ""}

        response = self.client.post(reverse("companies:application_create"), payload)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Company.objects.exists())
        self.assertContains(
            response, "A commercial company must provide an official registry code."
        )

    def test_the_cause_is_shown_beside_the_registry_code_field(self):
        """UR08 - Show the cause beside a refused field."""
        payload = COMMERCIAL_APPLICATION | {"registry_code": ""}

        response = self.client.post(reverse("companies:application_create"), payload)

        self.assertIn("registry_code", response.context["form"].errors)
        self.assertContains(response, "field-row--invalid")

    def test_a_commercial_application_cannot_use_the_artisan_track(self):
        payload = COMMERCIAL_APPLICATION | {"verification_track": VerificationTrack.ARTISAN_REVIEW}

        response = self.client.post(reverse("companies:application_create"), payload)

        self.assertIn("verification_track", response.context["form"].errors)
        self.assertFalse(Company.objects.exists())


class ArtisanApplicationTests(TestCase):
    """FR09 - Accept artisan companies without a registry code."""

    def setUp(self):
        self.owner = make_owner()
        self.client.force_login(self.owner)

    def test_the_application_is_accepted_with_no_registry_code(self):
        response = self.client.post(reverse("companies:application_create"), ARTISAN_APPLICATION)

        company = Company.objects.get(owner=self.owner)
        self.assertRedirects(response, reverse("companies:application_detail"))
        self.assertEqual(company.registry_code, "")

    def test_the_stored_record_is_flagged_for_manual_review(self):
        self.client.post(reverse("companies:application_create"), ARTISAN_APPLICATION)

        company = Company.objects.get(owner=self.owner)
        self.assertEqual(company.verification_track, VerificationTrack.ARTISAN_REVIEW)
        self.assertTrue(company.requires_manual_review)

    def test_an_artisan_application_may_not_carry_a_registry_code(self):
        payload = ARTISAN_APPLICATION | {"registry_code": "NIT-900123456-7"}

        response = self.client.post(reverse("companies:application_create"), payload)

        self.assertIn("registry_code", response.context["form"].errors)
        self.assertFalse(Company.objects.exists())


class EditWhileOpenTests(TestCase):
    """FR10 - Edit an application while pending or rejected."""

    def setUp(self):
        self.owner = make_owner()
        self.admin = make_admin()
        self.client.force_login(self.owner)

    def test_a_pending_application_can_be_opened_for_editing(self):
        make_company(self.owner, status=CompanyStatus.PENDING)

        response = self.client.get(reverse("companies:application_edit"))

        self.assertEqual(response.status_code, 200)

    def test_a_rejected_application_can_be_opened_for_editing(self):
        company = make_company(self.owner)
        company.reject(actor=self.admin, reason="The registry code does not match.")

        response = self.client.get(reverse("companies:application_edit"))

        self.assertEqual(response.status_code, 200)

    def test_resubmitting_returns_the_application_to_pending(self):
        company = make_company(self.owner)
        company.reject(actor=self.admin, reason="The registry code does not match.")

        payload = COMMERCIAL_APPLICATION | {"registry_code": "NIT-900999888-1"}
        response = self.client.post(reverse("companies:application_edit"), payload)

        company.refresh_from_db()
        self.assertRedirects(response, reverse("companies:application_detail"))
        self.assertEqual(company.status, CompanyStatus.PENDING)
        self.assertEqual(company.registry_code, "NIT-900999888-1")


class EditRefusedTests(TestCase):
    """FR11 - Refuse edits to approved or suspended applications."""

    def setUp(self):
        self.owner = make_owner()
        self.admin = make_admin()
        self.client.force_login(self.owner)

    def test_an_approved_application_cannot_be_edited(self):
        company = make_company(self.owner)
        company.approve(actor=self.admin)

        response = self.client.get(reverse("companies:application_edit"))

        self.assertEqual(response.status_code, 403)

    def test_a_suspended_application_cannot_be_edited(self):
        company = make_company(self.owner)
        company.suspend(actor=self.admin, reason="Counterfeit reports under review.")

        response = self.client.get(reverse("companies:application_edit"))

        self.assertEqual(response.status_code, 403)

    def test_the_refusal_states_the_reason(self):
        company = make_company(self.owner)
        company.approve(actor=self.admin)

        response = self.client.get(reverse("companies:application_edit"))

        self.assertContains(
            response,
            "This application cannot be edited because it is approved.",
            status_code=403,
        )

    def test_a_post_to_the_edit_view_changes_nothing(self):
        company = make_company(self.owner)
        company.approve(actor=self.admin)

        self.client.post(
            reverse("companies:application_edit"),
            COMMERCIAL_APPLICATION | {"legal_name": "Renamed SAS"},
        )

        company.refresh_from_db()
        self.assertEqual(company.legal_name, "Artesanias La Bonga SAS")
        self.assertEqual(company.status, CompanyStatus.APPROVED)


class ReviewListTests(TestCase):
    """FR12 - List company applications filtered by status."""

    def setUp(self):
        self.admin = make_admin()
        self.client.force_login(self.admin)

        self.pending = make_company(make_owner("one@tuchin.co"))
        self.approved = make_company(make_owner("two@tuchin.co"))
        self.approved.approve(actor=self.admin)
        self.rejected = make_company(make_owner("three@tuchin.co"))
        self.rejected.reject(actor=self.admin, reason="Registry code not found.")
        self.suspended = make_company(make_owner("four@tuchin.co"))
        self.suspended.suspend(actor=self.admin, reason="Counterfeit reports.")

    def test_the_administrator_sees_every_application(self):
        response, seconds = elapsed(lambda: self.client.get(reverse("companies:review_list")))

        self.assertEqual(len(response.context["applications"]), 4)
        self.assertLess(seconds, 3, "Results must be shown within 3 seconds.")

    def test_filtering_by_each_status_returns_the_matching_applications(self):
        expected = {
            CompanyStatus.PENDING: self.pending,
            CompanyStatus.APPROVED: self.approved,
            CompanyStatus.REJECTED: self.rejected,
            CompanyStatus.SUSPENDED: self.suspended,
        }

        for status, company in expected.items():
            with self.subTest(status=status):
                response = self.client.get(reverse("companies:review_list"), {"status": status})
                applications = list(response.context["applications"])

                self.assertEqual(applications, [company])

    def test_an_unknown_status_falls_back_to_showing_everything(self):
        response = self.client.get(reverse("companies:review_list"), {"status": "NOPE"})

        self.assertEqual(len(response.context["applications"]), 4)
        self.assertEqual(response.context["selected_status"], "")

    def test_the_list_is_reserved_for_the_administrator(self):
        self.client.force_login(make_owner("intruder@tuchin.co"))

        response = self.client.get(reverse("companies:review_list"))

        self.assertEqual(response.status_code, 403)


class ApproveTests(TestCase):
    """FR13 - Approve a pending company application."""

    def setUp(self):
        self.admin = make_admin()
        self.company = make_company(make_owner())
        self.client.force_login(self.admin)

    def test_the_status_changes_to_approved(self):
        _, seconds = elapsed(
            lambda: self.client.post(reverse("companies:review_approve", args=[self.company.pk]))
        )

        self.company.refresh_from_db()
        self.assertEqual(self.company.status, CompanyStatus.APPROVED)
        self.assertLess(seconds, 3, "The status must change within 3 seconds.")

    def test_the_approved_company_can_then_register_products(self):
        from products.models import Product, ProductType

        self.client.post(reverse("companies:review_approve", args=[self.company.pk]))
        self.company.refresh_from_db()

        product = Product(
            company=self.company,
            product_type=ProductType.COMMERCIAL_ORIGINAL,
            name="Sombrero vueltiao 21 vueltas",
            description="Hand woven.",
            category="Headwear",
            origin="Tuchin, Cordoba",
        )
        product.clean()  # raises ValidationError when the company is not approved

        self.assertTrue(self.company.can_register_products)

    def test_a_pending_company_cannot_register_products(self):
        from django.core.exceptions import ValidationError

        from products.models import Product, ProductType

        product = Product(
            company=self.company,
            product_type=ProductType.COMMERCIAL_ORIGINAL,
            name="Sombrero vueltiao 21 vueltas",
            description="Hand woven.",
            category="Headwear",
            origin="Tuchin, Cordoba",
        )

        with self.assertRaises(ValidationError):
            product.clean()


class RejectTests(TestCase):
    """FR14 - Reject an application with a written reason."""

    def setUp(self):
        self.admin = make_admin()
        self.company = make_company(make_owner())
        self.client.force_login(self.admin)

    def test_a_rejection_without_a_reason_is_refused(self):
        response = self.client.post(
            reverse("companies:review_reject", args=[self.company.pk]), {"reason": ""}
        )

        self.company.refresh_from_db()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.company.status, CompanyStatus.PENDING)
        self.assertContains(
            response,
            "A reason is required to reject an application.",
            status_code=400,
        )

    def test_a_reason_of_only_whitespace_is_refused(self):
        response = self.client.post(
            reverse("companies:review_reject", args=[self.company.pk]), {"reason": "   "}
        )

        self.company.refresh_from_db()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.company.status, CompanyStatus.PENDING)

    def test_the_status_changes_and_the_reason_is_stored(self):
        self.client.post(
            reverse("companies:review_reject", args=[self.company.pk]),
            {"reason": "The registry code does not match the Chamber of Commerce."},
        )

        self.company.refresh_from_db()
        self.assertEqual(self.company.status, CompanyStatus.REJECTED)
        self.assertEqual(
            self.company.status_reason,
            "The registry code does not match the Chamber of Commerce.",
        )


class ApplicationStatusVisibleToOwnerTests(TestCase):
    """FR17 - Show application status and reason to the owner."""

    def setUp(self):
        self.owner = make_owner()
        self.admin = make_admin()
        self.company = make_company(self.owner)
        self.client.force_login(self.owner)

    def test_the_owner_sees_the_current_status(self):
        response = self.client.get(reverse("companies:application_detail"))

        self.assertContains(response, "Pending")

    def test_a_rejection_shows_the_stored_reason(self):
        self.company.reject(actor=self.admin, reason="The registry code does not match.")

        response = self.client.get(reverse("companies:application_detail"))

        self.assertContains(response, "Rejected")
        self.assertContains(response, "The registry code does not match.")

    def test_a_suspension_shows_the_stored_reason(self):
        self.company.suspend(actor=self.admin, reason="Counterfeit reports under review.")

        response = self.client.get(reverse("companies:application_detail"))

        self.assertContains(response, "Suspended")
        self.assertContains(response, "Counterfeit reports under review.")

    def test_an_owner_without_an_application_is_sent_to_the_form(self):
        self.client.force_login(make_owner("new@tuchin.co"))

        response = self.client.get(reverse("companies:application_detail"))

        self.assertRedirects(response, reverse("companies:application_create"))


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
        company = make_company(make_owner())

        self.assertIsNotNone(company.submitted_at)

    def test_the_status_change_timestamp_is_updated_on_every_status_change(self):
        admin = make_admin()
        company = make_company(make_owner())
        before = company.status_changed_at

        company.approve(actor=admin)
        after_approval = company.status_changed_at
        company.suspend(actor=admin, reason="Counterfeit reports.")
        after_suspension = company.status_changed_at

        self.assertGreater(after_approval, before)
        self.assertGreater(after_suspension, after_approval)

    def test_one_company_per_account(self):
        owner = make_owner()
        make_company(owner)

        with self.assertRaises(IntegrityError), transaction.atomic():
            make_company(owner, legal_name="Second SAS")


class ReasonRequiredTests(TestCase):
    """DBR12 - Require a reason on negative decisions (company side)."""

    def setUp(self):
        self.admin = make_admin()
        self.company = make_company(make_owner())

    def test_a_rejection_without_a_reason_is_refused(self):
        with self.assertRaises(ValueError):
            self.company.reject(actor=self.admin, reason="")

        self.company.refresh_from_db()
        self.assertEqual(self.company.status, CompanyStatus.PENDING)

    def test_a_suspension_without_a_reason_is_refused(self):
        with self.assertRaises(ValueError):
            self.company.suspend(actor=self.admin, reason="   ")

        self.company.refresh_from_db()
        self.assertEqual(self.company.status, CompanyStatus.PENDING)

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
        owner = make_owner()

        with self.assertRaises(IntegrityError), transaction.atomic():
            make_company(
                owner,
                company_type=CompanyType.COMMERCIAL,
                verification_track=VerificationTrack.ARTISAN_REVIEW,
            )

    def test_the_database_refuses_a_commercial_company_with_no_registry_code(self):
        owner = make_owner()

        with self.assertRaises(IntegrityError), transaction.atomic():
            make_company(owner, registry_code="")
