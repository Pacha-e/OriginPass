"""The printable QR sheet carries one code per active passport, each pointing at its own address."""

# ---- External imports ----
import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import qrcode
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.urls import reverse

# ---- Internal imports ----
from products.models import ProductStatus
from test_support.factories import make_admin, make_company, make_product, make_user

BASE = "http://54.12.34.56"


# ---- Public API ----
class ExportPassportQrTests(TestCase):
    def setUp(self):
        owner = make_user(email="maker@tuchin.co")
        self.product = make_product(
            company=make_company(owner=owner, status="APPROVED"),
            name="Sombrero vueltiao",
        )
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.output = Path(self.tmp.name)

    def _export(self, base=BASE):
        call_command(
            "export_passport_qr",
            "--base-url",
            base,
            "--output",
            str(self.output),
            stdout=StringIO(),
        )

    def test_writes_a_png_per_active_passport_and_one_sheet(self):
        self._export()

        self.assertEqual(self.product.status, ProductStatus.ACTIVE)
        self.assertTrue((self.output / f"qr-{self.product.passport_code}.png").is_file())
        self.assertTrue((self.output / "hoja-qr.png").is_file())

    def test_each_code_encodes_the_public_address_of_its_passport(self):
        real_make = qrcode.make
        with patch("products.management.commands.export_passport_qr.qrcode.make") as make:
            make.side_effect = real_make
            self._export()

        address = BASE + reverse("verification:verify", args=[self.product.passport_code])
        make.assert_called_once_with(address)

    def test_a_revoked_passport_gets_a_code_too(self):
        self.product.revoke(actor=make_admin(), reason="Counterfeit reports")

        self._export()

        self.assertTrue((self.output / f"qr-{self.product.passport_code}.png").is_file())

    def test_an_empty_database_is_an_error(self):
        self.product.delete()

        with self.assertRaises(CommandError):
            self._export()

    def test_refuses_an_address_without_scheme_or_host(self):
        with self.assertRaises(CommandError):
            self._export(base="54.12.34.56")
