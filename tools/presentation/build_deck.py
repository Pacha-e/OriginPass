"""Build the Deliverable 3 presentation: one PDF of slides and the presenter's script.

Each slide is written as HTML in the project's own identity (the añil and caña
palette, Bahnschrift headings, the ringed P), rendered at 1920x1080 in a
headless browser, and the pages are joined into a PDF. The script that goes
with each slide is written beside it and saved as Markdown, so the deck and
what is said over it change together.

Run from the repository root:  python tools/presentation/build_deck.py
Writes to tools/presentation/build/.
"""

import base64
import html
import io
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent.parent
BUILD = Path(__file__).resolve().parent / "build"
SLIDES = BUILD / "slides"
PDF = BUILD / "OriginPass-Entrega-3-presentacion.pdf"
SCRIPT = BUILD / "OriginPass-Entrega-3-guion.md"

SHOTS = ROOT / "docs/brand/screenshots"
DIAGRAMS = ROOT / "docs/diagrams/export"

MARK = """<svg viewBox="0 0 48 48" aria-hidden="true">
<rect x="5" y="5" width="8" height="38" rx="1.5" fill="currentColor"/>
<circle cx="26.5" cy="19" r="12" fill="none" stroke="currentColor" stroke-width="4.5"/>
<circle cx="26.5" cy="19" r="6.4" fill="none" stroke="#D9C28A" stroke-width="3"
 stroke-dasharray="3.1 1.6"/>
<circle cx="26.5" cy="19" r="2.4" fill="currentColor"/></svg>"""

CSS = (Path(__file__).resolve().parent / "deck.css").read_text(encoding="utf-8")


def esc(value):
    return html.escape(value, quote=False)


def tagged(text):
    """Turn a trailing ' [FR35, FR38]' into a pill, so the requirement is visible."""
    if text.endswith("]") and " [" in text:
        body, tag = text[:-1].rsplit(" [", 1)
        return f'{esc(body)} <span class="tag">{esc(tag)}</span>'
    return esc(text)


def image_uri(path):
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{data}"


