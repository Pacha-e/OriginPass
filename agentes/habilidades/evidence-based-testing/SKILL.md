---
name: evidence-based-testing
description: Enforces behavior-focused tests and defect reproduction when changing Python or Django code, fixing defects, testing views and APIs, or validating critical user flows.
---
Ejemplos de otros lenguajes se ignoran; aplica el principio a Python/Django.

# Evidence-Based Testing

## Moral
Verify behavior with evidence that can expose failures.

## Rules
- **G-TEST-01:** Add focused unit and integration tests for changed behavior and end-to-end tests for critical user flows; different boundaries expose different failures.
- **G-TEST-02:** Demonstrate defects with a failing test or repeatable reproduction before fixing them; the evidence must distinguish faulty behavior from corrected behavior.

## How to check
- Map acceptance criteria and failure cases to assertions; run the smallest relevant suite. Inspect integration tests for real boundaries and critical flows for end-to-end coverage.
- Record the failing result before the fix and the passing result after it; confirm the reproduction exercises the reported symptom.
- Coverage percentage alone does not establish behavioral confidence.

## Example
```ts
// Bad: the result is never asserted.
it('calculates a total', () => { calculateTotal(2, 3); });

// Good: an observable result is checked.
it('calculates a total', () => { expect(calculateTotal(2, 3)).toBe(5); });
```

## When not to apply
- Do not add an end-to-end test for a trivial pure calculation when a focused test demonstrates the requirement.
- If automation is impractical or hazardous, use a documented manual or production-safe reproduction.

## References
- [Global rules](../../reglas/global-rules.md#testing) ? G-TEST-01 and G-TEST-02.
- Test pyramid evidence (fuente no incluida) ? lines 18?74.
- Professor feedback (fuente no incluida) ? line 48.
