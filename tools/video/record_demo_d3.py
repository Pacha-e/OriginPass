"""Record the Deliverable 3 walkthrough: the MVP loop end to end.

Beats, in order, matching what the narration says while they are on screen:
the workshop registers a product and sees its passport, the buyer's phone
verifies it and sees the journey, the custody is offered and accepted, the
journey grows on the public page, and the analytics close the loop.

The interface is served in Spanish (UR04), so every locator matches the
Spanish a visitor reads.

Run against a server started with `manage.py runserver 8765` and a seeded
database (`seed_demo`).
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import django
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent.parent
BUILD = Path(__file__).resolve().parent / "build"
RAW = BUILD / "demo-raw"
TARGET = BUILD / "demo.webm"

BASE = "http://127.0.0.1:8765"

WORKSHOP_EMAIL = "taller@tuchin.co"
#: The seed demo shares one password across every demo account.
PASSWORD = "OriginPass-2026"
DISTRIBUTOR_EMAIL = "ventas@importadoraandina.co"

#: A name the seed data does not use, so runs never collide with it.
DEMO_NAME = "Sombrero vueltiao 23 vueltas"


def setup_django():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    # Three levels up from tools/video/record_demo_d3.py: video -> tools -> root.
    root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(root))
    django.setup()


def reset_demo_product():
    """Remove pieces left by a previous run so the walk starts clean."""
    from products.models import Alert, CustodyTransfer, Product

    gone = 0
    for stale in Product.objects.filter(name=DEMO_NAME):
        Alert.objects.filter(product=stale).delete()
        CustodyTransfer.objects.filter(product=stale).delete()
        stale.delete()
        gone += 1
    return gone


def fresh_product():
    """The piece this walk created, once it exists."""
    from products.models import Product

    return Product.objects.filter(name=DEMO_NAME).order_by("-id").first()


def beat(page, seconds=1.6):
    page.wait_for_timeout(int(seconds * 1000))


def type_slowly(page, selector, value, delay=45):
    page.click(selector)
    page.type(selector, value, delay=delay)


def submit(page):
    page.click("main form button[type=submit]")


def login(page, email):
    page.goto(f"{BASE}/accounts/login/")
    type_slowly(page, "#id_email", email, delay=25)
    type_slowly(page, "#id_password", PASSWORD, delay=25)
    submit(page)
    page.wait_for_load_state("networkidle")
    beat(page, 1.0)


def logout(page):
    page.click("form[action*='logout'] button")
    page.wait_for_load_state("networkidle")
    beat(page, 0.6)


def main():
    setup_django()
    gone = reset_demo_product()
    if gone:
        print(f"cleaned {gone} stale demo piece(s) from a previous run")

    if RAW.exists():
        shutil.rmtree(RAW)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            viewport={"width": 1600, "height": 900},
            record_video_dir=str(RAW),
            record_video_size={"width": 1600, "height": 900},
            device_scale_factor=1,
        )
        page = context.new_page()

        # --- the workshop's own list, and a new product ----------------------
        login(page, WORKSHOP_EMAIL)
        page.goto(f"{BASE}/products/")
        beat(page, 2.4)

        page.click("text=Registrar un producto")
        page.wait_for_load_state("networkidle")
        beat(page, 1.2)
        type_slowly(page, "#id_name", DEMO_NAME, delay=28)
        type_slowly(page, "#id_category", "Sombreros", delay=30)
        type_slowly(page, "#id_origin", "Tuchín, Córdoba", delay=28)
        type_slowly(
            page,
            "#id_description",
            "Tejido a mano en caña flecha por tres generaciones del taller.",
            delay=11,
        )
        beat(page, 0.8)
        submit(page)
        page.wait_for_load_state("networkidle")
        beat(page, 2.2)

        # the fresh passport's detail page: code, QR and transfer code shown
        page.wait_for_selector("text=Descargar el código QR", timeout=8000)
        beat(page, 2.6)

        # The public page link carries the passport code; reading it from the
        # page keeps Django's ORM out of Playwright's async context.
        verify_url = (
            page.locator("a", has_text="Ver la página pública").first.get_attribute("href")
        )
        if verify_url and verify_url.startswith("/"):
            verify_url = f"{BASE}{verify_url}"

        # --- the buyer's phone: the public verdict with the journey ----------
        page.goto(verify_url)
        beat(page, 3.2)
        page.locator("text=Recorrido de este producto").scroll_into_view_if_needed()
        beat(page, 2.4)

        # --- the workshop hands the piece to the distributor -----------------
        page.goto(f"{BASE}/products/")
        beat(page, 1.4)
        page.locator("a", has_text=DEMO_NAME).first.click(force=True)
        page.wait_for_load_state("networkidle")
        beat(page, 1.6)

        page.click("text=Entregar este producto", force=True)
        page.wait_for_load_state("networkidle")
        beat(page, 1.2)
        type_slowly(page, "#id_to_holder_email", DISTRIBUTOR_EMAIL, delay=22)
        type_slowly(
            page,
            "#id_note",
            "Entrega al distribuidor en Montería.",
            delay=16,
        )
        beat(page, 0.8)
        submit(page)
        page.wait_for_load_state("networkidle")
        beat(page, 2.0)
        logout(page)

        # --- the distributor receives it --------------------------------------
        login(page, DISTRIBUTOR_EMAIL)
        page.goto(f"{BASE}/products/custody/")
        beat(page, 2.0)
        page.locator("a", has_text="Responder").first.click(force=True)
        page.wait_for_load_state("networkidle")
        beat(page, 1.8)
        page.click("text=Recibir el producto", force=True)
        page.wait_for_load_state("networkidle")
        beat(page, 2.2)
        logout(page)

        # --- the public page again: the journey grew --------------------------
        page.goto(verify_url)
        beat(page, 2.2)
        page.locator("text=Recorrido de este producto").scroll_into_view_if_needed()
        beat(page, 3.0)

        # --- the analytics close the loop --------------------------------------
        login(page, WORKSHOP_EMAIL)
        page.goto(f"{BASE}/products/analytics/")
        beat(page, 2.6)
        logout(page)

        video_path = page.video.path()
        context.close()
        browser.close()

    shutil.copy(video_path, TARGET)
    shutil.rmtree(RAW, ignore_errors=True)

    probe = subprocess.run(
        [
            sys.executable,
            "-c",
            "import imageio_ffmpeg,subprocess,sys;"
            "exe=imageio_ffmpeg.get_ffmpeg_exe();"
            "print(subprocess.run([exe,'-i',sys.argv[1]],capture_output=True,text=True).stderr)",
            str(TARGET),
        ],
        capture_output=True,
        text=True,
    )
    duration = [line for line in probe.stdout.splitlines() if "Duration" in line]

    print(f"recorded: {TARGET}")
    print(f"size: {TARGET.stat().st_size / 1024:.0f} KB")
    if duration:
        print(duration[0].strip())


if __name__ == "__main__":
    main()
