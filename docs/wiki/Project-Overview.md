# Project Overview

## What the product is

OriginPass is a web application that issues a verifiable digital passport for every physical product and records each change of custody along its journey.

A producer registers a unit. The system issues a passport code that cannot be guessed from any other code, and a QR that points to a public verification page. A buyer scans the QR, sees whether the product is genuine, who made it, and where it has been. No account, no app, no waiting.

## How it works

```
  Company applies  ──►  Administrator reviews  ──►  Company approved
                                                          │
                                                          ▼
                                              Company registers a product
                                                          │
                                          passport code + QR are issued
                                                          │
                    ┌─────────────────────────────────────┤
                    ▼                                     ▼
        Custody transfers recorded            Buyer scans the QR
        maker → distributor → owner                       │
                    │                                     ▼
                    └───────────────────►  Verification page shows
                                           verdict, product, company
                                           and the custody chain
                                                          │
                                                          ▼
                                              Scan recorded and analysed
```

## Two verification tracks

Most origin schemes assume the producer is a registered company. In the sectors where counterfeiting hurts most, that assumption excludes exactly the people who need protecting. OriginPass therefore verifies companies two ways:

| Track | For | How trust is established |
|---|---|---|
| Registry | Commercial companies | An official registry code, reviewed by the administrator |
| Artisan review | Artisan workshops, often informal, with or without a NIT | Manual review by the administrator of the evidence of the craft the workshop describes; no registry code required |

Neither track is a lesser version of the other. Both end in the same approved status and the same ability to issue passports.

## What makes verification trustworthy

- **One passport per unit.** A leaked code legitimises one item, not a batch.
- **Codes that cannot be derived from one another.** Holding a genuine code gives no help in producing another.
- **A uniform answer for unknown codes.** The response cannot be used to map which codes exist.
- **An append-only history.** Custody transfers and status changes are added, never rewritten.
- **A reason on every negative decision.** Rejections, suspensions and revocations are all explainable after the fact.

## Analytics

Every verification is recorded, without personal data, keeping the timestamp, a coarse region and the device category. That record answers questions a producer cannot otherwise answer: where are my products actually being checked, which lines attract the most scrutiny, and is one of my codes turning up in two places at once.

The last of those is the interesting one. A passport scanned in two different regions within twenty-four hours, say in Córdoba and in Bogotá on the same day, is a strong signal that the QR has been photographed and reprinted. The system raises an alert on that pattern, which turns verification data into an early warning rather than a report.

## Scope for this semester

Built: company verification with both tracks, product passports with QR, public verification, chain of custody, scan analytics with duplicate detection, revocation and audit.

Not built, and why: records on a blockchain (a ledger proves a record did not change, not that it was true when written; records are signed and chained in the application instead, and publishing the head of the chain outside the operator's control, on Monad, is the Sprint 4 goal — see the [Domain Model](Domain-Model)), payments (the product is being validated, not sold), a native app (the whole point is that no install is needed), automated registry integration (depends on access outside the project).

## Related pages

- [Product Vision Board](Product-Vision-Board)
- [Problem Validation](Problem-Validation)
- [Requirements Specification](Requirements-Specification)
- [Domain Model](Domain-Model)
