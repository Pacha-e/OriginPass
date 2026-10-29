# Tabla de requisitos funcionales — OriginPass (ST0251, Entregable 4)

**Alcance:** los 58 requisitos funcionales FR01–FR58. Los 10 de usabilidad (UR) y los 12 de base de datos (DBR) quedan fuera de esta tabla.

**Fuentes de planificación:** `WIKI\Requirements-Specification.md` (ID, prioridad, sprint planificado), `WIKI\Deliverable-1.md` §2 (E1 = FR01–FR55), `WIKI\Requirements-Specification.md` (FR56 añadido el 12 de agosto de 2026; FR57 y FR58 añadidos el 10 de septiembre de 2026).

**Método de verificación:** "Sí" se asigna cuando la wiki marca el requisito como entregado y el módulo existe en `origin/main`, comprobado con `git grep` y `git ls-tree` de solo lectura. No se ejecutaron pruebas.

| ID | Requisito | Origen (E1/nuevo) | Sprint | Responsable | Desarrollado (Sí/Parcial/No) | Evidencia (commit/PR/archivo) |
|---|---|---|---|---|---|---|
| FR01 | Crear cuenta con correo y contraseña | E1 | 1 | Emmanuel Hernández Melo | Sí | `origin/main:accounts/forms.py:16` (RegistrationForm) |
| FR02 | Rechazar correo ya registrado con mensaje | E1 | 1 | Emmanuel Hernández Melo | Sí | `origin/main:accounts/forms.py:27` (clean_email) |
| FR03 | Inicio de sesión con correo y contraseña | E1 | 1 | Emmanuel Hernández Melo | Sí | `origin/main:accounts/forms.py:59` (LoginForm) |
| FR04 | Error de autenticación idéntico para correo desconocido y contraseña errónea | E1 | 1 | Emmanuel Hernández Melo | Sí | `origin/main:accounts/forms.py:68` (LoginForm.clean) |
| FR05 | Cierre de sesión | E1 | 1 | Emmanuel Hernández Melo | Sí | `origin/main:accounts/views.py:109` (log_out) |
| FR06 | Enlace de restablecimiento de contraseña por correo | E1 | 4 | Emmanuel Hernández Melo | Sí | `origin/main:accounts/urls.py:19-24` (construido en Sprint 3, `Sprint-3-Review.md`) |
| FR07 | Enviar solicitud de empresa | E1 | 1 | Emmanuel Hernández Melo | Sí | `origin/main:companies/views.py:35` (application_create) |
| FR08 | Código de registro obligatorio para empresa comercial | E1 | 1 | Emmanuel Hernández Melo | Sí | `origin/main:companies/forms.py:21, :85` (CompanyApplicationForm.clean) |
| FR09 | Artesano sin código de registro, marcado para revisión manual (ampliado el 15-oct) | E1 | 1 | Emmanuel Hernández Melo | Sí | `origin/main:companies/forms.py:21, :85`; `Requirements-Specification.md` nota FR09 |
| FR10 | Editar y reenviar mientras esté Pendiente o Rechazada | E1 | 1 | Emmanuel Hernández Melo | Sí | `origin/main:companies/models.py:157` (is_editable), `:285` (resubmit) |
| FR11 | Rechazar edición si está Aprobada o Suspendida, con motivo | E1 | 1 | Emmanuel Hernández Melo | Sí | `origin/main:companies/models.py:170` (edit_refusal_reason) |
| FR12 | Listar solicitudes filtradas por estado (administrador) | E1 | 1 | Emmanuel Hernández Melo | Sí | `origin/main:companies/views.py:106` (review_list) |
| FR13 | Aprobar solicitud pendiente | E1 | 1 | Emmanuel Hernández Melo | Sí | `origin/main:companies/models.py:247` (approve), `companies/views.py:144` (review_approve) |
| FR14 | Rechazar solicitud con motivo escrito | E1 | 1 | Emmanuel Hernández Melo | Sí | `origin/main:companies/models.py:256` (reject), `companies/forms.py:142` (RejectionForm), `companies/views.py:165` |
| FR15 | Suspender empresa aprobada con motivo | E1 | 4 | Emmanuel Hernández Melo | Sí | `origin/main:companies/views.py:191` (suspend_company) (construido en Sprint 3) |
| FR16 | Reactivar empresa suspendida | E1 | 4 | Emmanuel Hernández Melo | Sí | `origin/main:companies/views.py:213` (reactivate_company) (construido en Sprint 3) |
| FR17 | Mostrar al dueño el estado y el motivo guardado | E1 | 1 | Emmanuel Hernández Melo | Sí | `origin/main:companies/views.py:26` (application_detail) |
| FR18 | Perfil público de empresa aprobada (ampliado el 15-oct) | E1 | 3 | Emmanuel Hernández Melo | Sí | `origin/main:companies/views.py:228` (public_profile) |
| FR19 | Empresa aprobada registra producto | E1 | 2 | Emmanuel Hernández Melo | Sí | `origin/main:products/views.py:116` (product_create) |
| FR20 | Rechazar registro de empresa no aprobada, con motivo | E1 | 2 | Emmanuel Hernández Melo | Sí | `origin/main:products/views.py:47` (REFUSAL_BY_STATUS), `:126` |
| FR21 | Código de pasaporte único y no derivable | E1 | 2 | Emmanuel Hernández Melo | Sí | `origin/main:products/models.py:51` (generate_passport_code) |
| FR22 | Imagen QR descargable en PNG | E1 | 2 | Emmanuel Hernández Melo | Sí | `origin/main:products/views.py:236` (qr_download) |
| FR23 | Tipo de producto acorde al tipo de empresa | E1 | 2 | Emmanuel Hernández Melo | Sí | `origin/main:products/models.py:45` (PRODUCT_TYPE_BY_COMPANY_TYPE), `:136` (Product.clean) |
| FR24 | Listar productos propios filtrados por estado | E1 | 2 | Emmanuel Hernández Melo | Sí | `origin/main:products/views.py:79` (product_list) |
| FR25 | Buscar productos por nombre, categoría o código | E1 | 2 | Emmanuel Hernández Melo | Sí | `origin/main:products/views.py:79` (product_list) |
| FR26 | Editar campos descriptivos sin cambiar el código | E1 | 2 | Emmanuel Hernández Melo | Sí | `origin/main:products/views.py:190` (product_edit), `products/forms.py:21` (ProductForm) |
| FR27 | Registro masivo de productos desde CSV | E1 | 4 | Emmanuel Hernández Melo | No | Sin importación CSV en `origin/main`; solo exportación en `products/views.py:498` (company_analytics_csv). `Sprint-3-Review.md` lo marca como no hecho |
| FR28 | Verificación pública sin cuenta | E1 | 2 | Emmanuel Hernández Melo | Sí | `origin/main:verification/views.py:106` (verify) |
| FR29 | Veredicto Genuino con datos de producto y empresa | E1 | 2 | Emmanuel Hernández Melo | Sí | `origin/main:verification/views.py:106` (verify), `verification/models.py:21` (Verdict) |
| FR30 | Veredicto Anulado con fecha de anulación | E1 | 2 | Emmanuel Hernández Melo | Sí | `origin/main:verification/views.py:106`, `verification/models.py:21` |
| FR31 | Veredicto No encontrado con mensaje uniforme | E1 | 2 | Emmanuel Hernández Melo | Sí | `origin/main:verification/views.py:106` |
| FR32 | Trayectoria del producto en orden cronológico | E1 | 3 | Emmanuel Hernández Melo | Sí | `origin/main:verification/views.py:185` (_public_chain) |
| FR33 | Registrar cada escaneo con región y categoría de dispositivo | E1 | 3 | Emmanuel Hernández Melo | Sí | `origin/main:verification/views.py:67` (_region_for), `:45` (_device_category); `verification/models.py:27` (ScanEvent) |
| FR34 | Límite por minuto con mensaje de espera | E1 | 4 | Emmanuel Hernández Melo | No | Sin coincidencias de límite por minuto ni de mensaje de espera en `origin/main` (`git grep`). FR58 no lo sustituye (`verification/views.py:88`). Reabierto el 15-oct (`Sprint-3-Review.md` §5.1, `Development-Log.md` semana 15) |
| FR35 | El titular actual ofrece la custodia a otra cuenta | E1 | 3 | Emmanuel Hernández Melo | Sí | `origin/main:products/views.py:284` (transfer_initiate), `products/forms.py:71` (TransferInitiateForm) |
| FR36 | El receptor acepta o rechaza la transferencia | E1 | 3 | Emmanuel Hernández Melo | Sí | `origin/main:products/views.py:343` (transfer_respond) |
| FR37 | Transferencia aceptada se añade a la cadena firmada | E1 | 3 | Emmanuel Hernández Melo | Sí | `origin/main:products/models.py:223` (CustodyTransfer) |
| FR38 | Rechazar oferta de cuenta que no tiene el producto | E1 | 3 | Emmanuel Hernández Melo | Sí | `origin/main:products/forms.py:112` (TransferInitiateForm.clean), `products/models.py:61` (held_by) |
| FR39 | Rechazar transferencias de producto anulado | E1 | 3 | Emmanuel Hernández Melo | Sí | `origin/main:products/models.py:344` (CustodyTransfer.clean) |
| FR40 | Reclamar propiedad con código de pasaporte y código de entrega | E1 | 3 | Emmanuel Hernández Melo | Sí | `origin/main:products/views.py:380` (transfer_claim), `products/forms.py:130` (TransferClaimForm) |
| FR41 | La empresa registradora anula su producto con motivo | E1 | 4 | Emmanuel Hernández Melo | Sí | `origin/main:products/views.py:546` (product_revoke) (construido en Sprint 3) |
| FR42 | El administrador anula cualquier producto con motivo | E1 | 4 | Emmanuel Hernández Melo | Sí | `origin/main:products/views.py:576` (admin_revoke_product) (construido en Sprint 3) |
| FR43 | Entrada de auditoría por cada cambio de estado | E1 | 4 | Emmanuel Hernández Melo | Sí | `origin/main:audit/models.py:35` (AuditEntry); firmada y encadenada desde el 12-ago (`Sprint-3-Review.md`) |
| FR44 | Consultar bitácora filtrada por actor, acción o fechas | E1 | 4 | Emmanuel Hernández Melo | Sí | `origin/main:audit/views.py:23` (audit_log), `audit/forms.py:10-22` (actor, action, since, until) |
| FR45 | Conservar cada entrada de auditoría durante el periodo de retención definido | E1 | 4 | Emmanuel Hernández Melo | Parcial | Inmutabilidad firmada en `origin/main:audit/integrity.py` y `audit/models.py`. El periodo de retención no aparece en el código (`git grep -i retention` solo devuelve `docs/wiki/Requirements-Specification.md`). PENDIENTE: periodo de retención definido para el sistema |
| FR46 | Número de escaneos por rango de fechas | E1 | 3 | Emmanuel Hernández Melo | Sí | `origin/main:products/views.py:417` (company_analytics) |
| FR47 | Distribución de escaneos por región | E1 | 3 | Emmanuel Hernández Melo | Sí | `origin/main:products/views.py:417` (company_analytics) |
| FR48 | Productos ordenados por número de escaneos | E1 | 3 | Emmanuel Hernández Melo | Sí | `origin/main:products/views.py:417` (company_analytics) |
| FR49 | Alerta de escaneo duplicado por código en regiones distintas | E1 | 3 | Emmanuel Hernández Melo | Sí | `origin/main:products/models.py:396` (Alert); `verification/views.py` (alerta, `Sprint-3-Review.md`) |
| FR50 | Totales de empresas y productos por estado (administrador) | E1 | 3 | Emmanuel Hernández Melo | Sí | `origin/main:products/views.py:607` (admin_overview) |
| FR51 | Exportar analítica del rango seleccionado en CSV | E1 | 4 | Emmanuel Hernández Melo | Sí | `origin/main:products/views.py:498` (company_analytics_csv) (construido en Sprint 3) |
| FR52 | Tendencia frente al periodo anterior de igual duración | E1 | 4 | Emmanuel Hernández Melo | Sí | `origin/main:products/views.py:417` (previous_total, líneas 431–477) (construido en Sprint 3) |
| FR53 | Correo al solicitante con la decisión y el motivo | E1 | 4 | Emmanuel Hernández Melo | Sí | `origin/main:accounts/emails.py:35` (notify_company_decision) (construido en Sprint 3) |
| FR54 | Correo al receptor de una transferencia | E1 | 4 | Emmanuel Hernández Melo | Sí | `origin/main:accounts/emails.py:55` (notify_transfer) (construido en Sprint 3) |
| FR55 | Correo al titular tras una anulación | E1 | 4 | Emmanuel Hernández Melo | Sí | `origin/main:accounts/emails.py:68` (notify_revocation) (construido en Sprint 3) |
| FR56 | Publicar la cabeza de la cadena fuera del control del operador | nuevo (12-ago-2026) | 4 | Emmanuel Hernández Melo | No | Sin publicación externa en `origin/main`. `audit/integrity.py` (docstring) y `audit/management/commands/verify_integrity.py:102` describen el anclaje como pendiente. `Sprint-3-Review.md` §5.1 lo marca como abierto |
| FR57 | Bloqueo tras 5 fallos en 15 minutos por correo | nuevo (10-sep-2026) | 3 | Emmanuel Hernández Melo | Sí | `origin/main:accounts/models.py:71` (LoginAttempt) |
| FR58 | Máximo 60 escaneos registrados por dirección por hora | nuevo (10-sep-2026) | 3 | Emmanuel Hernández Melo | Sí | `origin/main:verification/views.py:88` (_under_scan_cap) |

