# OriginPass para artesanos — plan de implementación

> **Para workers agénticos:** SUB-SKILL REQUERIDA: usar superpowers:subagent-driven-development (recomendado) o superpowers:executing-plans para implementar este plan tarea por tarea. Los pasos usan casillas (`- [ ]`) para el seguimiento.

**Objetivo:** que un artesano pueda, solo y desde el celular, inscribir su taller, registrar un producto una vez y sacarle N pasaportes, imprimir los QR en un PDF, y entregar piezas o lotes en persona. También que una persona reciba la pieza en su cuenta o por correo.

**Arquitectura:**

- `ProductLine` es el producto que se registra una vez. `Product` sigue siendo la unidad con pasaporte, firmada y con su cadena de custodia.
- El traspaso en persona escribe directamente una fila `ACCEPTED` de `CustodyTransfer`. Lo autoriza un código de 6 dígitos que se calcula con HMAC y no se guarda en ningún lado. Ese código existe por pieza y por lote (`TransferBatch`).
- La interfaz pasa a una barra inferior con íconos SVG propios y a un asistente de inscripción por pasos.

**Tecnología:** Django 5.2, PostgreSQL 17, Pillow y qrcode (ya instalados), plantillas Django con CSS propio (`static/css/originpass.css`) y el JS mínimo sin frameworks que ya usa el proyecto.

**Spec:** `docs/superpowers/specs/2026-11-07-originpass-para-artesanos-design.md`. Quien ejecute lee el spec y este plan.

## Restricciones globales

- **Wiki congelada.** No se toca ni `03-OriginPass-wiki/` ni la wiki de GitHub.
- **Dependencias.** Ninguna nueva sin preguntar a Emmanuel.
- **Git.** Todo el trabajo va en la rama `artesanos-ux`. Commit al final de cada tarea; ya hay permiso dado para commits en esta rama. Push y despliegue necesitan permiso aparte.
- **Firmas.**
  - Todo cambio en `signed_parts()` va acompañado de una migración que vuelve a firmar las filas existentes, siguiendo el precedente de `products/migrations/0008_resign_products_with_status.py`.
  - `python manage.py verify_integrity` tiene que pasar después de cada migración, contra la base con `seed_demo` cargado.
- **Migraciones con restricciones.** Antes de un `CHECK` o `UNIQUE` nuevo, contar las filas que lo violan. Si hay alguna, la migración se hace en tres pasos: permisivo, corregir datos, endurecer.
- **Textos.**
  - Todo texto visible va en `{% translate %}` o `_()`, con el msgid en inglés y la traducción en `locale/es/LC_MESSAGES/django.po`.
  - La traducción tiene que tutear, usar frases cortas y ningún tecnicismo. Quedan prohibidas en la interfaz: «criptográfico», «hash», «UUID», «token», «razón social», «vía de verificación», y además «pieza», «custodia», «traspaso» y «revocar» (la prueba `pages.tests.test_guidance.PlainWordsTests` falla si aparecen en el catálogo). Se dice «producto», «entregar», «recibir» y «anular».
- **Íconos.** Nada de emojis ni librerías de íconos. Solo el sprite propio de la Tarea 12.
- **Código de entrega.**
  - 6 dígitos que cambian cada **120 s**, con **15 s** de gracia.
  - Queda inválido al hacerse el traspaso.
  - **5** fallos en **15 min** bloquean la pieza o el lote durante **15 min**.
- **Lotes.** Una cuenta `Role.HOLDER` entrega lotes de **5** piezas como máximo. Una empresa no tiene límite. Recibir no tiene límite.
- **Correo a persona sin cuenta.** El enlace firmado vale **30 días**. Registrarse con el mismo correo sin usar el enlace **no** reclama la pieza.
- **Página pública.** Si quien tiene la pieza no es una empresa aprobada, se muestra «Una persona». Nunca se muestra un correo.
- **PDF de QR.** Hojas carta de 2550×3300 px a 300 dpi, 3×4 = **12** QR por hoja, generadas con Pillow.
- **Entorno.**
  - El hook de prettier puede romper plantillas `.html` escritas con Edit: después de editar, renderizar la página y revisarla.
  - Escribir archivos con LF.
  - Ruff se corre como `python -m ruff ... --force-exclude`.
- **Verificación al cerrar cada tarea.** Correr `python manage.py test <app>`. Al final, la suite entera, `python manage.py makemigrations --check --dry-run`, `python -m ruff check . --force-exclude`, `python -m ruff format --check . --force-exclude` y `python manage.py verify_integrity`.

## Foco de revisión

