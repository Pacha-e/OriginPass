# D4-09 Gestión del proyecto: OriginPass (ST0251, Entregable 4)

Fuentes leídas (WIKI = `D:\Universidad\Proyecto integrador 1\OriginPass-wiki`): Daily-Log.md, Retrospectives.md, Sprint-1-Review.md, Sprint-2-Plan.md, Sprint-2-Review.md, Sprint-3-Review.md, Team.md, Activities-and-Homeworks.md, Development-Log.md, Home.md.
Nota de método: la lectura con lean-ctx devolvió solo encabezados (triage), por lo que el contenido se leyó con la herramienta Read nativa. No se leyó ningún PDF, DOCX ni PPTX. No se leyeron Requirements-Specification, Requirements-Prioritisation ni el tablero GitHub; los criterios de aceptación no constan en las páginas leídas.

## A. Backlog

Estado general: Sprint 1 cerrado 11 agosto 2026 (Sprint-1-Review.md:11-13); Sprint 2 cerrado 8 septiembre (Sprint-2-Review.md:13-15); Sprint 3 cerrado 13 octubre y fusionado en `main` vía PR #82 (Sprint-3-Review.md:16-18, 68-70).

| ID | Historia | Criterios de aceptación | Estado | Tareas | Responsable |
|---|---|---|---|---|---|
| FR01, FR02, FR03, FR04, FR05 | Cuenta, correo único, login, error genérico, logout | PENDIENTE: criterios no constan (solo se lee "un test por criterio", Sprint-1-Review.md:38) | Entregado, Sprint 1 (Sprint-1-Review.md:17-21) | Formularios y vistas de `accounts` | Emmanuel Hernández Melo (Team.md:7,16-17) |
| FR07, FR08, FR09, FR10, FR11, FR12, FR13, FR14, FR17 | Solicitud de empresa, revisión, aprobación y rechazo con motivo | PENDIENTE: criterios no constan | Entregado, Sprint 1 (Sprint-1-Review.md:22-30) | `companies` | Emmanuel Hernández Melo |
| UR08, DBR01, DBR11, DBR12 | Causa junto al campo, registro de empresa, contraseñas con hash, motivo obligatorio | PENDIENTE: criterios no constan | Entregado, Sprint 1 (Sprint-1-Review.md:31-34) | Modelo y restricciones | Emmanuel Hernández Melo |
| FR19, FR20, FR21, FR22, FR23 | Registro de producto, rechazo por estado, código de pasaporte, QR PNG, tipo de producto | PENDIENTE: criterios no constan (Sprint-2-Plan.md:22 indica que están en el tablero GitHub, no leído) | Entregado, Sprint 2 (Sprint-2-Review.md:19-23) | `products` | Emmanuel Hernández Melo |
| FR24, FR25, FR26 | Lista de productos, búsqueda, edición sin cambiar el código | PENDIENTE: criterios no constan | Entregado, Sprint 2 (Sprint-2-Review.md:24-26) | `products` | Emmanuel Hernández Melo |
| FR28, FR29, FR30, FR31, UR01, UR02, UR03, UR04, UR06, UR10 | Verificación pública sin sesión, veredictos, UI en español, límites de 3G y 360 px | PENDIENTE: criterios no constan | Entregado, Sprint 2 (Sprint-2-Review.md:27-36) | `verification`, `locale/es` | Emmanuel Hernández Melo |
| DBR02, DBR03, DBR04, DBR10 | Registro de producto, unicidad y clave foránea, índice | PENDIENTE: criterios no constan | Entregado, Sprint 2 (Sprint-2-Review.md:37-40) | Modelo | Emmanuel Hernández Melo |
| FR18, FR32, FR33, FR35, FR36, FR37, FR38, FR39, FR40 | Perfil público, cadena de custodia, registro de escaneos, transferencias | PENDIENTE: criterios no constan | Entregado, Sprint 3 (Sprint-3-Review.md:20-40) | `products`, `verification`, `companies` | Emmanuel Hernández Melo |
| FR46, FR47, FR48, FR49, FR50, FR57, FR58 | Analítica, alerta de duplicado, vista de administrador, límites de login y escaneo | PENDIENTE: criterios no constan | Entregado, Sprint 3 (Sprint-3-Review.md:31-35) | `products`, `accounts`, `verification` | Emmanuel Hernández Melo |
| UR07, UR09, DBR05, DBR06, DBR07, DBR09 | Teclado, contraste, transferencias, escaneos sin borrado automático | PENDIENTE: criterios no constan | Entregado, Sprint 3 (Sprint-3-Review.md:36-39) | Modelo y CSS | Emmanuel Hernández Melo |
| FR06, FR15, FR16, FR41, FR42, FR44, FR51, FR52, FR53, FR54, FR55 | Recuperación de contraseña, suspensión, revocación, auditoría, CSV, correos | PENDIENTE: criterios no constan | Construido antes de lo planeado en Sprint 4 (Sprint-3-Review.md:42-48) | Varios | Emmanuel Hernández Melo |
| FR27 | Registro masivo desde CSV | PENDIENTE: criterios no constan | Pendiente, Sprint 4 (Sprint-3-Review.md:104; Retrospectives.md:111-112) | — | Emmanuel Hernández Melo |
| FR34 | Límite por minuto con mensaje de espera | PENDIENTE: criterios no constan | Pendiente, Sprint 4; cerrado sin construir y reabierto (Development-Log.md:33-34) | — | Emmanuel Hernández Melo |
| FR56 | Publicar la cabeza de la cadena fuera del servidor (objetivo Monad) | PENDIENTE: criterios no constan | Pendiente, Sprint 4 (Sprint-2-Review.md:79; Sprint-3-Review.md:104) | — | Emmanuel Hernández Melo |
| UR05 | Interfaz en inglés | PENDIENTE: criterios no constan | Pendiente, Sprint 4 (Sprint-3-Review.md:106) | — | Emmanuel Hernández Melo |
| Despliegue | Puesta en producción | PENDIENTE: criterios no constan | Pendiente (Retrospectives.md:112; Development-Log.md:43) | — | Emmanuel Hernández Melo |

