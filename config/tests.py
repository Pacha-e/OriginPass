"""The public landing page, which is reachable without an account."""

from django.test import TestCase
from django.urls import reverse

from accounts.models import User


class HomePageTests(TestCase):
    def test_a_visitor_can_open_the_home_page(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A verifiable passport for every product")

    def test_a_visitor_is_offered_the_account_actions(self):
        response = self.client.get(reverse("home"))

        self.assertContains(response, reverse("accounts:register"))
        self.assertContains(response, reverse("accounts:login"))

    def test_an_administrator_is_pointed_at_the_review_queue(self):
        admin = User.objects.create_superuser("admin@originpass.co", "Admin-Pass-2026")
        self.client.force_login(admin)

        response = self.client.get(reverse("home"))

        self.assertContains(response, reverse("companies:review_list"))

    def test_a_company_user_is_pointed_at_their_application(self):
        owner = User.objects.create_user("weaver@tuchin.co", "Vueltiao-2026")
        self.client.force_login(owner)

        response = self.client.get(reverse("home"))

        self.assertContains(response, reverse("companies:application_detail"))