1. **Doble envío de «Recibir»** (doble toque o recargar). La segunda petición no crea otra fila y responde «Ya es tuyo». Prueba en la Tarea 5.
2. **Dos personas escriben el mismo código a la vez.** Solo una recibe y la otra ve «Este código ya no sirve». Se resuelve con `select_for_update` sobre el producto. Prueba en la Tarea 5.
3. **Código escrito con espacios o guion** («482 913», «482-913»). Se acepta, porque se normaliza a dígitos. Prueba en la Tarea 4.
4. **Pieza anulada que está dentro de un lote abierto.** Al confirmar el lote, falla el lote entero con un mensaje que nombra la pieza. Prueba en la Tarea 7.
5. **Enlace del correo abierto con la sesión de otra cuenta.** Pide cerrar sesión o entrar con la cuenta correcta. Nunca reclama la pieza para la cuenta equivocada. Prueba en la Tarea 6.

## Cadena de GitHub (por cada tarea)

1. **Issue.**
   - Se abre una por tarea, con la etiqueta `artesanos` y su prioridad (`must`, `should` o `could`).
   - El cuerpo enlaza el spec y la tarea del plan, y copia sus pruebas como criterios de aceptación.
   - Todas cuelgan de la épica «OriginPass para artesanos» como sub-issues.
2. **Rama.** Se crea `artesanos/NN-<slug>` desde `main` actualizado. Si la tarea anterior todavía espera aprobación, se ramifica desde esa rama y se apila.
3. **Commits.** Pequeños, con el porqué en el mensaje. El último cierra la tarea.
4. **PR hacia `main`.**
   - Lleva `Closes #<issue>`, un resumen, la lista de archivos tocados con su porqué y capturas a 390 px si la tarea cambia la interfaz.
   - Se revisa con `interface-review` (pantallas) o con `superpowers:requesting-code-review` (modelo y seguridad) antes de pedir aprobación.
5. **CI.** El `.github/workflows/ci.yml` tiene que quedar en verde: migraciones, pruebas, ruff check y ruff format. Si falla, se arregla en la misma rama.
6. **Aprobación.** Emmanuel aprueba la promoción a `main`. Hasta que lo diga explícitamente, no hay merge.
7. **Merge.** Squash a `main`, se borra la rama y se cierra el issue por el `Closes`.

## Skills por tarea

| Tareas | Skills |
|---|---|
| Todas | `superpowers:test-driven-development`, `superpowers:verification-before-completion`, `django-tdd` (proyecto) |
| 1–7 (modelos, firmas, traspaso) | `django-expert`, `django-security` (proyecto), `superpowers:systematic-debugging` si algo falla, `superpowers:requesting-code-review` |
| 9, 13 (QR, listas) | `impeccable`, `better-interface` (proyecto) |
| 10, 11 (registro, asistente) | `form-design`, `onboarding-design`, `error-handling-ux` (proyecto), `clarify` |
| 12 (íconos, barra) | `icon-system`, `navigation-patterns` (proyecto), `impeccable`, `frontend-design` |
| 10–14 (textos) | `better-writing` (proyecto), `design:ux-copy`, `clarify` |
| 11–13, 15 (accesibilidad y QA) | `accessibility` y `better-accessibility` (proyecto), `design:accessibility-review`, `interface-review`, `playwright-best-practices` (proyecto), `webapp-testing` |

Las skills del proyecto están fijadas en `skills-lock.json`. Se restauran con `npx skills experimental_install`, y sus carpetas (`.agents/` y `.claude/skills/`) no se versionan.

## Reparto de trabajo

| Quién | Tareas |
|---|---|
| Orquestador (modelo principal), por tocar firmas, cadena o seguridad | 1, 3, 4, 5, 6, 7 |
| Worker Haiku `ux-worker` (plantillas, CSS, vistas simples) | 9, 10, 11, 12, 13 |
| Worker Haiku `i18n-worker` | 14 |
| Worker Haiku `test-worker` | Pruebas de interfaz de las Tareas 10 a 13, cuando el orquestador las reparta |

El orquestador revisa cada tarea de un worker antes de hacer commit.

---

### Tarea 0: Herramientas del proyecto

**Archivos:**
- Crear: `.claude/agents/ux-worker.md`, `.claude/agents/test-worker.md`, `.claude/agents/i18n-worker.md`
- Crear: `tools/ux/recorrido.py`

**Interfaces:**
- Produce:
  - Los agentes `ux-worker`, `test-worker` e `i18n-worker`, con `model: haiku` y `tools: Read, Edit, Write, Grep, Glob, Bash`. Las herramientas van restringidas porque, con todas cargadas, el contexto de Haiku se desborda.
  - El comando `python tools/ux/recorrido.py --base http://127.0.0.1:8000 --out <dir>`, que escribe capturas JPEG de 390 px, numeradas, de las cinco tareas del spec §1. Cada captura se recorta en trozos de 1700 px de alto.

