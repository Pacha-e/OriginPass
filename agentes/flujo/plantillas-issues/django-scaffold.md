Create the Django base for <app>:

- App folder with `apps.py`, `models.py`, `views.py`, `urls.py`, `admin.py` and `tests`.
- Register the app in `INSTALLED_APPS` and include its URLs in `config\urls.py` (only when the task owns that file).
- Base template extending the project base template.
- First migration generated with `makemigrations`.
- Smoke test: the index URL returns 200.

No feature pages in this issue.