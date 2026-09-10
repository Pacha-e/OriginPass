"""UR04 - The interface is served in Spanish.

Asserted on the page a stranger reaches, because that is the one page whose
reader was never given a choice about the language: the buyer scanning a QR code
in a market in Monteria did not sign up, did not set a preference, and gets one
chance to understand the answer.
"""

import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from test_support.factories import make_product

CATALOGUE = Path(settings.BASE_DIR) / "locale" / "es" / "LC_MESSAGES" / "django.po"

#: One quoted chunk of a .po field, where a quote inside the text is escaped.
#: Matching with a plain `[^"]*` would stop at the first `\"` and silently read
#: half of every entry that contains an HTML attribute.
QUOTED = r'"(?:[^"\\]|\\.)*"'

#: One entry: a msgid and its msgstr, each possibly continued over several lines.
ENTRY = re.compile(
    rf"^msgid\s+((?:{QUOTED}\s*)+)^msgstr\s+((?:{QUOTED}\s*)+)",
    re.MULTILINE,
)


def joined(quoted_lines):
    """The value of a .po field, which the format allows to be split over lines."""
    chunks = re.findall(r'"((?:[^"\\]|\\.)*)"', quoted_lines)
    return "".join(chunks).replace('\\"', '"').replace("\\\\", "\\")


def catalogue_entries():
    text = CATALOGUE.read_text(encoding="utf-8")
    for msgid, msgstr in ENTRY.findall(text):
        # The first entry of a .po carries the file's own headers as an empty
        # msgid, which is not a translation and has nothing to check.
        if joined(msgid):
            yield joined(msgid), joined(msgstr)


class InterfaceLanguageTests(TestCase):
    def test_the_page_declares_itself_as_spanish(self):
        response = self.client.get(reverse("pages:home"))

        self.assertContains(response, '<html lang="es"')

    def test_the_verification_verdict_is_written_in_spanish(self):
        product = make_product()

        response = self.client.get(reverse("verification:verify", args=[product.passport_code]))

        self.assertContains(response, "Auténtico")
        self.assertNotContains(response, "Genuine")

    def test_the_navigation_is_written_in_spanish(self):
        response = self.client.get(reverse("pages:home"))

        self.assertContains(response, "Verificar un producto")
        self.assertContains(response, "Iniciar sesión")

    def test_a_visitor_who_asks_for_english_is_answered_in_english(self):
        """The source strings are English, so English costs nothing to offer."""
        response = self.client.get(reverse("pages:home"), headers={"accept-language": "en"})

        self.assertContains(response, '<html lang="en"')
        self.assertContains(response, "A verifiable passport for every product")


class TranslationCatalogueTests(SimpleTestCase):
    """Every string collected for translation has one.

    An entry left with an empty translation is not an error to gettext: it falls
    back to the English source and the page quietly serves the wrong language.
    Read from the .po rather than the compiled catalogue so that this fails on
    the file a person edits.
    """

    def test_the_catalogue_is_present(self):
        self.assertTrue(CATALOGUE.exists(), f"no catalogue at {CATALOGUE}")

    def test_the_entries_are_read(self):
        """Guards the check below: an unparsed file would pass it silently."""
        self.assertGreater(len(list(catalogue_entries())), 50)

    def test_no_entry_is_left_untranslated(self):
        untranslated = [msgid for msgid, msgstr in catalogue_entries() if not msgstr]

        self.assertEqual(untranslated, [])