- [ ] **Paso 1:** Escribir los tres agentes. El cuerpo de cada uno copia la sección «Restricciones globales» y añade una regla de su oficio:
  - `ux-worker`: renderizar la página a 390 px y mirar la captura antes de terminar.
  - `test-worker`: una prueba que falle sin el cambio.
  - `i18n-worker`: tuteo, frases cortas, ningún tecnicismo.
- [ ] **Paso 2:** Escribir `tools/ux/recorrido.py` a partir de `recon.py` de la sesión: Playwright con viewport 390×844, `is_mobile`, `has_touch` y las cuentas de `seed_demo` (contraseña `OriginPass-2026`). Las rutas que todavía no existen se saltan con un aviso.
- [ ] **Paso 3:** Correr el recorrido con el servidor local. Se espera ver las capturas y avisos de las rutas faltantes, sin excepciones.
- [ ] **Paso 4:** Commit: `Add the Haiku workers and the 390 px walkthrough tool`.

### Tarea 1: `ProductLine` y la migración de los productos existentes

**Archivos:**
- Modificar: `products/models.py` (modelo nuevo y FK en `Product`)
- Crear: `products/migrations/0009_productline.py`, `0010_lines_for_existing_products.py` y `0011_product_line_required.py`
- Probar: `products/tests/test_product_lines.py`

**Interfaces:**
- Produce:
  - `class ProductLine(models.Model)`, con los campos `company` (FK `Company`, PROTECT, `related_name="lines"`), `product_type`, `name`, `description`, `category`, `origin`, `image`, `created_at` y `updated_at`.
  - `Product.line`: FK `ProductLine`, PROTECT, `related_name="passports"`. Nulo en la 0009 y obligatorio en la 0011.
  - `Product.signed_parts()` **no cambia**.

- [ ] **Paso 1:** Escribir `test_every_existing_product_gets_its_own_line`. Usa `MigrationExecutor` para migrar a `0008`, crear 2 productos, migrar a `0011` y comprobar que hay 2 líneas, que los nombres coinciden y que `product.is_intact` sigue siendo `True`.
- [ ] **Paso 2:** Correr `python manage.py test products.tests.test_product_lines`. Se espera FALLO: la migración no existe.
- [ ] **Paso 3:** Implementar el modelo y las tres migraciones.
  - La 0010 crea una línea por producto, copiando sus campos y su `image`.
  - La 0011 marca la FK como `null=False`.
- [ ] **Paso 4:** Correr la prueba y, con `seed_demo` cargado, `python manage.py migrate && python manage.py verify_integrity`. Se espera PASS y «intact».
- [ ] **Paso 5:** Commit: `Group passports under a product line registered once`.

### Tarea 2: Sacar N pasaportes de una línea

**Archivos:**
- Modificar: `products/models.py`
- Probar: `products/tests/test_product_lines.py`

**Interfaces:**
- Consume: `ProductLine` de la Tarea 1.
- Produce: `ProductLine.issue_passports(count: int, actor) -> list[Product]`.
  - Todo ocurre en una transacción.
  - Cada `Product` copia `name`, `category`, `origin` y `product_type` de la línea y queda firmado.
  - Por cada pasaporte se añade una entrada `AuditEntry` `PRODUCT_REGISTERED`.
  - Lanza `ValueError` si `count` no está entre 1 y 200. El tope de 200 es decisión mía.
  - Lanza `ValueError` si la empresa no está `APPROVED`.

- [ ] **Paso 1:** Escribir las pruebas:
  - `test_issue_twenty_passports_copies_the_line`: 20 códigos distintos, todos `is_intact` y todos `line_id == line.pk`.
  - `test_issue_rejects_zero_and_201`.
  - `test_issue_refused_for_unapproved_company`.
  - `test_editing_line_does_not_alter_issued_passports`: después de cambiar `line.name`, el pasaporte conserva su nombre y sigue `is_intact`.
- [ ] **Paso 2:** Correrlas. Se espera FALLO.
- [ ] **Paso 3:** Implementar `issue_passports`.
- [ ] **Paso 4:** Correrlas. Se espera PASS.
- [ ] **Paso 5:** Commit: `Issue many passports from one product line`.

### Tarea 3: Custodia a nombre de un correo y cierre de las ofertas abiertas

**Archivos:**
- Modificar: `products/models.py` (`CustodyTransfer`, `ProductQuerySet.held_by` y `Product.current_holder`)
- Crear: `products/migrations/0012_custody_email.py`, `0013_resign_custody_with_email.py` y `0014_close_open_offers.py`
- Probar: `products/tests/test_custody_email.py`

