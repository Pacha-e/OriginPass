"""FR41-42: revocation with reason and the admin platform overview."""

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import Role
from products.models import ProductStatus
from test_support.factories import (
    ADMIN_PASSWORD,
    OWNER_PASSWORD,
    make_admin,
    make_company,
    make_product,
    make_user,
)


class ProductRevokeTests(TestCase):
    def setUp(self):
        self.owner = make_user(email="maker@tuchin.co")
        self.company = make_company(owner=self.owner, status="APPROVED")
        self.product = make_product(company=self.company)
        self.admin = make_admin(email="admin@originpass.co")
        self.client = Client(enforce_csrf_checks=True)
        self.url = reverse("products:product_revoke", args=[self.product.pk])

    def test_company_can_revoke_with_reason(self):
        assert self.client.login(email=self.owner.email, password=OWNER_PASSWORD)
        self.client.get(self.url)
        csrf = self.client.cookies["csrftoken"].value
        response = self.client.post(
            self.url,
            {"reason": "Stopped by supplier alert.", "csrfmiddlewaretoken": csrf},
        )
        self.assertEqual(response.status_code, 302)
        self.product.refresh_from_db()
        self.assertEqual(self.product.status, ProductStatus.REVOKED)
        self.assertEqual(self.product.revocation_reason, "Stopped by supplier alert.")

    def test_revoked_product_is_refused_again(self):
        self.product.revoke(actor=self.owner, reason="Recalled.")
        assert self.client.login(email=self.owner.email, password=OWNER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "already been revoked", status_code=403)

    def test_admin_revoke_requires_login(self):
        response = self.client.get(reverse("products:admin_revoke", args=[self.product.pk]))
        self.assertEqual(response.status_code, 302)


class AdminOverviewTests(TestCase):
    def setUp(self):
        self.owner = make_user(email="maker@tuchin.co")
        self.company = make_company(owner=self.owner, status="APPROVED")
        self.product = make_product(company=self.company)
        self.admin = make_admin(email="admin@originpass.co")
        self.url = reverse("products:admin_overview")

    def test_platform_totals_shown(self):
        client = Client(enforce_csrf_checks=True)
        assert client.login(email=self.admin.email, password=ADMIN_PASSWORD)
        response = client.get(self.url)
        self.assertContains(response, "Companies by status", status_code=200)
        self.assertContains(response, "Products by status", status_code=200)

    def test_non_admin_cannot_open(self):
        client = Client(enforce_csrf_checks=True)
        assert client.login(email=self.owner.email, password=OWNER_PASSWORD)
        response = client.get(self.url)
        self.assertEqual(response.status_code, 302)
