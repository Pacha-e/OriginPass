"""The QR code of a passport: small, with the OriginPass mark in its centre.

Used by the owner's download on the passport page and by the export command for
the printed sheet, so both produce the same image.
"""

# ---- External imports ----
import io
import math

import qrcode
from PIL import Image, ImageDraw

# ---- Constants ----

#: Side of the code in pixels: 300 px printed at 300 dpi is about 2.5 cm.
QR_SIZE = 300

#: Resolution written into every PNG, so a printer uses 300 dpi rather than the
#: 96 dpi a viewer assumes, which would make the code about 8 cm wide.
PRINT_DPI = 300

#: Pixels per module before scaling down to QR_SIZE.
BOX_SIZE = 10

#: Quiet zone in modules: the blank margin a scanner needs around the code.
BORDER = 4

#: Share of the code's side covered by the centre mark. Level H recovers the
#: codewords under it; this covers about 5% of the area.
LOGO_RATIO = 0.22

#: Side of the square used when a passport has no photograph.
CARD_SIDE = 1200

#: The code's side as a share of the card's width.
CARD_CODE_RATIO = 0.28

#: White margin around the code, and distance from the card's edges, as shares of the width.
CARD_PAD_RATIO = 0.015
CARD_MARGIN_RATIO = 0.03

NAVY = "#1E2B58"
GOLD = "#D9C28A"

# ---- Public API ----


def passport_qr_image(address):
    """A QR_SIZE square image of the address, with the mark in its centre."""
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


def passport_card_image(address, photo=None):
    """The photograph with the passport code on a white square in its lower-right corner.

    Without a photograph, the code alone, centred on a white square.
    """
    code = passport_qr_image(address)
    if photo is None:
        side = CARD_SIDE
        card = Image.new("RGB", (side, side), "white")
        scaled = round(side * CARD_CODE_RATIO)
        offset = (side - scaled) // 2
        card.paste(code.resize((scaled, scaled), Image.Resampling.NEAREST), (offset, offset))
        return card

    card = photo.convert("RGB")
    width, height = card.size
    scaled = round(width * CARD_CODE_RATIO)
    pad = round(width * CARD_PAD_RATIO)
    panel = scaled + 2 * pad
    left = width - panel - round(width * CARD_MARGIN_RATIO)
    top = height - panel - round(width * CARD_MARGIN_RATIO)
    card.paste(Image.new("RGB", (panel, panel), "white"), (left, top))
    card.paste(code.resize((scaled, scaled), Image.Resampling.NEAREST), (left + pad, top + pad))
    return card


# ---- Private helpers ----


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
