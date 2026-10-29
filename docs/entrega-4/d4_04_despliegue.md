# Evidencia del despliegue: OriginPass (ST0251, Entregable 4)

Estado de la documentación al 2026-10-28. Solo lectura. No se ejecutaron comandos de AWS ni despliegues.

## Convenciones y alcance de la fuente

| Prefijo | Fuente |
|---|---|
| `[R]` | Repo `OriginPass`, leído con `git show` / `git grep origin/main` |
| `[W]` | Wiki `OriginPass-wiki`, leída desde el directorio de trabajo (no desde git) |
| `[T4]` | `Workshop 1\moviereviewsproject\docs\taller4\DEPLOY_EC2.md` (referencia, otro proyecto) |

Limitaciones de la búsqueda:
- Varias llamadas a git fallaron por falta de memoria del sistema (`fork: Resource temporarily unavailable`). Las lecturas que sí salieron de `origin/main` están citadas; cualquier archivo no leído queda sin cubrir.
- No se abrieron `.env`, `openAI.env` ni `*.sqlite3`. Un hook de seguridad bloqueó `.env.example`, así que tampoco se leyó.

## (a) Estado documentado, con fuente

**Conclusión: no hay ningún despliegue en AWS ni en otro host público documentado.** La documentación describe un sistema que corre en local.

1. **Sin menciones de AWS ni EC2.** Búsqueda `aws|ec2|amazon|lightsail|beanstalk|heroku|render|railway|vercel|netlify|cloudfront` sobre `origin/main`: cero coincidencias de proveedor. El único acierto fue un hash SHA-256 en `[R] delivery/media-manifest.json:20`. La wiki tampoco contiene estas palabras.
2. **Ejecución local documentada.** `[R] README.md:126` (`docker compose up -d`, PostgreSQL en `localhost:5432`) y `[R] README.md:136` (`python manage.py runserver`).
3. **El servidor de aplicación no tiene WSGI en producción.**
   - `[W] Deliverable-2.md:17`: "A WSGI server belongs on the application server and there is not one yet. Sprint 4 is where the course covers deployment".
   - `[R] docs/diagrams/deployment-model.drawio:47`: el nodo con id `gunicorn` tiene la etiqueta "Django development server, manage.py runserver".
   - `[R] docs/diagrams/deployment-model.drawio:157`: nota "Where the project stands today": "The application runs locally ... Deployment is the subject of Sprint 4 ... a WSGI server arrives with it".
   - `[R] requirements.txt` no incluye gunicorn, uwsgi ni waitress (búsqueda negativa en `requirements.txt`, `requirements-dev.txt`, `pyproject.toml`).
4. **Despliegue pendiente, Sprint 4.**
   - `[W] Retrospectives.md:111-112`: "FR56 ... FR34, FR27 and UR05; the deployment."
   - `[W] Development-Log.md:43`: "FR34, FR27 and UR05, and the deployment."
   - `[W] Deliverable-3.md:257`: los requisitos abiertos de Sprint 4 son FR27, FR34, FR56 y UR05. El despliegue no aparece como requisito con código de FR.
5. **Modelo de despliegue (diagrama, no evidencia de servidor real).** `[W] Deliverable-3.md:52`: "Application server | Ubuntu 24.04, Python 3.12, Django 5.2". El mismo entregable dice "Ubuntu 24.04" solo en la tabla del modelo. No hay un servidor con esa configuración documentado como existente.
6. **Configuración de producción presente en código, sin valores reales.** `[R] config/settings.py`:
   - `:32` `SECRET_KEY = require_env("SECRET_KEY")`
   - `:36-37` `DEBUG = env_flag("DEBUG")`, `ALLOWED_HOSTS` desde variable de entorno
   - `:84` `WSGI_APPLICATION = "config.wsgi.application"`
   - `:89` `DATABASES` desde `DATABASE_URL`, solo PostgreSQL
   - `:151` `TRUST_GEO_HEADERS` por defecto `True` solo si `DEBUG`
   - `:157-160` `SECURE_SSL_REDIRECT`, cookies seguras y HSTS, todos apagados por defecto
