No hay sesiones de prueba de usabilidad con usuarios documentadas en WIKI ni en REPO (origin/main), y tampoco hay evaluación heurística de Nielsen. La evidencia disponible son autoensayos del equipo, pruebas automatizadas y declaraciones de diseño.

Fuentes: WIKI = `D:\Universidad\Proyecto integrador 1\OriginPass-wiki`; REPO = `origin/main` de `D:\Universidad\Proyecto integrador 1\OriginPass\OriginPass`. Rutas de archivo relativas a WIKI o REPO según corresponda. Equipo unipersonal: Emmanuel Hernández Melo ocupa los tres roles (WIKI `Team.md`, citado en D4 `d4_03_requisitos.md:15`).

Escala de severidad: Alta / Media / Baja (la escala Nielsen 1-4 no aplica porque no hay evaluación heurística).

## Problemas de usabilidad y su tratamiento

| Problema | Fuente (quién/cuándo/archivo:línea) | Severidad | Mejora implementada | Estado |
|---|---|---|---|---|
| Interfaz servida en inglés en un equipo limpio: fallaron 21 pruebas y el catálogo de traducción no estaba versionado (afecta UR04, Must) | Emmanuel Hernández Melo, autoensayo, semana 11 (9 y 10 sep 2026). WIKI `Development-Log.md:145` | Alta | Catálogo `locale/es/LC_MESSAGES/django.po` y `django.mo` versionados (REPO `locale/es/LC_MESSAGES/`); prueba `pages/tests/test_language.py:108`. PENDIENTE: hash del commit que versiona el catálogo | Resuelto según la wiki |
| Video de demostración con narración en español pero interfaz en inglés | Entregable 1 (sin fecha en la línea citada). WIKI `Deliverable-1-Video.md:152` | Media | UR04 entregado en Sprint 2 (WIKI `Daily-Log.md:19`; commits `ae46b12`, `4d5fbd5`, `d3c1449`, `7b5a827`). PENDIENTE: confirmación de que el video se regrabó | Resuelto en el producto; video PENDIENTE de confirmar |
| Doble envío del formulario de solicitud de empresa devolvía error de servidor | Emmanuel Hernández Melo, auto-revisión adversarial, semana 11 (9 y 10 sep 2026). WIKI `Development-Log.md:140` | Media | Commit `93d2557` ("Answer a double-submitted application instead of failing on it"); prueba `companies/tests/test_application_submission.py:52` | Resuelto |
| Accesibilidad y diseño responsive (UR01, UR03, UR07, UR09) no comprobados en navegador | Emmanuel Hernández Melo, semana 15 (6 al 15 oct 2026). WIKI `Development-Log.md:154` | Media | Parcial. UR01: prueba estática de anchos fijos en píxeles (`verification/tests/test_layout.py:35`), no un render. UR07: foco visible (REPO `static/css/originpass.css:151-153`), sin prueba. UR09: contraste declarado en REPO `static/css/originpass.css:16`, sin prueba ni medición. PENDIENTE: verificación en navegador de UR01, UR03, UR07 y UR09 | Abierto (parcial) |
| Sin evidencia de cómo perciben el producto compradores y productores (supuestos A1, A2 y A4 en estado Pending) | WIKI `Problem-Validation.md:113,114,116`; `Sprint-1-Review.md:61`; `Sprint-2-Review.md:81`; `Sprint-3-Review.md:108`; `Development-Log.md:159`; `Retrospectives.md:36` | Alta | PENDIENTE: entrevistas a productores y encuesta a compradores (la wiki dice que no han comenzado) | Abierto |
| Cambio de idioma a inglés (UR05) sin selector en la interfaz | WIKI `Sprint-3-Review.md:105`; `Deliverable-3.md:257` (Open). REPO `config/settings.py:59` registra `LocaleMiddleware`, sin selector de idioma en la interfaz | Baja (requisito Could) | PENDIENTE: selector de idioma y su prueba | Abierto |

## (a) Estado de UR01 a UR10

La tabla de D4 (`C:\Users\Acer Nitro\.claude\orquesta-2026-10-28\d4\d4_03_requisitos.md:3`) excluye UR01 a UR10, así que su estado sale de la wiki y del REPO. Prioridad y sprint según WIKI `Requirements-Specification.md:137-146`.

