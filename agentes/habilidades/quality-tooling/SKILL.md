---
name: quality-tooling
description: Enforces shared quality checks and deliberate dependency management when editing Python code, pyproject.toml, requirements files, lint or formatter configuration, or preparing a delivery.
---
Ejemplos de otros lenguajes se ignoran; aplica el principio a Python/Django.

# Quality Tooling

## Moral
Use reproducible checks and manage dependencies deliberately.

## Rules
- **G-TOOL-01:** Run the project formatter, linter, and relevant checks using shared configuration before delivery; consistent automated feedback reveals defects and noisy diffs.
- **G-TOOL-02:** Pin or lock dependencies where supported and review updates for compatibility and known vulnerabilities; reproducible dependencies limit unexpected changes and supply-chain exposure.

## How to check
- Inspect project configuration and recorded command results. Review each new suppression and its reason; search changed files for `eslint-disable` and lint rules set to `off`.
- Inspect changed manifests and lockfiles, and available audit results for changed dependencies.
- Review course-specific hard rules alongside automated results: external imports before internal imports; alphabetize names within source sections and use separator comments; place utilities in classes as methods; write developer-facing source in English. Preserve behavior-sensitive order and framework-required forms, and retain localization and verbatim quotes. See G-STRUCT-01, G-STRUCT-02 and G-NAME-02 in [global rules](../../reglas/global-rules.md).

## Example
```ts
// Bad: suppresses a rule without explaining the cause.
// eslint-disable-next-line no-console
console.log(result);

// Good: remove the unnecessary debug output.
return result;
```

## When not to apply
- If a tool is unavailable or inapplicable, report the missing check and use suitable available verification.
- Libraries may publish compatible version ranges while keeping a development lockfile; do not lock out security updates indefinitely.

## References
- [Global rules](../../reglas/global-rules.md#tooling) ? G-TOOL-01 and G-TOOL-02.
- Dependency evidence (fuente no incluida) ? lines 606?650.
- Course author tooling (fuente no incluida) ? lines 37?45.
- Professor feedback (fuente no incluida) ? lines 34?38 and 48.
