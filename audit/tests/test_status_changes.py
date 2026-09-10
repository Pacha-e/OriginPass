"""A status is changed by the transition that owns it, or it is not changed.

The trail is only worth reading if nothing changes a status behind its back.
The review pages and the model methods append an entry for every decision, but
Django's own administration site edits model fields directly: it calls `save()`
without going near `approve`, `reject` or `revoke`, so a status changed there
would move with no check that the change was allowed, no reason stored, and
nothing in the trail. FR43 asks for an entry after every status change of a
company or of a product, and this is the one way in that could not give it one.

The administration site is not being taken away here. What it may no longer do
is decide, which is what the pages built for deciding are for.
"""

from django.test import TestCase
from django.urls import reverse

from audit.models import AuditEntry
from companies.models import CompanyStatus
from products.models import ProductStatus
from test_support.factories import ADMIN_PASSWORD, make_admin, make_approved_company, make_product


class CompanyStatusTests(TestCase):
    def setUp(self):
        self.admin = make_admin()
        self.company = make_approved_company(email="weaver@tuchin.co")
        self.client.login(email=self.admin.email, password=ADMIN_PASSWORD)

    def _post_change(self, **overrides):
        payload = {
            "owner": self.company.owner_id,
            "legal_name": self.company.legal_name,
            "company_type": self.company.company_type,
            "verification_track": self.company.verification_track,
            "description": self.company.description,
            "location": self.company.location,
            "website": "",
            "registry_code": self.company.registry_code,
            "status": self.company.status,
            "status_reason": "",
        }
        payload.update(overrides)
        return self.client.post(
            reverse("admin:companies_company_change", args=[self.company.pk]), payload
        )

    def test_the_edit_itself_still_goes_through(self):
        response = self._post_change(location="Tuchin, Cordoba")

        self.assertEqual(response.status_code, 302)
        self.company.refresh_from_db()
        self.assertEqual(self.company.location, "Tuchin, Cordoba")

    def test_a_status_posted_to_the_administration_site_is_ignored(self):
        entries_before = AuditEntry.objects.count()

        self._post_change(status=CompanyStatus.SUSPENDED, status_reason="Set from the admin.")

        self.company.refresh_from_db()
        self.assertEqual(self.company.status, CompanyStatus.APPROVED)
        self.assertEqual(AuditEntry.objects.count(), entries_before)

    def test_the_stored_reason_is_not_rewritten_afterwards(self):
        self.company.suspend(actor=self.admin, reason="Counterfeit reports.")

        self._post_change(status_reason="A milder reason, written later.")

        self.company.refresh_from_db()
        self.assertEqual(self.company.status_reason, "Counterfeit reports.")


class ProductStatusTests(TestCase):
    def setUp(self):
        self.admin = make_admin()
        self.product = make_product(make_approved_company(email="weaver@tuchin.co"))
        self.client.login(email=self.admin.email, password=ADMIN_PASSWORD)

    def _post_change(self, **overrides):
        payload = {
            "company": self.product.company_id,
            "product_type": self.product.product_type,
            "name": self.product.name,
            "description": self.product.description,
            "category": self.product.category,
            "origin": self.product.origin,
            "status": self.product.status,
            "revocation_reason": "",
        }
        payload.update(overrides)
        return self.client.post(
            reverse("admin:products_product_change", args=[self.product.pk]), payload
        )

    def test_the_edit_itself_still_goes_through(self):
        response = self._post_change(category="Sombreros")

        self.assertEqual(response.status_code, 302)
        self.product.refresh_from_db()
        self.assertEqual(self.product.category, "Sombreros")

    def test_a_revocation_posted_to_the_administration_site_is_ignored(self):
        entries_before = AuditEntry.objects.count()

        self._post_change(status=ProductStatus.REVOKED, revocation_reason="Set from the admin.")

        self.product.refresh_from_db()
        self.assertEqual(self.product.status, ProductStatus.ACTIVE)
        self.assertEqual(AuditEntry.objects.count(), entries_before)

    def test_the_stored_reason_is_not_rewritten_afterwards(self):
        self.product.revoke(actor=self.admin, reason="Reported as a counterfeit.")

        self._post_change(revocation_reason="A milder reason, written later.")

        self.product.refresh_from_db()
        self.assertEqual(self.product.revocation_reason, "Reported as a counterfeit.")