**Interfaces:**
- Produce:
  - `CustodyTransfer.from_holder` y `CustodyTransfer.to_holder` pasan a ser `null=True`. Se añaden `from_email = EmailField(blank=True)` y `to_email = EmailField(blank=True)`.
  - Dos `CHECK`:
    - `custody_transfer_one_sender`: exactamente uno entre `from_holder` y `from_email`;
    - `custody_transfer_one_receiver`: exactamente uno entre `to_holder` y `to_email`.
  - `signed_parts()` pasa a ser `(product_id, from_holder_id, from_email, to_holder_id, to_email, note, created_at.isoformat())`.
  - `Product.current_holder` devuelve `User | None`. Devuelve `None` cuando la última fila aceptada va a un correo.
  - Nueva propiedad `Product.holder_email -> str`: el `to_email` de esa última fila, o `""`.
  - `held_by(user)` sigue la misma regla y nunca incluye piezas a nombre de un correo.

- [ ] **Paso 1:** Contar las filas `INITIATED` en la base de demostración y anotar el número en el commit.
- [ ] **Paso 2:** Escribir las pruebas:
  - `test_transfer_to_email_leaves_no_account_holder`.
  - `test_check_refuses_both_receivers`: un `IntegrityError` con `to_holder` y `to_email` a la vez.
  - `test_old_chains_verify_after_resign`, usando `MigrationExecutor` de 0011 a 0013 y luego `CustodyTransfer.verify_chain(product)` igual a `(True, None)`.
  - `test_open_offers_are_declined_with_note`.
- [ ] **Paso 3:** Correrlas. Se espera FALLO.
- [ ] **Paso 4:** Implementar. La 0013 recorre cada producto en orden de `id`, recalcula `previous_hash` y `entry_hash` con `sign` y deja también en el registro de auditoría la nueva firma de cada fila. La 0014 cierra las ofertas con `_resolve(TransferState.DECLINED, …)`, sin actor y con la nota «Cerrada al cambiar el sistema de entregas».
- [ ] **Paso 5:** Correr las pruebas de products y `verify_integrity` sobre `seed_demo`. Se espera PASS e «intact».
- [ ] **Paso 6:** Commit: `Let custody rest on an email address and close the old open offers`.

### Tarea 4: El código de entrega de 6 dígitos

**Archivos:**
- Crear: `products/handover.py` y `products/migrations/0015_handover_attempt.py`
- Modificar: `products/models.py` (modelo `HandoverAttempt`)
- Probar: `products/tests/test_handover_code.py`

**Interfaces:**
- Produce:
  - `WINDOW_SECONDS = 120`, `GRACE_SECONDS = 15`, `MAX_FAILURES = 5`, `LOCK_MINUTES = 15`.
  - `handover_code(subject: str, subject_id: int, holder_key: str, counter: int, at: datetime) -> str`. `subject` vale `"product"` o `"batch"`. Devuelve un HMAC-SHA256 de la clave derivada de `SECRET_KEY`, con namespace `"originpass.handover"`, sobre `subject|subject_id|holder_key|counter|floor(at/120)`, reducido a 6 dígitos con relleno de ceros.
  - `seconds_left(at: datetime) -> int`, entre 1 y 120.
  - `normalise(typed: str) -> str`: deja solo los dígitos.
  - `check_handover_code(subject, subject_id, holder_key, counter, typed: str, at: datetime) -> bool`. Acepta la ventana actual, y la anterior si `at` está a 15 s o menos de su cambio. Compara con `hmac.compare_digest`.
  - `is_locked(subject, subject_id, at) -> bool` y `record_failure(subject, subject_id, at) -> None`, con el modelo `HandoverAttempt(subject, subject_id, failed_at)`.
  - `holder_key` es el pk del dueño actual o su correo. `counter` es el número de filas `ACCEPTED` de la pieza; para un lote, su `state`.

- [ ] **Paso 1:** Escribir las pruebas:
  - `test_same_code_within_window` y `test_code_changes_next_window`.
  - `test_accepts_previous_code_within_15_seconds` y `test_refuses_previous_code_after_15_seconds`.
  - `test_code_dies_when_holder_or_counter_changes`.
  - `test_normalises_spaces_and_hyphen`: «482 913» y «482-913».
  - `test_five_failures_lock_for_fifteen_minutes`: bloqueado en t+1 min y libre en t+16 min.
  - `test_code_is_six_digits_with_leading_zeros`: un caso con el reloj fijado.
- [ ] **Paso 2:** Correrlas. Se espera FALLO.
- [ ] **Paso 3:** Implementar.
- [ ] **Paso 4:** Correrlas. Se espera PASS.
- [ ] **Paso 5:** Commit: `Derive a six-digit handover code that rotates every two minutes`.

### Tarea 5: Entregar y recibir una pieza en persona

