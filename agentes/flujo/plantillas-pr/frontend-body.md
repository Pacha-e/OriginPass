## Summary
- Templates changed: <list>.
- Business logic moved out of templates into <view or service>: <yes/no, where>.

## Verification
`ruff check .` <result> · `ruff format --check .` <result> · `manage.py check` <result> · `manage.py test --noinput <app>` <result>

Closes #<n>