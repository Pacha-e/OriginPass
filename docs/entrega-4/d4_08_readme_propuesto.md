# D4-08 · README.md propuesto para origin/main

Fuente: `git show origin/main:<ruta>` (commit `81fbe6d`). Solo lectura: no se modificó el README ni ningún archivo del repositorio. Cada afirmación cita `archivo:línea` del árbol de origin/main. Lo no verificable se marca `PENDIENTE`.

## Hallazgos previos

- El README de origin/main (300 líneas, `README.md`) ya cubre las 7 secciones pedidas. La propuesta conserva su contenido y corrige o completa lo siguiente.
- Omisión: el README no nombra `DATABASE_URL`. `config/settings.py:89` la exige con `require_env` y sin ella `manage.py` no arranca. El README solo menciona `SECRET_KEY` (`README.md:132`). `.github/workflows/ci.yml:28-32` define el bloque `env` de CI.
- Omisión: el árbol de carpetas (`README.md:205-224`) no incluye `delivery/`, `docker/`, `docs/`, `tools/presentation/` ni `test_support/`, que existen en `git ls-tree origin/main`.
- Contradicción de gettext: `README.md:113-114` y `docs/ready-to-present.md:157` dicen que gettext no hace falta para ejecutar el proyecto. Pero `README.md:134` y `.github/workflows/ci.yml:53` ejecutan `compilemessages`, que necesita `msgfmt`. Ver PENDIENTE-2.
- Idioma: el repositorio documenta en inglés (`README.md:101-104`). La propuesta sigue esa convención en el cuerpo del README. Ver PENDIENTE-1.
- Comandos de gestión existentes en origin/main (`git ls-tree`): `audit/management/commands/describe_schema.py`, `audit/management/commands/verify_integrity.py`, `companies/management/commands/seed_demo.py`. Solo `describe_schema` no aparece en el README actual.

---

## README.md propuesto

```markdown
# OriginPass

A web application that issues a verifiable digital passport for every physical product and records each change of custody along its journey, so that a buyer can confirm a product is genuine without having to trust the seller.

Course project for ST0251 Proyecto Integrador 1, 2026-2, Universidad EAFIT.

## 1. Description and documentation

OriginPass verifies companies (commercial companies with an official registry code, and artisan workshops through manual review), issues one passport per product unit, publishes a QR verification page that needs no account, records the chain of custody, and analyses scans to surface signs of QR cloning.

This repository is a working Django and PostgreSQL MVP. It writes nothing to any blockchain; anchoring the integrity chain on Monad is roadmap, not implemented.

All project documentation lives in the [Wiki](https://github.com/Pacha-e/OriginPass/wiki). Start with the [Project Overview](https://github.com/Pacha-e/OriginPass/wiki/Project-Overview) and [Deliverable 3](https://github.com/Pacha-e/OriginPass/wiki/Deliverable-3). A versioned snapshot of the wiki pages is in [docs/wiki/](docs/wiki/).

## 2. Libraries and versions

Runtime, from `requirements.txt`:

| Package | Version constraint |
|---|---|
| Django | >=5.2,<6.0 |
| psycopg[binary] | >=3.2 |
| dj-database-url | >=2.3 |
| python-dotenv | >=1.0 |
| Pillow | >=11.0 |
| qrcode | >=8.0 |

Development, from `requirements-dev.txt` (includes the runtime file):

| Package | Version |
|---|---|
| ruff | 0.16.2 (pinned) |

Other pinned services: PostgreSQL 17 (`postgres:17-alpine`) and pgAdmin 9.17 (`dpage/pgadmin4:9.17`, development only), both in `docker-compose.yml`. Python 3.12 is used in CI.

## 3. Prerequisites

- Python 3.12
- Docker with Docker Compose. On Windows, Docker Desktop.
- PostgreSQL 17, started with Docker Compose. The application has no fallback to another database engine.
- Git, to clone the repository.
- GNU gettext only if you change a translation (see `locale/`).

## 4. Installation

Start the database and pgAdmin from the repository root (both platforms):

```bash
docker compose up -d
```

PostgreSQL listens on `localhost:5432`; pgAdmin on `127.0.0.1:8080`.

### Windows (PowerShell)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

Create `.env` from `.env.example` and fill in the variables (see below). PENDIENTE-3

Git Bash on Windows also accepts `source .venv/Scripts/activate`.

### Linux and macOS

```bash
python3.12 -m venv .venv         # PENDIENTE-7
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
```

### Environment variables

Set in `.env` (loaded by `config/settings.py:12`):

| Variable | Required | Notes |
|---|---|---|
| `SECRET_KEY` | yes | Also the key every integrity signature derives from. Generate one with the command below. |
| `DATABASE_URL` | yes | PostgreSQL connection URL. A missing value stops startup. |
| `SECRET_KEY_FALLBACKS` | no | Comma-separated retired keys, accepted for verification only. |
| `DEBUG` | no | Defaults to off. `seed_demo` refuses to run with it off unless `--force` is given. |
| `ALLOWED_HOSTS` | no | Comma-separated host names. |
| `EMAIL_BACKEND` | no | Defaults to the console backend. |
| `TRUST_GEO_HEADERS` | no | Defaults to on only when `DEBUG` is on. |
| `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_HSTS_SECONDS` | no | Transport hardening for a deployment behind TLS. |

Generate a secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key as k; print(k())"
```

