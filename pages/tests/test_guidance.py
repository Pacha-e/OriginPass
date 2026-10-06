"""The interface explains itself to someone who has never used software like it.

Many of the people OriginPass serves are artisans and farmers, often on a phone.
What is asserted here is the part of that which can be checked without a
person: every main action names what it does, every form field explains itself
before it is filled in, photographs carry a description, and the interface uses
one plain word for each idea instead of the vocabulary of the code.
"""

import gettext
import re
import tempfile
from html.parser import HTMLParser
from io import StringIO
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from products.models import CustodyTransfer, Product
from test_support.factories import OWNER_PASSWORD, make_company, make_product, make_user


class _Described(HTMLParser):
    """Collects the elements that point at a description, and the descriptions."""

    def __init__(self):
        super().__init__()
        self.pointers = []
        self.ids = {}
        self._open = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("aria-describedby"):
            self.pointers.append(attrs["aria-describedby"])
        if attrs.get("id") and attrs.get("role") == "tooltip":
            self._open = attrs["id"]
            self.ids[self._open] = ""

    def handle_data(self, data):
        if self._open:
            self.ids[self._open] += data

    def handle_endtag(self, tag):
        if tag == "span":
            self._open = None


def tooltips(response):
    parser = _Described()
    parser.feed(response.content.decode())
    return parser


class ActionsExplainThemselvesTests(TestCase):
    def setUp(self):
        self.owner = make_user(email="maker@tuchin.co")
        self.product = make_product(company=make_company(owner=self.owner, status="APPROVED"))
        self.client.login(email=self.owner.email, password=OWNER_PASSWORD)

    def assert_every_tooltip_says_something(self, url):
        found = tooltips(self.client.get(url))
        tooltip_pointers = [p for p in found.pointers if p in found.ids]
        self.assertGreater(len(tooltip_pointers), 0, f"no explained action on {url}")
        for pointer in tooltip_pointers:
            self.assertGreater(len(found.ids[pointer].strip()), 20, pointer)

    def test_the_product_page_explains_each_action(self):
        url = reverse("products:product_detail", args=[self.product.pk])
        found = tooltips(self.client.get(url))
        for action in ("tip-public", "tip-edit", "tip-qr", "tip-transfer", "tip-revoke"):
            with self.subTest(action=action):
                self.assertIn(action, found.pointers)
                self.assertTrue(found.ids.get(action, "").strip())

    def test_the_other_working_pages_explain_their_actions(self):
        for url in (
            reverse("products:product_list"),
            reverse("products:custody"),
            reverse("products:product_create"),
            reverse("products:transfer_initiate", args=[self.product.pk]),
            reverse("products:transfer_claim"),
            reverse("products:product_revoke", args=[self.product.pk]),
            reverse("products:analytics"),
        ):
            with self.subTest(url=url):
                self.assert_every_tooltip_says_something(url)

    def test_the_navigation_explains_each_entry(self):
        found = tooltips(self.client.get(reverse("products:product_list")))
        for entry in ("nav-verify", "nav-products", "nav-scans", "nav-custody", "nav-company"):
            with self.subTest(entry=entry):
                self.assertIn(entry, found.pointers)

    def test_a_field_explains_itself_before_the_input(self):
        body = self.client.get(reverse("products:product_create")).content.decode()
        help_at = body.index('id="id_name_helptext"')
        input_at = body.index('id="id_name"')
        self.assertLess(help_at, input_at)
        self.assertIn('aria-describedby="id_name_helptext"', body)

    def test_the_photo_field_opens_the_phone_camera_or_gallery(self):
        body = self.client.get(reverse("products:product_create")).content.decode()
        self.assertIn('accept="image/*"', body)

    def test_a_handover_code_is_explained_where_it_is_shown(self):
        CustodyTransfer.objects.create(
            product=self.product, from_holder=self.owner, to_holder=make_user(email="b@x.co")
        )
        response = self.client.get(reverse("products:custody"))
        self.assertContains(response, "Un código secreto solo para esta entrega")


class PublicPagesTests(TestCase):
    def test_the_home_page_asks_what_the_visitor_wants_to_do(self):
        response = self.client.get(reverse("pages:home"))
        self.assertContains(response, "Voy a comprar")
        self.assertContains(response, "Hago o vendo artesanías")
        self.assertContains(response, "¿Dónde está el código?")

    def test_every_photograph_on_the_home_page_is_described(self):
        body = self.client.get(reverse("pages:home")).content.decode()
        for tag in re.findall(r"<img [^>]*>", body):
            with self.subTest(tag=tag[:60]):
                self.assertRegex(tag, r'alt="[^"]*"')

    def test_the_verdict_explains_its_terms(self):
        product = make_product()
        response = self.client.get(reverse("verification:verify", args=[product.passport_code]))
        self.assertContains(response, "¿Qué significa esto?")
        self.assertContains(response, "Cada producto tiene uno distinto")

    def test_the_photo_credits_name_every_author(self):
        from pages.views import PHOTO_CREDITS

        response = self.client.get(reverse("pages:credits"))
        for credit in PHOTO_CREDITS:
            with self.subTest(image=credit["image"]):
                self.assertContains(response, credit["author"])
                self.assertTrue((Path(settings.BASE_DIR) / "static" / credit["image"]).exists())

    def test_every_page_links_to_the_credits(self):
        response = self.client.get(reverse("verification:lookup"))
        self.assertContains(response, reverse("pages:credits"))


class PlainWordsTests(TestCase):
    """One plain word per idea: the code says custody, transfer and revoke; the
    interface says entregar and anular, and never mixes in the other words."""

    JARGON = re.compile(r"\b(custodia|traspas\w*|revoc\w*|piezas?)\b", re.IGNORECASE)

    def test_the_spanish_catalogue_uses_the_plain_words(self):
        catalogue = Path(settings.BASE_DIR) / "locale" / "es" / "LC_MESSAGES" / "django.mo"
        with catalogue.open("rb") as handle:
            messages = gettext.GNUTranslations(handle)._catalog
        offenders = [text for text in messages.values() if self.JARGON.search(text)]
        self.assertEqual(offenders, [])


class DemoPhotosTests(TestCase):
    @override_settings(DEBUG=True, MEDIA_ROOT=tempfile.mkdtemp(prefix="originpass-media-"))
    def test_every_demo_passport_has_a_real_photograph(self):
        call_command("seed_demo", stdout=StringIO())
        products = Product.objects.all()
        self.assertGreater(products.count(), 0)
        for product in products:
            with self.subTest(product=product.name):
                self.assertTrue(product.image)
                self.assertTrue(product.is_intact)
