Clean up the Django backend of <app> so it follows the global rules and the Django section of `agentes\reglas\global-rules.md`:

- Models: explicit field types and constraints. Invariants that the database can express as CHECK or UNIQUE go into a migration, not only into forms.
- Views are function-based; forms validate input; no ORM queries inside templates.
- Services and utilities are classes with static or instance methods; no loose functions in services or utilities.
- Migrations: applied migrations are never edited; data migrations are tested against a copy of real data.
- Section separator comments; alphabetical names inside each section; English identifiers and comments; interface text through gettext.
- Verification: `ruff check .`, `ruff format --check .`, `manage.py makemigrations --check --dry-run`, `manage.py test --noinput` on PostgreSQL 17.