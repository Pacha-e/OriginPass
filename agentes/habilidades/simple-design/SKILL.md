---
name: simple-design
description: Enforces minimal present-focused design, shared domain knowledge, and composition for variable behavior. Use when implementing or reviewing Python features, abstractions, duplicated business rules, or inheritance hierarchies.
---
Ejemplos de otros lenguajes se ignoran; aplica el principio a Python/Django.

# Simple Design

## Moral
Model present needs without speculative complexity.

## Rules
- **G-DESIGN-01:** Implement the present requirement with the fewest moving parts that preserve domain distinctions. Speculative abstractions add maintenance and hide behavior.
- **G-DESIGN-03:** Consolidate repeated domain knowledge once a shared rule is established, using the third occurrence as the default abstraction trigger. Shared knowledge avoids drift; similar text alone does not prove a shared rule.
- **G-DESIGN-04:** Assemble interchangeable behavior from collaborators instead of introducing inheritance by default. Composition limits coupling to parent internals.

## How to check
1. Trace every added abstraction and option to an acceptance criterion; inspect the diff for unrelated edits.
2. Locate repeated rules and compare their business meaning and change history before extracting a common authority.
3. Search for `extends`, assess substitution and coupling, and compare a collaborator-based alternative.

## Example
Bad:
```ts
class EmailNotifier { send(): void { /* send email */ } }
class OrderNotifier extends EmailNotifier {}
```
Good:
```ts
class EmailNotifier { send(): void { /* send email */ } }
class OrderNotifier {
  constructor(private readonly email: EmailNotifier) {}
  send(): void { this.email.send(); }
}
```

## When not to apply
- Add an extension point required by an existing contract or demonstrated constraint.
- Keep lookalike cases separate when their meanings or reasons for change differ; establish one authority before three copies when an invariant requires it.
- Use inheritance when a stable subtype contract and framework integration make it clearer.

## References
- [Global rules: G-DESIGN-01, G-DESIGN-03, G-DESIGN-04](../../reglas/global-rules.md#L59)
- KISS and DRY evidence (fuente no incluida); composition evidence (fuente no incluida)
