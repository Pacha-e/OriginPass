"""Export the three draw.io models as cropped SVG, PNG and vector PDF.

Requires Playwright and network access to the official diagrams.net viewer.
Run before build_deck.py after changing a .drawio source.
"""

import base64
import math
import urllib.parse
import zlib
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "docs/diagrams"
EXPORT = SOURCE / "export"
MODELS = {
    "deployment-model": "deployment-model-Deployment-model",
    "components-model": "components-model-Component-model",
    "data-model": "data-model-Data-model",
}

# mxGraph uses enormous, invisible foreignObject boxes to position HTML labels.
# getBBox() includes those boxes. Measure painted shapes and actual label divs.
CROPPED_SVG = """svg => {
    const inverse = svg.getScreenCTM().inverse();
    const bounds = [];
    for (const e of svg.querySelectorAll(
        'path,rect,ellipse,circle,line,polyline,polygon,text,image,' +
        'foreignObject div[style*="inline-block"]')) {
        const s = getComputedStyle(e);
        if (s.visibility === 'hidden' || s.display === 'none') continue;
        if (e.namespaceURI.includes('svg') && s.fill === 'none' && s.stroke === 'none')
            continue;
        const r = e.getBoundingClientRect();
        if (!r.width && !r.height) continue;
        bounds.push(new DOMPoint(r.left, r.top).matrixTransform(inverse));
        bounds.push(new DOMPoint(r.right, r.bottom).matrixTransform(inverse));
    }
    if (!bounds.length) throw new Error('Empty diagram');
    const x = Math.min(...bounds.map(p => p.x)) - 16;
    const y = Math.min(...bounds.map(p => p.y)) - 16;
    const width = Math.max(...bounds.map(p => p.x)) - x + 16;
    const height = Math.max(...bounds.map(p => p.y)) - y + 16;
    const copy = svg.cloneNode(true);
    copy.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
    copy.setAttribute('xmlns:xlink', 'http://www.w3.org/1999/xlink');
    copy.setAttribute('viewBox', `${x} ${y} ${width} ${height}`);
    copy.setAttribute('width', width);
    copy.setAttribute('height', height);
    copy.setAttribute('style', 'display:block;background:#fff;color-scheme:light');
    return {markup: new XMLSerializer().serializeToString(copy), width, height};
}"""


def viewer_url(xml):
    model = xml[xml.index("<mxGraphModel") : xml.index("</mxGraphModel>") + 15]
    compressor = zlib.compressobj(9, zlib.DEFLATED, -15)
    raw = compressor.compress(urllib.parse.quote(model).encode()) + compressor.flush()
    data = urllib.parse.quote(base64.b64encode(raw).decode(), safe="")
    return f"https://viewer.diagrams.net/?lightbox=1&nav=0&layers=0&toolbar=0#R{data}"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for stem, target in MODELS.items():
            viewer = browser.new_page(viewport={"width": 2000, "height": 1450})
            viewer.emulate_media(color_scheme="light")
            viewer.goto(
                viewer_url((SOURCE / f"{stem}.drawio").read_text(encoding="utf-8")),
                wait_until="networkidle",
                timeout=90000,
            )
            viewer.wait_for_selector("svg foreignObject")
            viewer.evaluate("document.fonts.ready")
            drawing = viewer.locator("svg").first.evaluate(CROPPED_SVG)
            width, height = math.ceil(drawing["width"]), math.ceil(drawing["height"])
            if not (200 < width < 5000 and 200 < height < 5000):
                raise ValueError(f"Unexpected diagram bounds: {width}x{height}")
            markup = drawing["markup"]
            (EXPORT / f"{target}.svg").write_text(markup, encoding="utf-8")
            sheet = browser.new_page(
                viewport={"width": width, "height": height}, device_scale_factor=2.5
            )
            sheet.set_content(
                '<html><head><meta charset="utf-8"><style>'
                "*{box-sizing:border-box}html,body{margin:0;background:white;"
                "color-scheme:light}svg{position:static!important}"
                "</style></head><body>" + markup + "</body></html>"
            )
            sheet.evaluate("document.fonts.ready")
            sheet.screenshot(path=str(EXPORT / f"{target}.png"), timeout=30000)
            sheet.pdf(
                path=str(EXPORT / f"{target}.pdf"),
                width=f"{width}px",
                height=f"{height}px",
                print_background=True,
                margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
            )
            sheet.close()
            viewer.close()
            print(f"Exported {target}: {width}x{height}, SVG / PNG 2.5x / vector PDF")
        browser.close()


if __name__ == "__main__":
    main()
