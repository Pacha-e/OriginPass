---
name: measured-performance
description: Enforces measurement before optimization when profiling Python or Django code, improving response time, reducing database queries, or reviewing performance changes.
---
Ejemplos de otros lenguajes se ignoran; aplica el principio a Python/Django.

# Measured Performance

## Moral
Optimize demonstrated bottlenecks.

## Rules
- **G-PERF-01:** Profile a representative workload and target a measured bottleneck before adding performance complexity; evidence prevents complexity that does not improve the relevant outcome.

## How to check
- Record the representative workload, baseline measurement, and identified bottleneck before changing the implementation.
- Repeat the same workload and measurement method after the change; compare results and state whether the targeted outcome improved.

## Example
```ts
// Bad: an unmeasured workload justifies an extra cache.
const useCache = true;

// Good: add complexity only after profiling the representative workload.
const useCache = measuredLookupBottleneck;
```

## When not to apply
- Apply known necessary limits or suitable algorithms before profiling when an established resource or security constraint requires them.

## References
- [Global rules](../../reglas/global-rules.md#performance) ? G-PERF-01.
- Performance evidence (fuente no incluida) ? lines 489?539.
- Professor feedback (fuente no incluida) ? line 50.