7. **Base de datos.** `[R] docker-compose.yml:3` `image: postgres:17-alpine`. `[W] Sprint-1-Review.md:53`: PostgreSQL 17 obligatorio en desarrollo y "deployment".
8. **CI.** `[R] .github/workflows/ci.yml:20` servicio PostgreSQL; `:31` `DEBUG: "False"`; `:32` `ALLOWED_HOSTS: localhost,127.0.0.1`. CI no contiene job de despliegue.

## (b) Plantilla de evidencia del despliegue

| Campo | Valor documentado | Fuente | Estado |
|---|---|---|---|
| URL pública | No existe | (a)1, (a)3 | PENDIENTE: URL pública (no hay fuente) |
| IP o dominio | No existe | (a)1 | PENDIENTE: IP pública o dominio |
| Fecha de verificación | No existe | (a)4 | PENDIENTE: fecha en que se comprobó la URL |
| Captura | No existe | (a)1 | PENDIENTE: captura. Ruta sugerida: `OriginPass-wiki/images/despliegue/01-url-publica.png` |
| Servidor y SO | Modelo: Ubuntu 24.04 (no verificado) | `[W] Deliverable-3.md:52` | PENDIENTE: instancia real, región y SO verificados |
| Stack | Python 3.12, Django 5.2 (`>=5.2,<6.0`), PostgreSQL 17 | `[W] Deliverable-3.md:52`; `[R] requirements.txt:1` | Documentado como diseño; PENDIENTE: versiones instaladas en el servidor |
| Servidor de aplicación | Servidor de desarrollo de Django; WSGI ausente | `[R] docs/diagrams/deployment-model.drawio:47`; `[W] Deliverable-2.md:17` | Documentado; el WSGI es pendiente de Sprint 4 |
| Comando de arranque | Local: `python manage.py runserver` | `[R] README.md:136` | PENDIENTE: comando de producción (no existe) |
| Puertos | Local: `5432` (PostgreSQL) y `127.0.0.1:8080` (pgAdmin) | `[R] docker-compose.yml:10,42` | Documentado para local; PENDIENTE: puerto público de la app |
| Security Group | No hay evidencia de AWS | (a)1 | PENDIENTE: reglas entrantes/salientes del Security Group |
| Base de datos | Local: `postgres:17-alpine`, usuario/clave por defecto en compose | `[R] docker-compose.yml:3,7-8` | PENDIENTE: base del servidor (host, versión real, si es local o gestionada) |
| Limitaciones | Ver lista abajo | (a)3, (a)6 | Documentado |

Limitaciones documentadas:
- Sin servidor WSGI en producción: `[W] Deliverable-2.md:17`.
- Los flags de transporte seguro están apagados por defecto: `[R] config/settings.py:157-160`.
- La cadena de integridad no está anclada fuera del servidor: `[W] Deliverable-3.md:27-29` (anclaje en Monad es meta de Sprint 4).
- Un código QR fotocopiado resuelve el mismo pasaporte: `[W] Deliverable-3.md:30-32`.

Campos adicionales necesarios para la evidencia:
- Responsable de la cuenta o del laboratorio: PENDIENTE: confirmar si se usa Learner Lab para OriginPass (no hay mención en la wiki ni en el repo).
- Logs de arranque o de verificación del servicio: PENDIENTE: salida real del comando de arranque en el servidor.

## (c) Pasos reproducibles de DEPLOY_EC2.md (referencia)

`[T4]` es la guía de un taller individual previo, con otro repositorio (`Pacha-e/Workshop-P1`, película-reseñas) y SQLite. No aplica tal cual a OriginPass. Se resume como referencia:

1. Crear instancia Amazon Linux 2023, t2.micro, sin key pair, HTTP y HTTPS habilitados. `[T4]:3`
2. Conectar con EC2 Instance Connect. `[T4]:4`
3. Instalar dependencias: `sudo dnf install python3.11 python3.11-pip git -y`. `[T4]:9`
4. Clonar el repositorio, entrar y `sudo python3.11 -m pip install -r requirements.txt`. `[T4]:15-17`
5. La base de datos (`db.sqlite3`) viene en el repo. Esto no aplica a OriginPass, que usa PostgreSQL. `[T4]:20-21`
6. Crear `openAI.env` en la instancia con la clave de IA. La clave no se sube al repo. `[T4]:25-31` (no se reproduce la clave).
7. Arrancar: `sudo python3.11 manage.py runserver 0.0.0.0:80`. `[T4]:37`
8. Abrir `http://<IP pública>/recommendations/` en el navegador. `[T4]:40`
9. Al terminar: `Ctrl+C`; en EC2, Estado de la instancia, Detener instancia; en Learner Lab, End Lab. `[T4]:44`

Adaptación propuesta a OriginPass, no verificada: Python 3.12 (`[W] Deliverable-1.md:29`), `DATABASE_URL`, `SECRET_KEY` y `ALLOWED_HOSTS` como variables (`[R] config/settings.py:32,37,89`), y un servidor WSGI que hoy no existe (`[W] Deliverable-2.md:17`). El paso 7 con `runserver` no debe presentarse como despliegue final.

## (d) Riesgos

| Riesgo | Fuente | Acción |
|---|---|---|
| Costos de Learner Lab: la instancia sigue consumiendo créditos si no se detiene o se termina el laboratorio | `[T4]:44` | Detener la instancia y terminar el laboratorio al cerrar la sesión. PENDIENTE: créditos disponibles en la cuenta |
| Instancia detenida: el servicio cae y la URL deja de responder | `[T4]:44` | Documentar la URL solo con verificación de fecha. PENDIENTE: confirmar si la IP pública cambia al detener la instancia (no documentado en el repo) |
| Secretos en la instancia: clave de IA en `openAI.env` | `[T4]:28-31` | No pegar la clave en la wiki ni en el repo. Usar variables de entorno |
| Credenciales por defecto en compose: usuario y clave `originpass` | `[R] docker-compose.yml:7-8,45` | Cambiar antes de exponer el servicio |
| Puerto de base de datos publicado en todas las interfaces (`5432:5432`) | `[R] docker-compose.yml:10`; `[R] docs/ready-to-present.md:114` (`0.0.0.0:5432`) | No abrir 5432 en el Security Group |
| `runserver` como servidor público; sin WSGI | `[T4]:37`; `[W] Deliverable-2.md:17` | Usar un servidor WSGI antes de declarar despliegue |
| `SECRET_KEY` y `DATABASE_URL` obligatorios; sin valor en la documentación | `[R] config/settings.py:32,89` | Pasarlos como variables de entorno, nunca en el código |
| Transporte no forzado por defecto (HTTPS, cookies seguras, HSTS) | `[R] config/settings.py:157-160` | Activar en el entorno del despliegue si hay TLS |
| Repositorio local contiene `.env` (no leído) | Listado de `D:\Universidad\Proyecto integrador 1\OriginPass\OriginPass` | Verificar que `.env` no está versionado en `origin/main` (PENDIENTE: confirmar con `git ls-files`) |

## Pendientes consolidados

Número de cada PENDIENTE en este documento, en orden de aparición:

1. URL pública
2. IP o dominio
3. Fecha de verificación
4. Captura del despliegue
5. Instancia real, región y SO verificados
6. Versiones instaladas en el servidor
7. Comando de arranque de producción
8. Puerto público de la aplicación
9. Reglas del Security Group
10. Base de datos del servidor (host, versión real)
11. Responsable de la cuenta o laboratorio (Learner Lab)
12. Logs de arranque o verificación
13. Créditos disponibles en la cuenta
14. Cambio de IP pública al detener la instancia
15. Confirmación de que `.env` no está versionado
