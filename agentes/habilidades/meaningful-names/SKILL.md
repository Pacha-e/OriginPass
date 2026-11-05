---
name: meaningful-names
description: Enforces domain-revealing names and English developer-facing source text. Use when creating, renaming, or reviewing Python identifiers, methods, comments, labels, or literals in source files.
---
Ejemplos de otros lenguajes se ignoran; aplica el principio a Python/Django.

# Meaningful Names

## Moral
Use consistent words that reveal domain meaning.

## Rules
- **G-NAME-01:** Choose descriptive names that express domain meaning and distinguish each operation. Clear names prevent ambiguous calls.
- **G-NAME-02:** Write identifiers, comments, and developer-facing source text in English. One source language makes code and review consistent.

## How to check
1. Read each changed identifier as a domain phrase; search for placeholders and ambiguous names such as `aRespuesta`.
2. Inspect changed identifiers, comments, labels, and literals for mixed-language text; explicitly review each exception.
3. Compare operation names with their actual behavior and distinguish different domain operations.

## Example
Bad:
```ts
class ResponseMapper { aRespuesta(): string { return 'ok'; } }
```
Good:
```ts
class ResponseMapper { formatSuccessResponse(): string { return 'ok'; } }
```

## When not to apply
- Use conventional short local indices or mathematical variables when their meaning is immediately apparent.
- Preserve required Spanish quotations, user-provided data, localized user-facing text, and externally mandated names.

## References
- [Global rules: G-NAME-01 and G-NAME-02](../../reglas/global-rules.md#L41)
- Professor feedback on names and mixed languages (fuente no incluida)
