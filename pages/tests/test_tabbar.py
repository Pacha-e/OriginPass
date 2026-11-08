"""The navigation of a signed-in person or company: a bar of tabs, not a header full of links.

Who sees which tabs is decided by the account. The same markup is the bottom bar
on a phone and the top menu on a desktop; only the stylesheet places it.
"""

from html.parser import HTMLParser
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from test_support.factories import make_admin, make_approved_company, make_product, make_user

ICONS = (
    "icon-products",
    "icon-print",
    "icon-handover",
    "icon-workshop",
    "icon-pieces",
    "icon-receive",
    "icon-verify",
    "icon-account",
)


class _Tabs(HTMLParser):
    """Collects each tab of the bar: where it goes, whether it is the current one, its word."""

    def __init__(self):
        super().__init__()
        self.tabs = []
        self._open = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a" and "tabbar__tab" in (attrs.get("class") or "").split():
            self._open = {"href": attrs["href"], "current": "aria-current" in attrs, "label": ""}
            self.tabs.append(self._open)

    def handle_data(self, data):
        if self._open is not None:
            self._open["label"] += data

    def handle_endtag(self, tag):
        if tag == "a":
            self._open = None


def tabs(response):
    parser = _Tabs()
    parser.feed(response.content.decode())
    return parser.tabs


class CompanyTabsTests(TestCase):
    def setUp(self):
        self.owner = make_user(email="maker@tuchin.co")
        self.company = make_approved_company(owner=self.owner)
        self.client.force_login(self.owner)

    def test_company_sees_four_tabs(self):
        found = tabs(self.client.get(reverse("products:product_list")))

        self.assertEqual(
            [tab["href"] for tab in found],
            [
                reverse("products:product_list"),
                reverse("products:print_qr"),
                reverse("products:custody"),
                reverse("companies:application_detail"),
            ],
        )

    def test_products_tab_stays_current_on_a_product_page(self):
        product = make_product(company=self.company)

        found = tabs(self.client.get(reverse("products:product_detail", args=[product.pk])))

        self.assertEqual([tab["current"] for tab in found], [True, False, False, False])


class PersonTabsTests(TestCase):
    def setUp(self):
        self.person = make_user(email="holder@tuchin.co")
        self.client.force_login(self.person)

    def test_person_sees_three_tabs(self):
        found = tabs(self.client.get(reverse("products:custody")))

        self.assertEqual(
            [tab["href"] for tab in found],
            [
                reverse("products:custody"),
                reverse("verification:lookup"),
                reverse("accounts:account"),
            ],
        )

    def test_active_tab_marked(self):
        found = tabs(self.client.get(reverse("products:custody")))

        self.assertEqual([tab["current"] for tab in found], [True, False, False])

    def test_every_tab_has_a_visible_word(self):
        found = tabs(self.client.get(reverse("products:custody")))

        self.assertTrue(all(tab["label"].strip() for tab in found))


class AccountPageTests(TestCase):
    def setUp(self):
        self.person = make_user(email="holder@tuchin.co")

    def test_account_page_shows_email_password_and_logout(self):
        self.client.force_login(self.person)

        response = self.client.get(reverse("accounts:account"))

        self.assertContains(response, self.person.email)
        self.assertContains(response, f'href="{reverse("accounts:password_change")}"')
        self.assertContains(response, f'action="{reverse("accounts:logout")}"')

    def test_anonymous_visitor_is_sent_to_login(self):
        response = self.client.get(reverse("accounts:account"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)


class WhereTheBarIsNotTests(TestCase):
    def test_visitor_sees_no_tabbar(self):
        response = self.client.get(reverse("pages:home"))

        self.assertNotContains(response, 'class="tabbar"')

    def test_admin_sees_no_tabbar(self):
        self.client.force_login(make_admin())

        response = self.client.get(reverse("products:admin_overview"))

        self.assertNotContains(response, 'class="tabbar"')


class IconSpriteTests(TestCase):
    def test_sprite_has_every_icon(self):
        html = self.client.get(reverse("pages:home")).content.decode()

        for icon in ICONS:
            with self.subTest(icon=icon):
                self.assertEqual(html.count(f'id="{icon}"'), 1)


class EmojiTests(SimpleTestCase):
    """Emoji are not used as icons: the brand's own icons are the only pictures in the interface."""

    EMOJI_RANGES = ((0x1F300, 0x1FAFF), (0x2600, 0x27BF))

    def test_no_emoji_in_templates(self):
        base = Path(settings.BASE_DIR)
        roots = [base / "templates", *base.glob("*/templates")]
        files = [
            path
            for root in roots
            if root.is_dir()
            for path in root.rglob("*.html")
            if ".venv" not in path.parts
        ]
        self.assertGreater(len(files), 10, "the walk must find the templates it checks")

        offenders = []
        for path in files:
            for char in path.read_text(encoding="utf-8"):
                code = ord(char)
                if any(low <= code <= high for low, high in self.EMOJI_RANGES):
                    offenders.append(f"{path.relative_to(base)}: U+{code:04X}")

        self.assertEqual(offenders, [])
