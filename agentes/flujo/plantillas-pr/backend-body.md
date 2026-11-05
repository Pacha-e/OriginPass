## Summary
- <Models, views, forms or migrations changed, one line each.>
- Migrations: <new migration names, or none>; applied from zero on PostgreSQL 17.

## Verification
`ruff check .` <result> · `ruff format --check .` <result> · `makemigrations --check --dry-run` <result> · `manage.py test --noinput` <result>

Closes #<n>