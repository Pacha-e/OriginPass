## Summary
- Models changed: <list>.
- Migrations: <names>; constraints enforced by the database: <list>.

## Verification
`manage.py makemigrations --check --dry-run` <result> · migration applied from zero on PostgreSQL 17 <result>

Closes #<n>