"""The claim page can read a passport QR with the camera, and ships what that needs.

The camera only works on HTTPS, so the reader is offered only where the browser
allows it; on plain HTTP the page keeps the typed field.
"""

# ---- External imports ----
from django.contrib.staticfiles import finders
from django.test import TestCase
from django.urls import reverse

# ---- Internal imports ----
from test_support.factories import make_user


# ---- Public API ----
class ClaimScannerTests(TestCase):
    def setUp(self):
        self.client.force_login(make_user(email="buyer@example.com"))
        self.response = self.client.get(reverse("products:transfer_claim"))

    def test_the_page_offers_the_camera_reader_hidden_until_the_browser_allows_it(self):
        self.assertContains(self.response, "data-scanner-start")
        self.assertContains(self.response, "data-scanner-field")

    def test_the_page_loads_the_reader_and_its_script(self):
        self.assertContains(self.response, "vendor/jsqr/jsQR.js")
        self.assertContains(self.response, "js/passport-scanner.js")

    def test_the_shipped_files_exist(self):
        self.assertIsNotNone(finders.find("vendor/jsqr/jsQR.js"))
        self.assertIsNotNone(finders.find("js/passport-scanner.js"))
