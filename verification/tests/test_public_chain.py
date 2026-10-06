"""FR32 the chain on the public page, FR33 the region of a scan, FR49 the
duplicate-scan alert and FR58 the scan cap.

The page is public, so what it must not show matters as much as what it shows:
the accounts in a chain of custody are never named by their email address.
"""

from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from products.models import Alert, AlertKind
from test_support.factories import make_company, make_product, make_user
from verification.models import ScanEvent, Verdict


@override_settings(TRUST_GEO_HEADERS=True)
class VerifyPageTests(TestCase):
    """Behind a CDN that sets the geolocation headers."""

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
        self.assertEqual(ScanEvent.objects.get().region, "CO")

    def test_the_first_level_region_wins_over_the_country(self):
        self.client.get(self._url(), HTTP_CF_REGION="Antioquia", HTTP_CF_IPCOUNTRY="CO")
        self.assertEqual(ScanEvent.objects.get().region, "Antioquia")

    def test_scan_event_records_region_from_app_engine(self):
        self.client.get(self._url(), HTTP_X_APPENGINE_COUNTRY="US")
        self.assertEqual(ScanEvent.objects.get().region, "US")

    def test_an_unknown_region_is_left_blank_rather_than_guessed(self):
        self.client.get(self._url())
        self.assertEqual(ScanEvent.objects.get().region, "")

    def test_a_long_or_odd_region_header_cannot_take_the_page_down(self):
        response = self.client.get(self._url(), HTTP_CF_REGION="<script>" + "X" * 500)
        self.assertContains(response, "Auténtico", status_code=200)
        region = ScanEvent.objects.get().region
        self.assertLessEqual(len(region), 100)
        self.assertNotIn("<", region)

    def test_two_regions_in_short_window_raise_an_alert(self):
        self.client.get(self._url(), HTTP_CF_IPCOUNTRY="CO")
        self.client.get(self._url(), HTTP_CF_IPCOUNTRY="CN")
        alert = Alert.objects.get()
        self.assertEqual(alert.kind, AlertKind.DUPLICATE_SCAN)
        self.assertEqual(alert.product, self.product)

    def test_same_region_does_not_alert(self):
        self.client.get(self._url(), HTTP_CF_IPCOUNTRY="CO")
        self.client.get(self._url(), HTTP_CF_IPCOUNTRY="CO")
        self.assertEqual(Alert.objects.count(), 0)

    def test_a_scan_with_no_region_does_not_alert(self):
        self.client.get(self._url())
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

    def test_chain_of_custody_shows_in_order_without_emails(self):
        buyer = make_user(email="buyer@example.com")
        transfer = self.product.custody_transfers.create(
            product=self.product,
            from_holder=self.owner,
            to_holder=buyer,
            note="Sold in Montería",
        )
        transfer.accept()
        response = self.client.get(self._url())
        self.assertContains(response, "Recorrido de este producto")
        self.assertContains(response, "Sacó el pasaporte")
        self.assertContains(response, "Comprador particular")
        self.assertContains(response, "Sold in Montería")
        self.assertNotContains(response, "buyer@example.com")
        self.assertNotContains(response, "maker@tuchin.co")

    def test_a_company_holder_is_named_by_its_public_name(self):
        distributor = make_user(email="dist@example.com")
        make_company(owner=distributor, status="APPROVED", legal_name="Distribuidora Caribe SAS")
        self.product.custody_transfers.create(
            product=self.product, from_holder=self.owner, to_holder=distributor
        ).accept()
        response = self.client.get(self._url())
        self.assertContains(response, "Distribuidora Caribe SAS")
        self.assertNotContains(response, "dist@example.com")

    def test_revoked_product_still_shows_chain_and_reason(self):
        self.product.custody_transfers.create(
            product=self.product,
            from_holder=self.owner,
            to_holder=make_user(email="dist@example.com"),
            note="Distributor handover",
        ).accept()
        self.product.revoke(actor=self.owner, reason="Recalled for a defect.")
        response = self.client.get(self._url())
        self.assertContains(response, "Anulado", status_code=200)
        self.assertContains(response, "Recalled for a defect.")
        self.assertContains(response, "Distributor handover")

    def test_chain_only_shows_accepted_transfers(self):
        self.product.custody_transfers.create(
            product=self.product,
            from_holder=self.owner,
            to_holder=make_user(email="pending@example.com"),
            note="Still waiting",
        )
        response = self.client.get(self._url())
        self.assertNotContains(response, "Still waiting")


@override_settings(TRUST_GEO_HEADERS=False)
class UntrustedHeaderTests(TestCase):
    """Without a CDN in front, the geolocation headers are written by the client."""

    def setUp(self):
        cache.clear()
        self.product = make_product()

    def test_a_forged_header_is_ignored_and_raises_no_alert(self):
        url = reverse("verification:verify", args=[self.product.passport_code])
        self.client.get(url, HTTP_CF_IPCOUNTRY="CO")
        self.client.get(url, HTTP_CF_IPCOUNTRY="CN")
        self.assertEqual(set(ScanEvent.objects.values_list("region", flat=True)), {""})
        self.assertEqual(Alert.objects.count(), 0)
