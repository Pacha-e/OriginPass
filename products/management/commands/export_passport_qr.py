"""Printable QR codes for every passport, for the live demonstration.

Each code encodes the public verification address of one passport, built from
--base-url. Run it on the server whose database holds those passports: codes and
signatures belong to one database and one SECRET_KEY, so a QR made anywhere else
does not verify here.
"""

# ---- External imports ----
import math
from pathlib import Path
from urllib.parse import urlsplit

from django.core.management.base import BaseCommand, CommandError
from django.urls import reverse
from PIL import Image, ImageDraw, ImageFont

# ---- Internal imports ----
from products.models import Product, ProductStatus
from products.qr import QR_SIZE, passport_qr_image

# ---- Constants ----

#: Three columns fit an A4 page at QR_SIZE.
COLUMNS = 3

MARGIN = 40

#: Room under each code for the product name.
LABEL_HEIGHT = 60

SHEET_FILE = "hoja-qr.png"

# ---- Public API ----


class Command(BaseCommand):
    help = "Write one PNG per passport and a printable sheet with every code."

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
        tiles = []
        for product in products:
            address = base + reverse("verification:verify", args=[product.passport_code])
            code = passport_qr_image(address)
            code.save(output / f"qr-{product.passport_code}.png")
            tiles.append((_label(product), code))

        _sheet(tiles).save(output / SHEET_FILE)
        self.stdout.write(f"{len(tiles)} QR codes written to {output}")


# ---- Private helpers ----


def _label(product):
    """The name under the code; a passport that is not active says so on the sheet."""
    if product.status == ProductStatus.ACTIVE:
        return product.name
    return f"{product.name} ({product.get_status_display()})"


def _validated_base(url):
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.netloc:
        raise CommandError(f"--base-url must start with http:// or https:// and name a host: {url}")
    return url.rstrip("/")


def _sheet(tiles):
    rows = math.ceil(len(tiles) / COLUMNS)
    cell_height = QR_SIZE + LABEL_HEIGHT + MARGIN
    width = COLUMNS * (QR_SIZE + MARGIN) + MARGIN
    height = rows * cell_height + MARGIN
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=20)

    for index, (name, code) in enumerate(tiles):
        x = MARGIN + (index % COLUMNS) * (QR_SIZE + MARGIN)
        y = MARGIN + (index // COLUMNS) * cell_height
        sheet.paste(code, (x, y))
        draw.text((x, y + QR_SIZE + 12), name, fill="black", font=font)

    return sheet
