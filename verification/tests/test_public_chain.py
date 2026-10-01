"""Sprint 3 additions to the public verification page tests."""

from datetime import timedelta

from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from products.models import Alert, AlertKind, TransferState
from test_support.factories import make_company, make_product, make_user
from verification.models import ScanEvent, Verdict


class VerifyPageTests(TestCase):
    """The page is the one address a stranger hits; the rest of the system
    exists to serve it well.
    """

    def setUp(self):
        cache.clear()
        self.owner = make_user(email="maker@tuchin.co")
        self.company = make_company(owner=self.owner, status="APPROVED")
        self.product = make_product(company=self.company)
        self.client = Client(enforce_csrf_checks=True)

    def _url(self, code=None):
        return reverse("verification:verify", args=[code or self.product.passport_code])

    def test_scan_event_records_region_from_the_cdn_header(self):
        self.client.get(self._url(), HTTP_CF_IPCOUNTRY="CO")
        scan = ScanEvent.objects.get()
        self.assertEqual(scan.region, "CO")

    def test_scan_event_records_region_from_app_engine(self):
        self.client.get(self._url(), HTTP_X_APPENGINE_COUNTRY="US")
        scan = ScanEvent.objects.get()
        self.assertEqual(scan.region, "US")

    def test_scan_event_region_defaults_to_colombia(self):
        self.client.get(self._url())
        scan = ScanEvent.objects.get()
        self.assertEqual(scan.region, "CO")

    def test_two_regions_in_short_window_raise_an_alert(self):
        self.client.get(self._url(), HTTP_CF_IPCOUNTRY="CO")
        # Second scan from a different country inside the window.
        self.client.get(self._url(), HTTP_CF_IPCOUNTRY="CN")
        alert = Alert.objects.get()
        self.assertEqual(alert.kind, AlertKind.DUPLICATE_SCAN)
        self.assertEqual(alert.product, self.product)

    def test_same_region_does_not_alert(self):
        self.client.get(self._url(), HTTP_CF_IPCOUNTRY="CO")
        self.client.get(self._url(), HTTP_CF_IPCOUNTRY="CO")
        self.assertEqual(Alert.objects.count(), 0)

    def test_scan_cap_drops_records_past_the_limit_but_still_answers(self):
        from verification.views import SCAN_CAP_PER_HOUR
        for _ in range(SCAN_CAP_PER_HOUR + 5):
            self.client.get(self._url(), HTTP_CF_IPCOUNTRY="CO")
        scans = ScanEvent.objects.filter(verdict=Verdict.GENUINE).count()
        self.assertEqual(scans, SCAN_CAP_PER_HOUR)
        # The last capped requests still answered with the verdict, not a block page.
        response = self.client.get(self._url(), HTTP_CF_IPCOUNTRY="CO")
        self.assertContains(response, "Auténtico", status_code=200)

    def test_chain_of_custody_shows_in_order(self):
        buyer = make_user(email="buyer@example.com")
        transfer = self.product.custody_transfers.create(
            product=self.product,
            from_holder=self.owner,
            to_holder=buyer,
            note="Sold in Montería",
        )
        transfer.accept()
        response = self.client.get(self._url())
        self.assertContains(response, "Chain of custody")
        self.assertContains(response, "Registered the passport")
        self.assertContains(response, "buyer@example.com")
        self.assertContains(response, "Sold in Montería")

    def test_revoked_product_still_shows_chain(self):
        transfer = self.product.custody_transfers.create(
            product=self.product,
            from_holder=self.owner,
            to_holder=make_user(email="dist@example.com"),
            note="Distributor handover",
        )
        transfer.accept()
        self.product.revoke(actor=self.owner, reason="Recalled for a defect.")
        response = self.client.get(self._url())
        self.assertContains(response, "Revocado", status_code=200)
        self.assertContains(response, "Chain of custody")

    def test_chain_only_shows_accepted_transfers(self):
        pending = self.product.custody_transfers.create(
            product=self.product,
            from_holder=self.owner,
            to_holder=make_user(email="pending@example.com"),
        )
        response = self.client.get(self._url())
        self.assertNotContains(response, "pending@example.com")
