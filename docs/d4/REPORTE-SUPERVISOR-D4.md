# Reporte para el supervisor: Entregable 4 de OriginPass

## 0. Current status (5 November 2026)

This section is the current status. Sections 1 onward are the record of 29 October 2026 and are kept as history.

| Item | Status |
|---|---|
| Deployment | Deployed on AWS EC2 (AWS Academy Learner Lab), Ubuntu 26.04.1 LTS. Public URL: `https://13-220-96-49.sslip.io`, HTTPS with Let's Encrypt. `/healthz/` answered `{"status": "ok"}` on 5 November 2026 |
| Availability | At the time of this update the instance did not answer from outside. Check the Learner Lab session and `/healthz/` before the demonstration |
| Code | Branch `main`, pushed to `origin`. Latest commits include `64990f9` (CI expression fixed, update script, deployment record) |
| Automated tests | 349 tests passed on PostgreSQL 17 in the last full run (commit `047089f`) |
| Changes since 29 October | Password change for signed-in accounts; printable QR codes at 300 dpi on US Letter sheets, twelve per page; the claim page reads the passport QR from the camera (HTTPS only) or from an uploaded photo; media files served by nginx on the instance |
| CI | Invalid `env` references removed in `64990f9`. The remote run was not checked from this environment |
| Pending | Usability validation with users; PVB validation; Wiki pages for Entregable 4; QR photo reading checked on the final phones; the external audit findings (`05-Auditorias-y-planes/OriginPass-pendientes-auditoria.md`), mainly custody signatures and concurrency; the update script not yet run on the server |

## Record of 29 October 2026 (superseded)

Fecha: 29-oct-2026. Estado: **NO APTO PARA MERGE**.

Este reporte separa lo heredado, lo propuesto, lo escrito por los workers, lo añadido hoy, y lo integrado y probado frente a lo pendiente. Lo no ejecutado se marca como no ejecutado. La afirmación anterior de "todo listo" fue incorrecta y no se repite aquí.

## 1. Veredicto

| Punto | Resultado |
|---|---|
| Merge a `main` | **NO.** Falta la suite completa con PostgreSQL, el ensayo del kit en el portátil, la confirmación de Azure y la autorización de Emmanuel Hernández. |
| Rama de trabajo | `d4/integracion-20261029`, worktree `OriginPass-d4-integracion-20261029`, desde `81fbe6d`. **Sin commits.** |
| URL de despliegue | **No existe.** Azure no se ha ejecutado. |

## 2. Heredado del MVP y de D3

| Elemento | Evidencia |
|---|---|
| `main` @ `81fbe6d`, 81 commits, un solo autor | `git log` |
| 290 archivos versionados; 5 apps con modelos (accounts, audit, companies, products, verification); 8 modelos | Inventario del repo (`D:\OriginPass-D4-orq\auditoria\baseline-inventario.md`) |
| 18 migraciones | `git ls-files`, excluyendo `__init__.py` |
| 314 funciones `test_*` en 39 archivos. **No se ejecutaron en esta sesión.** | `git grep -c` |
| FR 58, UR 10, DBR 12 | `docs/wiki/Requirements-Specification.md` |
| FR abiertos al 15-oct-2026: FR27, FR34, FR56 | `docs/wiki/Deliverable-3.md:257` |
| CI: ruff, format, `makemigrations --check`, migrate y test sobre PostgreSQL 17 | Inventario, §4 |
| Kit de D3 (`delivery/build_portable.py`), presentación y videos de D3 (congelados) | `delivery/`, `tools/` |

## 3. Propuesto por los auditores (sesión anterior)

- Seis informes de auditoría con Haiku: rúbrica, runtime, AWS, wiki, organización y plan integrado. Son **propuestas no verificadas**.
- El ledger registra la revisión independiente interrumpida por límite de gasto del proveedor (`WAITING_FOR_PROVIDER`). Nada de eso se aceptó.
- Auditoría de verificación de lo que dejó Hermes (`D:\OriginPass-D4-orq\auditoria\hermes-verificacion.md`): 34 afirmaciones evaluadas.
  - **Falsas:** "`/healthz/` implementado" (resuelve a `home`); "diagramas revisados" (tamaños idénticos al baseline); cifras de la infografía (45/54 frente a 31/43 palabras reales; "8 Apps" frente a 6); "kit listo" (271 entradas, 0 migraciones); "QA global verde" (75 errores de ruff).
  - **Verificadas por log:** 321 pruebas Django en verde en el paquete de rescate; 15 y 19 pruebas del kit; `migration drift` sin cambios; CI del PR #85 en verde (2026-10-15).
  - **Autoría:** cambios de runtime e infografía sin worker que los respalde (NO DETERMINABLE).

## 4. Escrito por los workers de Hermes

