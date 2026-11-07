"""Walk the artisan journeys on a 390 px phone and keep a screenshot of every screen.

Used before and after each interface change of the artisan plan
(docs/superpowers/plans/2026-11-07-originpass-para-artesanos.md) so that a person
can look at what an artisan would see. It needs the development server running and
the demonstration data loaded (`python manage.py seed_demo`).

    python tools/ux/recorrido.py --base http://127.0.0.1:8000 --out <dir>

Each full-page capture is cut into JPEG pieces 1700 px tall, numbered in the
order of the walk. A screen that does not exist yet (404) is reported and skipped,
so the same walk serves before and after the screens are built.
"""

import argparse
import sys
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

VIEWPORT = {"width": 390, "height": 844}
PIECE_HEIGHT = 1700
DEMO_PASSWORD = "OriginPass-2026"
WORKSHOP = "taller@tuchin.co"
PERSON = "comprador@correo.co"

# (journey, screen name, account or None for a visitor, path)
WALK = [
    ("1-inscripcion", "inicio", None, "/"),
    ("1-inscripcion", "crear-cuenta", None, "/accounts/register/"),
    ("1-inscripcion", "asistente", PERSON, "/companies/inscripcion/kind/"),
    ("1-inscripcion", "formulario-actual", PERSON, "/companies/application/new/"),
    ("2-taller", "mi-taller", WORKSHOP, "/companies/application/"),
    ("2-taller", "productos", WORKSHOP, "/products/"),
    ("2-taller", "producto-nuevo", WORKSHOP, "/products/new/"),
    ("2-taller", "entregas", WORKSHOP, "/products/custody/"),
    ("2-taller", "analitica", WORKSHOP, "/products/analytics/"),
    ("3-imprimir", "imprimir-qr", WORKSHOP, "/products/imprimir/"),
    ("4-entregar", "lote-nuevo", WORKSHOP, "/products/lote/nuevo/"),
    ("5-persona", "mis-piezas", PERSON, "/products/custody/"),
    ("5-persona", "recibir", PERSON, "/v/"),
]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", default="http://127.0.0.1:8000")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)

    missing = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        sessions = {}
        for number, (journey, name, account, path) in enumerate(WALK, start=1):
            page = _page_for(browser, sessions, args.base, account)
            response = page.goto(args.base + path)
            if response is None or response.status == 404:
                missing.append(path)
                print(f"skip {path}: not built yet", file=sys.stderr)
                continue
            page.wait_for_load_state("networkidle")
            stem = f"{number:02d}-{journey}-{name}"
            _save_pieces(page, args.out, stem)
            print(f"{stem}  {page.url}")
        browser.close()

    if missing:
        print(f"{len(missing)} screen(s) not built yet: {', '.join(missing)}", file=sys.stderr)
    return 0


def _page_for(browser, sessions, base, account):
    """One logged-in phone per account, reused along the walk."""
    if account not in sessions:
        context = browser.new_context(
            viewport=VIEWPORT, is_mobile=True, has_touch=True, locale="es-CO"
        )
        page = context.new_page()
        if account:
            page.goto(base + "/accounts/login/")
            page.fill("input[type=email]", account)
            page.fill("input[type=password]", DEMO_PASSWORD)
            page.click("form button[type=submit]")
            page.wait_for_load_state("networkidle")
        sessions[account] = page
    return sessions[account]


def _save_pieces(page, out, stem):
    full = out / f"{stem}.png"
    page.screenshot(path=str(full), full_page=True)
    image = Image.open(full).convert("RGB")
    for index, top in enumerate(range(0, image.height, PIECE_HEIGHT)):
        piece = image.crop((0, top, image.width, min(image.height, top + PIECE_HEIGHT)))
        piece.save(out / f"{stem}-{index}.jpg", quality=70)
    full.unlink()


if __name__ == "__main__":
    sys.exit(main())