**Archivos:**
- Modificar: `products/models.py`, `products/views.py`, `products/urls.py` y `products/forms.py`
- Crear: `products/templates/products/handover.html`, `products/templates/products/receive.html` y `static/js/handover-ring.js`
- Modificar: `verification/templates/verification/verdict.html`, para añadir el botón «Recibir este producto» si la pieza está activa.
- Probar: `products/tests/test_handover_in_person.py`

**Interfaces:**
- Consume: la Tarea 4 y `holder_email` de la Tarea 3.
- Produce:
  - `CustodyTransfer.record_handover(product, *, to_holder=None, to_email="", actor) -> CustodyTransfer`. Es un classmethod.
    - Abre una transacción y bloquea el producto con `select_for_update`.
    - Revisa que la pieza esté activa y que el remitente sea el dueño actual.
    - Añade una fila con `state=ACCEPTED` y `resolved_at=now` usando `_append`, y una entrada `CUSTODY_ACCEPTED` en auditoría.
    - El remitente es `from_holder=product.current_holder` o `from_email=product.holder_email`.
  - Rutas:
    - `products:handover`, `<int:pk>/entregar/`, solo para el dueño. Muestra el QR de la pieza (la misma URL `/v/<code>/`), el código en grande, la cuenta regresiva y el anillo.
    - `products:handover_code`, `<int:pk>/entregar/codigo.json`, solo para el dueño. Responde `{"code": "482913", "seconds_left": 87}` con `Cache-Control: no-store`.
    - `products:receive`, `recibir/<str:passport_code>/`, con `login_required`. GET muestra foto, nombre, quién la hizo y «la tiene ahora»; POST recibe `code`.
  - `handover-ring.js` cuenta hacia atrás cada segundo, dibuja el anillo SVG que se cierra y vuelve a pedir el JSON al llegar a 0.

- [ ] **Paso 1:** Escribir las pruebas:
  - `test_holder_sees_code_and_others_get_404`, sobre las dos rutas del dueño.
  - `test_receive_with_right_code_moves_the_piece`.
  - `test_wrong_code_counts_a_failure_and_says_so`.
  - `test_code_is_dead_right_after_handover`.
  - `test_double_submit_does_not_add_a_second_row`: la segunda petición responde «Ya es tuyo».
  - `test_concurrent_receivers_only_one_wins`: dos clientes con el mismo código, y solo hay una fila nueva.
  - `test_revoked_piece_cannot_be_received`.
  - `test_receive_page_shows_photo_name_maker_holder`.
- [ ] **Paso 2:** Correrlas. Se espera FALLO.
- [ ] **Paso 3:** Implementar el modelo, las vistas, las plantillas y el JS. El flujo viejo (`transfer_initiate`, `transfer_claim` y `transfer_respond`) sale de `urls.py` y del menú; sus pruebas se reescriben o se retiran en esta tarea.
- [ ] **Paso 4:** Correr `python manage.py test products verification`. Se espera PASS.
- [ ] **Paso 5:** Commit: `Hand a piece over in person with the rotating code`.

### Tarea 6: Entregar a una persona sin cuenta, por correo

**Archivos:**
- Modificar: `products/views.py`, `products/urls.py` y `products/forms.py`
- Crear: `products/email_handover.py`, `products/templates/products/handover_email.html`, `products/templates/products/claim_email.html` y `products/templates/products/email/possession.txt`
- Probar: `products/tests/test_handover_email.py`

**Interfaces:**
- Consume: `record_handover(..., to_email=...)` de la Tarea 5.
- Produce:
  - `make_claim_token(transfer: CustodyTransfer) -> str`, con `TimestampSigner` y salt `"originpass.claim"`, sobre `transfer.pk` y `transfer.entry_hash`.
  - `read_claim_token(token) -> CustodyTransfer`. Lanza `BadSignature` o `SignatureExpired`; `max_age` es de 30 días.
  - Rutas:
    - `products:handover_email`, `<int:pk>/entregar/correo/`: el dueño escribe el correo dos veces.
    - `products:claim_email`, `reclamar/<str:token>/`: si no hay sesión, ofrece crear cuenta o entrar y vuelve aquí. Si la sesión tiene otro correo, explica que hay que entrar con la cuenta de ese correo.
    - `products:resend_email` y `products:correct_email`: para quien entregó, mientras nadie haya reclamado.
  - La corrección añade una fila de `from_email` viejo a `to_email` nuevo, y entonces el token anterior deja de valer porque cambió la última fila.

- [ ] **Paso 1:** Escribir las pruebas:
  - `test_mismatched_emails_refused`.
  - `test_email_sent_with_link`: `mail.outbox` tiene 1 mensaje, con el enlace y el nombre de la pieza.
  - `test_claim_with_matching_account_moves_to_account`: la cadena queda `correo → cuenta` y verifica.
  - `test_registering_same_email_without_link_does_not_claim`.
  - `test_logged_in_as_other_account_cannot_claim`.
  - `test_expired_token_after_30_days`.
  - `test_correction_kills_old_link`.
  - `test_public_page_shows_una_persona_not_email`.
