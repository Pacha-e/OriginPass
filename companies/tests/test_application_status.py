"""FR17 - Show the application status, and the reason behind a negative one, to its owner."""

from django.test import TestCase
from django.urls import reverse

from test_support.factories import make_admin, make_company, make_user


class ApplicationStatusVisibleToOwnerTests(TestCase):
    """FR17 - Show application status and reason to the owner."""

    def setUp(self):
        self.owner = make_user()
        self.admin = make_admin()
        self.company = make_company(self.owner)
        self.client.force_login(self.owner)

    def test_the_owner_sees_the_current_status(self):
        response = self.client.get(reverse("companies:application_detail"))

        self.assertContains(response, "Pendiente")

    def test_a_rejection_shows_the_stored_reason(self):
        self.company.reject(actor=self.admin, reason="The registry code does not match.")

        response = self.client.get(reverse("companies:application_detail"))

        self.assertContains(response, "Rechazada")
        self.assertContains(response, "The registry code does not match.")

    def test_a_suspension_shows_the_stored_reason(self):
        self.company.approve(actor=self.admin)
        self.company.suspend(actor=self.admin, reason="Counterfeit reports under review.")

        response = self.client.get(reverse("companies:application_detail"))

        self.assertContains(response, "Suspendida")
        self.assertContains(response, "Counterfeit reports under review.")

    def test_an_owner_without_an_application_is_sent_to_the_form(self):
        self.client.force_login(make_user("new@tuchin.co"))

        response = self.client.get(reverse("companies:application_detail"))

        self.assertRedirects(response, reverse("companies:application_create"))
