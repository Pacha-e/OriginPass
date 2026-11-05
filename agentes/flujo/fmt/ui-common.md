UI CLEANUP CONTEXT (Django templates):
- Templates live in `templates\` (project level) and `<app>\templates\<app>\` (app level). Read the base template and the app's `views.py` before editing a page.
- Order inside each template: `{% extends %}` first, then `{% load %}`, then blocks in the order the base template declares them. Do not reorder blocks that the base template depends on.
- When a template has more than one section, separate them with `{# --- Section --- #}` comments.
- Views prepare the context; templates only render it. No business math, no ORM queries and no conditional business rules inside templates.
- Every visible string goes through `{% trans %}` or `{% blocktrans %}` with the Spanish translation in `locale\`. Identifiers, comments, CSS class names and element ids are in English.
- Accessible markup: labels linked with `for`, alt text on images, semantic elements (`nav`, `main`, `table` with `th` scope).
- Behavior and URLs unchanged; only structure, naming, language and markup order change.
- Touch only OWNED files.
SKILLS for this task (in addition to the common ones): `agentes\habilidades\simple-design\SKILL.md`, `agentes\habilidades\maintain-documentation\SKILL.md`.
VERIFY from the repo root with `D:\OriginPass-D4-orq\venv\Scripts\python.exe`: `-m ruff check <your files>`, `-m ruff format --check <your files>`, `manage.py check`. Run the tests of the touched app only when the orchestrator allows it.