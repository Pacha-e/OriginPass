"""The public landing page, which is reachable without an account."""

from django.test import TestCase
from django.urls import reverse

from testing.factories import make_admin, make_user


class HomePageTests(TestCase):
    def test_a_visitor_can_open_the_home_page(self):
        response = self.client.get(reverse("pages:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Un pasaporte verificable para cada producto")

    def test_a_visitor_is_offered_the_account_actions(self):
        response = self.client.get(reverse("pages:home"))

        self.assertContains(response, reverse("accounts:register"))
        self.assertContains(response, reverse("accounts:login"))

    def test_an_administrator_is_pointed_at_the_review_queue(self):
        self.client.force_login(make_admin())

        response = self.client.get(reverse("pages:home"))

        self.assertContains(response, reverse("companies:review_list"))

    def test_a_company_user_is_pointed_at_their_application(self):
        self.client.force_login(make_user())

        response = self.client.get(reverse("pages:home"))

        self.assertContains(response, reverse("companies:application_detail"))
