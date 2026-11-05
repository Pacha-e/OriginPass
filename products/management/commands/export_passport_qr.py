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
from django.urls import reverse
from PIL import Image, ImageDraw, ImageFont

# ---- Internal imports ----
from products.models import Product, ProductStatus
from products.qr import PRINT_DPI, QR_SIZE, passport_qr_image

# ---- Constants ----

#: US Letter at PRINT_DPI: the sheets are printed at 100% on Letter paper.
PAGE_SIZE = (2550, 3300)

COLUMNS = 3
ROWS = 4
PER_PAGE = COLUMNS * ROWS

LABEL_FONT_SIZE = 36

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
        tiles = []
        for product in products:
            address = base + reverse("verification:verify", args=[product.passport_code])
            code = passport_qr_image(address)
            code.save(output / f"qr-{product.passport_code}.png", dpi=(PRINT_DPI, PRINT_DPI))
            tiles.append((_label(product), code))

        pages = [tiles[start : start + PER_PAGE] for start in range(0, len(tiles), PER_PAGE)]
        for number, page in enumerate(pages, start=1):
            _page(page).save(output / f"hoja-qr-{number}.png", dpi=(PRINT_DPI, PRINT_DPI))
        self.stdout.write(f"{len(tiles)} QR codes on {len(pages)} page(s) written to {output}")


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


def _page(tiles):
    width, height = PAGE_SIZE
    cell_width = width // COLUMNS
    cell_height = height // ROWS
    sheet = Image.new("RGB", PAGE_SIZE, "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=LABEL_FONT_SIZE)

    for index, (name, code) in enumerate(tiles):
        cell_x = (index % COLUMNS) * cell_width
        cell_y = (index // COLUMNS) * cell_height
        x = cell_x + (cell_width - QR_SIZE) // 2
        y = cell_y + (cell_height - QR_SIZE) // 2
        sheet.paste(code, (x, y))
        draw.text(
            (cell_x + cell_width // 2, y + QR_SIZE + 30),
            name,
            fill="black",
            font=font,
            anchor="mt",
        )

    return sheet
