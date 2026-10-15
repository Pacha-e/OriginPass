"""FR15 suspend, FR16 reactivate, FR18 the public profile of a company."""

from django.test import TestCase
from django.urls import reverse

from audit.models import Action, AuditEntry
from companies.models import CompanyStatus
from test_support.factories import ADMIN_PASSWORD, make_admin, make_company, make_product


class SuspensionTests(TestCase):
    def setUp(self):
        self.company = make_company(status=CompanyStatus.APPROVED)
        self.admin = make_admin()
        self.client.login(email=self.admin.email, password=ADMIN_PASSWORD)

    def test_the_administrator_suspends_with_a_reason(self):
        response = self.client.post(
            reverse("companies:suspend", args=[self.company.pk]),
            {"reason": "Reports of copies under its name."},
        )
        self.assertRedirects(response, reverse("companies:review_detail", args=[self.company.pk]))
        self.company.refresh_from_db()
        self.assertEqual(self.company.status, CompanyStatus.SUSPENDED)
        self.assertEqual(self.company.status_reason, "Reports of copies under its name.")
        self.assertFalse(self.company.can_register_products)
        self.assertTrue(
            AuditEntry.objects.filter(action=Action.COMPANY_SUSPENDED, reason__contains="copies")
        )

    def test_a_suspension_without_a_reason_is_refused(self):
        response = self.client.post(
            reverse("companies:suspend", args=[self.company.pk]), {"reason": " "}
        )
        self.assertEqual(response.status_code, 400)
        self.company.refresh_from_db()
        self.assertEqual(self.company.status, CompanyStatus.APPROVED)

    def test_the_administrator_reactivates(self):
        self.company.suspend(actor=self.admin, reason="Checking reports.")
        self.client.post(reverse("companies:reactivate", args=[self.company.pk]))
        self.company.refresh_from_db()
        self.assertEqual(self.company.status, CompanyStatus.APPROVED)
        self.assertTrue(self.company.can_register_products)

    def test_the_review_page_offers_the_suspension(self):
        response = self.client.get(reverse("companies:review_detail", args=[self.company.pk]))
        self.assertContains(response, reverse("companies:suspend", args=[self.company.pk]))


class PublicProfileTests(TestCase):
    def test_an_approved_company_has_a_public_page(self):
        company = make_company(status=CompanyStatus.APPROVED, legal_name="Taller Tuchín")
        product = make_product(company=company)
        response = self.client.get(reverse("companies:public_profile", args=[company.pk]))
        self.assertContains(response, "Taller Tuchín")
        self.assertContains(response, company.get_verification_track_display())
        self.assertContains(response, product.name)
        self.assertNotContains(response, company.owner.email)

    def test_a_company_that_is_not_approved_has_none(self):
        for status in (CompanyStatus.PENDING, CompanyStatus.REJECTED, CompanyStatus.SUSPENDED):
            company = make_company(status=status, email=f"{status.lower()}@example.com")
            response = self.client.get(reverse("companies:public_profile", args=[company.pk]))
            self.assertEqual(response.status_code, 404, status)
