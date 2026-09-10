"""Acceptance criteria of FR10 and FR11: who may edit an application, and when."""

from django.test import TestCase
from django.urls import reverse

from companies.models import CompanyStatus
from test_support.factories import make_admin, make_company, make_user

from .payloads import COMMERCIAL_APPLICATION


class EditWhileOpenTests(TestCase):
    """FR10 - Edit an application while pending or rejected."""

    def setUp(self):
        self.owner = make_user()
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
        self.owner = make_user()
        self.admin = make_admin()
        self.client.force_login(self.owner)

    def test_an_approved_application_cannot_be_edited(self):
        company = make_company(self.owner)
        company.approve(actor=self.admin)

        response = self.client.get(reverse("companies:application_edit"))

        self.assertEqual(response.status_code, 403)

    def test_a_suspended_application_cannot_be_edited(self):
        company = make_company(self.owner)
        company.approve(actor=self.admin)
        company.suspend(actor=self.admin, reason="Counterfeit reports under review.")

        response = self.client.get(reverse("companies:application_edit"))

        self.assertEqual(response.status_code, 403)

    def test_the_refusal_states_the_reason(self):
        company = make_company(self.owner)
        company.approve(actor=self.admin)

        response = self.client.get(reverse("companies:application_edit"))

        self.assertContains(
            response,
            "Esta solicitud no se puede editar porque está aprobada.",
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
