---
name: failure-handling
description: Enforces explicit failure handling and safe retries when writing except blocks, views, multi-step writes, transactions, or retryable jobs in Python or Django services.
---
Ejemplos de otros lenguajes se ignoran; aplica el principio a Python/Django.

# Failure Handling

## Moral
Make failures and retries safe and observable.

## Rules
- **G-ERROR-01:** Handle expected failures at the appropriate boundary or propagate them with useful context; silent catches hide defects and prevent recovery.
- **G-ERROR-02:** Use transactions, compensation, or safe ordering for operations that can partially fail; partial writes can leave inconsistent state.
- **G-ERROR-03:** Make repeatable operations idempotent or reject duplicate attempts consistently; retries must not cause unintended repeated effects.

## How to check
- Search for `catch` blocks and failed return paths; inspect logs and reproduce representative failures. Confirm each failure is handled or propagated with useful context.
- Force the second step of a multi-step operation to fail; verify rollback, compensation, or the documented safe state.
- Run a repeatable operation twice using the same identity; inspect both responses and persisted effects.

## Example
```ts
// Bad: an error appears to be success.
try { await saveOrder(order); } catch { }

// Good: preserve failure and add context for the caller.
try {
  await saveOrder(order);
} catch (cause) {
  throw new Error('Could not save order', { cause });
}
```

## When not to apply
- A deliberately ignored failure is acceptable only if its harmlessness is documented and it is observable where needed.
- Do not add transactional machinery to an atomic single operation or an explicitly acceptable independent side effect.
- Do not deduplicate a contract that intentionally records each distinct invocation.

## References
- [Global rules G-ERROR-01–03](../../reglas/global-rules.md#error-handling)
- Failure handling research (fuente no incluida)
