# Deliverable 3: MVP

**Sprint 3 closure.** OriginPass now does the thing it exists to do — publicly,
from a QR — and tells its operator when something looks off. This page records
what the sprint added, what is not in it, and how to run and show it.

---

## 1. Architecture & Data

### 1.1 Deployment diagram

The diagram in `docs/diagrams/` is the same Sprint 2 shape with the additions
this sprint layered on top:

- **Web tier** (Django 5.2) still holds the three public paths: `/v/` (the
  verification page), `/accounts/` (login and registration — now throttled,
  FR57), and the company workspace. New: `POST /products/<pk>/transfer/` and
  `/products/transfers/claim/` move a product between holders.
- **Database** (PostgreSQL 17) grows four tables: `products_transferrequest`
  and `products_custodytransfer` continue the append-only chain pattern
  (DBR05–06), `verification_scanevent` gains a `region` column (FR33), and
  `products_alert` records each duplicate-scan signal (FR49). `accounts_
  loginattempt` holds the (email, IP) failure streaks (FR57).
- **Email** is a config dependency: dev answers to the console backend,
  production swaps in SMTP by env-var. Decisions (FR53), transfer offers (FR54)
  and revocations (FR55) share one helper so the three templates live together.

The draw.io file is `docs/diagrams/deployment-v3.drawio`; the PNG on this page
was exported from it.

### 1.2 Component diagram

| Component | What it does now |
|---|---|
| **accounts** | Registration, login with five-in-fifteen lockout (FR57), password reset (FR06) |
| **companies** | Application, review approval and rejection with email (FR13/14), suspension (FR15/16), public profile (FR18) |
| **products** | Passport registration (FR19–26, UR10), custody transfers (FR35–40), revocation with audit (FR41/42), analytics (FR46–49), CSV export (FR51) |
| **verification** | Public verdict with chain of custody (FR32), region-stamped scans (FR33), duplicate-scan alert (FR49), scan cap (FR58) |
| **audit** | Chained integrity hashes and a `verify-chain` command — FR45 and the seed of FR56 |
| **pages** | The landing, the error pages, and nothing else |

### 1.3 Data model

The diagram now includes:
- `CustodyTransfer(product, from_holder, to_holder, state, note, transfer_code,
  previous_hash)` — one chain per product, ordered by the hash link.
- `ScanEvent(product?, scanned_at, region, device_category, verdict)` — coarse
  region and device class, never a coordinate.
- `Alert(product, scan, kind)` — at most one per scan.
- `LoginAttempt(email, ip_address, failed_count, locked_until)` — the (email,
  IP) pair is the unit, so a shared office NAT doesn't hold two accounts.

## 2. Corporate image

The logo stays: the **OP** monogram on a terracotta tile that reads as wax
and clay, not blue. The new colour set — terracotta ink, forest shade, cream,
and a brown for text — is the one every page had already respected since
Sprint 2; what changed is the page layout of the product views.

- **Logo**: `docs/brand/originpass-mark.svg`
- **Slogan**: *"El QR que firma el origen."*
- **Palette**: terracotta `#c75b39`, forest `#4a6741`, cream `#faf7f2`,
  ink `#3e2f25`, all passing WCAG 4.5:1 (UR09).
- **Typeface**: the system serif sits on headings so a web font request never
  competes with the verdict (UR06).

Screenshots in `docs/brand/`: landing, login, the public verification verdict
genuine and revoked, a company dashboard, the admin overview.

## 3. Repository

- **requirements.txt** unchanged: `Django==5.2.*`, `qrcode[pil]`, `Pillow`,
  `python-gettext` (for makemessages on Windows). Everything runs inside
  `docker-compose` for the database and the standard `python -m venv`.
- **README** now points at the wiki: it covers the run-up steps
  (`docker compose up -d`, `migrate`, `compilemessages`, `seed_demo`,
  `runserver`) and the demo flow for the sprint video, so a fresh machine
  makes the demo work without touch-ups.
- **Commits** follow the project rule: one concern per commit, the message
  says what the code does and why — in Spanish in the log, in English in the
  tests and docstrings. `git log --oneline` is the readable summary.

## 4. Video

The runbook `docs/sprint-3-demo-runbook.md` covers the live demo:

1. Pre-flight: postgres, migrate, seed_demo. The seeder prints the demo
   accounts and passports with their `/v/` paths.
2. Login as an admin, approve the pending application — watch the email hit
   the console (FR53).
3. Register a product, download its QR — the claim code lives on it.
4. Verify from a phone-shaped narrow window: genuine.
5. Transfer it to a buyer, answer, and the verification page now shows the
   chain (FR32).
6. Scan the same code from a fake second region — the analytics dashboard
   shows the duplicate-scan alert (FR49).
7. Revoke the product (FR41/42); watch the verdict turn red.

Length: about 4 minutes as rehearsed.

## 5. Project management

### 5.1 Backlog

The public project board at
[github.com/Pacha-e/projects/1](https://github.com/Pacha-e/projects/1) keeps
every requirement, with `sprint-3` and `sprint-4` labels now closed where the
tests assert them.

### 5.2 Weekly meetings

Three short syncs during the sprint:

- Week 1: custody model and chain — agreed `TransferRequest` wraps `Custody-
  Transfer`, and `accept()` does the resolve inside one transaction.
- Week 2: verification page now chains; duplicate-scan alert is the trigger
  for the analytics tab.
- Sprint 2 sync: the verification page must stay below 3 seconds even with
  the chain (UR06) — a chain stays off the verdict path.

### 5.3 Retrospective

**Continue.** Chaining every status change at write. Every test measuring its
own bound (UR06's 3 seconds on the verification page).

**Start.** A migration dry-run gate alongside the tests (read, not just
write), i18n keys with the string they translate to beside them so the review
catches a missing one, and a demo runbook that the next sprint inherits.

**Stop.** A sprint branch that lands before the suite runs on it; an `x`
`.po` placeholder that compiles; asking for a reason only at the admin end of
a workflow (FR57's lock is silent, the revocation is loud).

## 6. Sprint review

**Pitch.** A product that carries its own passport beats a certificate every
time someone points a phone at it: the seller can't argue with the chain.

**Demo.** A new application, an approval email, a registered product, two
transfers, a cloned scan flagging the alert, and a revoked passport. Five
minutes, live.
