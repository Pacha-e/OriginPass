---
name: module-boundaries
description: Enforces ownership by layer and groups decisions by reason for change. Use when creating, moving, or reviewing modules, services, controllers, seeders, storage, types, or architecture diagrams.
---
Ejemplos de otros lenguajes se ignoran; aplica el principio a Python/Django.

# Module Boundaries

## Moral
Put each decision behind the boundary responsible for it.

## Rules
- **G-STRUCT-03:** Place each definition in the folder and layer responsible for its role. Separate ownership makes seeds, storage, services, and types understandable.
- **G-DESIGN-02:** Group code around decisions that change for the same actor and hide unstable details behind a small interface. Cohesion limits the impact of changes.

## How to check
1. Compare changed definitions and imports against documented folder responsibilities and the architecture diagram; verify the diagram matches the code.
2. Identify the actor and decision behind each module. Trace a typical change and count the files needed to understand it.
3. Inspect services for embedded seeders or unrelated storage and types; move responsibilities to their documented owners.

## Example
Bad:
```ts
class UserService {
  seedUsers(): void { /* seed data here */ }
  createUser(): void { /* business operation here */ }
}
```
Good:
```ts
class UserSeeder { seedUsers(): void { /* seed data here */ } }
class UserService { createUser(): void { /* business operation here */ } }
```

## When not to apply
- Keep a small cohesive definition with its consumer if a separate layer does not clarify ownership and course rules allow it.
- Do not split a cohesive module solely because it is long, or add an interface that hides no decision.

## References
- [Global rules: G-STRUCT-03 and G-DESIGN-02](../../reglas/global-rules.md#L31)
- Professor feedback on mixed responsibilities (fuente no incluida)
- Layer and domain evidence (fuente no incluida); actor-based responsibility (fuente no incluida)
