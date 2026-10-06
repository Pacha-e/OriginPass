"""FR44: the administrator lists the audit trail filtered by actor, action and date."""

from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from audit.models import Action
from companies.models import CompanyStatus
from test_support.factories import (
    ADMIN_PASSWORD,
    OWNER_PASSWORD,
    make_admin,
    make_company,
    make_user,
)
from test_support.timing import measure


class AuditLogViewTests(TestCase):
    def setUp(self):
        self.admin = make_admin()
        approved = make_company(email="one@example.com")
        approved.approve(actor=self.admin)
        rejected = make_company(email="two@example.com", legal_name="Otra SAS")
        rejected.reject(actor=self.admin, reason="No registry match.")
        self.client.login(email=self.admin.email, password=ADMIN_PASSWORD)
        self.url = reverse("audit:log")

    def test_it_lists_the_entries_and_reports_the_chain(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Empresa aprobada")
        self.assertContains(response, "Empresa rechazada")
        self.assertContains(response, "La cadena firmada está íntegra")

    def test_it_filters_by_action(self):
        response = self.client.get(self.url, {"action": Action.COMPANY_REJECTED})
        self.assertContains(response, "No registry match.")
        self.assertNotContains(response, "<td>Empresa aprobada</td>", html=False)

    def test_it_filters_by_actor(self):
        response = self.client.get(self.url, {"actor": "nobody-like-this"})
        self.assertContains(response, "Ningún registro coincide")

    def test_it_filters_by_date_range(self):
        tomorrow = (timezone.localdate() + timedelta(days=1)).isoformat()
        response = self.client.get(self.url, {"since": tomorrow})
        self.assertContains(response, "Ningún registro coincide")

    def test_it_answers_within_three_seconds(self):
        _response, seconds = measure(
            lambda: self.client.get(self.url, {"action": Action.COMPANY_APPROVED})
        )
        self.assertLess(seconds, 3.0)

    def test_it_is_for_the_administrator_only(self):
        owner = make_user(email="owner@example.com")
        make_company(owner=owner, status=CompanyStatus.APPROVED)
        self.client.logout()
        self.client.login(email=owner.email, password=OWNER_PASSWORD)
        self.assertEqual(self.client.get(self.url).status_code, 403)
