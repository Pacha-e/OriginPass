---
name: reviewed-delivery
description: Enforces reviewable integration and auditable repository contents when preparing pull requests, integrating feature branches, reviewing staged files, or delivering generated artifacts.
---
# Reviewed Delivery

## Moral
Make integration reviewable and repository history useful.

## Rules
- **G-VCS-01:** Use a feature branch and a reviewed pull request with relevant checks before integrating into the shared main branch; review and checks provide an independent gate.
- **G-VCS-02:** Keep generated dependencies and build artifacts out of version control unless the project explicitly requires them; generated files obscure meaningful changes and inflate history.

## How to check
- Inspect branch protection, pull request review, and relevant check results before integration.
- Inspect the staged file list and ignore rules for dependency directories and build outputs; verify whether tracked generated files are explicitly required.
- Confirm the delivered revision corresponds to the reviewed submission. The professor noted: ?despliegue basado en repo actualizado, que incluye commits por fuera del tiempo de entrega? (professor feedback, line 39); this observation identifies a delivery-version mismatch.

## Example
```ts
// Bad: generated dependency output is included in the change.
const stagedFiles = ['src/user.ts', 'node_modules/pkg/index.js'];

// Good: the review contains the project source.
const stagedFiles = ['src/user.ts'];
```

## When not to apply
- A solo offline exercise or emergency fix may use a documented alternative review process when repository policy permits it.
- Track generated artifacts when distribution, deployment, or course submission explicitly requires them.

## References
- [Global rules](../../reglas/global-rules.md#version-control) ? G-VCS-01 and G-VCS-02.
- Review workflow evidence (fuente no incluida) ? lines 290?334 and 551?590.
- Professor feedback (fuente no incluida) ? lines 39?41 and 49.
