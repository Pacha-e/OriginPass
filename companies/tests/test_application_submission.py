"""Acceptance criteria of FR07, FR08 and FR09: submitting an application.

Where an issue states a time bound, the test measures the response and asserts it.
"""

from django.test import TestCase
from django.urls import reverse

from accounts.models import Role
from companies.models import Company, CompanyStatus, VerificationTrack
from test_support.factories import make_user
from test_support.timing import measure

from .payloads import ARTISAN_APPLICATION, COMMERCIAL_APPLICATION


class SubmitApplicationTests(TestCase):
    """FR07 - Submit a company application."""

    def setUp(self):
        self.owner = make_user()
        self.client.force_login(self.owner)

    def test_the_form_captures_every_required_detail(self):
        response = self.client.get(reverse("companies:application_create"))

        for field in ["legal_name", "company_type", "description", "location", "website"]:
            self.assertIn(field, response.context["form"].fields)

    def test_the_record_is_stored_with_status_pending(self):
        response, seconds = measure(
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
        self.client.force_login(make_user())

    def test_a_commercial_application_without_a_code_is_refused(self):
        payload = COMMERCIAL_APPLICATION | {"registry_code": ""}

        response = self.client.post(reverse("companies:application_create"), payload)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Company.objects.exists())
        self.assertContains(
            response, "Una empresa comercial debe dar un código de registro oficial."
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
    """FR09 - Accept an artisan application for manual review."""

    def setUp(self):
        self.owner = make_user()
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
