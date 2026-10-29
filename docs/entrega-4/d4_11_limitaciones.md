# D4-11: Limitaciones y trabajo futuro (OriginPass, ST0251 Entregable 4)

Código: `origin/main` del repositorio `OriginPass/OriginPass` (commit `81fbe6d` según d4_04), leído con `git show` y `git grep`. Solo lectura.
Marca **[V]**: línea verificada en `origin/main` en esta corrida. Sin marca: cita tomada de d4_03, d4_04 o d4_09 y ya documentada allí.
Prioridad: **Alta** = bloquea la promesa del producto o la entrega; **Media** = afecta uso real o calidad; **Baja** = mejora o consistencia documental.

## A. Limitaciones técnicas

| # | Limitación | Evidencia | Prioridad | Justificación |
|---|---|---|---|---|
| A1 | La cadena de integridad se firma con una clave derivada de `SECRET_KEY`, que posee el mismo servidor. Quien administra el servidor puede reconstruir la cadena. No hay publicación externa de la cabeza. | `audit/integrity.py:41-48` [V] (`sign` deriva la clave de `settings.SECRET_KEY`); `audit/integrity.py:20-23` [V] (anclaje "not implemented here"); `audit/management/commands/verify_integrity.py:102` [V] | Alta | Límite central de autenticidad: la cadena prueba consistencia interna, no origen. |
| A2 | El tope de 60 escaneos por hora se aplica por `REMOTE_ADDR`. Detrás de un proxy o CDN, todos los escaneos comparten IP y el tope se agota (inferencia, no probada). El contador usa la caché por defecto: `config/settings.py` no define `CACHES` [V], por lo que sería memoria local por proceso y no compartida entre workers (inferencia de la configuración por defecto de Django). Los escaneos sobre el tope no se registran; el veredicto sí se responde. | `verification/views.py:42` [V]; `verification/views.py:57-58` [V]; `verification/views.py:88-103` [V]; `verification/views.py:118` [V]; `config/settings.py` sin `CACHES` [V] | Media | Subconteo en la analítica (FR46 a FR48) y límite que cambia según el despliegue. |
| A3 | Despliegue no verificado. `requirements.txt` no incluye servidor WSGI [V]; el único arranque documentado es `runserver` (`docs/diagrams/deployment-model.drawio:157`, según d4_04); `ci.yml` solo prueba y hace lint (según d4_04). PENDIENTE: URL pública, IP o dominio, y servidor real (d4_04 P1, P2, P5). | `requirements.txt:1-6` [V]; `config/wsgi.py:7` (según d4_04); `docs/diagrams/deployment-model.drawio:47,157`; `.github/workflows/ci.yml` (según d4_04) | Alta | Sin URL verificada no hay evidencia de producción para la wiki. |
| A4 | Estáticos y transporte apagados por defecto. `STATIC_ROOT` apunta a `staticfiles/` [V] sin servidor de estáticos (no hay whitenoise en `requirements.txt` [V]); `config/urls.py:20-21` [V] sirve MEDIA solo con `DEBUG`; `SECURE_SSL_REDIRECT`, cookies seguras y HSTS apagados por defecto [V]. Que Django no sirva estáticos con DEBUG apagado es comportamiento documentado de Django (inferencia; d4_04 P9). | `config/settings.py:131` [V]; `config/urls.py:20-21` [V]; `config/settings.py:157-160` [V] | Media | Un despliegue sin variables explícitas puede servir sin HTTPS ni estáticos. |
| A5 | Correo a consola por defecto. Sin `EMAIL_BACKEND` en el servidor, los correos de FR53 a FR55 no salen del sistema. | `config/settings.py:143` [V] | Baja | Afecta solo a producción; en desarrollo es el comportamiento esperado. |
| A6 | Credenciales de base de datos por defecto versionadas en el compose, con PostgreSQL publicado en todas las interfaces. | `docker-compose.yml:6-8` [V] (credenciales omitidas aquí); `docker-compose.yml:9-10` [V]; d4_04 riesgo 4 | Media | Si el puerto 5432 queda accesible en el servidor, la base queda expuesta con credenciales conocidas. |

## B. Limitaciones funcionales (requisitos No o Parcial en d4_03)

| ID | Estado | Requisito | Motivo | Evidencia |
|---|---|---|---|---|
| FR27 | No | Registro masivo de productos desde CSV | Solo existe exportación CSV de analítica (FR51). No hay importador. | `products/urls.py:14` [V]; `products/views.py:498` (`company_analytics_csv`, según d4_03) |
| FR34 | No | Límite de intentos por minuto con mensaje de espera | No hay límite por minuto. El único bloqueo es FR57 (5 fallos en 15 min) y FR58 es un tope horario, no el mismo requisito. | `accounts/models.py:74,81-82` [V]; `accounts/views.py:65-66` [V]; `verification/views.py:42` [V]; d4_03 fila FR34 |
| FR45 | Parcial | Conservar cada entrada de auditoría sin cambios durante el periodo de retención | Inmutabilidad presente (`on_delete=PROTECT`, sin borrado en admin, según d4_03). Falta el periodo de retención, que el requisito exige definir y no existe en código ni en settings. PENDIENTE: periodo de retención del sistema (ver C4). | `docs/wiki/Requirements-Specification.md:88` [V]; búsqueda `retention`/`retención` en `origin/main` sin definición [V]; `audit/admin.py` y `audit/models.py` (según d4_03) |
| FR56 | No | Publicar la cabeza de la cadena fuera del control del operador | Solo está documentado. No hay publicación externa. | `audit/integrity.py:20-23` [V]; `audit/management/commands/verify_integrity.py:102` [V] |