- Según el responsable: la rama de documentación produjo cambios; las ramas de runtime y de diseño reportaron bloqueos.
- Paquete `rescate-2h/integration/delivery/build-d4/OriginPass-Portatil-D4-integrado.zip` (9,5 MB, 314 entradas):
  - 18 migraciones.
  - `healthz` en `app/config/urls.py:21` y `app/pages/views.py:126`.
  - `app/docs/deployment/RUNBOOK-EC2.md`, un runbook de **AWS EC2**.
  - Ocho archivos de infografía y diagramas `d4-*.drawio` y `.svg` que no están integrados en el repo.
  - Scripts `VERIFICAR-D4.py` y `ARRANCAR-D4.ps1`, y `KIT-MANIFEST-D4.json`.
  - **No verificado:** no se ha ejecutado ni integrado.

## 5. Añadido directamente hoy (orquestación)

- Health check: `pages/urls.py`, `pages/views.py` (`healthz` con `SELECT 1`), `pages/tests/test_healthz.py` (3 pruebas).
- `requirements.txt`: `gunicorn>=23.0,<24`.
- `deploy/azure/`: `desplegar-azure.ps1`, `verificar-azure.ps1`, `README-AZURE.md`. **No ejecutados.**
- `delivery/`: `build_d4_kit.py`, `verificar-kit-d4.py`, `LEEME-PORTATIL-D4.md`.
- `docs/d4/`: visión, matriz de requisitos, analítica, usabilidad (protocolo), backlog, limitaciones, seguimiento, retrospectiva (borrador), pitch y demo, diagramas, este reporte y `PREGUNTAS-REVISION.md`.
- `README.md`: sección de Entregable 4. Pendiente de revisión.
- Worktree `d4/integracion-20261029`, creado a las 10:15 por la orquestación de hoy, sin commits (E20).

Nota: el ZIP de rescate de Hermes (09:34) no es una entrega válida: sus fuentes cambiaron entre 09:46 y 09:51 (E13).

## 6. Integrado y probado frente a pendiente

| Elemento | Estado | Evidencia |
|---|---|---|
| `/healthz/`: ruta y vista | **Probado** (unitario) | 3/3 pruebas en verde; ruff sin errores |
| `/healthz/` con la base inalcanzable | **Probado** sin mocks | Sonda real: `STATUS 503`, `{"status": "unavailable"}` |
| `/healthz/` con PostgreSQL vivo (200) | **No probado** | No hay base accesible en este equipo |
| Suite completa | **Probado** | 318 pruebas OK sobre PostgreSQL 17 (2026-10-29, 10:52) |
| `makemigrations --check` | **No ejecutado** | |
| Kit: listado y verificación previa | **Probado** | `--solo-listar`: 290 rastreados, 18 migraciones, 307 archivos de origen, 0 excluidos. Build final: 309 entradas, 18 migraciones, verificador OK (308 archivos, 0 fallos) |
| Kit: build final | Ver sección 9 | |
| Kit en el portátil | **No probado** | Pendiente de ensayo |
| Azure: despliegue | **No ejecutado** | Sin `az login`; requiere ejecución de Emmanuel |
| Diagramas UML (despliegue, componentes, datos) | **Parcial** | `docs/d4/diagramas.md`: 4 bloques Mermaid, 4 de 4 validados por herramienta (una variante sin IP) |
| Matriz de requisitos | **Parcial** | 54 con prueba que la cita, 2 parciales (FR45, FR56), 2 pendientes (FR27, FR34). "Con prueba" no significa que la prueba pase hoy |
| Product Vision Board | **Supuesto** | 0 validados, 5 supuestos (`docs/d4/vision-board.md`) |
| Analítica | **Solo demostración** | Datos de `seed_demo`; no hay datos reales |
| Usabilidad | **No realizada** | Sin sesiones; no se inventan resultados |
| Infografía de una página | **No hecha para D4** | La de Hermes está sin verificar |
| Wiki D4 publicada | **No** | Documentos en curso; deben estar en inglés |

## 7. Errores encontrados (evidencia reproducible)

