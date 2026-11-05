Clean up the Django templates of <app> (`templates\` and `<app>\templates\`):

- `{% extends %}` and `{% load %}` first, then blocks in the order the base template declares them.
- Section comments `{# --- Section --- #}` when a template has more than one section.
- Every visible string wrapped in `{% trans %}` or `{% blocktrans %}`; Spanish translations in `locale\`.
- Accessible markup: labels linked with `for`, alt text, semantic elements.
- No business logic or ORM queries in templates.
- Behavior and URLs unchanged.