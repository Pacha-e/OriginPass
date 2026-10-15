"""Record the Deliverable 3 features as a silent walkthrough with on-screen captions.

Every step of the MVP loop, in the order a presenter explains it: the workshop
issues a passport, the buyer checks it, the piece passes to a distributor and on
to a buyer who claims it with two codes, the analytics catch a copied QR, the
passport is revoked, and the administrator reads the signed audit trail. There
is no narration, so a caption at the foot of the screen says what each step is.

The interface is served in Spanish (UR04), so every locator matches the Spanish
a visitor reads.

Run against a seeded database (`manage.py seed_demo`) and a server started with
`manage.py runserver 127.0.0.1:8765`. Writes
`tools/video/build/OriginPass-Entrega-3-recorrido.mp4`.
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
RAW = BUILD / "recorrido-raw"
TARGET = BUILD / "OriginPass-Entrega-3-recorrido.mp4"
PHOTO = ROOT / "companies/management/commands/demo_photos/sombrero-vueltiao-21.jpg"

BASE = "http://127.0.0.1:8765"

#: The seed demo shares one password across every demo account.
PASSWORD = "OriginPass-2026"
WORKSHOP = "taller@tuchin.co"
DISTRIBUTOR = "contacto@labonga.co"
BUYER = "comprador@correo.co"
ADMIN = "admin@originpass.co"

#: A name the seed data does not use, so runs never collide with it.
DEMO_NAME = "Sombrero vueltiao 23 vueltas"

VIEWPORT = {"width": 1280, "height": 720}
#: Playwright never scales a recording up, so it records at the viewport size and
#: the encoder scales the result to 1080p.
VIDEO_SIZE = VIEWPORT

#: Draws the caption from sessionStorage on every page, so it survives the
#: navigations between one step and the next.
CAPTION_SCRIPT = """
(() => {
  const draw = () => {
    const text = sessionStorage.getItem('op-caption');
    let box = document.getElementById('op-caption');
    if (!text) { if (box) box.remove(); return; }
    if (!box) {
      box = document.createElement('div');
      box.id = 'op-caption';
      box.setAttribute('aria-hidden', 'true');
      Object.assign(box.style, {
        position: 'fixed', left: '50%', bottom: '22px', transform: 'translateX(-50%)',
        zIndex: 2147483647, maxWidth: '1080px', width: 'calc(100% - 64px)',
        background: 'rgba(20, 29, 61, 0.94)', color: '#ffffff',
        borderLeft: '8px solid #d9c28a', borderRadius: '6px',
        padding: '14px 22px', boxShadow: '0 10px 30px rgba(0,0,0,.28)',
        font: '600 21px/1.35 Bahnschrift, "Segoe UI", system-ui, sans-serif',
        whiteSpace: 'pre-line', pointerEvents: 'none',
      });
      document.body.appendChild(box);
    }
    box.textContent = text;
  };
  window.__opDraw = draw;
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', draw);
  } else {
    draw();
  }
})();
"""

SET_CAPTION = """text => {
  sessionStorage.setItem('op-caption', text);
  if (window.__opDraw) window.__opDraw();
}"""

#: The public profile link of the verdict page, read from the page itself.
PROFILE_LINK = """() => [...document.querySelectorAll('main a')]
  .map(a => a.getAttribute('href'))
  .find(h => /^\\/companies\\/\\d+\\/$/.test(h || ''))"""

#: The ringed P of the brand, drawn in white for the añil cards.
MARK = (
    '<svg viewBox="0 0 48 48" aria-hidden="true">'
    '<rect x="5" y="5" width="8" height="38" rx="1.5" fill="currentColor"/>'
    '<circle cx="26.5" cy="19" r="12" fill="none" stroke="currentColor" stroke-width="4.5"/>'
    '<circle cx="26.5" cy="19" r="6.4" fill="none" stroke="#D9C28A" stroke-width="3" '
    'stroke-dasharray="3.1 1.6"/>'
    '<circle cx="26.5" cy="19" r="2.4" fill="currentColor"/></svg>'
)

CARD = """<!doctype html><html lang="es"><head><meta charset="utf-8"><style>
body {{ margin:0; height:100vh; display:flex; flex-direction:column; justify-content:center;
  padding:0 110px; background:#1e2b58; color:#fff;
  font-family:Bahnschrift,"Segoe UI",system-ui,sans-serif; }}
