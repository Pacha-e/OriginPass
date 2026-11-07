"""Printable QR codes for every passport, for the live demonstration.

Each code encodes the public verification address of one passport, built from
--base-url. Run it on the server whose database holds those passports: codes and
signatures belong to one database and one SECRET_KEY, so a QR made anywhere else
does not verify here.
"""

# ---- External imports ----
from pathlib import Path
from urllib.parse import urlsplit

from django.core.management.base import BaseCommand, CommandError

# ---- Internal imports ----
from products.models import Product
from products.qr import PRINT_DPI
from products.sheets import qr_tiles, tile_sheets

# ---- Public API ----


class Command(BaseCommand):
    help = "Write one PNG per passport and Letter-size sheets with every code."

    def add_arguments(self, parser):
        parser.add_argument(
            "--base-url",
            required=True,
            help="Public address the QR codes point to, e.g. http://54.12.34.56",
        )
        parser.add_argument(
            "--output",
            required=True,
            type=Path,
            help="Directory where the PNG files are written.",
        )

    def handle(self, *args, **options):
        base = _validated_base(options["base_url"])
        output = options["output"]

        products = list(Product.objects.order_by("pk"))
        if not products:
            raise CommandError("There are no passports in this database.")

        output.mkdir(parents=True, exist_ok=True)
        tiles = qr_tiles(products, base)
        for product, (_name, code) in zip(products, tiles, strict=True):
            code.save(output / f"qr-{product.passport_code}.png", dpi=(PRINT_DPI, PRINT_DPI))

        pages = tile_sheets(tiles)
        for number, page in enumerate(pages, start=1):
            page.save(output / f"hoja-qr-{number}.png", dpi=(PRINT_DPI, PRINT_DPI))
        self.stdout.write(f"{len(tiles)} QR codes on {len(pages)} page(s) written to {output}")


# ---- Private helpers ----


def _validated_base(url):
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.netloc:
        raise CommandError(f"--base-url must start with http:// or https:// and name a host: {url}")
    return url.rstrip("/")