## C. Trabajo futuro

### C.1 Funcionalidades pendientes

| # | Ítem | Evidencia | Prioridad | Justificación |
|---|---|---|---|---|
| C1 | FR56: anclar la cabeza de la cadena en un servicio externo (meta declarada: Monad) | `audit/integrity.py:20-23` [V]; `tools/presentation/deck_content.py:401` [V] | Alta | Cierra A1; sin esto la autenticidad depende del operador. |
| C2 | FR27: importador CSV para registro masivo | `products/urls.py:14` [V]; d4_03 | Media | Permite cargar catálogos grandes; no bloquea el flujo principal. |
| C3 | FR34: límite por minuto con mensaje de espera | d4_03 fila FR34; ver B | Media | Requisito abierto según d4_03; FR58 no lo cubre. |
| C4 | FR45: definir el periodo de retención de auditoría y su aplicación. PENDIENTE: plazo de retención y acción al vencer. | `docs/wiki/Requirements-Specification.md:88` [V]; d4_03 nota 3 | Media | Sin plazo no hay purga ni prueba de cumplimiento. |
| C5 | UR05: selector de idioma e interfaz en inglés | `config/settings.py:59` [V] (`LocaleMiddleware` activo); d4_03 nota 6; `Sprint-3-Review.md:105` (según d4_09) | Baja | El middleware existe; falta el selector y la traducción. |

### C.2 Pendientes de seguridad de WORKER-RESULT (verificados en código; vigentes)

| # | Ítem | Evidencia | Prioridad | Justificación |
|---|---|---|---|---|
| C6 | Un producto de empresa SUSPENDED se muestra como Genuine. `verify` solo consulta `product.status` y no el estado de la empresa. Decisión de diseño pendiente de ratificar. | `verification/views.py:108-115` [V]; `OriginPass-WORKER-RESULT.md:87-89` [V] | Alta | Un producto de una empresa suspendida sigue validando como auténtico. |
| C7 | Sin tope de tamaño de subidas. No hay `FILE_UPLOAD_MAX_MEMORY_SIZE` ni `DATA_UPLOAD_MAX_MEMORY_SIZE`. | `config/settings.py` sin ambas variables [V]; campos de subida `products/models.py:95` [V] y `companies/models.py:92` [V]; `OriginPass-WORKER-RESULT.md:87-89` [V] | Media | Riesgo de agotamiento de disco; mitigado porque solo suben cuentas autenticadas. |
| C8 | `TRUST_GEO_HEADERS` vale True cuando DEBUG está activo. Las cabeceras de ubicación se pueden falsificar. | `config/settings.py:151` [V]; `OriginPass-WORKER-RESULT.md:87-89` [V] | Media | Riesgo solo si DEBUG llega a producción (d4_04 riesgo 5). |
| C9 | Despliegue real: servidor WSGI, proxy inverso, TLS y pipeline. PENDIENTE: URL pública, servidor real, certificado y confirmación de pipeline fuera del repo (d4_04 P1 a P5, P13, P14). | `Development-Log.md:43` (según d4_09); d4_04 §(c) pasos 7 a 9 | Alta | Sprint 4 lo deja abierto y la wiki no tiene evidencia de despliegue. |
| C10 | Licencias CC BY-SA de 5 fotos del video, modificadas. Hay que publicar con atribución CC BY-SA 4.0 o reemplazarlas. | `OriginPass-AUDIT.md` §1.5 [V]; `OriginPass-WORKER-RESULT.md:90-91` [V] | Media | Obligación de licencia antes de difundir el video. |

### C.3 Otros pendientes documentados

| # | Ítem | Evidencia | Prioridad | Justificación |
|---|---|---|---|---|
| C11 | Re-render de voz y master D3 con líneas antiguas, y QA integral de audio y sincronía. PENDIENTE: confirmar si se hizo después del 14 de octubre. La frase «la base de datos lo exige» no aparece en `tools/` de `origin/main` [V]. | `OriginPass-WORKER-RESULT.md:76-79` [V] | Baja | Puede estar resuelto en el repo; falta confirmar el master publicado. |
| C12 | Rúbrica formal de Entrega 3 no localizada en el material local. PENDIENTE: rúbrica oficial en EAFIT Interactiva. | `OriginPass-WORKER-RESULT.md:80-82` [V] | Media | La duración y contenido del video dependen de una cifra no oficial. |
| C13 | `docs/GUIA-DEMO.md` cita 293 tests; el worker reportó 312 el 14 de octubre. PENDIENTE: conteo actual de la suite. | `docs/GUIA-DEMO.md:47,93` [V]; `OriginPass-WORKER-RESULT.md:83-84` [V] | Baja | Consistencia documental; no afecta el código. |
| C14 | Wiki remota sin alinear con el copy nuevo (Domain Model y página Deliverable-3). | `OriginPass-WORKER-RESULT.md:85-86` [V] | Baja | Consistencia documental entre wiki local y remota. |

---

Total de ítems: 24 (A: 6, B: 4, C: 14). PENDIENTE abiertos en esta sección: 7 (A3, B FR45, C4, C9, C11, C12, C13).