body::after {{ content:""; position:fixed; left:0; right:0; bottom:0; height:14px;
  background:#d9c28a; }}
svg {{ width:120px; height:120px; color:#ffffff; margin-bottom:30px; }}
p {{ margin:0; color:#d9c28a; font-size:22px; letter-spacing:.12em; text-transform:uppercase; }}
h1 {{ margin:.25em 0 .3em; font-size:58px; line-height:1.1; font-weight:600; }}
h2 {{ margin:0; font-size:28px; font-weight:400; color:#e7eaf3; max-width:900px; }}
</style></head><body>{logo}<p>{eyebrow}</p><h1>{title}</h1><h2>{subtitle}</h2></body></html>"""


def setup_django():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    sys.path.insert(0, str(ROOT))
    django.setup()


def reset_demo_product():
    """Remove pieces left by a previous run so the walk starts clean."""
    from products.models import Alert, CustodyTransfer, Product

    for stale in Product.objects.filter(name=DEMO_NAME):
        Alert.objects.filter(product=stale).delete()
        CustodyTransfer.objects.filter(product=stale).delete()
        stale.delete()


def wait(page, seconds):
    page.wait_for_timeout(int(seconds * 1000))


def say(page, text, seconds=0.0):
    page.evaluate(SET_CAPTION, text)
    wait(page, seconds)


def card(page, eyebrow, title, subtitle, seconds):
    logo = MARK
    page.set_content(CARD.format(logo=logo, eyebrow=eyebrow, title=title, subtitle=subtitle))
    wait(page, seconds)


def clear(page):
    """Drop the caption before leaving a page, so it never sits over the next one."""
    page.evaluate("() => { try { sessionStorage.removeItem('op-caption'); } catch (e) {} }")


def go(page, path, seconds=0.6):
    clear(page)
    page.goto(f"{BASE}{path}")
    page.wait_for_load_state("networkidle")
    wait(page, seconds)


def type_slowly(page, selector, value, delay=40):
    page.click(selector)
    page.type(selector, value, delay=delay)


def submit(page, selector="main form button[type=submit]"):
    clear(page)
    page.click(selector)
    page.wait_for_load_state("networkidle")


def login(page, email):
    go(page, "/accounts/login/", 0.4)
    type_slowly(page, "#id_email", email, delay=22)
    type_slowly(page, "#id_password", PASSWORD, delay=22)
    submit(page)
    wait(page, 0.8)


def logout(page):
    clear(page)
    page.click("form[action*='logout'] button")
    page.wait_for_load_state("networkidle")
    wait(page, 0.4)


def scroll_to(page, selector, seconds):
    page.locator(selector).first.scroll_into_view_if_needed()
    wait(page, seconds)


def demo_product_path(page):
    go(page, "/products/", 0.5)
    href = page.locator("a", has_text=DEMO_NAME).first.get_attribute("href")
    return href


def record():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            viewport=VIEWPORT,
            device_scale_factor=1.5,
            record_video_dir=str(RAW),
            record_video_size=VIDEO_SIZE,
            locale="es-CO",
        )
        context.add_init_script(CAPTION_SCRIPT)
        page = context.new_page()

        card(
            page,
            "Entrega 3 · El MVP",
            "OriginPass: recorrido de las funciones nuevas",
            "La cadena de custodia, la verificación pública, la analítica que detecta copias, "
            "la anulación y el panel del administrador.",
            5,
        )

        go(page, "/", 0.2)
        say(
            page,
            "Inicio · El visitante elige si va a comprar o si hace y vende artesanías,\n"
            "y puede verificar un producto escribiendo el código impreso bajo el QR.",
            5.5,
        )

        # --- 1. The workshop issues a passport ---------------------------------
        login(page, WORKSHOP)
        go(page, "/products/new/", 0.2)
        say(page, "1 · El taller artesanal registra un producto nuevo, con su foto.", 1.5)
        type_slowly(page, "#id_name", DEMO_NAME, delay=30)
        type_slowly(page, "#id_category", "Sombreros", delay=34)
        type_slowly(page, "#id_origin", "Tuchín, Córdoba", delay=30)
        type_slowly(
            page,
            "#id_description",
            "Tejido a mano en caña flecha por tres generaciones del taller.",
            delay=14,
        )
        page.set_input_files("#id_image", str(PHOTO))
        say(
            page,
            "1 · Cada campo explica qué pedir antes de escribir, con un ejemplo dentro.\n"
            "La foto se puede tomar con la cámara del teléfono.",
            3.5,
        )
        submit(page)
        wait(page, 0.6)
        say(
            page,
            "1 · El pasaporte: un código por unidad física, imposible de adivinar,\n"
            "y su QR listo para descargar e imprimir en la etiqueta.",
            5,
        )
        page.hover("a[href$='/qr/']")
        say(
            page,
            "1 · Cada botón dice qué hace al pasar el mouse por encima.\n"
            "En el teléfono, la misma frase aparece escrita debajo del botón.",
            4.5,
        )
        product_path = page.url.replace(BASE, "")
        public_link = page.locator("a", has_text="Ver la página pública").first
        verify_path = public_link.get_attribute("href").replace(BASE, "")
        passport_code = verify_path.rstrip("/").split("/")[-1]

        # --- 2. The buyer checks it ---------------------------------------------
        go(page, verify_path, 0.2)
        say(
            page,
            "2 · Lo que ve el comprador al escanear el QR, sin cuenta ni aplicación:\n"
            "el veredicto Auténtico, sellado, con los datos del producto y del taller.",
            6,
        )
        page.locator("details.info summary").first.click()
        say(page, "2 · Cada término tiene un «?» que abre su significado en el mismo lugar.", 4)
        scroll_to(page, "text=Recorrido de este producto", 0.2)
        say(page, "2 · El recorrido del producto: por ahora solo ha estado en el taller.", 4.5)
        profile = page.evaluate(PROFILE_LINK)
        go(page, profile, 0.2)
        say(page, "2 · El perfil público del taller verificado y sus productos activos.", 4.5)

        # --- 3. The workshop hands it to a distributor ---------------------------
        go(page, product_path.rstrip("/") + "/transfer/", 0.2)
        say(page, "3 · El taller entrega el producto a un distribuidor: escribe su correo.", 1.2)
        type_slowly(page, "#id_to_holder_email", DISTRIBUTOR, delay=26)
        type_slowly(page, "#id_note", "Entrega al distribuidor en Montería.", delay=20)
        say(
            page,
            "3 · El producto sigue a nombre del taller hasta que el distribuidor lo reciba.",
            3,
        )
        submit(page)
        wait(page, 0.5)
        say(
            page,
            "3 · La oferta queda pendiente, con un código de entrega propio de esa entrega.",
            4.5,
        )
        logout(page)

        # --- 4. The distributor accepts -------------------------------------------
        login(page, DISTRIBUTOR)
        go(page, "/products/custody/", 0.2)
        say(page, "4 · El distribuidor ve la oferta en Entregas, esperando su respuesta.", 3.5)
        page.locator("tr", has_text=DEMO_NAME).locator("a[href$='/answer/']").first.click()
        page.wait_for_load_state("networkidle")
        say(page, "4 · Revisa el producto y lo recibe solo si lo tiene en sus manos.", 3.5)
        submit(page, "button[value=accept]")
        say(page, "4 · Recibido: ahora el producto está a nombre del distribuidor.", 3.5)

        # --- 5. The distributor sells it on ----------------------------------------
        go(page, product_path.rstrip("/") + "/transfer/", 0.2)
        say(page, "5 · El distribuidor se lo vende a un comprador particular.", 1)
        type_slowly(page, "#id_to_holder_email", BUYER, delay=26)
        submit(page)
        wait(page, 0.5)
        row = page.locator("tr", has_text=DEMO_NAME).filter(has=page.locator(".code-chip"))
        transfer_code = row.locator(".code-chip").first.inner_text().strip()
        say(
            page,
            "5 · En la venta le entrega el producto y este código de entrega.",
            4.5,
        )
        logout(page)

        # --- 6. The buyer claims it with the two codes -----------------------------
        login(page, BUYER)
        go(page, "/products/custody/claim/", 0.2)
        say(
            page,
            "6 · El comprador lo pone a su nombre con dos códigos:\n"
            "el del pasaporte, impreso bajo el QR, y el de entrega que le dio el vendedor.",
            3,
        )
        type_slowly(page, "#id_passport_code", passport_code, delay=18)
        type_slowly(page, "#id_transfer_code", transfer_code, delay=10)
        wait(page, 1)
        submit(page)
        say(page, "6 · Los dos códigos coinciden: el producto ya es del comprador.", 4)
        logout(page)

        # --- 7. The journey grew ------------------------------------------------------
        go(page, verify_path, 0.2)
        scroll_to(page, "text=Recorrido de este producto", 0.2)
        say(
            page,
            "7 · El recorrido creció: taller → distribuidor → comprador.\n"
            "Cada paso queda firmado y encadenado; no se muestran correos de nadie.",
            6.5,
        )

        # --- 8. The analytics catch a copied QR -----------------------------------------
        login(page, WORKSHOP)
        go(page, "/products/analytics/", 0.2)
        say(
            page,
            "8 · La analítica del taller: escaneos por día, por región y por producto,\n"
            "comparados con el periodo anterior.",
            5,
        )
        if page.locator("text=Posibles copias").count():
            scroll_to(page, "text=Posibles copias", 0.2)
        say(
            page,
            "8 · Alerta de posible copia: el mismo pasaporte escaneado en Córdoba y en Bogotá\n"
            "en menos de un día. La copia de un QR responde igual; dos lugares a la vez, no.",
            6.5,
        )
        page.hover("a[href*='/analytics/csv/']")
        say(page, "8 · Todo se puede exportar en CSV.", 3)

        # --- 9. Revocation ---------------------------------------------------------------
        go(page, product_path.rstrip("/") + "/revoke/", 0.2)
        say(
            page,
            "9 · Si el producto se pierde, se daña o lo copian, el taller anula el pasaporte\n"
            "y escribe el motivo. No se puede deshacer.",
            2,
        )
        type_slowly(page, "#id_reason", "Pieza reportada como perdida en el transporte.", delay=16)
        submit(page)
        wait(page, 0.5)
        go(page, verify_path, 0.2)
        say(
            page,
            "9 · Desde ese momento el QR responde Anulado, con la fecha y el motivo.\n"
            "El dueño actual recibe un correo avisándole.",
            6,
        )
        go(page, "/v/CODIGO-QUE-NO-EXISTE/", 0.2)
        say(
            page,
            "9 · Un código que no existe responde No encontrado, siempre igual,\n"
            "para no revelar qué códigos existen.",
            5,
        )
        logout_needed = page.locator("form[action*='logout'] button").count() > 0
        if logout_needed:
            logout(page)

        # --- 10. The administrator ------------------------------------------------------
        login(page, ADMIN)
        go(page, "/products/admin/overview/", 0.2)
        say(
            page,
            "10 · El administrador ve la plataforma completa:\nempresas y productos por estado.",
            5,
        )
        go(page, "/audit/", 0.2)
        say(
            page,
            "10 · El registro de auditoría: cada decisión firmada y encadenada.\n"
            "Arriba dice si la cadena está íntegra; se filtra por actor, acción y fecha.",
            6.5,
        )
        go(page, "/companies/review/", 0.2)
        say(
            page,
            "10 · Las solicitudes de empresas: comerciales con su registro oficial,\n"
            "talleres informales con la evidencia de su oficio, que revisa una persona.",
            5.5,
        )
        logout(page)

        # --- 11. Account protection --------------------------------------------------------
        go(page, "/accounts/login/", 0.2)
        page.hover("a[href*='password-reset']")
        say(
            page,
            "11 · Recuperar la contraseña con un enlace firmado que vence.\n"
            "Cinco intentos fallidos en 15 minutos bloquean el acceso de ese correo.",
            5.5,
        )
        say(page, "", 0)

        card(
            page,
            "OriginPass",
            "El origen no se imita.",
            "314 pruebas automáticas contra PostgreSQL, en integración continua · "
            "github.com/Pacha-e/OriginPass",
            5,
        )

        video_path = page.video.path()
        context.close()
        browser.close()
    return Path(video_path)


def encode(raw):
    """Re-encode to H.264 so any player, and PowerPoint, can open it."""
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-i",
            str(raw),
            "-c:v",
            "libx264",
            "-preset",
            "slow",
            "-crf",
            "18",
            "-vf",
            "scale=1920:1080:flags=lanczos",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            "-an",
            str(TARGET),
        ],
        check=True,
    )


def main():
    setup_django()
    reset_demo_product()
    if RAW.exists():
        shutil.rmtree(RAW)
    raw = record()
    encode(raw)
    shutil.rmtree(RAW, ignore_errors=True)
    print(f"recorded: {TARGET} ({TARGET.stat().st_size / 1_048_576:.1f} MB)")


if __name__ == "__main__":
    main()