| # | Error | Evidencia |
|---|---|---|
| E1 | El ZIP de orquestación no tiene migraciones, `healthz`, runbook ni infografía | `D:\OriginPass-D4-orq\auditoria\inventario-zip-orquestacion.json` (primera entrada: `migraciones.total_py_sin_init = 0`, `healthz` vacío, `runbook.total = 0`) |
| E2 | `/healthz/` no existía en `81fbe6d` | `git grep -n healthz 81fbe6d`: sin coincidencias |
| E3 | Los diagramas del repo no se actualizaron | Repo principal: sin cambios en `docs/diagrams/` |
| E4 | El paquete de rescate incluye un runbook de AWS EC2 | `app/docs/deployment/RUNBOOK-EC2.md` en el ZIP de rescate |
| E5 | Configuración de producción incompleta (corregida) | `config/settings.py`: WhiteNoise, `CSRF_TRUSTED_ORIGINS` y `BEHIND_TLS_PROXY` añadidos; `/static/favicon.svg` responde 200 con `DEBUG=False` |
| E6 | Umbral de migraciones equivocado en el generador del kit (20 frente a 18) | `delivery/build_d4_kit.py:45` antes de la corrección. Error de orquestación; corregido |
| E7 | Documentos D4 escritos en español; el curso y el repo piden inglés | `config/settings.py:114-118`. Corregido en los documentos para la Wiki (visión, matriz, analítica, usabilidad, diagramas, backlog, limitaciones, seguimiento, retrospectiva, pitch y README). Este reporte y `PREGUNTAS-REVISION.md` son internos y siguen en español. Pendiente de revisión humana |
| E8 | Credenciales de desarrollo versionadas (no se reproducen) | `docker-compose.yml:8` y `:45`; `.github/workflows/ci.yml:19` y `:30` |
| E9 | El puerto 5432 se publica en todas las interfaces | `docker-compose.yml:10`: `"5432:5432"` |
| E10 | Solo 4 de 81 commits citan un ID de requisito | `git log` |
| E11 | El aviso pide despliegue en AWS; el plan usa Azure | `referencia/aviso-profesor.md:3` |
| E12 | "healthz implementado", "diagramas revisados", "QA verde" y "kit listo" en los informes de Hermes, sin sustento | `hermes-verificacion.md` §1, filas 1, 10, 23 y 11 |
| E13 | El ZIP de rescate (09:34) está desfasado: sus fuentes cambiaron entre 09:46 y 09:51 | `hermes-verificacion.md`, E7 |
| E14 | Cambios de runtime e infografía (02:30–02:42) sin worker que los respalde | `hermes-verificacion.md`, E9 y §6 |
| E15 | El worker de documentación reportó "ninguno" con 24 escrituras registradas y 2 `file_change` fallidos | `hermes-verificacion.md`, E8 |
| E16 | El worker de seguridad AWS falló (`returncode 1`) sin informe final | `hermes-verificacion.md`, E10 |
| E17 | Un worker imprimió valores de desarrollo de `docker-compose.yml` en su transcripción (no reproducidos aquí) | `hermes-verificacion.md`, E13 |
| E18 | Lint rojo en los scripts D4 del rescate: `generar_d4.py` 56 errores, `comprobar_entrega.py` 9, `comprobar_d4.py` 8. El repo base no se ve afectado | `hermes-verificacion.md`, E17 |
| E19 | Infografía del worktree no autocontenida (imagen externa) y con cifras falsas | `hermes-verificacion.md`, E3 y E14 |
| E20 | Worktree `d4/integracion-20261029` creado por la orquestación de hoy sin estar registrado en ningún informe | `hermes-verificacion.md`, E16 |
| E21 | Intentos de comandos denegados por política: `wsl ... -c` y `docker ps` en el worker de kit-final; invocación de Claude en el revisor | `hermes-verificacion.md`, E11 y E12 |

## 8. Preguntas para la revisión

Ver `docs/d4/PREGUNTAS-REVISION.md`:
- A1–A11 para el profesor.
- B1–B6 para Emmanuel Hernández.

## 9. Lo que debe estar listo antes de presentar

| Requisito del enunciado | Estado |
|---|---|
| URL de despliegue accesible, captura y limitaciones (§1.4) | **No** |
| Validación de los cinco elementos del Product Vision Board (§1.1) | **Parcial**: supuestos, sin validación |
| Analítica: datos, información y decisiones (§1.2) | **Parcial**: solo demostración |
| Requisitos iniciales y nuevos con estado, sprint y responsable (§1.3) | **Parcial**: matriz escrita, estado sin ejecutar pruebas |
| UML de despliegue y componentes, y modelo de datos (§2) | **Parcial**: borrador en Mermaid |
| Usabilidad con usuarios potenciales (§3) | **No** |
| README reproducible y repositorio (§4) | **Parcial**: sección añadida; ensayo pendiente |
| Infografía de una página (§5) | **No** |
| Limitaciones, backlog, seguimiento, retrospectiva, pitch y demo (§6–§8) | **Borrador** |
| Wiki de GitHub con la documentación (en inglés) | **No** |

Build del kit: `delivery/build_d4_kit.py` genera `OriginPass-Portatil-D4.zip` y `SHA256SUMS.txt` en `D:\OriginPass-D4-orq\entrega\`. La verificación es de contenido, no de funcionamiento. El ensayo en el portátil no está hecho.

## 10. Orden recomendado a partir de ahora

1. Confirmar Azure con el profesor (A1) y decidir la asesoría sin URL (A3).
2. B2 aplicado y autorizado por el responsable; suite completa en verde (318 pruebas, PostgreSQL 17).
3. Ejecutar la suite completa con PostgreSQL, equivalente al CI, antes de cualquier merge.
4. Ensayar el kit en el portátil con `verificar-kit-d4.py`.
5. Traducir y revisar la documentación al inglés, y publicarla en la Wiki con autorización.
6. Hacer la prueba de usabilidad con usuarios reales. Hoy no existe.
