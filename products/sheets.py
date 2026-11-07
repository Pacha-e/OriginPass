"""Letter sheets of passport QR codes, twelve to a page, for printing at 100%.

The export command and the owner's PDF both build their sheets here, so the
printed page is the same whichever way it was asked for.
"""

# ---- External imports ----
import io

from django.urls import reverse
from PIL import Image, ImageDraw, ImageFont

# ---- Internal imports ----
from products.models import ProductStatus
from products.qr import PRINT_DPI, QR_SIZE, passport_qr_image

# ---- Constants ----

#: US Letter at PRINT_DPI: the sheets are printed at 100% on Letter paper.
PAGE_SIZE = (2550, 3300)

COLUMNS = 3
ROWS = 4
PER_PAGE = COLUMNS * ROWS

LABEL_FONT_SIZE = 36

# ---- Public API ----


def qr_tiles(products, base_url):
    """One (label, code image) per product, in the order given."""
    return [
        (
            _label(product),
            passport_qr_image(
                base_url + reverse("verification:verify", args=[product.passport_code])
            ),
        )
        for product in products
    ]


def tile_sheets(tiles):
    """Letter pages of (label, code image) tiles, PER_PAGE to a page."""
    return [_page(tiles[start : start + PER_PAGE]) for start in range(0, len(tiles), PER_PAGE)]


def qr_sheets(products, base_url):
    """One Letter sheet per PER_PAGE products, each code pointing at its passport."""
    return tile_sheets(qr_tiles(products, base_url))


def qr_sheets_pdf(products, base_url):
    """The sheets of qr_sheets saved as one PDF at PRINT_DPI."""
    first, *rest = qr_sheets(products, base_url)
    buffer = io.BytesIO()
    first.save(buffer, format="PDF", save_all=True, append_images=rest, resolution=PRINT_DPI)
    return buffer.getvalue()


# ---- Private helpers ----


def _label(product):
    """The name under the code; a passport that is not active says so on the sheet."""
    if product.status == ProductStatus.ACTIVE:
        return product.name
    return f"{product.name} ({product.get_status_display()})"


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
