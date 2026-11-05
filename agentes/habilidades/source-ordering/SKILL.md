---
name: source-ordering
description: Enforces ordered source sections, alphabetized names, and class-based utilities and services. Use when creating, editing, or reviewing Python modules, Django views, service classes, or utility modules.
---
Ejemplos de otros lenguajes se ignoran; aplica el principio a Python/Django.

# Source Ordering

## Moral
Keep source sections predictable while preserving behavior-sensitive order.

## Rules
- **G-STRUCT-01:** Divide each source file into sections in this order: external imports, internal imports, constants, types/enums/interfaces, class or exported members, private helpers. Introduce each present section with a separator comment and alphabetize names within sections, including import lines and specifiers, constants, properties, methods, and functions. Predictable locations speed navigation. Never reorder function bodies.
- **G-STRUCT-02:** Put utility functions and service operations in appropriately named classes as methods. The course requires class-based utilities and services, making ownership explicit.

## How to check
1. Inspect separator comments and compare section order and names against an alphabetical sort. Check both import lines and specifiers.
2. Before changing order, inspect side-effect imports, initialization dependencies, and framework execution order.
3. Search utility and service files for top-level function declarations; verify each method belongs to its class.

## Example
Bad:
```ts
export function formatPrice(value: number): string { return value.toFixed(2); }
```
Good:
```ts
// Exported members
export class PriceFormatter {
  static format(value: number): string { return value.toFixed(2); }
}
```

## When not to apply
- Preserve meaningful order in the CSS cascade, route declarations, Django template blocks, package scripts, middleware/pipelines, decorators, side-effect imports, and initialization dependencies.
- Omit absent sections; do not insert comments in formats that prohibit them.
- Keep framework-required callbacks, language entry points, and constructs that cannot be methods in their required form.

## References
- [Global rules: G-STRUCT-01 and G-STRUCT-02](../../reglas/global-rules.md#L15)
- Professor feedback: views and utilities (fuente no incluida)