## 5. Running

```bash
python manage.py migrate
python manage.py compilemessages     # needs GNU gettext; see PENDIENTE-2
python manage.py createsuperuser     # the platform administrator
python manage.py runserver           # http://127.0.0.1:8000/
```

Demo data and integrity checks:

```bash
python manage.py seed_demo                 # DEBUG must be on, or pass --force
python manage.py verify_integrity          # exits non-zero on any failed record
python manage.py describe_schema           # tables and constraints as the database holds them
```

`seed_demo` creates five company applications (one per status), four passports, a revoked one, and a month of scans. Running it again adds nothing that already exists. Its accounts share one password, which the command prints.

Translations: after changing a source string, run `python manage.py makemessages -l es`, then `python manage.py compilemessages`.

## 6. Tests and quality

```bash
python manage.py test                              # the suite (CI runs --verbosity 2)
python manage.py makemigrations --check --dry-run  # no model change left unmigrated
ruff check .                                       # lint
ruff format --check .                              # formatting
```

CI runs these four commands on every push and pull request against a PostgreSQL 17 service. It compiles the translations before the test suite. PENDIENTE-9

## 7. Repository layout

```
OriginPass/
├── accounts/         User model, registration, login, logout, password reset
├── audit/            append-only AuditEntry, integrity checks, describe_schema
├── companies/        Company model, applications, administrator review, seed_demo
├── config/           settings, root URLs, WSGI and ASGI entry points
├── delivery/         portable presentation kit: setup and launch scripts, build_portable.py
├── docker/           pgAdmin server registration used by docker-compose.yml
├── docs/             brand, diagrams, demo guide and the wiki snapshot (docs/wiki/)
├── locale/es/        the Spanish the interface is served in
├── pages/            the landing page
├── products/         Product and CustodyTransfer models, passports and QR codes
├── static/           stylesheet, favicon and brand marks
├── templates/        base template, shared partials and error pages
├── test_support/     factories and helpers shared by the test suites
├── tools/            presentation build (tools/presentation/) and video build (tools/video/)
├── verification/     public verification page and its ScanEvent record
├── .github/workflows/ci.yml
├── docker-compose.yml
├── manage.py
├── pyproject.toml    ruff configuration
├── requirements.txt
└── requirements-dev.txt
```