Total de PENDIENTE en la tabla de backlog: 15 (una por fila).

## B. Reuniones semanales

No existen actas de reunión. El profesor pidió un registro diario individual en lugar de actas (Daily-Log.md:3-4). Las secciones siguientes se toman de Development-Log.md.

| Semana | Qué hice | Qué haré | Obstáculos |
|---|---|---|---|
| S1 (14 jul) | Presentación del curso y definición del equipo (Daily-Log.md:12; Development-Log.md:311) | Sin registro en Development-Log, solo calendario de curso | Sin registro |
| S2 (15-21 jul) | Sin registro (Development-Log.md:303-305) | Sin registro | Sin registro |
| S3 (22-28 jul) | Sin registro (Development-Log.md:297-299) | Sin registro | Sin registro |
| S4 (29 jul-4 ago) | Revisión del prototipo, arquitectura, visión de producto, requisitos, MoSCoW, Entregable 1 (Development-Log.md:276-279) | Registrar requisitos Must en el backlog; entrevistas y encuesta; video; scaffold Django (Development-Log.md:282-288) | Investigación primaria no iniciada; artefactos escritos en lote (Development-Log.md:292-293) |
| S5 (5-11 ago) | Wiki, backlog, app Sprint 1, 80 pruebas, elevator pitch, revisión Sprint 1 (Development-Log.md:250-257) | Entrevistas y encuesta; Sprint 2; CI (Development-Log.md:261-263) | Investigación primaria sin iniciar (Development-Log.md:267) |
| S6 (12-18 ago) | Trazas firmadas, `verify_integrity`, FR56, licencia AGPL-3.0, video (Development-Log.md:232-236) | Iniciar funcionalidades de Sprint 2 (Development-Log.md:240) | Investigación primaria sin iniciar (Development-Log.md:244) |
| S7-S8 (19 ago-1 sep) | Solo un diagrama en la wiki el 27 de agosto; sin commits (Development-Log.md:213-214) | Funcionalidades de Sprint 2 (Development-Log.md:220) | Sin obstáculo externo; tiempo no usado (Development-Log.md:224) |
| S9 (2-8 sep) | Funcionalidades de Sprint 2, pruebas por criterio, diagramas, corrección de plantilla (Development-Log.md:193-196) | Cerrar UR04; reorganizar repositorio (Development-Log.md:200-201) | UR04 sin empezar; sprint cerrado tarde (Development-Log.md:205) |
| S10 (9 sep) | Reorganización, fábricas de pruebas, UR04, corrección de aprobación, 179 pruebas, revisión Sprint 2 (Development-Log.md:169-174) | Mockups y video; exportar diagramas; cerrar 22 issues (Development-Log.md:178-180) | Docker sin funcionar; verificación en un solo punto (Development-Log.md:184); investigación sin iniciar (Development-Log.md:185) |
| S11 (9-10 sep) | Revisión adversarial, siete defectos corregidos, pgAdmin, `describe_schema`, fusión a `main` (Development-Log.md:134-148) | Video de entrega; auditar plantillas y UR01/UR03/UR07/UR09 (Development-Log.md:152-154) | Investigación sin iniciar (Development-Log.md:159) |
| S12-S13 (11-29 sep) | Sin commits ni cambios en la wiki (Development-Log.md:115-117) | Sin registro | Ninguno externo; tiempo no usado (Development-Log.md:124) |
| S14 (30 sep-1 oct) | Funcionalidades de Sprint 3, auditoría, identidad visual, retroalimentación del profesor el 1 de octubre (Development-Log.md:61-95) | Revisión de sprint, retrospectiva, grabar video; cerrar issues; Sprint 4 (Development-Log.md:101-104) | Sin obstáculo técnico; pregunta abierta si el seguimiento del 1 de octubre cuenta como reunión con el Product Owner (Development-Log.md:108-109) |
| S15 (6-15 oct) | Respuesta al Product Owner, CI en rojo corregido, fusión PR #82, kit de presentación, videos (Development-Log.md:15-37) | Revisión de sprint en clase; retrospectiva; Sprint 4; investigación primaria (Development-Log.md:41-44) | Ninguno técnico; falta ensayar el kit en la máquina de clase (Development-Log.md:48-49) |

