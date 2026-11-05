---
name: maintain-documentation
description: Enforces accurate comments, docstrings, documentation, and diagrams when changing Python or Django code, templates, views, behavior, architecture, or project guides.
---
Ejemplos de otros lenguajes se ignoran; aplica el principio a Python/Django.

# Maintain Documentation

## Moral
Keep explanations and diagrams truthful.

## Rules
- **G-DOC-01:** Document rationale, constraints, and necessary section boundaries without restating obvious code; useful comments preserve context code cannot express. Required section separators are mandatory, including those requested in course views.
- **G-DOC-02:** Update affected documentation, diagrams, and user-facing descriptions when behavior or structure changes; stale claims mislead readers.

## How to check
- Review each changed comment against adjacent code for rationale, constraints, and accuracy. Keep required separators, API documentation, legal notices, and generated annotations.
- Trace changed behavior and structure to documentation and diagrams; compare each claim and depicted relationship with current code. Verify stated guarantees.
- In Django templates, check the section comments and block order required by source-ordering.

## Example
```ts
// Bad: repeats the code.
// Increase the retry count.
retryCount += 1;

// Good: explains a constraint that the code alone cannot express.
// Count this attempt so the external service's retry limit is respected.
retryCount += 1;
```

## When not to apply
- Do not remove mandatory separators, required API documentation, legal notices, or generated annotations as obvious comments.
- Do not rewrite clearly labeled historical snapshots as if they described current behavior.

## References
- [Global rules G-DOC-01–02](../../reglas/global-rules.md#comments-and-documentation)
- Comment rationale (fuente no incluida)
- Professor feedback, including diagrams and separators (fuente no incluida)
