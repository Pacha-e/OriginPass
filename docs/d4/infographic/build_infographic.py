"""Render the one-page executive infographic of Deliverable 4 (section 5).

The page is written in HTML and printed by Chromium through Playwright, as a
PNG for the wiki and a PDF for printing on US Letter paper.

    python docs/d4/infographic/build_infographic.py
    python docs/d4/infographic/build_infographic.py --url https://<name>

Without --url the deployed address is given as a pointer to the README,
because the Learner Lab instance changes address when it is started again.
"""

# ---- Imports ----
import argparse
import html
from pathlib import Path

from playwright.sync_api import sync_playwright

# ---- Constants ----
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TEMPLATE = HERE / "infographic.html"
OUT_PNG = HERE.parent / "images" / "infographic.png"
OUT_PDF = HERE.parent / "images" / "infographic.pdf"
README_POINTER = "current address in the README of the repository (section Entregable 4)"


# ---- Main ----
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="public address of the deployed application")
    args = parser.parse_args()

    deployed = html.escape(args.url) if args.url else README_POINTER
    page_html = TEMPLATE.read_text(encoding="utf-8").replace("{{DEPLOYED}}", deployed)
    rendered = HERE / "_rendered.html"
    rendered.write_text(page_html, encoding="utf-8")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1275, "height": 1650}, device_scale_factor=2)
            page.goto(rendered.as_uri(), wait_until="networkidle")
            page.screenshot(path=str(OUT_PNG), full_page=False)
            page.pdf(
                path=str(OUT_PDF),
                width="8.5in",
                height="11in",
                print_background=True,
                page_ranges="1",
            )
            browser.close()
    finally:
        rendered.unlink(missing_ok=True)
    print(f"written {OUT_PNG.relative_to(ROOT)} and {OUT_PDF.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
