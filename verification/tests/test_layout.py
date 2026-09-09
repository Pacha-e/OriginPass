"""UR01 - The verification result fits a 360 pixel screen.

A 360 pixel viewport is the narrowest phone still in common use, and this is the
page most likely to be opened on one: a buyer standing in front of a stall.

What is checked here is what can be checked without a browser, and it is the
thing that actually breaks such a screen: a rule that fixes a width in pixels
wider than the screen forces the page to scroll sideways, where `max-width` only
ever makes an element narrower. The rendering itself is confirmed by eye.
"""

import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from testing.factories import make_product

NARROWEST_SCREEN = 360

STYLESHEET = Path(settings.BASE_DIR) / "static" / "css" / "originpass.css"

#: A width fixed in pixels. `max-width` and `min-width` are deliberately not
#: matched: neither of them can force a page wider than its screen.
FIXED_WIDTH = re.compile(r"(?<!-)\bwidth:\s*(\d+)px")


class NarrowScreenTests(SimpleTestCase):
    def test_the_stylesheet_is_found(self):
        """Guards the check below: a missing file would pass it without checking anything."""
        self.assertTrue(STYLESHEET.exists(), f"no stylesheet at {STYLESHEET}")

    def test_no_rule_fixes_a_width_wider_than_the_narrowest_screen(self):
        css = STYLESHEET.read_text(encoding="utf-8")

        too_wide = [int(px) for px in FIXED_WIDTH.findall(css) if int(px) > NARROWEST_SCREEN]

        self.assertEqual(too_wide, [], "fixed widths force a 360 pixel screen to scroll sideways")


class ViewportTests(TestCase):
    def test_the_verdict_page_scales_to_the_device(self):
        """Without this the phone renders at desktop width and shrinks the result."""
        product = make_product()

        response = self.client.get(reverse("verification:verify", args=[product.passport_code]))

        self.assertContains(response, 'name="viewport"')
        self.assertContains(response, "width=device-width")
