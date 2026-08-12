"""Build each slide as HTML and render it to a 1920x1080 PNG.

The slides borrow the palette and the shapes of the application itself, so the
deck and the product look like one thing rather than two.
"""

import html
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).parent))
from script import SECTIONS  # noqa: E402

BUILD = Path(__file__).parent / "build"
SLIDES = BUILD / "slides"

WIDTH, HEIGHT = 1920, 1080

CSS = """
:root {
  --ink:#16181d; --ink-soft:#5b6270; --ink-faint:#8b91a0;
  --surface:#ffffff; --sunken:#f6f7f9; --border:#e3e6ec;
  --accent:#3f4bd8; --accent-wash:#eef0fd;
  --ok:#1a7f52; --warning:#a8630b; --danger:#c02a2a;
}
* { box-sizing:border-box; margin:0; padding:0; }
body {
  width:1920px; height:1080px; overflow:hidden;
  font-family:system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  color:var(--ink); background:var(--sunken);
  display:flex; flex-direction:column; justify-content:center;
  padding:110px 150px; position:relative;
}
body::before {
  content:""; position:absolute; inset:0 0 auto 0; height:8px; background:var(--accent);
}
.eyebrow {
  font-size:24px; font-weight:650; letter-spacing:.09em; text-transform:uppercase;
  color:var(--accent); margin-bottom:26px;
}
h1 { font-size:82px; line-height:1.08; letter-spacing:-.025em; font-weight:700; }
h2 { font-size:60px; line-height:1.14; letter-spacing:-.02em; font-weight:680; }
.body { font-size:34px; line-height:1.5; color:var(--ink-soft); margin-top:34px; max-width:1350px; }
.mark {
  width:96px; height:96px; border-radius:24px; background:var(--accent); color:#fff;
  display:flex; align-items:center; justify-content:center;
  font-size:38px; font-weight:700; margin-bottom:46px;
}
.subtitle { font-size:42px; color:var(--ink-soft); margin-top:26px; }
.footer {
  position:absolute; left:150px; bottom:80px;
  font-size:26px; color:var(--ink-faint);
}
ul { list-style:none; margin-top:48px; }
li {
  font-size:36px; line-height:1.4; color:var(--ink); padding-left:52px;
  position:relative; margin-bottom:34px; max-width:1500px;
}
li::before {
  content:""; position:absolute; left:0; top:16px;
  width:20px; height:20px; border-radius:6px; background:var(--accent);
}
table { width:100%; border-collapse:collapse; margin-top:46px; font-size:30px; }
th {
  text-align:left; padding:20px 26px; font-size:22px; font-weight:650;
  text-transform:uppercase; letter-spacing:.05em; color:var(--ink-faint);
  border-bottom:2px solid var(--border);
}
td { padding:22px 26px; border-bottom:1px solid var(--border); vertical-align:top; }
tr:last-child td { border-bottom:0; }
.card {
  background:var(--surface); border:1px solid var(--border);
  border-radius:22px; padding:16px 30px; box-shadow:0 2px 6px rgba(22,24,29,.05);
}
.num { font-variant-numeric:tabular-nums; font-weight:650; }
.tag {
  display:inline-block; padding:6px 18px; border-radius:999px;
  font-size:22px; font-weight:650;
}
.tag--done { color:var(--ok); background:#e7f5ee; }
.tag--next { color:var(--warning); background:#fdf3e3; }
.code { color:var(--accent); font-weight:650; }
.stat-wrap { display:flex; align-items:flex-start; gap:90px; margin-top:50px; }
.stat-block { flex:0 0 620px; }
.stat {
  font-size:250px; line-height:.9; font-weight:750; color:var(--danger);
  letter-spacing:-.05em;
}
.stat-label {
  font-size:32px; line-height:1.35; color:var(--ink-soft);
  margin-top:22px; padding-left:8px; border-left:4px solid var(--danger);
  padding-left:22px;
}
.note { margin-top:38px; font-size:26px; color:var(--ink-faint); }
.member { display:flex; align-items:center; gap:34px; margin-top:52px; }
.avatar {
  width:120px; height:120px; border-radius:34px; background:var(--accent-wash);
  color:var(--accent); display:flex; align-items:center; justify-content:center;
  font-size:46px; font-weight:700;
}
.member-name { font-size:46px; font-weight:680; }
.member-meta { font-size:28px; color:var(--ink-soft); margin-top:8px; }
.links { margin-top:52px; }
.links div { font-size:32px; color:var(--ink-soft); margin-bottom:16px; }
.center { align-items:center; text-align:center; }
"""


def esc(value):
    return html.escape(str(value))


