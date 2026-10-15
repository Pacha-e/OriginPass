"""Build the Deliverable 3 presentation: one PDF of slides and the presenter's script.

Each slide is written as HTML in the project's own identity (the añil and caña
palette, Bahnschrift headings, the ringed P), rendered at 1920x1080 in a
headless browser, and printed directly to a vector PDF. The script that goes
with each slide is written beside it and saved as Markdown, so the deck and
what is said over it change together.

Run from the repository root:  python tools/presentation/build_deck.py
Writes to tools/presentation/build/.
"""

import base64
import html
import shutil
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent.parent
BUILD = Path(__file__).resolve().parent / "build"
SLIDES = BUILD / "slides"
PDF = BUILD / "OriginPass-Entrega-3-presentacion.pdf"
SCRIPT = BUILD / "OriginPass-Entrega-3-guion.md"
HTML = BUILD / "OriginPass-Entrega-3-presentacion.html"

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
    """Inline SVG keeps shapes and diagram labels vectorial in Chromium's PDF."""
    return path.with_suffix(".svg").read_text(encoding="utf-8")


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
        stem = Path(slide["image"]).stem
        return (
            head(slide)
            + '<div class="diagram"><div class="img">'
            + diagram_uri(DIAGRAMS / slide["image"])
            + '</div></div><p class="diagram-link"><span class="screen-only">'
            + "Ampliar por separado: "
            + f'<a href="diagramas/{stem}.pdf">PDF</a> · '
            + f'<a href="diagramas/{stem}.svg">SVG</a> · '
            + '<a href="diagramas/index.html">Todos los diagramas</a></span>'
            + f'<span class="print-only">Ampliar: diagramas/{stem}.pdf</span></p>'
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


def slide_html(slide, number, total):
    dark = slide["kind"] in ("cover", "close", "statement")
    foot = (
        ""
        if dark
        else f'<div class="foot"><span class="brand">{MARK}OriginPass · Entrega 3</span>'
        f"<span>{number} / {total}</span></div>"
    )
    capture = ""
    if slide.get("shot"):
        name = slide["shot"]
        capture = (
            '<p class="capture-link"><span class="screen-only">'
            f'<a href="capturas/{name}">Abrir captura a tamaño original</a></span>'
            f'<span class="print-only">Captura completa: capturas/{name}</span></p>'
        )
    return (
        f'<section class="slide {"dark" if dark else ""}" id="slide-{number}">'
        f"{'' if dark else '<div class=pinta></div>'}{render(slide)}{capture}{foot}</section>"
    )


def document(slides):
    return (
        '<!doctype html><html lang="es"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>OriginPass · Entrega 3</title><style>{CSS}</style></head><body>"
        + "".join(slide_html(slide, n, len(slides)) for n, slide in enumerate(slides, 1))
        + "</body></html>"
    )


def copy_diagrams(deck):
    folder = BUILD / "diagramas"
    folder.mkdir(exist_ok=True)
    links = []
    for slide in deck:
        if slide["kind"] != "diagram":
            continue
        stem = Path(slide["image"]).stem
        formats = []
        for extension in ("pdf", "svg", "png"):
            name = f"{stem}.{extension}"
            shutil.copy2(DIAGRAMS / name, folder / name)
            formats.append(f'<a href="{name}">{extension.upper()}</a>')
        source = stem.split("-", 2)[:2]
        source_name = "-".join(source) + ".drawio"
        shutil.copy2(ROOT / "docs/diagrams" / source_name, folder / source_name)
        links.append(f"<li><h2>{esc(slide['title'])}</h2>{' · '.join(formats)}</li>")
    (folder / "index.html").write_text(
        '<!doctype html><html lang="es"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        "<title>OriginPass · Diagramas</title><style>"
        'body{font:20px/1.5 "Segoe UI",sans-serif;max-width:900px;margin:40px auto;'
        "padding:0 24px;color:#1e2b58;background:#f3f4ee}"
        "li{margin-bottom:32px}a{display:inline-block;padding:8px;color:#1e2b58}"
        "</style><h1>Diagramas de OriginPass</h1>"
        "<p>Abre el PDF para ampliar con texto nítido. El SVG se abre en el navegador. "
        "El PNG de alta resolución sirve como respaldo. Los archivos .drawio son editables.</p>"
        "<ul>" + "".join(links) + "</ul></html>",
        encoding="utf-8",
    )


def copy_captures(deck):
    folder = BUILD / "capturas"
    folder.mkdir(exist_ok=True)
    links = []
    for slide in deck:
        if not slide.get("shot"):
            continue
        name = slide["shot"]
        shutil.copy2(SHOTS / name, folder / name)
        links.append(f'<li><a href="{name}">{esc(slide["title"])}</a></li>')
    (folder / "index.html").write_text(
        '<!doctype html><html lang="es"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        "<title>OriginPass · Capturas completas</title><style>"
        'body{font:20px/1.5 "Segoe UI",sans-serif;max-width:900px;margin:40px auto;'
        "padding:0 24px;color:#1e2b58;background:#f3f4ee}"
        "a{display:inline-block;padding:10px;color:#1e2b58}"
        "</style><h1>Capturas completas de la aplicación</h1>"
        "<p>Abre una captura y pulsa sobre ella para verla a tamaño original.</p><ul>"
        + "".join(links)
        + "</ul></html>",
        encoding="utf-8",
    )


def build():
    from deck_content import SLIDES as DECK

    SLIDES.mkdir(parents=True, exist_ok=True)
    for old in SLIDES.glob("*.png"):
        old.unlink()
    copy_diagrams(DECK)
    copy_captures(DECK)
    HTML.write_text(document(DECK), encoding="utf-8")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        tab = context.new_page()
        tab.goto(HTML.as_uri(), wait_until="networkidle")
        tab.evaluate("document.fonts.ready")
        tab.pdf(
            path=str(PDF),
            width="1920px",
            height="1080px",
            print_background=True,
            prefer_css_page_size=True,
            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
        )
        for number, _slide in enumerate(DECK, 1):
            target = SLIDES / f"{number:02d}.png"
            tab.locator(f"#slide-{number}").screenshot(path=str(target))
        browser.close()

    lines = [
        "# OriginPass — Entrega 3: guion de la presentación",
        "",
        "Lo que se dice sobre cada diapositiva de `OriginPass-Entrega-3-presentacion.pdf`.",
        "",
    ]
    for number, slide in enumerate(DECK, 1):
        title = slide.get("title", "").replace("\n", " ")
        lines += [f"## {number}. {title}", "", slide["say"], ""]
        if slide["kind"] == "diagram":
            lines += ["Nuevo en el Sprint 3:", ""]
            lines += [f"- {change}" for change in slide["changes"]]
            lines += ["", f"Ampliar: `diagramas/{Path(slide['image']).stem}.pdf`.", ""]
    SCRIPT.write_bytes("\n".join(lines).encode("utf-8"))
    print(f"{PDF} ({len(DECK)} slides)")
    print(SCRIPT)


if __name__ == "__main__":
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    build()