def diagram_uri(path):
    """The diagram cropped to its drawing: the draw.io export carries a wide empty page."""
    picture = Image.open(path).convert("RGB")
    ink = picture.convert("L").point(lambda level: 255 if level < 225 else 0)
    left, top, right, bottom = ink.getbbox()
    pad = 24
    picture = picture.crop(
        (
            max(left - pad, 0),
            max(top - pad, 0),
            min(right + pad, picture.width),
            min(bottom + pad, picture.height),
        )
    )
    buffer = io.BytesIO()
    picture.save(buffer, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")


def head(slide):
    parts = []
    if slide.get("eyebrow"):
        parts.append(f'<p class="eyebrow">{esc(slide["eyebrow"])}</p>')
    parts.append(f"<h1>{esc(slide['title'])}</h1>")
    if slide.get("lead"):
        parts.append(f'<p class="lead">{esc(slide["lead"])}</p>')
    return "".join(parts)


def points(items):
    return '<ul class="points">' + "".join(f"<li>{tagged(i)}</li>" for i in items) + "</ul>"


def render(slide):
    kind = slide["kind"]
    if kind == "cover":
        return f"""<div class="cover-mark">{MARK}</div>
<p class="eyebrow">{esc(slide["eyebrow"])}</p><h1>{esc(slide["title"])}</h1>
<p class="lead" style="font-size:40px">{esc(slide["lead"])}</p>
<p class="cover-slogan">{esc(slide["slogan"])}</p>
<p class="cover-who">{esc(slide["who"])}</p>"""
    if kind == "statement":
        return head(slide)
    if kind == "cols":
        cards = "".join(
            f'<div class="card{" on" if c.get("on") else ""}"><h2>{esc(c["title"])}</h2>'
            f"<p>{esc(c['text'])}</p>"
            + (f'<p class="num">{esc(c["num"])}</p>' if c.get("num") else "")
            + "</div>"
            for c in slide["cards"]
        )
        return head(slide) + f'<div class="cols">{cards}</div>'
    if kind == "steps":
        steps = "".join(
            f'<div class="step"><b>{n}</b><p>{esc(s)}</p></div>'
            for n, s in enumerate(slide["steps"], 1)
        )
        return head(slide) + f'<div class="steps">{steps}</div>'
    if kind == "split":
        shot = f'<div class="shot"><img src="{image_uri(SHOTS / slide["shot"])}" alt=""></div>'
        return head(slide) + f'<div class="body">{points(slide["points"])}{shot}</div>'
    if kind == "points":
        note = f'<p class="note">{esc(slide["note"])}</p>' if slide.get("note") else ""
        return head(slide) + f'<div class="body">{points(slide["points"])}</div>' + note
    if kind == "table":
        rows = "".join(f"<tr><td>{esc(a)}</td><td>{tagged(b)}</td></tr>" for a, b in slide["rows"])
        header = "".join(f"<th>{esc(h)}</th>" for h in slide["columns"])
        return head(slide) + f"<table><tr>{header}</tr>{rows}</table>"
    if kind == "diagram":
        changes = "".join(f"<li>{tagged(c)}</li>" for c in slide["changes"])
        return (
            head(slide)
            + '<div class="diagram"><div class="img">'
            + f'<img src="{diagram_uri(DIAGRAMS / slide["image"])}" alt=""></div>'
            + '<aside><h2><span class="legend"></span>Nuevo en el Sprint 3</h2>'
            f"<ul>{changes}</ul></aside></div>"
        )
    if kind == "stats":
        stats = "".join(
            f'<div class="stat"><b>{esc(n)}</b><span>{esc(t)}</span></div>'
            for n, t in slide["stats"]
        )
        note = f'<p class="note">{esc(slide["note"])}</p>'
        return head(slide) + f'<div class="stats">{stats}</div>' + note
    if kind == "brand":
        swatches = "".join(
            f'<div class="sw" style="background:{bg};color:{fg}">'
            f"<b>{esc(name)}</b>{esc(role)}</div>"
            for name, bg, fg, role in slide["palette"]
        )
        picture = image_uri(SHOTS / slide["shot"])
        shot = f'<div class="shot" style="flex-basis:640px"><img src="{picture}" alt=""></div>'
        return (
            f'<p class="eyebrow">{esc(slide["eyebrow"])}</p>'
            '<div class="body" style="margin-top:10px">'
            '<div style="flex:1;display:flex;flex-direction:column">'
            f'<div class="brandrow">{MARK}<span class="word">OriginPass</span></div>'
            f'<p class="slogan">{esc(slide["slogan"])}</p>'
            f'<p class="lead" style="font-size:27px;margin-bottom:30px">{esc(slide["lead"])}</p>'
            f'<div class="swatches">{swatches}</div></div>{shot}</div>'
        )
    if kind == "close":
        return f"""<div class="cover-mark">{MARK}</div><h1>{esc(slide["title"])}</h1>
<p class="lead" style="margin-top:34px;font-size:34px">{esc(slide["lead"])}</p>
<p class="cover-who">{"<br>".join(esc(link) for link in slide["links"])}</p>"""
    raise ValueError(kind)


def page(slide, number, total):
    dark = slide["kind"] in ("cover", "close", "statement")
    foot = (
        ""
        if dark
        else f'<div class="foot"><span class="brand">{MARK}OriginPass · Entrega 3</span>'
        f"<span>{number} / {total}</span></div>"
    )
    return (
        f'<!doctype html><html lang="es"><head><meta charset="utf-8"><style>{CSS}</style></head>'
        f'<body class="{"dark" if dark else ""}">'
        f"{'' if dark else '<div class=pinta></div>'}{render(slide)}{foot}</body></html>"
    )


def build():
    from deck_content import SLIDES as DECK

    SLIDES.mkdir(parents=True, exist_ok=True)
    for old in SLIDES.glob("*.png"):
        old.unlink()
    images = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        tab = context.new_page()
        for number, slide in enumerate(DECK, 1):
            tab.set_content(page(slide, number, len(DECK)))
            tab.wait_for_timeout(150)
            target = SLIDES / f"{number:02d}.png"
            tab.screenshot(path=str(target))
            images.append(target)
        browser.close()

    pages = [Image.open(path).convert("RGB") for path in images]
    pages[0].save(PDF, save_all=True, append_images=pages[1:], resolution=144)

    lines = [
        "# OriginPass — Entrega 3: guion de la presentación",
        "",
        "Lo que se dice sobre cada diapositiva de `OriginPass-Entrega-3-presentacion.pdf`.",
        "",
    ]
    for number, slide in enumerate(DECK, 1):
        title = slide.get("title", "").replace("\n", " ")
        lines += [f"## {number}. {title}", "", slide["say"], ""]
    SCRIPT.write_bytes("\n".join(lines).encode("utf-8"))
    print(f"{PDF} ({len(DECK)} slides)")
    print(SCRIPT)


if __name__ == "__main__":
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    build()
