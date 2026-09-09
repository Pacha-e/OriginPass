"""Acceptance criteria of FR12, FR13 and FR14: the administrator's review queue.

Where an issue states a time bound, the test measures the response and asserts it.
"""

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from companies.models import CompanyStatus
from products.models import Product, ProductType
from testing.factories import make_admin, make_company, make_user
from testing.timing import measure


def unsaved_product_for(company):
    """A product that has not been written yet, so `clean` can be asked about it."""
    return Product(
        company=company,
        product_type=ProductType.COMMERCIAL_ORIGINAL,
        name="Sombrero vueltiao 21 vueltas",
        description="Hand woven.",
        category="Headwear",
        origin="Tuchin, Cordoba",
    )


class ReviewListTests(TestCase):
    """FR12 - List company applications filtered by status."""

    def setUp(self):
        self.admin = make_admin()
        self.client.force_login(self.admin)

        self.pending = make_company(make_user("one@tuchin.co"))
        self.approved = make_company(make_user("two@tuchin.co"))
        self.approved.approve(actor=self.admin)
        self.rejected = make_company(make_user("three@tuchin.co"))
        self.rejected.reject(actor=self.admin, reason="Registry code not found.")
        self.suspended = make_company(make_user("four@tuchin.co"))
        self.suspended.approve(actor=self.admin)
        self.suspended.suspend(actor=self.admin, reason="Counterfeit reports.")

    def test_the_administrator_sees_every_application(self):
        response, seconds = measure(lambda: self.client.get(reverse("companies:review_list")))

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
        self.client.force_login(make_user("intruder@tuchin.co"))

        response = self.client.get(reverse("companies:review_list"))

        self.assertEqual(response.status_code, 403)


class ApproveTests(TestCase):
    """FR13 - Approve a pending company application."""

    def setUp(self):
        self.admin = make_admin()
        self.company = make_company(make_user())
        self.client.force_login(self.admin)

    def test_the_status_changes_to_approved(self):
        _, seconds = measure(
            lambda: self.client.post(reverse("companies:review_approve", args=[self.company.pk]))
        )

        self.company.refresh_from_db()
        self.assertEqual(self.company.status, CompanyStatus.APPROVED)
        self.assertLess(seconds, 3, "The status must change within 3 seconds.")

    def test_the_approved_company_can_then_register_products(self):
        self.client.post(reverse("companies:review_approve", args=[self.company.pk]))
        self.company.refresh_from_db()

        # Raises ValidationError when the company is not approved.
        unsaved_product_for(self.company).clean()

        self.assertTrue(self.company.can_register_products)

    def test_a_pending_company_cannot_register_products(self):
        with self.assertRaises(ValidationError):
            unsaved_product_for(self.company).clean()


class RejectTests(TestCase):
    """FR14 - Reject an application with a written reason."""

    def setUp(self):
        self.admin = make_admin()
        self.company = make_company(make_user())
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
            "Hay que dar un motivo para rechazar una solicitud.",
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
