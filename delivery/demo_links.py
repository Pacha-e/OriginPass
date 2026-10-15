"""Write the local presentation links using this database's actual passport codes."""

import html
import os
import sys
from pathlib import Path


def main():
    folder = Path(__file__).resolve().parent
    root = folder / "app" if (folder / "app/manage.py").exists() else folder.parent
    sys.path.insert(0, str(root))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django

    django.setup()
    from products.models import Product

    base = "http://127.0.0.1:8000"
    links = [
        ("Inicio", "/"),
        ("Ingresar a otra cuenta", "/accounts/login/"),
        ("Mis productos (taller)", "/products/"),
        ("Entregas (taller, distribuidor o comprador)", "/products/custody/"),
        ("Escaneos y alerta de posible copia (taller)", "/products/analytics/"),
        ("Panel del administrador", "/products/admin/overview/"),
        ("Solicitudes de empresas (administrador)", "/companies/review/"),
        ("Auditoría (administrador)", "/audit/"),
        ("Veredicto No encontrado", "/v/NO-EXISTE/"),
    ]
    links.extend(
        (f"{product.name} ({product.get_status_display()})", f"/v/{product.passport_code}/")
        for product in Product.objects.order_by("name")
    )
    items = "".join(
        f'<li><a href="{base}{html.escape(path)}">{html.escape(label)}</a></li>'
        for label, path in links
    )
    target = folder / "ABRIR-DEMO.html"
    target.write_text(
        '<!doctype html><html lang="es"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        "<title>OriginPass · Demostración local</title><style>"
        'body{font:20px/1.5 "Segoe UI",sans-serif;max-width:1000px;margin:40px auto;'
        "padding:0 24px;color:#1e2b58;background:#f3f4ee}li{margin:12px 0}"
        "a{display:inline-block;padding:6px 0;color:#1e2b58}</style>"
        "<h1>Demostración local</h1><p>Abre las cuentas en ventanas separadas: "
        "taller@tuchin.co, contacto@labonga.co y admin@originpass.co. "
        "La contraseña de demostración aparece al ejecutar Setup-Portatil.ps1.</p>"
        "<p>Los pasaportes siguientes corresponden a los datos de este equipo.</p>"
        f"<ul>{items}</ul></html>",
        encoding="utf-8",
    )
    print(f"Demo links ready: {target} ({len(links)} links)")


if __name__ == "__main__":
    main()
