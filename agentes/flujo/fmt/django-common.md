DJANGO CONTEXT:
- Repo root is OriginPass: Django 5.2, Python 3.12, PostgreSQL 17 through `DATABASE_URL`. Read `pyproject.toml`, `config\settings.py` and the app you touch before editing.
- First-party apps (`known-first-party` in `pyproject.toml`): accounts, audit, companies, config, pages, products, test_support, verification. Read the app's `models.py`, `views.py` and `urls.py` before changing it.
- Views are function-based (for example `def log_in(request)`). Keep that style unless the task says otherwise.
- Migrations are immutable: never edit a migration that already exists. Create a new migration only when the task owns that app's `migrations\` folder.
- Do NOT edit shared files (`config\settings.py`, `config\urls.py`, `pyproject.toml`, `requirements*.txt`, `docker-compose.yml`, `.env*`) unless the OWNED list names them.
- No new packages: anything else is NEED.
- Interface text in Spanish through `gettext`; code in English.
SKILLS for this task (in addition to the common ones): the skills the task lists under `agentes\habilidades\`.
VERIFY from the repo root with `D:\OriginPass-D4-orq\venv\Scripts\python.exe`: `-m ruff check <your files>`, `-m ruff format --check <your files>`, `manage.py makemigrations --check --dry-run`. The full test suite (about 6 minutes) runs only when the orchestrator asks for it.