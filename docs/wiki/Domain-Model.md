# Domain Model

The entities below drive both the database design and the Django models.

## Entities

### User

The account behind every authenticated action. Authentication uses the Django user model extended with a role.

| Field | Type | Notes |
|---|---|---|
| email | text | Unique; used as the login identifier |
| password | text | Stored as a salted one-way hash (DBR11) |
| role | enum | `ADMIN`, `COMPANY`, `HOLDER` |
| is_active | boolean | |
| date_joined | timestamp | |

A buyer verifying a product is not a User. Verification is anonymous by design.

### Company

One record per company that has applied, whatever the outcome.

| Field | Type | Notes |
|---|---|---|
| owner | FK → User | The account that submitted the application |
| legal_name | text | |
| company_type | enum | `COMMERCIAL`, `ARTISAN` |
| verification_track | enum | `CHAMBER_OF_COMMERCE`, `OFFICIAL_REGISTRY`, `ARTISAN_REVIEW` |
| status | enum | `PENDING`, `APPROVED`, `REJECTED`, `SUSPENDED` |
| description | text | |
| location | text | |
| website | url | Optional |
| logo | image | Optional |
| registry_code | text | Required when `company_type` is `COMMERCIAL` (FR08) |
| evidence_notes | text | The evidence of the craft an artisan workshop offers for review; required for an artisan application, read only by the reviewer (FR09) |
| publish_consent | boolean | The applicant agrees to the public profile shown once approved (FR18) |
| status_reason | text | Required whenever status becomes `REJECTED` or `SUSPENDED` (DBR12) |
| submitted_at | timestamp | |
| status_changed_at | timestamp | |

Constraint: a commercial company uses `CHAMBER_OF_COMMERCE` or `OFFICIAL_REGISTRY`; an artisan company uses `ARTISAN_REVIEW`.

### Product

One record per physical unit, not per product line. This is the point on which the product's value rests: a code that covered a whole batch would legitimise every copy of it.

| Field | Type | Notes |
|---|---|---|
| company | FK → Company | Must exist (DBR04) |
| passport_code | text | Unique and indexed (DBR03, DBR10); generated so it cannot be derived from another code (FR21) |
| product_type | enum | `COMMERCIAL_ORIGINAL`, `ARTISAN`; must match the company type (FR23) |
| status | enum | `ACTIVE`, `REVOKED` |
| name | text | |
| description | text | |
| category | text | |
| origin | text | Place of manufacture |
| image | image | Optional |
| integrity_hash | text | Signature over the identifying fields, keyed from outside the database, so later tampering is detectable. Not a plain hash: see below |
| revocation_reason | text | Required when status becomes `REVOKED` (DBR12) |
| registered_at | timestamp | |
| updated_at | timestamp | |

### CustodyTransfer

An append-only chain. Once accepted, a row is never edited (DBR06).

| Field | Type | Notes |
|---|---|---|
| product | FK → Product | |
| from_holder | FK → User | The holder at the time of the transfer |
| to_holder | FK → User | |
| transfer_code | uuid | Unique; the code the seller hands over at the sale, which the buyer uses to claim the product (FR40) |
| state | enum | `INITIATED`, `ACCEPTED`, `DECLINED` |
| note | text | Optional; shown on the public journey |
| created_at | timestamp | |
| resolved_at | timestamp | Set when accepted or declined |
| previous_hash | text | The signature of the previous accepted transfer of the same product |
| entry_hash | text | This transfer's own signature |

A product has at most one `INITIATED` transfer at a time, held by a partial unique index, so it cannot be offered to two accounts and sold twice.

The current holder of a product is the `to_holder` of its most recent accepted transfer, or the owner of the registering company when no transfer has been accepted.

### ScanEvent

Written on every verification. Feeds the analytics (FR46 – FR49) and holds no personal data.

| Field | Type | Notes |
|---|---|---|
| product | FK → Product | Empty when the code matched nothing; those scans are kept too |
| scanned_at | timestamp | |
| region | text | Coarse geographic region, not a precise position |
| device_category | enum | `MOBILE`, `TABLET`, `DESKTOP`, `UNKNOWN` |
| verdict | enum | `GENUINE`, `REVOKED`, `NOT_FOUND` |

### AuditEntry

Append-only. Written on every status change of a company or a product (FR43, FR45).

| Field | Type | Notes |
|---|---|---|
| actor | FK → User | |
| action | text | For example `COMPANY_APPROVED`, `PRODUCT_REVOKED` |
| target_type | text | |
| target_id | integer | |
| reason | text | |
| created_at | timestamp | |
| previous_hash | text | The signature of the entry before it |
| entry_hash | text | This entry's own signature |

### Alert

Raised when one passport is scanned from two different regions within twenty-four hours, the sign of a photographed and reprinted QR (FR49).

| Field | Type | Notes |
|---|---|---|
| product | FK → Product | |
| scan | FK → ScanEvent | The scan that raised it; one alert per scan |
| kind | enum | `DUPLICATE_SCAN` |
| created_at | timestamp | |

### LoginAttempt

A streak of failed logins for one email address from one origin (FR57). Five failures within fifteen minutes lock that pair for fifteen minutes.

| Field | Type | Notes |
|---|---|---|
| email | text | Normalised to lower case |
| ip_address | text | |
| failed_count | integer | |
| first_failed_at | timestamp | Start of the current window |
| locked_until | timestamp | Empty unless locked |
| last_attempt | timestamp | |

## Relationships

```
User 1 ──── 0..1 Company
Company 1 ──── * Product
Product 1 ──── * CustodyTransfer
Product 1 ──── * ScanEvent
Product 1 ──── * Alert
ScanEvent 1 ──── 0..1 Alert
User 1 ──── * CustodyTransfer   (as from_holder and as to_holder)
User 1 ──── * AuditEntry        (as actor)
```

