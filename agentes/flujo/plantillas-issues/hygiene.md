Repository hygiene for OriginPass:

- Remove committed tool artifacts (caches, screenshots, browser-tool folders); extend `.gitignore` for Python caches, virtual environments, `.env`, `staticfiles` and uploaded media.
- English, accurate root `README.md` covering stack, layout, local run, quality gates and deploy.
- `.editorconfig` and a pinned Python version file.
- `docker-compose.yml` with PostgreSQL 17 and a named data volume; passwords come from `.env`, never hardcoded.
- Pull request and issue templates.