- [ ] **Paso 2:** Correrlas. Se espera FALLO.
- [ ] **Paso 3:** Implementar.
- [ ] **Paso 4:** Correrlas. Se espera PASS.
- [ ] **Paso 5:** Commit: `Hand a piece to a person by email and let them claim it by the link`.

### Tarea 7: Lotes

**Archivos:**
- Modificar: `products/models.py` (`TransferBatch` y `TransferBatchItem`)
- Crear: `products/migrations/0016_transfer_batch.py`, `products/batches.py` y las plantillas `batch_new.html`, `batch_handover.html` y `batch_receive.html`
- Modificar: `products/views.py` y `products/urls.py`
- Probar: `products/tests/test_batches.py`

**Interfaces:**
- Consume: las Tareas 4 y 5.
- Produce:
  - `TransferBatch(owner FK User, public_code CharField unique default generate_passport_code, state CharField OPEN/HANDED/CANCELLED, created_at)` y `TransferBatchItem(batch FK, product FK)`.
  - Un `UniqueConstraint(fields=["product"], condition=Q(batch__state="OPEN"))`, o un campo `open_flag` si la condición no puede cruzar la FK; decide quien implementa y lo deja anotado.
  - `create_batch(owner, products) -> TransferBatch`. Lanza `ValueError` si una pieza no es del dueño, si está anulada o si ya está en un lote abierto, y también si `owner.role == Role.HOLDER` y hay más de 5 piezas.
  - `receive_batch(batch, receiver, typed_code, at) -> list[CustodyTransfer]`. En una transacción bloquea las piezas, vuelve a comprobar que todas son del dueño y están activas, y llama a `record_handover` por cada una. Al terminar marca el lote `HANDED`. Si algo falla, no pasa ninguna pieza.
  - Rutas: `products:batch_new` (`lote/nuevo/`), `products:batch_handover` (QR del lote y código), `products:batch_receive` (`lote/<public_code>/`, con la lista «20 × Sombrero…» y el código), `products:batch_cancel`.

- [ ] **Paso 1:** Escribir las pruebas:
  - `test_person_limited_to_five`: 6 piezas lanzan `ValueError` y 5 pasan.
  - `test_company_unlimited`, con 30 piezas.
  - `test_receive_moves_all_and_closes_batch`.
  - `test_revoked_piece_in_batch_fails_whole_batch_and_names_it`.
  - `test_piece_cannot_be_in_two_open_batches`.
  - `test_batch_code_dies_when_handed`.
  - `test_batch_not_shown_on_public_page`.
- [ ] **Paso 2:** Correrlas. Se espera FALLO.
- [ ] **Paso 3:** Implementar.
- [ ] **Paso 4:** Correrlas. Se espera PASS.
- [ ] **Paso 5:** Commit: `Hand over many pieces at once as a batch`.

### Tarea 8: Correo por SMTP

**Archivos:** modificar `config/settings.py:158-164`, `.env.example` y `deploy/aws/README-AWS.md`. Probar en `accounts/tests/test_email_settings.py`.

**Interfaces:** `EMAIL_HOST`, `EMAIL_PORT` (int, por defecto 587), `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` y `EMAIL_USE_TLS` (por defecto `True`), leídos del entorno. `EMAIL_BACKEND` sigue siendo el de consola por defecto.

- [ ] **Paso 1:** Escribir `test_smtp_settings_read_from_environment`, que recarga los settings con `mock.patch.dict(os.environ, …)` y el módulo recargado.
- [ ] **Paso 2:** Correrla. Se espera FALLO.
- [ ] **Paso 3:** Implementar y documentar, sin poner valores reales.
- [ ] **Paso 4:** Correrla. Se espera PASS.
- [ ] **Paso 5:** Commit: `Read the SMTP settings from the environment`.

### Tarea 9: PDF de hojas de QR

**Archivos:**
- Crear: `products/sheets.py`
- Modificar: `products/management/commands/export_passport_qr.py` (para usar `sheets.py`), `products/views.py` y `products/urls.py`
- Crear: `products/templates/products/print_qr.html`
- Probar: `products/tests/test_qr_sheets_pdf.py`

**Interfaces:**
- Produce:
  - `qr_sheets(products, base_url: str) -> list[Image.Image]`, que mueve aquí `_page`, `_label`, `COLUMNS`, `ROWS` y `PAGE_SIZE` desde el comando.
  - `qr_sheets_pdf(products, base_url) -> bytes`, con `save_all=True`, `resolution=300`.
  - Ruta `products:print_qr`, `imprimir/`. GET lista los pasaportes del usuario agrupados por línea, con casillas y un botón «Marcar todos los de este producto». POST con `product` (lista de ids) devuelve `application/pdf`, con `Content-Disposition: attachment; filename="originpass-qr.pdf"`. `base_url` sale de `request.build_absolute_uri("/")`.