Reuniones con el Product Owner:
- 1 oct 2026: seguimiento con el profesor, que señaló que una usuaria es la artesana rural; respondido el mismo día (Sprint-3-Review.md:96-97; Development-Log.md:88-95). Estado como reunión de PO: PENDIENTE: confirmación del profesor (Development-Log.md:108-109).
- 15 oct 2026: retroalimentación del Product Owner sobre fotos, variedad de demostración y productores formales e informales; respondida (Sprint-3-Review.md:98-100; Development-Log.md:18-23).
- Sin registro de reuniones de PO con fecha, asistentes ni acta. PENDIENTE: acta de reunión del Product Owner.

## C. Retrospectiva Sprint 3 (Retrospectives.md:73-114)

Sprint 3, 9 sep a 13 oct 2026.

**Continuar**
- Auditar el trabajo contra los requisitos antes de declararlo terminado (Retrospectives.md:81-84).
- Responder la retroalimentación el mismo día (Retrospectives.md:85-86).
- Poner reglas en la base de datos cuando puede sostenerlas, por ejemplo un índice único parcial (Retrospectives.md:87-89).
- Dejar que la integración continua decida la fusión (Retrospectives.md:90-91).

**Empezar**
- Vigilar las ejecuciones de integración en la rama del sprint, no solo en `main` (Retrospectives.md:95-96).
- Revisar cada issue contra el código antes de cerrarlo (Retrospectives.md:97-98).
- Mantener archivos generados fuera del repositorio desde el inicio (Retrospectives.md:99-101).

**Dejar de hacer**
- Dejar el código del sprint para los últimos dos días (Retrospectives.md:105-106).
- Postergar la investigación primaria; cuarto sprint arrastrado (Retrospectives.md:107).

**Arrastrado al siguiente sprint**
- FR56, FR34, FR27, UR05, despliegue (Retrospectives.md:111-112).
- Ejecutar entrevistas y encuesta (Retrospectives.md:113).
- Ensayar el kit de presentación antes de cada revisión (Retrospectives.md:114).

Estado de la actualización: la retrospectiva del Sprint 3 está escrita en la wiki, pero sus puntos se derivan del trabajo y no constan respuestas reales del equipo. Como el equipo es una sola persona (Team.md:9), no hay respuestas de otros miembros. PENDIENTE: respuestas reales del equipo para validar la retrospectiva (una por cada pregunta de Continuar, Empezar y Dejar de hacer).

## Resumen de PENDIENTE
- Tabla A: 15 PENDIENTE (criterios de aceptación, una por fila).
- Sección B: 2 PENDIENTE (confirmación del profesor sobre la reunión del 1 de oct; acta de reunión del PO).
- Sección C: 1 PENDIENTE (respuestas reales del equipo).
Total: 18 PENDIENTE.
