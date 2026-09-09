"""Every visit is recorded, including the ones that matched nothing.

A run of unmatched codes is somebody probing the code space, which is exactly the
signal that would be lost by recording only the successes.
"""

from django.test import TestCase
from django.urls import reverse

from testing.factories import make_product
from verification.models import ScanEvent, Verdict

ANDROID = "Mozilla/5.0 (Linux; Android 14) Mobile Safari/537.36"


class ScanEventTests(TestCase):
    def test_a_genuine_verification_writes_a_scan_event(self):
        product = make_product()

        self.client.get(reverse("verification:verify", args=[product.passport_code]))

        event = ScanEvent.objects.get()
        self.assertEqual(event.product, product)
        self.assertEqual(event.verdict, Verdict.GENUINE)

    def test_an_unmatched_code_is_recorded_with_no_product(self):
        self.client.get(reverse("verification:verify", args=["nothing-here"]))

        event = ScanEvent.objects.get()
        self.assertIsNone(event.product)
        self.assertEqual(event.verdict, Verdict.NOT_FOUND)

    def test_the_device_category_is_taken_from_the_browser(self):
        product = make_product()

        self.client.get(
            reverse("verification:verify", args=[product.passport_code]),
            HTTP_USER_AGENT=ANDROID,
        )

        self.assertEqual(ScanEvent.objects.get().device_category, "MOBILE")

    def test_every_visit_is_recorded_separately(self):
        product = make_product()
        url = reverse("verification:verify", args=[product.passport_code])

        self.client.get(url)
        self.client.get(url)

        self.assertEqual(ScanEvent.objects.count(), 2)
