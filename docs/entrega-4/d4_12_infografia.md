# D4-12 · Infografía ejecutiva OriginPass (una página)

Base de citas: `OriginPass/` = `D:\Universidad\Proyecto integrador 1\OriginPass\OriginPass` (copia local; README.md indica "Sprint 2"). `WIKI/` = `D:\Universidad\Proyecto integrador 1\OriginPass-wiki`. Funcionalidades de analítica: `D4-02` cita código de `origin/main`, no de la copia local.

---

## 1. Proyecto y equipo

**OriginPass** — Proyecto Integrador 1 (ST0251), 2026-2, Universidad EAFIT. (`OriginPass/README.md:1,5`)

Equipo número 1. Integrante único: **Emmanuel Hernández Melo** (Scrum Master, Product Owner y Developer). Proyecto individual, aprobado antes del Entregable 1. (`WIKI/Team.md:3,5-7,9,13-17`)

## 2. Problema (50 palabras)

Las falsificaciones son indistinguibles de los originales en el punto de venta. Las artesanías de origen protegido sufren: una copia industrial del sombrero vueltiao se vende junto al tejido real de Tuchín sin que el comprador pueda distinguirlos. Los productores pierden ventas y reputación, y los certificados impresos se fotocopian. (50 palabras)

Fuente: `OriginPass/README.md:7-11`.

## 3. Solución (78 palabras)

OriginPass emite un pasaporte verificable por cada unidad de producto y registra cada cambio de custodia desde el fabricante hasta el dueño actual. Verifica empresas por dos vías: registro comercial oficial, o revisión manual para talleres artesanales. Cada pasaporte tiene un código no adivinable que se publica en una página de verificación accesible por QR, sin cuenta. El sistema analiza los escaneos para detectar clonación de QR, como un mismo pasaporte escaneado en lugares distantes en poco tiempo. (78 palabras)

Fuente: `OriginPass/README.md:13-19`.

## 4. Captura del sistema

PENDIENTE: captura de pantalla del sistema (no existe imagen verificada en el repo ni en la wiki).

Pantalla recomendada: **página pública de veredicto de verificación** (la que abre cualquier comprador al escanear el QR). Es la pantalla central del producto.
- Cómo obtenerla: `python manage.py seed_demo` imprime la ruta de verificación de cada pasaporte demo; abrir esa ruta bajo `http://127.0.0.1:8000/`. (`OriginPass/README.md:86,91-98`)
- Alternativa: panel de analítica de la empresa, `products/templates/products/analytics.html` (según `D4-02`, FR46-FR52).

## 5. Funcionalidades (5)

- **Verificación de empresas en dos vías:** registro comercial con código oficial o revisión manual para artesanos. (`OriginPass/README.md:15`; revisión del administrador en `README.md:184`)
- **Pasaporte por unidad con QR y veredicto público sin cuenta:** código no adivinable y página de verificación accesible por QR. (`OriginPass/README.md:16-17`; `README.md:186-187`)
- **Analítica de escaneos:** conteo por rango de 7/30/90/365 días, distribución por región, ranking de productos, tendencia contra el periodo anterior y exportación CSV. (`D4-02`, FR46, FR47, FR48, FR51, FR52)
- **Alerta de escaneo duplicado:** misma clave escaneada en dos regiones en 24 h, con registro `Alert`. (`D4-02`, FR49; `verification/views.py:37,127-145` en `origin/main`)
- **Registro de auditoría con integridad firmada:** entradas firmadas con clave derivada de `SECRET_KEY`, detección de manipulación con `verify_integrity`. (`OriginPass/README.md:159-171`; `D4-02` cita `audit/views.py:23-40`)

Nota: la cadena de custodia (`README.md:18`) no se incluye como funcionalidad entregada. Ver PENDIENTE 3.

## 6. Stack con versiones

| Capa | Tecnología | Versión | Fuente |
|---|---|---|---|
| Lenguaje | Python | 3.12 | `OriginPass/README.md:41`; `.github/workflows/ci.yml:39` |
| Framework web | Django | 5.2 (rango `>=5.2,<6.0`) | `requirements.txt:1`; `README.md:42` |
| Base de datos | PostgreSQL | 17 (`postgres:17-alpine`) | `docker-compose.yml:3`; `README.md:43` |
| Driver BD | psycopg | `>=3.2` | `requirements.txt:2` |
| Imágenes y QR | Pillow / qrcode | `>=11.0` / `>=8.0` | `requirements.txt:5-6` |
| Interfaz | HTML, CSS y plantillas Django (MVT), sin framework CSS | n/a | `README.md:44` |
| Linter | Ruff | 0.16.2 | `requirements-dev.txt:5` (según `D4-05` §1) |
| Admin de BD | pgAdmin | 9.17 | `docker-compose.yml:39` (según `D4-05` §1) |
| CI | GitHub Actions; checkout v4; setup-python v5 | `ubuntu-latest` | `.github/workflows/ci.yml:11,35,37` |

Las versiones de rango (`requirements.txt`) no tienen lock file en el repo: las instaladas en producción son PENDIENTE 2.

## 7. Enlace al repositorio

https://github.com/Pacha-e/OriginPass

Verificado con `git remote -v` en la copia local: `origin https://github.com/Pacha-e/OriginPass.git`. Coincide con `WIKI/Team.md:32`.

## 8. Enlace a la aplicación desplegada

PENDIENTE: URL pública de la aplicación desplegada.

Estado verificado: no hay URL de despliegue. El repo declara "MVP de trabajo" y el despliegue es tema de Sprint 4 (`OriginPass/README.md:23-30`; `D4-05` §4). La dirección `http://127.0.0.1:8000/` (`README.md:86`) es local y no cuenta como despliegue.

---

## Resumen de PENDIENTE

1. PENDIENTE: captura de pantalla real del sistema (sección 4); la pantalla recomendada es el veredicto público generado con `seed_demo`.
2. PENDIENTE: URL de la aplicación desplegada y versiones exactas instaladas en producción (sección 8; `D4-05` §6, puntos 1 y 7).
3. PENDIENTE: confirmar estado de la cadena de custodia y de la analítica en `origin/main`. `OriginPass/README.md:190` indica que las transferencias de custodia y la analítica llegan en sprints posteriores, mientras que `D4-02` describe la analítica como implementada en `origin/main`. Hay que verificar `origin/main` antes de presentar la funcionalidad como entregada.

Total de PENDIENTE: 3.