- [ ] **Paso 1:** Escribir las pruebas:
  - `test_thirteen_passports_make_two_pages`, contando las páginas del PDF con Pillow.
  - `test_foreign_product_ids_refused`: responde 404 o los ignora sin incluirlos; quien implementa decide y la prueba fija esa decisión.
  - `test_command_still_writes_png_sheets`.
- [ ] **Paso 2:** Correrlas. Se espera FALLO.
- [ ] **Paso 3:** Implementar.
- [ ] **Paso 4:** Correrlas. Se espera PASS.
- [ ] **Paso 5:** Commit: `Print the chosen QR codes as one PDF of Letter sheets`.

### Tarea 10: Registro de cuenta con tipo e inicio de sesión automático

**Archivos:** modificar `accounts/forms.py:50`, `accounts/views.py:76-91` y `accounts/templates/accounts/register.html`. Probar en `accounts/tests/test_registration.py`.

**Interfaces:**
- `RegistrationForm` recibe el campo `kind` con las opciones `"business"` y `"person"`, presentadas como dos tarjetas grandes con ícono.
- Después de guardar se llama a `login()`. Si `kind == "business"`, redirige a `companies:application_wizard`; si es `"person"`, a `products:custody` («Mis productos»).
- El rol sigue siendo `HOLDER` hasta que se envía la solicitud, como hoy en `companies/views.py:51`.

- [ ] **Paso 1:** Escribir las pruebas:
  - `test_register_logs_in_and_sends_business_to_wizard`.
  - `test_register_person_lands_on_my_pieces`.
  - `test_kind_is_required`.
- [ ] **Paso 2:** Correrlas. Se espera FALLO.
- [ ] **Paso 3:** Implementar.
- [ ] **Paso 4:** Correrlas. Se espera PASS.
- [ ] **Paso 5:** Commit: `Ask the account kind at registration and sign the person in`.

### Tarea 11: Asistente de inscripción, un dato por pantalla

**Archivos:**
- Crear: `companies/wizard.py` y `companies/templates/companies/wizard_step.html`
- Modificar: `companies/views.py` y `companies/urls.py`
- Probar: `companies/tests/test_application_wizard.py`

**Interfaces:**
- `STEPS` es una lista ordenada de `(key, field_names)` y depende del tipo:
  - taller: `kind` → `legal_name` → `location` → `description` → `craft_evidence` → `consent`;
  - empresa: `kind` → `legal_name` → `verification_track` + `registry_code` → `location` → `description` → `website` → `consent`.

  Los nombres de campo deben coincidir con `CompanyApplicationForm`; quien implementa los verifica.
- El avance se guarda en `request.session["application_wizard"]`.
- Ruta `companies:application_wizard`, `inscripcion/<str:step>/`.
- En cada paso se valida solo ese campo con el formulario actual. Al final se valida el formulario completo y se reutiliza el guardado de `application_create`, con su manejo de `IntegrityError`.
- Cada pantalla muestra «Paso X de Y», una barra de progreso y los botones Siguiente y Atrás.
- La primera pantalla son dos tarjetas: «Hago productos a mano» y «Tengo empresa o tienda con NIT».
- El consentimiento es una tarjeta que se toca entera, no una casilla diminuta.

- [ ] **Paso 1:** Escribir las pruebas:
  - `test_artisan_path_skips_registry_fields`.
  - `test_back_keeps_typed_values`.
  - `test_invalid_step_stays_with_message`.
  - `test_finish_creates_pending_application_once`, con doble POST al final.
  - `test_progress_label_counts_steps`.
- [ ] **Paso 2:** Correrlas. Se espera FALLO.
- [ ] **Paso 3:** Implementar.
- [ ] **Paso 4:** Correrlas y renderizar cada paso a 390 px con `tools/ux/recorrido.py`. Se espera PASS y capturas sin desbordes.
- [ ] **Paso 5:** Commit: `Walk the application one question per screen`.

### Tarea 12: Íconos propios y barra inferior

**Archivos:**
- Crear: `templates/partials/icons.html` (sprite SVG con `<symbol>`) y `templates/partials/tabbar.html`
- Modificar: `templates/base.html` y `static/css/originpass.css`
- Probar: `pages/tests/test_tabbar.py`, o en una app existente si `pages` no tiene `tests/`