| ID | Requisito (resumen) | Prioridad / sprint | Estado según wiki | Evidencia en REPO | Estado verificado |
|---|---|---|---|---|---|
| UR01 | Resultado de verificación en pantalla de 360 px sin desplazamiento lateral | Must / 2 | Hecho (`Sprint-2-Review.md:31`) | Prueba estática `verification/tests/test_layout.py:35`; regla `static/css/originpass.css:19` | Parcial. PENDIENTE: render en pantalla de 360 px |
| UR02 | Verificación en como máximo dos interacciones desde el escaneo | Must / 2 | Hecho (`Sprint-2-Review.md:32`) | `verification/tests/test_verdicts.py:54` | Hecho en prueba |
| UR03 | Veredicto con etiqueta de texto además del color | Must / 2 | Hecho (`Sprint-2-Review.md:33`) | `verification/templates/verification/verdict.html:13,23-26` | Hecho en código. PENDIENTE: comprobación con usuario o navegador |
| UR04 | Interfaz en español por defecto | Must / 2 | Hecho (`Development-Log.md:171`; `Daily-Log.md:19`) | `locale/es/LC_MESSAGES/django.po`; `pages/tests/test_language.py:108` | Hecho en prueba |
| UR05 | Cambio de idioma a inglés en menos de 2 s | Could / 4 | Abierto (`Sprint-3-Review.md:105`; `Deliverable-3.md:257`) | Sin selector en REPO (`config/settings.py:59` solo activa el middleware) | Abierto |
| UR06 | Página de verificación en menos de 3 s sobre 3G | Must / 2 | Hecho según la wiki (`Sprint-2-Review.md:35`); la prueba afirma el límite, sin medición registrada | `verification/tests/test_verdicts.py:85`. PENDIENTE: registro de la medición sobre 3G con herramienta y ajustes (`Sprint-2-Plan.md:60` lo pide) | Parcial |
| UR07 | Alcanzar cada control de formulario con la tecla Tab | Should / 3 | Hecho (`Deliverable-3.md:249`; `Sprint-3-Review.md:36`) | Controles nativos y `:focus-visible` en `static/css/originpass.css:151-153,489-493`; sin prueba | Parcial. PENDIENTE: prueba de teclado en navegador |
| UR08 | Causa del rechazo junto al campo | Must / 1 | Hecho (`Sprint-1-Review.md:31`) | `accounts/tests/test_registration.py:70`; `companies/tests/test_application_submission.py:89` | Hecho en prueba |
| UR09 | Contraste mínimo de 4.5 a 1 en cada página | Should / 3 | Hecho (`Deliverable-3.md:130,249`; `Sprint-3-Review.md:37`) | Declarado en `static/css/originpass.css:16`; sin prueba. PENDIENTE: medición de contraste con herramienta | Declarado, no medido |
| UR10 | Registro de producto con como máximo cinco campos obligatorios | Should / 2 | Hecho (`Sprint-2-Review.md:36`) | `products/tests/test_registration.py:70` | Hecho en prueba |

Resumen: 6 hechos en prueba o código (UR02, UR04, UR08, UR10, y UR01 y UR06 con reservas), 2 declarados sin medición (UR07 y UR09), 1 abierto (UR05), y UR03 hecho en código sin comprobación con usuario.

## (b) Plan de prueba de usabilidad (PROPUESTA, no ejecutada)

Esta sección es una propuesta del autor del documento y no tiene respaldo en sesiones realizadas.

- Participantes (propuesta): 5 compradores que usen smartphone con pantalla de unos 360 px, sin experiencia previa con OriginPass; 2 dueños de empresa de artesanía o manufactura pequeña para el flujo de registro. Reclutamiento por los canales de la wiki (`Primary-Research-Plan.md`). PENDIENTE: consentimiento informado y tamaño de muestra definitivo.
- Tareas (propuesta), en orden:
  1. T1 (comprador): escanear un código de prueba y decir si el producto es auténtico (UR02, UR03).
  2. T2 (comprador): explicar qué significa un veredicto "Revocado" y uno "No encontrado" sin ayuda (UR03).
  3. T3 (dueño de empresa): registrar un producto con los cinco campos obligatorios y corregir un campo rechazado (UR08, UR10).
  4. T4 (usuario de teclado): completar el formulario de solicitud solo con Tab (UR07).
  5. T5 (cualquiera): cambiar la interfaz a inglés (UR05). Solo si el selector existe.
- Métricas (propuesta): tasa de éxito por tarea; tiempo hasta completar cada tarea; número de interacciones (UR02 exige dos o menos); número de errores y de intentos de corrección; puntaje SUS con su cuestionario de diez ítems; severidad de cada problema observado en escala Alta/Media/Baja. Complementaria: evaluación heurística de Nielsen por dos evaluadores sobre las pantallas de verificación y registro, con escala 0 a 4 de Nielsen. PENDIENTE: fecha y lugar de las sesiones.
- Medición técnica complementaria (propuesta): registrar el tiempo de carga de la verificación sobre 3G (UR06) y el contraste de cada par de color (UR09) con una herramienta de medición. PENDIENTE: herramienta elegida y ajustes de red.

Archivos modificados en esta tarea: solo `C:\Users\Acer Nitro\.claude\orquesta-2026-10-28\d4\d4_10_usabilidad.md` (nuevo).
