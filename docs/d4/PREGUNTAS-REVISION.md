# Preguntas para la revisión: Entregable 4 de OriginPass

Estado a 29-oct-2026. Cada pregunta indica su fuente y la decisión por defecto si no hay respuesta. Ninguna respuesta está dada todavía.

## A. Para el profesor

| # | Pregunta | Fuente | Por defecto si no hay respuesta |
|---|---|---|---|
| A1 | ¿Es válido el despliegue en AWS EC2 (Learner Lab)? | `referencia/aviso-profesor.md:3` pide "desplegada en AWS". | Sí. Se usa AWS EC2 (Learner Lab), como pide el profesor. Azure se retiró. |
| A2 | El enunciado pide **reuniones semanales registradas** (3 respuestas por estudiante y semana). ¿Aplica a D4 la **bitácora** que se aceptó en D3? | Enunciado §7.2. La bitácora no aparece en ningún archivo fuente. | Se presenta bitácora y se pide confirmación. |
| A3 | ¿Se necesita una demo local con capturas si no hay URL pública? | Enunciado §1.4 permite "motivos y evidencia alternativa". | No aplica: hay URL pública (https://44-206-186-9.sslip.io). La demo local queda como respaldo. |
| A4 | ¿La **Wiki de D4** debe estar en **inglés**? | `config/settings.py:114-118` dice que el curso pide artefactos en inglés. D3 se reescribió en inglés. | Inglés. Los documentos en español de `docs/d4/` se traducirán antes de publicar. |
| A5 | ¿Cuáles son los **criterios de evaluación**, los pesos y la fecha de entrega final? | No aparecen en el enunciado ni en el aviso. | No hay criterios: se entrega según el enunciado. |
| A6 | ¿Cuántos **participantes** mínimos y qué perfil se aceptan para la prueba de usabilidad (§3)? | Enunciado §3: actividades y tabla de severidad High/Medium/Low. | No se ha hecho ninguna sesión. No se inventan resultados. |
| A7 | ¿Los requisitos "del Entregable 1" (§1.3) son los **FR/UR/DBR** de la especificación de la Wiki? ¿Qué cuenta como "Yes" en la columna de componentes (§2.2)? | Enunciado §1.3 y §2.2. | Sí, con FR27, FR34 y FR56 abiertos al 15-oct. |
| A8 | En un **proyecto individual**, ¿cómo se cumplen los requisitos que hablan de "todos los integrantes": commits (§4) y pitch y demo por integrante (§8)? | Enunciado §4 y §8. | Se presenta solo el trabajo de Emmanuel Hernández. |
| A9 | ¿Hace falta **reescribir el historial** para que los commits citen su requisito, o basta con citarlo desde ahora? | Enunciado §4. Solo 4 de 81 commits citan un ID. | Desde ahora, sin reescribir. |
| A10 | ¿Basta el **modelo de datos relacional** de Django (diagrama ER generado desde los modelos) o piden otra notación? | Enunciado §2.3: el modelo relacional normalizado es sugerencia. | Modelo relacional de Django. |
| A11 | ¿La **Sprint Review** (§8) se presenta con la aplicación desplegada o puede ser local? | Enunciado §8: "demo de la app desplegada". | Se presenta con la aplicación desplegada en AWS; la demo local es el respaldo. |

## B. Para Emmanuel Hernández (decisiones internas)

| # | Decisión | Estado |
|---|---|---|
| B1 | Desplegar en AWS EC2 (Learner Lab). | Hecho el 5 de noviembre de 2026. Las actualizaciones usan `deploy/aws/actualizar-ec2.sh`. |
| B2 | Autorizar los cambios de producción en `config/settings.py`: WhiteNoise para estáticos, `CSRF_TRUSTED_ORIGINS` y `SECURE_PROXY_SSL_HEADER`. Requieren la suite completa con PostgreSQL. | Pendiente. Sin autorización no se toca. |
| B3 | Credenciales de desarrollo versionadas: `docker-compose.yml:8` y `:45`, `.github/workflows/ci.yml:19` y `:30` (solo ubicación). ¿Se rotan y se mueven a variables de entorno? | Pendiente. No se reproducen los valores. |
| B4 | Videos de D3 congelados: ¿quedan excluidos del kit de D4? | Por defecto, excluidos. |
| B5 | El ZIP de rescate de Hermes (9,5 MB, 314 entradas) incluye un runbook de **EC2 (AWS)**. ¿Se descarta o se conserva solo como referencia? | Por defecto, referencia no integrada. |
| B6 | Merge a `main`. | No se hace sin tu autorización explícita. |
