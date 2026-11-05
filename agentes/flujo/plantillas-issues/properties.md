Model and migration changes for <app>:

- Field names in English; explicit `on_delete` on every foreign key; `verbose_name` through gettext.
- Constraints that the database enforces (CHECK, UNIQUE) are part of the migration.
- One migration per logical change; applied migrations are never edited.

Acceptance: `manage.py makemigrations --check --dry-run` passes; the migration applies from zero on PostgreSQL 17.