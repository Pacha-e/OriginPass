# Guía de la revisión — Seguimiento del Entregable 3 (1 de octubre, 10:50–11:10)

La sesión pide avance en **desarrollo, pruebas e integración**, más preguntas puntuales.
Son 20 minutos: ~12 de demostración, ~4 de pruebas e integración, ~4 de preguntas.

## 1. Arranque (5 minutos antes, en PowerShell)

```powershell
cd "D:\Universidad\Proyecto integrador 1\OriginPass"
docker compose up -d db
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_demo
.\.venv\Scripts\python.exe manage.py runserver
```

Abrir http://127.0.0.1:8000. Los correos (aprobación, aviso de entrega, anulación,
restablecer contraseña) se imprimen en esta misma terminal: dejarla visible.

Cuentas (contraseña de todas: la que imprime `seed_demo`):

| Cuenta | Para mostrar |
|---|---|
| `admin@originpass.co` | Panel, solicitudes, suspender, anular, auditoría |
| `taller@tuchin.co` | Pasaportes, QR, Escaneos, Entregas, entrega pendiente |
| `contacto@labonga.co` | Distribuidor: responder la oferta abierta |
| `comprador@correo.co` | Comprador particular que tiene una pieza |
| `info@mochilaswayuu.co` | Solicitud pendiente (para aprobarla en vivo) |

## 2. Demostración (~12 min)

| # | Qué hacer | Requisitos |
|---|---|---|
| 1 | Inicio: logo, eslogan, verificador en el hero. Pegar el código del sombrero de 21 vueltas. | Identidad, FR28 |
| 2 | Veredicto **Auténtico**: sello, hoja de datos, franja MRZ, **recorrido** taller → La Bonga → comprador particular (sin emails). Mostrarlo a 360 px (F12 → móvil). | FR29, FR32, UR01, UR03 |
| 3 | Hamaca de San Jacinto: **Anulado** con fecha y motivo. Un código inventado: **No encontrado**. | FR30, FR31 |
| 4 | Entrar como `taller@tuchin.co` → Escaneos: por día y por región, **tendencia vs periodo anterior**, **alerta de posible copia** (Córdoba y Bogotá en menos de un día). Exportar CSV. | FR46–FR49, FR51, FR52 |
| 5 | Mis productos → sombrero de 15 vueltas: QR, **entrega pendiente con su código de entrega** (solo lo ve quien vende). Pasar el mouse por cada botón muestra qué hace; en el celular la explicación sale debajo. | FR22, FR35, FR40 |
| 6 | Entrar como `contacto@labonga.co` → Entregas → Responder → Recibir el producto (o «Recibir un producto con sus códigos»). Volver a la página pública: el recorrido creció. | FR36, FR37, FR40 |
| 7 | Intentar traspasar una pieza que ya no tienes → rechazo con motivo. | FR38, FR39 |
| 8 | Entrar como admin → Panel: totales por estado y alertas. Anular un pasaporte → cae en la página pública, que ya dice Anulado y el motivo; en la terminal sale el correo al titular. | FR41, FR42, FR50, FR55 |
| 9 | Solicitudes → Mochilas Wayuu → Aprobar (correo en la terminal). Suspender otra empresa con motivo. | FR13, FR15, FR16, FR53 |
| 10 | Auditoría: filtrar por acción; banner "cadena firmada íntegra". | FR43–FR45, FR44 |
| 11 | Login: 5 fallos seguidos bloquean, con el mismo mensaje de error (no delata la cuenta). | FR57, FR04 |

## 3. Pruebas (~2 min)

- Suite: `python manage.py test` (293 tests, todos en verde).
  Cada criterio de aceptación tiene un test que lo afirma, incluidos los tiempos (3 s, 5 s).
- Mostrar `products/tests/test_custody_transfers.py`: cada defecto encontrado en la
  auditoría tiene un test de regresión que falla sin el arreglo.
- `ruff check .` y `ruff format --check .` en verde; `makemigrations --check` sin cambios.
- `python manage.py verify_integrity`: recorre la auditoría y cada cadena de custodia firmada.

## 4. Integración (~2 min)

- **CI** (`.github/workflows/ci.yml`): en cada push y PR a `main`, PostgreSQL 17 real,
  traducciones, migraciones, suite, lint y formato.
- **Base de datos**: las reglas que se pueden decir en SQL están también en la base
  (`CHECK`, `UNIQUE`, una sola oferta abierta por pieza como índice parcial). pgAdmin en
  http://127.0.0.1:8080 para mostrarlas.
- **Correo**: un solo módulo (`accounts/emails.py`), backend por configuración: consola
  en desarrollo, SMTP en despliegue. Un fallo de correo se registra, no tumba la decisión.
- **CDN**: la región del escaneo sale de las cabeceras de geolocalización solo si
  `TRUST_GEO_HEADERS` está activo (detrás de Cloudflare); si no, un cliente podría falsificar
  alertas de copia.

## 5. Preguntas para el profesor

1. ¿El seguimiento de hoy cuenta como la reunión con el Product Owner que pide 5.2, o
   debemos registrar una aparte?
2. El modelo de datos se pide en GenMyModel; el del Entregable 2 está en draw.io. ¿Se
   acepta draw.io si sigue la notación RDS?
3. Para la evidencia de percepción de usuarios (1 min del video): ¿basta una entrevista
   corta con un artesano o comprador, o se espera una encuesta?
4. FR56 (publicar la cabeza de la cadena de integridad fuera del sistema) quedó para el
   Sprint 4. ¿Es aceptable presentarlo como mejora posterior al MVP?

## 6. Lo que sigue abierto (decirlo antes de que lo pregunten)

- FR27 registro masivo por CSV (Could), UR05 cambio de idioma (Could), FR34 límite por
  minuto con mensaje de espera (Should), FR56 publicación externa de la cadena (Must, Sprint 4).
- Video del entregable (4–5 min) y la evidencia de percepción de usuarios.
- Diagramas actualizados al Sprint 3 y la página Deliverable-3 publicada en la wiki.

## 7. Si algo falla en vivo

- La base no responde: `docker compose up -d db` y esperar a que diga *healthy*.
- Datos raros: `python manage.py seed_demo` es idempotente; vuelve a crear lo que falte.
- Plan B: las capturas de `docs/brand/screenshots/` muestran cada pantalla.

## Estado verificado (1 de octubre, 06:38)

- `python manage.py test`: 293 tests, OK (977 s).
- `ruff check .` y `ruff format --check .`: limpios. `makemigrations --check`: sin cambios.