def render_body(slide):
    layout = slide["layout"]

    if layout == "title":
        return f"""
        <div class="mark">OP</div>
        <h1>{esc(slide["title"])}</h1>
        <div class="subtitle">{esc(slide["subtitle"])}</div>
        <div class="footer">{esc(slide["footer"])}</div>
        """

    if layout == "statement":
        return f"""
        <div class="eyebrow">{esc(slide["eyebrow"])}</div>
        <h2>{esc(slide["title"])}</h2>
        <div class="body">{esc(slide["body"])}</div>
        """

    if layout == "bullets":
        items = "".join(f"<li>{esc(b)}</li>" for b in slide["bullets"])
        return f"""
        <div class="eyebrow">{esc(slide["eyebrow"])}</div>
        <h2>{esc(slide["title"])}</h2>
        <ul>{items}</ul>
        """

    if layout == "table":
        head = "".join(f"<th>{esc(c)}</th>" for c in slide["columns"])
        rows = "".join(
            "<tr>" + "".join(f"<td>{esc(cell)}</td>" for cell in row) + "</tr>"
            for row in slide["rows"]
        )
        return f"""
        <div class="eyebrow">{esc(slide["eyebrow"])}</div>
        <h2>{esc(slide["title"])}</h2>
        <div class="card"><table><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>
        """

    if layout == "evidence":
        rows = "".join(
            f"<tr><td>{esc(name)}</td>"
            f"<td class='num' style='text-align:right'>{esc(count)}</td></tr>"
            for name, count in slide["rows"]
        )
        return f"""
        <div class="eyebrow">{esc(slide["eyebrow"])}</div>
        <h2>{esc(slide["title"])}</h2>
        <div class="stat-wrap">
          <div class="stat-block">
            <div class="stat">{esc(slide["stat"])}</div>
            <div class="stat-label">{esc(slide["statLabel"])}</div>
          </div>
          <div class="card" style="flex:1"><table style="margin-top:0;font-size:29px">
            <tbody>{rows}</tbody>
          </table></div>
        </div>
        <div class="note">{esc(slide["note"])}</div>
        """

    if layout == "team":
        members = "".join(
            f"""<div class="member">
                  <div class="avatar">{esc(m["name"][0])}</div>
                  <div>
                    <div class="member-name">{esc(m["name"])}</div>
                    <div class="member-meta">{esc(m["roles"])}</div>
                    <div class="member-meta">{esc(m["email"])}</div>
                  </div>
                </div>"""
            for m in slide["members"]
        )
        return f"""
        <div class="eyebrow">{esc(slide["eyebrow"])}</div>
        <h2>{esc(slide["title"])}</h2>
        {members}
        <div class="note">{esc(slide["note"])}</div>
        """

    if layout == "requirements":
        rows = ""
        for rank, code, text, state in slide["rows"]:
            tag = "done" if state == "Entregado" else "next"
            rows += (
                f"<tr><td class='num' style='color:var(--ink-faint);width:70px'>{esc(rank)}</td>"
                f"<td class='code' style='width:130px'>{esc(code)}</td>"
                f"<td>{esc(text)}</td>"
                f"<td style='text-align:right'>"
                f"<span class='tag tag--{tag}'>{esc(state)}</span></td></tr>"
            )
        return f"""
        <div class="eyebrow">{esc(slide["eyebrow"])}</div>
        <h2>{esc(slide["title"])}</h2>
        <div class="card"><table><tbody>{rows}</tbody></table></div>
        """

    if layout == "close":
        links = "".join(f"<div>{esc(link)}</div>" for link in slide["links"])
        title = esc(slide["title"]).replace("\n", "<br>")
        return f"""
        <div class="mark" style="margin:0 auto 46px">OP</div>
        <h2 style="text-align:center">{title}</h2>
        <div class="links" style="text-align:center">{links}</div>
        """

    raise ValueError(f"unknown layout: {layout}")


def page_html(slide):
    extra = " center" if slide["layout"] == "close" else ""
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<style>{CSS}</style></head><body class="{extra.strip()}">{render_body(slide)}</body></html>"""


def main():
    SLIDES.mkdir(parents=True, exist_ok=True)
    slides = [s for s in SECTIONS if s["kind"] == "slide"]

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": WIDTH, "height": HEIGHT})

        for section in slides:
            target = SLIDES / f"{section['id']}.png"
            page.set_content(page_html(section["slide"]))
            page.wait_for_timeout(120)
            page.screenshot(path=str(target))
            print(f"  {target.name}")

        browser.close()

    print(f"\n{len(slides)} slides rendered at {WIDTH}x{HEIGHT}")


if __name__ == "__main__":
    main()
