"""The public landing page, which is reachable without an account."""

from django.template.loader import get_template
from django.test import TestCase
from django.urls import reverse

from accounts.models import User

#: Every template the project renders, checked below for comments that are not
#: comments. Django's `{# #}` matches on a single line only, so one that spans
#: two lines is not stripped: it is served to the visitor as text.
ALL_TEMPLATES = [
    "403.html",
    "404.html",
    "500.html",
    "base.html",
    "home.html",
    "partials/field.html",
    "accounts/login.html",
    "accounts/register.html",
    "companies/application_detail.html",
    "companies/application_form.html",
    "companies/edit_refused.html",
    "companies/review_detail.html",
    "companies/review_list.html",
    "products/product_detail.html",
    "products/product_form.html",
    "products/product_list.html",
    "products/registration_refused.html",
    "verification/lookup.html",
    "verification/verdict.html",
]


class TemplateCommentTests(TestCase):
    """A comment that spans two lines is rendered, not stripped.

    This was found by reading the body of a passing test: the explanation above
    the verification verdict was being served to the visitor. The rule is not
    obvious and the failure is silent, so it is checked for every template
    rather than for the one where it was noticed.
    """

    def test_no_template_opens_a_comment_it_does_not_close_on_the_same_line(self):
        offenders = []

        for name in ALL_TEMPLATES:
            source = get_template(name).template.source
            for number, line in enumerate(source.splitlines(), start=1):
                if "{#" in line and "#}" not in line:
                    offenders.append(f"{name}:{number}")

        self.assertEqual(offenders, [], "use {% comment %} for a comment over two lines")


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


class ErrorPageTests(TestCase):
    def test_an_unknown_address_renders_the_project_404_page(self):
        response = self.client.get("/no-such-page/")

        self.assertContains(response, "Page not found", status_code=404)
        self.assertTemplateUsed(response, "404.html")