**Interfaces:**
- Íconos con ids `icon-products`, `icon-print`, `icon-handover`, `icon-workshop`, `icon-pieces`, `icon-receive`, `icon-verify`.
  - `viewBox 0 0 32 32`, trazo `currentColor` de 2,4 px y acento en `var(--cana)`.
  - Motivos: anillos y trenza del logo, sombrero, manos.
  - Se usan como `<svg aria-hidden="true"><use href="#icon-…"/></svg>`, siempre acompañados de su palabra.
- Pestañas de empresa: Productos (`products:product_list`), Imprimir QR (`products:print_qr`), Entregas (`products:custody`) y Mi taller (`companies:application_detail`).
- Pestañas de persona: Mis productos (`products:custody`), Recibir (`verification:lookup`, el lector de QR) y Mi cuenta.
- Visitante: sin barra.
- En pantallas de 768 px o más, la barra pasa a ser el menú superior. El correo y «Cambiar contraseña» salen de la cabecera y van dentro de Mi taller o Mi cuenta.
- La pestaña activa lleva `aria-current="page"`.

- [ ] **Paso 1:** Escribir las pruebas:
  - `test_company_sees_four_tabs`.
  - `test_person_sees_three_tabs`.
  - `test_visitor_sees_no_tabbar`.
  - `test_active_tab_marked`.
  - `test_no_emoji_in_templates`: recorre las plantillas buscando caracteres en los rangos de emoji U+1F300–U+1FAFF y U+2600–U+27BF.
- [ ] **Paso 2:** Correrlas. Se espera FALLO.
- [ ] **Paso 3:** Implementar.
- [ ] **Paso 4:** Correrlas y tomar capturas a 390 px y 1280 px. Se espera PASS y que la barra no tape contenido, lo que se resuelve con `padding-bottom` en `main`.
- [ ] **Paso 5:** Commit: `Navigate with a bottom bar and the brand's own icons`.

### Tarea 13: Pantallas de producto, pasaportes y listas en tarjetas

**Archivos:** modificar `products/templates/products/product_list.html`, `product_form.html`, `product_detail.html` y `custody.html`, más `products/views.py`, `products/forms.py` y `static/css/originpass.css`. Probar en `products/tests/test_line_screens.py`.

**Interfaces:**
- «Productos» lista **líneas** en tarjetas, con foto, nombre y conteos («12 activos · 3 entregados»).
- El detalle de una línea muestra sus pasaportes en tarjetas y el formulario «¿Cuántos pasaportes quieres sacar?», con un campo numérico grande y botones − y +, que llama a `issue_passports`. Al terminar ofrece «Imprimir sus QR».
- El formulario de registro de una línea:
  - `origin` viene ya lleno con la ubicación de la empresa;
  - el selector de foto es un botón propio traducido («Tomar o elegir foto»), sin el texto del navegador;
  - no lleva la frase sobre «fuente criptográficamente segura».
- Ninguna tabla se sale de la pantalla a 390 px.

- [ ] **Paso 1:** Escribir las pruebas:
  - `test_list_shows_lines_with_counts`.
  - `test_issue_form_creates_n`.
  - `test_origin_prefilled_from_company`.
  - `test_no_technical_words_on_product_pages`, contra la lista de palabras prohibidas.
- [ ] **Paso 2:** Correrlas. Se espera FALLO.
- [ ] **Paso 3:** Implementar.
- [ ] **Paso 4:** Correrlas y tomar capturas a 390 px. Se espera PASS y que nada se desborde.
- [ ] **Paso 5:** Commit: `Register a product once and issue its passports from cards`.

### Tarea 14: Traducciones

**Archivos:** `locale/es/LC_MESSAGES/django.po` y `.mo`.

- [ ] **Paso 1:** Extraer los msgid nuevos y traducirlos al español sencillo. No hay gettext; se usa la herramienta de i18n del proyecto con la que se compiló el `.mo` en entregas anteriores, buscándola en el repo o en `auditoria-2026-10-01`.
- [ ] **Paso 2:** Correr la prueba de vocabulario que ya existe (la que «falla si vuelve el vocabulario técnico») y toda la suite. Se espera PASS.
- [ ] **Paso 3:** Commit: `Translate the artisan screens into plain Spanish`.

### Tarea 15: Recorrido final y verificación completa

- [ ] **Paso 1:** Cargar `seed_demo` sobre una base migrada desde `main` y comprobar que la migración no pierde datos y que `verify_integrity` da «intact».
- [ ] **Paso 2:** Correr `python tools/ux/recorrido.py` con las cinco tareas del spec §1 y revisar cada captura a ojo.
- [ ] **Paso 3:** Correr las comprobaciones de las restricciones globales. Se espera todo en verde.
- [ ] **Paso 4:** Entregar a Emmanuel la lista de archivos tocados y las capturas. Push y despliegue solo con su permiso.
