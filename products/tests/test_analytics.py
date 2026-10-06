"""FR46 to FR52 through the company's analytics page and its CSV export."""

from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from test_support.factories import OWNER_PASSWORD, make_company, make_product, make_user
from verification.models import ScanEvent, Verdict


def scan(product, days_ago, region="Córdoba"):
    event = ScanEvent.objects.create(product=product, verdict=Verdict.GENUINE, region=region)
    ScanEvent.objects.filter(pk=event.pk).update(
        scanned_at=timezone.now() - timedelta(days=days_ago)
    )


class AnalyticsTests(TestCase):
    def setUp(self):
        self.owner = make_user(email="maker@tuchin.co")
        self.product = make_product(company=make_company(owner=self.owner, status="APPROVED"))
        self.client.login(email=self.owner.email, password=OWNER_PASSWORD)
        self.url = reverse("products:analytics")

    def test_a_range_that_is_not_a_number_falls_back_instead_of_failing(self):
        """Defect: ?days=abc answered with a server error."""
        self.assertEqual(self.client.get(self.url, {"days": "abc"}).status_code, 200)
        self.assertEqual(
            self.client.get(reverse("products:analytics_csv"), {"days": "abc"}).status_code, 200
        )

    def test_counts_and_trend_against_the_period_before(self):
        for days_ago in (1, 2, 3, 4):
            scan(self.product, days_ago)
        for days_ago in (10, 11):
            scan(self.product, days_ago)
        response = self.client.get(self.url, {"days": 7})
        self.assertEqual(response.context["total"], 4)
        self.assertEqual(response.context["previous_total"], 2)
        self.assertEqual(response.context["change"], 100)

    def test_regions_are_counted(self):
        scan(self.product, 1, "Córdoba")
        scan(self.product, 1, "Antioquia")
        scan(self.product, 2, "Antioquia")
        regions = {
            row["region"]: row["count"] for row in self.client.get(self.url).context["by_region"]
        }
        self.assertEqual(regions, {"Antioquia": 2, "Córdoba": 1})

    def test_a_company_sees_only_its_own_scans(self):
        other = make_product(company=make_company(email="other@example.com", status="APPROVED"))
        scan(other, 1)
        self.assertEqual(self.client.get(self.url).context["total"], 0)

    def test_the_csv_cannot_carry_a_formula(self):
        self.product.name = "=HYPERLINK(1)"
        self.product.save()
        scan(self.product, 1)
        body = self.client.get(reverse("products:analytics_csv")).content.decode()
        self.assertIn("'=HYPERLINK(1)", body)