Each app owns its models, views, templates under `<app>/templates/<app>/`, and tests under `<app>/tests/`. Business rules live in models, input validation in forms, orchestration in views, presentation in templates.
```

---

## Fuentes por sección

| Sección | Citas |
|---|---|
| 1 | `README.md:3`, `README.md:5`, `README.md:13-19`, `README.md:21-28`, `README.md:58`, `README.md:66-68`, `README.md:72` |
| 2 | `requirements.txt:1-6`; `requirements-dev.txt:3,5`; `README.md:94-96`; `.github/workflows/ci.yml:39`; `docker-compose.yml:3`, `docker-compose.yml:39`; `pyproject.toml:2-3` (ruff) |
| 3 | `README.md:94-96`, `README.md:118`; `.github/workflows/ci.yml:39`; `delivery/Setup-Portatil.ps1:11,20`; `config/settings.py:87-89`; `README.md:113-114`; `docs/ready-to-present.md:27,157` |
| 4 | `README.md:126-132`; `docs/ready-to-present.md:34`; `delivery/Setup-Portatil.ps1:19-26` (usa `requirements.txt`, no el de desarrollo) y `:28-37` (genera `.env` solo en el flujo del kit); `config/settings.py:12,32,33-37,89,143,151,157-163`; `README.md:181-185` |
| 5 | `README.md:109,133-136,139,145,148-153,170-171,242`; `companies/management/commands/seed_demo.py:254-269` (`--force` en `:259-261`); `audit/management/commands/verify_integrity.py:18-19,94`; `audit/management/commands/describe_schema.py:1-3` |
| 6 | `README.md:189-201`; `.github/workflows/ci.yml:53,56,59,62,65,68`; `docs/GUIA-DEMO.md:47,93` |
| 7 | `README.md:205-232`; listado de `git ls-tree origin/main` |

Comandos verificados en el repo: `migrate`, `runserver`, `createsuperuser`, `compilemessages`, `makemessages`, `makemigrations`, `test` y `check` son comandos integrados de Django (dependencia `requirements.txt:1`). `seed_demo`, `verify_integrity` y `describe_schema` están definidos en el repo (ver fuentes arriba). `ruff` está en `requirements-dev.txt:5`. `docker compose`, `python -m venv` y `pip` son herramientas externas, citadas por `README.md:126-130`.

---

## PENDIENTE

- PENDIENTE-1: idioma del README entregable. El repo documenta en inglés (`README.md:101-104`) y el enunciado pide español. Decisión del equipo.
- PENDIENTE-2: si `compilemessages` funciona en un clon limpio sin gettext. El README dice que el `.mo` está versionado (`README.md:113-114`), pero el paso de instalación lo ejecuta (`README.md:134`) y CI lo ejecuta (`.github/workflows/ci.yml:53`). No se ejecutó (solo lectura).
- PENDIENTE-3: comando PowerShell manual para copiar `.env.example` a `.env`. El repo solo lo hace en `delivery/Setup-Portatil.ps1:28-37`, que genera el archivo y no copia la plantilla.
- PENDIENTE-4: contenido de `.env.example`. No se abrió por las reglas de seguridad del entregable. Las variables requeridas se toman de `config/settings.py`, no de la plantilla.
- PENDIENTE-5: versiones exactas instaladas por pip. `requirements.txt` declara rangos y el árbol de origin/main no tiene archivo de bloqueo (`git ls-tree origin/main`). Requiere instalar, lo cual no se hizo.
- PENDIENTE-6: versión mínima de Docker Desktop y Docker Compose. No aparece en el repo.
- PENDIENTE-7: método de instalación de Python 3.12 en Linux y macOS. El repo solo documenta `py -3.12` en Windows (`delivery/Setup-Portatil.ps1:20`).
- PENDIENTE-8: la wiki en línea (`https://github.com/Pacha-e/OriginPass/wiki`) no se consultó (sin red en este entregable). No se confirmó que sus páginas coincidan con `docs/wiki/`.
- PENDIENTE-9: número de tests (293) y duración (977 s) según `docs/GUIA-DEMO.md:47,93`. No se ejecutó `python manage.py test` (solo lectura). Validar en el entorno de referencia antes de publicar la cifra.

Total de PENDIENTE en este archivo: 9.
