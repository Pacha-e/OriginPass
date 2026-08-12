"""Record the application walkthrough that plays under the demo narration.

The pacing is deliberate: each beat is held long enough to be read at video
speed, and the beats are ordered to match what the narration says while they
are on screen. Run it against a server started with `manage.py runserver 8765`.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import django
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).parent.parent
BUILD = Path(__file__).parent / "build"
RAW = BUILD / "demo-raw"
TARGET = BUILD / "demo.webm"

BASE = "http://127.0.0.1:8765"
EMAIL = "taller@vueltiaotuchin.co"
#: Deliberately shares no word with the email address: Django's
#: UserAttributeSimilarityValidator refuses a password that resembles it.
PASSWORD = "Origen-Seguro-2026"

APPLICATION = {
    "legal_name": "Sombreros Vueltiao de Tuchín",
    "description": (
        "Taller familiar en Tuchín, tres generaciones tejiendo sombrero vueltiao en caña flecha."
    ),
    "location": "Tuchín, Córdoba",
    "website": "https://vueltiaotuchin.co",
    "registry_code": "NIT-901447382-1",
}

ADMIN_EMAIL = "admin@originpass.co"
ADMIN_PASSWORD = "OriginPass-2026"


def reset_account():
    """Remove the walkthrough account so every recording starts from the same place."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    sys.path.insert(0, str(ROOT))
    django.setup()
    from accounts.models import User

    User.objects.filter(email=EMAIL).delete()


def beat(page, seconds=1.6):
    page.wait_for_timeout(int(seconds * 1000))


def type_slowly(page, selector, value, delay=45):
    page.click(selector)
    page.type(selector, value, delay=delay)


def submit(page):
    """Press the submit button of the form in the page body.

    Scoped to <main> on purpose: the header carries a "Create account" link
    styled with the same class, and it sits earlier in the document.
    """
    page.click("main form button[type=submit]")