## State machines

### Company

```
          submit
            │
            ▼
       ┌─────────┐  approve   ┌──────────┐  suspend   ┌───────────┐
       │ PENDING │───────────►│ APPROVED │───────────►│ SUSPENDED │
       └─────────┘            └──────────┘◄───────────└───────────┘
            │                              reactivate
            │ reject
            ▼
       ┌──────────┐
       │ REJECTED │──── edit and resubmit ────► PENDING
       └──────────┘
```

`PENDING` and `REJECTED` are editable by the owner; `APPROVED` and `SUSPENDED` are not (FR10, FR11).

### Product

```
   register              revoke
      │                    │
      ▼                    ▼
  ┌────────┐          ┌─────────┐
  │ ACTIVE │─────────►│ REVOKED │
  └────────┘          └─────────┘
```

Revocation is final. A revoked product accepts no custody transfer (FR39).

### Custody transfer

```
                accept
              ┌────────► ACCEPTED   (appended to the chain, never edited)
  INITIATED ──┤
              └────────► DECLINED
                decline
```

## Design notes

**Why the passport code is not sequential.** A sequential or otherwise derivable code would let anyone holding one genuine code produce codes that look valid, which defeats the purpose. The code is generated from a cryptographically secure random source and is long enough that guessing is impractical. Rate limiting on the verification endpoint (FR34, Sprint 4) will close the remaining avenue of probing the code space in bulk; until then FR58 caps how many scan records one address can write in an hour.

**Why an unmatched code returns a uniform message.** Distinguishing "this code does not exist" from "this code exists but belongs to another company" would leak information about which codes are live. Every unmatched code gets the same answer (FR31).

**Why the chain is append-only.** The value of a custody record is that it cannot be rewritten after the fact. Corrections are made by appending a new transfer, never by editing an old one. The same reasoning governs the audit log.

## What replaces the blockchain, and what it is actually worth

The prototype this project builds on stored passport hashes on a public chain. This version does not. The reasoning below is stated in full because it is the foundation the whole product rests on, and an earlier version of this page overstated what had been built.

### The threat, named

A record is worth something only if a reader can tell whether it has been changed since it was written. Three parties could change it:

| Who | What they can reach |
|---|---|
| A stranger | Nothing directly; they go through the application |
| Someone who reaches the database | Every row, through SQL that never runs application code |
| Whoever runs the server | The database **and** the signing key |

### What is built

**Signed, not hashed.** Every product carries a signature over its identifying fields, and every audit entry and custody record carries one over its own contents. The signature is an HMAC-SHA256 keyed from `SECRET_KEY`, which lives in the application's environment and not in the database. This matters: a plain hash over the same columns could be recomputed by anyone able to write to them, so an edited row could be left looking untouched. That was the state of this project until it was measured and found wanting.

**Chained.** Each audit entry carries the signature of the entry before it, and each custody record the signature of the previous handover of the same product. Rewriting one row invalidates its own signature; removing one leaves a gap where the links no longer meet. Neither is prevented — a model can only refuse what goes through it, and raw SQL does not — but both become visible.

**Linear, and the database says so.** A chain that forks is a chain that proves nothing, so `audit_entry_links_to_one_predecessor` and `custody_transfer_links_to_one_predecessor` make it impossible for one record to be the predecessor of two others. This is enforced rather than merely detected, because it is a shape the database can express and therefore should hold: two writers racing to append cannot both succeed, and the loser is rejected instead of forking the chain in silence.

**The key can be retired without accusing the past.** Signing uses the current key; verifying accepts it and any key listed in `SECRET_KEY_FALLBACKS`. Without that, rotating the key would make every record written beforehand report as altered, and a detector that accuses everything detects nothing. A key that was never ours is still refused, so the rotation costs nothing in what this catches.

**Checkable on demand.** `python manage.py verify_integrity` walks the trail, every product signature and every chain of custody, and names the first record that does not hold up.

### What this gives, stated precisely

Tampering by anyone holding **only the database** is detectable. That covers a stolen dump, a compromised database account, a careless migration and a bug in the application layer.

It does **not** cover whoever runs the server, who holds the key as well and can therefore rebuild the whole chain so that it verifies. For a product whose argument is that a buyer should not have to trust the seller, needing to trust the operator is a real limit, and it is recorded here rather than papered over.

### What would close it, and why it is not blockchain

The gap closes by publishing the head of the chain somewhere the operator does not control, so that a rebuilt chain no longer matches what was published. One hash, periodically. A timestamping authority under RFC 3161 does it, and so does a public ledger.

Anchoring on a chain is therefore a reasonable **future option**, and it is the only part of the prototype's design worth keeping. Running the product's records on a chain is not, for a reason that has nothing to do with cost:

> A ledger guarantees that a record was not changed. It does not guarantee that the record was true when it was written.

An artisan registering a product that is not what they claim produces an immutable record of a false claim. Someone photographing a QR code and reprinting it is not stopped by any ledger. The trust in OriginPass is anchored where the claim enters the system — the verification of the company, through a Chamber of Commerce code or through a person reviewing an artisan application — and that step is human and off-chain either way. The prototype had exactly this property: `RegistroEmpresas.sol` had an `administrador` who approved companies, on chain, by hand.

Moving the records onto a chain would relocate trust from the operator to whoever writes the records. It would not remove it. Anchoring the head externally removes the operator from the picture for a fraction of the work, which is why it is the direction chosen for Sprint 4, with Monad as the chain to anchor it on.