## Conteo final

| Concepto | Número |
|---|---|
| Total de filas | 58 |
| Sí | 54 |
| Parcial | 1 (FR45) |
| No | 3 (FR27, FR34, FR56) |

Conteo comprobado: 54 + 1 + 3 = 58.

## Notas

- **Responsable:** el equipo tiene una sola persona, Emmanuel Hernández Melo, con los roles de Scrum Master, Product Owner y desarrollador (`WIKI\Team.md`).
- **FR45 como Parcial:** la wiki no declara como cumplido el periodo de retención y el código no lo define. Es un criterio de este informe, no una afirmación de la wiki.
- **Sprint:** la columna indica el sprint planificado según `Requirements-Specification.md`. Cuando un requisito se entregó en un sprint anterior, la evidencia lo indica entre paréntesis.
- **Commits y PR:** la wiki cita el PR #82 (fusión de Sprint 3 en `main`) y los commits `cca4dbb`, `6f8396d`, `c60f7ff`, `1d6aa5e` y `ac2da6d` en `Development-Log.md`. No asocian commits a requisitos individuales, así que la evidencia por requisito es el archivo y la función en `origin/main`.
- **Discrepancia de conteo:** `Deliverable-1.md` §2 habla de FR01–FR55 (55 requisitos). `Requirements-Specification.md` tiene 58 FR desde el 10-sep-2026. La diferencia son FR56–FR58, marcados como nuevos.
- **Prioridades:** `Requirements-Prioritisation.md` menciona 39 requisitos Must. El resumen de `Requirements-Specification.md` indica 41. Según la propia wiki, la diferencia son FR56 y FR57, añadidos después de la priorización.
- **Estado de FR34:** `Sprint-3-Review.md` y `Deliverable-3.md` coinciden en que FR34 no existe. Ambos documentos indican que el mismo requisito se cerró por error el 6 de octubre y se reabrió el 15 de octubre.
- **Fuera de alcance de esta verificación:** no se ejecutaron pruebas ni se inspeccionaron los commits individuales. No se abrieron los archivos `.env`, `openAI.env` ni `*.sqlite3`, ni los PDF, DOCX o PPTX.

## PENDIENTE

1. PENDIENTE: periodo de retención definido para el sistema (FR45). No consta en la wiki ni en `origin/main`.
