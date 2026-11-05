"""Printable QR codes for the active passports, for the live demonstration.

Each QR encodes the public verification address of one passport, built from
--base-url. Run it on the server whose database holds those passports: codes and
signatures belong to one database and one SECRET_KEY, so a QR made anywhere else
does not verify here.
"""

# ---- External imports ----
import io
import math
from pathlib import Path
from urllib.parse import urlsplit

import qrcode
from django.core.management.base import BaseCommand, CommandError
from django.urls import reverse
from PIL import Image, ImageDraw, ImageFont

# ---- Internal imports ----
from products.models import Product, ProductStatus

# ---- Constants ----

#: Side of each code in pixels: 300 px printed at 300 dpi is about 2.5 cm.
QR_SIZE = 300

#: Three columns fit an A4 page at this size.
COLUMNS = 3

#: Pixels per module before scaling down to QR_SIZE.
BOX_SIZE = 10

#: Quiet zone in modules: the blank margin a scanner needs around the code.
BORDER = 4

#: Share of the code's side covered by the centre mark. Level H recovers the
#: codewords under it; this covers about 5% of the area.
LOGO_RATIO = 0.22

NAVY = "#1E2B58"
GOLD = "#D9C28A"

MARGIN = 40

#: Room under each QR for the product name.
LABEL_HEIGHT = 60

SHEET_FILE = "hoja-qr.png"

# ---- Public API ----


class Command(BaseCommand):
    help = "Write one PNG per active passport and a printable sheet with every QR."

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
            code = _qr_image(address)
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


def _qr_image(address):
    """A small code with the mark in its centre; level H keeps it readable under that cover."""
    code = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=BOX_SIZE,
        border=BORDER,
    )
    code.add_data(address)
    code.make(fit=True)

    buffer = io.BytesIO()
    code.make_image(fill_color="black", back_color="white").save(buffer, format="PNG")
    buffer.seek(0)
    image = Image.open(buffer).convert("RGB").resize((QR_SIZE, QR_SIZE), Image.Resampling.NEAREST)
    _cover_centre_with_mark(image)
    return image


def _cover_centre_with_mark(image):
    side = round(QR_SIZE * LOGO_RATIO)
    panel = Image.new("RGB", (side, side), "white")
    _draw_mark(ImageDraw.Draw(panel), side)
    offset = (QR_SIZE - side) // 2
    image.paste(panel, (offset, offset))


def _draw_mark(draw, side):
    """The OriginPass mark from static/brand/originpass-logo.svg, without its wordmark.

    The SVG is drawn in a 48-unit box; this maps that box into the panel with a
    10% margin on every side.
    """
    k = 0.8 * side / 48
    margin = 0.1 * side

    def at(unit):
        return margin + k * unit

    draw.rounded_rectangle([at(5), at(5), at(13), at(43)], radius=1.5 * k, fill=NAVY)

    cx, cy = at(26.5), at(19)
    outer = 12 * k
    stroke = round(4.5 * k)
    draw.ellipse(
        [
            cx - outer - stroke / 2,
            cy - outer - stroke / 2,
            cx + outer + stroke / 2,
            cy + outer + stroke / 2,
        ],
        outline=NAVY,
        width=stroke,
    )

    dashed = 6.4 * k
    dash_stroke = max(1, round(3 * k))
    dashed_box = [
        cx - dashed - dash_stroke / 2,
        cy - dashed - dash_stroke / 2,
        cx + dashed + dash_stroke / 2,
        cy + dashed + dash_stroke / 2,
    ]
    circumference = 2 * math.pi * 6.4
    dash_degrees = 360 * 3.1 / circumference
    period_degrees = 360 * (3.1 + 1.6) / circumference
    angle = 0.0
    while angle < 360:
        draw.arc(dashed_box, start=angle, end=angle + dash_degrees, fill=GOLD, width=dash_stroke)
        angle += period_degrees

    dot = 2.4 * k
    draw.ellipse([cx - dot, cy - dot, cx + dot, cy + dot], fill=NAVY)


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