def main():
    reset_account()

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

        # --- the company applies -------------------------------------------
        page.goto(f"{BASE}/accounts/register/")
        beat(page, 1.4)
        type_slowly(page, "#id_email", EMAIL)
        type_slowly(page, "#id_password1", PASSWORD)
        type_slowly(page, "#id_password2", PASSWORD)
        beat(page, 0.6)
        submit(page)
        page.wait_for_load_state("networkidle")
        if "/register/" in page.url:
            errors = (
                page.locator(".field-error").all_inner_texts()
                + page.locator(".form-error").all_inner_texts()
            )
            raise SystemExit(f"registration was refused: {errors or page.inner_text('form')}")
        beat(page, 1.0)

        type_slowly(page, "#id_email", EMAIL)
        type_slowly(page, "#id_password", PASSWORD)
        submit(page)
        page.wait_for_load_state("networkidle")
        beat(page, 1.6)

        # the two verification tracks
        type_slowly(page, "#id_legal_name", APPLICATION["legal_name"], delay=28)
        page.select_option("#id_company_type", "COMMERCIAL")
        beat(page, 1.2)
        page.select_option("#id_verification_track", "CHAMBER_OF_COMMERCE")
        beat(page, 1.0)
        type_slowly(page, "#id_description", APPLICATION["description"], delay=12)
        type_slowly(page, "#id_location", APPLICATION["location"], delay=28)
        type_slowly(page, "#id_website", APPLICATION["website"], delay=22)
        beat(page, 0.8)

        # submitted with no registry code: refused beside the field
        submit(page)
        page.wait_for_load_state("networkidle")
        page.locator(".field-row--invalid").scroll_into_view_if_needed()
        beat(page, 3.4)

        # with the code, it is accepted and sits at Pending
        type_slowly(page, "#id_registry_code", APPLICATION["registry_code"], delay=45)
        beat(page, 0.8)
        submit(page)
        page.wait_for_load_state("networkidle")
        beat(page, 3.0)

        # --- the administrator reviews it ----------------------------------
        page.click("form[action*='logout'] button")
        page.wait_for_load_state("networkidle")
        page.goto(f"{BASE}/accounts/login/")
        type_slowly(page, "#id_email", ADMIN_EMAIL, delay=25)
        type_slowly(page, "#id_password", ADMIN_PASSWORD, delay=25)
        submit(page)
        page.wait_for_load_state("networkidle")
        beat(page, 1.0)

        page.goto(f"{BASE}/companies/review/")
        beat(page, 2.2)
        page.click("text=Pending")
        page.wait_for_load_state("networkidle")
        beat(page, 2.0)
        page.click("text=Approved")
        page.wait_for_load_state("networkidle")
        beat(page, 1.6)
        page.click("text=All")
        page.wait_for_load_state("networkidle")
        beat(page, 1.2)

        # open the new application
        page.click(f"text={APPLICATION['legal_name']}")
        page.wait_for_load_state("networkidle")
        beat(page, 2.0)

        # a rejection with no reason is refused
        page.locator("form[action*='reject'] button").scroll_into_view_if_needed()
        beat(page, 0.8)
        page.click("form[action*='reject'] button")
        page.wait_for_load_state("networkidle")
        page.locator(".field-row--invalid").scroll_into_view_if_needed()
        beat(page, 3.2)

        # with a reason, it is stored with the decision
        type_slowly(
            page,
            "#id_reason",
            "El código de registro no coincide con la Cámara de Comercio. "
            "Envíe el certificado de existencia y vuelva a solicitar.",
            delay=11,
        )
        beat(page, 0.8)
        page.click("form[action*='reject'] button")
        page.wait_for_load_state("networkidle")
        beat(page, 2.0)

        # --- the owner sees the reason and resubmits ------------------------
        page.click("form[action*='logout'] button")
        page.wait_for_load_state("networkidle")
        page.goto(f"{BASE}/accounts/login/")
        type_slowly(page, "#id_email", EMAIL, delay=22)
        type_slowly(page, "#id_password", PASSWORD, delay=22)
        submit(page)
        page.wait_for_load_state("networkidle")
        beat(page, 3.4)

        page.click("text=Edit application")
        page.wait_for_load_state("networkidle")
        beat(page, 1.2)
        page.fill("#id_registry_code", "")
        type_slowly(page, "#id_registry_code", "NIT-901447382-9", delay=45)
        beat(page, 0.8)
        submit(page)
        page.wait_for_load_state("networkidle")
        beat(page, 2.6)

        # --- approved, and then no longer editable --------------------------
        page.click("form[action*='logout'] button")
        page.wait_for_load_state("networkidle")
        page.goto(f"{BASE}/accounts/login/")
        type_slowly(page, "#id_email", ADMIN_EMAIL, delay=20)
        type_slowly(page, "#id_password", ADMIN_PASSWORD, delay=20)
        submit(page)
        page.wait_for_load_state("networkidle")
        page.goto(f"{BASE}/companies/review/")
        page.click(f"text={APPLICATION['legal_name']}")
        page.wait_for_load_state("networkidle")
        beat(page, 1.2)
        page.click("form[action*='approve'] button")
        page.wait_for_load_state("networkidle")
        beat(page, 2.4)

        page.click("form[action*='logout'] button")
        page.wait_for_load_state("networkidle")
        page.goto(f"{BASE}/accounts/login/")
        type_slowly(page, "#id_email", EMAIL, delay=20)
        type_slowly(page, "#id_password", PASSWORD, delay=20)
        submit(page)
        page.wait_for_load_state("networkidle")
        beat(page, 2.6)

        page.goto(f"{BASE}/companies/application/edit/")
        beat(page, 3.4)

        video_path = page.video.path()
        context.close()
        browser.close()

    shutil.copy(video_path, TARGET)
    shutil.rmtree(RAW, ignore_errors=True)

    ffmpeg = subprocess.run(
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
    duration = [line for line in ffmpeg.stdout.splitlines() if "Duration" in line]

    print(f"recorded: {TARGET}")
    print(f"size: {TARGET.stat().st_size / 1024:.0f} KB")
    if duration:
        print(duration[0].strip())


if __name__ == "__main__":
    main()
