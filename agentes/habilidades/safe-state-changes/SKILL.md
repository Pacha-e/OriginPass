---
name: safe-state-changes
description: Enforces persistent invariants and migration recovery when changing database constraints, concurrent writes, schemas, backfills, or Django persistence code.
---
Ejemplos de otros lenguajes se ignoran; aplica el principio a Python/Django.

# Safe State Changes

## Moral
Preserve invariants across concurrent writes and migrations.

## Rules
- **G-SEC-04:** Enforce persistent invariants in the data store and protect concurrent read-modify-write operations; application-only checks can miss conflicting writers.
- **G-SEC-05:** Check existing data before tightening a constraint and provide a tested migration and recovery plan; existing rows may violate a new schema even when an empty database passes.

## How to check
- Inspect actual data-store constraints and locking or conditional writes; run concurrent attempts against the relevant store and check the invariant.
- Count violating records before adding a constraint; test the migration on a representative safe copy, including backfill and rollback or recovery steps.
- Inspect backend schema changes for the migration required by the course; the professor explicitly identified a missing migration (feedback (fuente no incluida), line 38).

## Example
```ts
// Bad: concurrent callers can both observe the same balance.
const balance = await store.readBalance(accountId);
await store.writeBalance(accountId, balance - amount);

// Good: one conditional store operation performs the check and update.
const updated = await store.debitIfSufficient(accountId, amount);
if (!updated) throw new Error('Insufficient balance');
```
The store implementation must make the conditional operation atomic and enforce the persistent balance invariant.

## When not to apply
- A verified single-writer immutable process may not need locks; establish its invariant.
- A new empty store with verified absence of existing data does not need a backfill, but schema changes still need an appropriate migration and recovery plan.

## References
- [Global rules G-SEC-04–05](../../reglas/global-rules.md#validation-and-security)
- Professor feedback on migrations (fuente no incluida)
