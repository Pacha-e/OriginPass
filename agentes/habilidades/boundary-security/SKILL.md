---
name: boundary-security
description: Enforces validation, injection-safe output, and secret protection when editing Django views, forms, serializers, ORM or raw SQL queries, HTML templates, commands, or settings.
---
Ejemplos de otros lenguajes se ignoran; aplica el principio a Python/Django.

# Boundary Security

## Moral
Treat external input and secrets as trust-boundary concerns.

## Rules
- **G-SEC-01:** Validate and bound external inputs on the authoritative server or receiving process before conversion to domain types; malformed or oversized input can cause harm.
- **G-SEC-02:** Use parameterized queries and commands and context-appropriate escaping or safe APIs for untrusted content; interpolation across interpretation boundaries enables injection.
- **G-SEC-03:** Load secrets from an appropriate secret store or environment and keep them out of source, logs, and URLs; exposure grants unauthorized access and complicates rotation.

## How to check
- Trace each external entry point to type, range, size, and authorization checks. Test invalid and oversized inputs; client validation alone is insufficient.
- Search query, command, and HTML construction for interpolation of external input; test representative injection payloads and inspect the output context.
- Inspect configuration and logging paths; run an available secret scanner without printing values. Check example configuration contains placeholders only.

## Example
```ts
// Bad: input becomes SQL syntax.
await db.query(`SELECT * FROM users WHERE email = '${email}'`);

// Good: input is bound as a value.
await db.query('SELECT * FROM users WHERE email = $1', [email]);
```

## When not to apply
- Do not repeat identical checks inside a trusted invariant-preserving module unless a new boundary is crossed.
- For dynamic identifiers that cannot be parameterized, use a documented safe API and an explicit allowlist.
- Public identifiers and deliberately public client configuration are not secrets; client-side secrets cannot remain confidential.

## References
- [Global rules G-SEC-01–03](../../reglas/global-rules.md#validation-and-security)
- Input validation and injection (fuente no incluida)
- Secrets management (fuente no incluida)
