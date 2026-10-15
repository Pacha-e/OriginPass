# Requirements Prioritisation

## Technique used

**MoSCoW.** Every requirement in the [Requirements Specification](Requirements-Specification) is placed in one of four categories:

| Category | Meaning | Marker in the requirement text |
|---|---|---|
| Must have | The release has no value without it | `SHALL` |
| Should have | Important, but the release still works without it | `SHOULD` |
| Could have | Desirable; included only if capacity remains | `COULD` |
| Won't have | Explicitly out of scope for this semester | `WON'T` |

MoSCoW was chosen over list classification, story points, urgency and KANO for two reasons. First, it maps directly onto the priority slot of the requirement specification template used in the course, so priority is carried in the requirement text itself rather than in a separate table that can drift out of step. Second, with one person building the product, the decision that matters is not the exact rank of requirement 14 against requirement 15, but whether a requirement is in the release at all.

Story points were used informally alongside MoSCoW to check that the Must set fits the available hours. That check is recorded below, because it changed the outcome.

## The twenty most relevant requirements

These are the requirements that define what OriginPass is. Remove any of them and the product no longer delivers its value proposition.

| # | ID | Requirement | Sprint |
|---|---|---|---|
| 1 | FR07 | Submit a company application with name, type, description, location and website | 1 |
| 2 | FR08 | Require an official registry code from commercial companies | 1 |
| 3 | FR09 | Accept artisan companies without a registry code, marked for manual review | 1 |
| 4 | FR13 | Administrator approves a pending company application | 1 |
| 5 | FR14 | Administrator rejects an application, storing a written reason | 1 |
| 6 | FR19 | An approved company registers a product | 2 |
| 7 | FR20 | Refuse product registration from a company that is not approved | 2 |
| 8 | FR21 | Generate a passport code that cannot be derived from another code | 2 |
| 9 | FR22 | Generate a downloadable QR image for the verification address | 2 |
| 10 | FR23 | Match product type to company type | 2 |
| 11 | FR24 | A company lists the products it registered | 2 |
| 12 | FR28 | Any visitor opens a verification page without authenticating | 2 |
| 13 | FR29 | Display the verdict Genuine with product and company data | 2 |
| 14 | FR30 | Display the verdict Revoked with the revocation date | 2 |
| 15 | FR31 | Display the verdict Not found with a uniform message | 2 |
| 16 | FR32 | Display the chain of custody in chronological order | 3 |
| 17 | FR33 | Record a scan event on every verification | 3 |
| 18 | FR35 | The current holder transfers custody to another account | 3 |
| 19 | FR37 | Append an accepted transfer to the chain of custody | 3 |
| 20 | FR49 | Raise a duplicate scan alert when one code appears in distant regions | 3 |

Authentication (FR01, FR03, FR05), revocation (FR41) and the audit log (FR43) are also Must requirements. They are absent from this list because they enable the product rather than define it: every web application has login, and few are chosen for it.

## Distribution across sprints

The course fixes four sprints. Requirements were assigned so that each sprint delivers something demonstrable on its own, and so that the class topics taught in a given sprint are the ones that sprint needs.

| Sprint | Dates | Theme | FR | UR | DBR | Total |
|---|---|---|---|---|---|---|
| 1 | 15 Jul – 11 Aug | Accounts, company applications, administrator review | 14 | 1 | 3 | 18 |
| 2 | 12 Aug – 8 Sep | Product passports, QR codes, public verification | 12 | 6 | 4 | 22 |
| 3 | 9 Sep – 13 Oct | Chain of custody and verification analytics | 16 | 2 | 4 | 22 |
| 4 | 14 Oct – 10 Nov | Revocation, audit, notifications, hardening, deployment | 16 | 1 | 1 | 18 |
| | | | **58** | **10** | **12** | **80** |

FR56 (Sprint 4), FR57 and FR58 (Sprint 3) were added after this prioritisation, each found by attacking the system, and are counted here.

Why this order. A product passport is meaningless unless the company issuing it has been verified, so company verification comes first. Verification by a buyer is the core value and therefore lands in Sprint 2, early enough to be exercised for the rest of the semester. The chain of custody and the analytics both feed on verification data, so they follow in Sprint 3, which is also when the course teaches analytics. Revocation, audit and deployment close the product in Sprint 4, matching the deployment sessions.

## Capacity check, and what it changed

The course allocates 96 hours of work outside class across the semester. Sprint 1 is already under way, which leaves roughly 84 hours:

| Sprint | Weeks remaining | Hours |
|---|---|---|
| 1 | 1 | 6 |
| 2 | 4 | 24 |
| 3 | 5 | 30 |
| 4 | 4 | 24 |
| | | **84** |

There are 39 functional Must requirements. At an estimated two hours each, including templates, views, models and tests, they consume 78 of those 84 hours. That leaves almost nothing for deployment, for the diagrams due in Sprint 2, for the analytics work in Sprint 3, or for the time it takes to learn Django while building with it.

This is the honest position: **the Must set is at the limit of what one person can deliver, not comfortably inside it.** Two decisions follow.

**First, a named contingency.** If velocity falls behind by the Sprint 2 review, the following requirements are dropped in this order, and the decision is recorded here rather than left implicit:

1. FR27 bulk CSV registration
2. FR52 comparative scan trend
3. FR55 revocation email
4. FR51 analytics export
5. FR40 buyer ownership claim
6. FR44 audit log filtering
7. FR34 verification rate limiting
8. FR06 password reset

None of it had to be dropped. By the end of Sprint 3, FR40, FR44, FR51, FR52, FR55 and FR06 were built; FR27 and FR34 remain open in Sprint 4.

**Second, a carry-over into Sprint 2 was planned and then did not happen.** With one week of Sprint 1 left and Deliverable 1 consuming it, the plan was to commit only the documentation, the Django foundation and the data model, and to move the account and company-application requirements into the first week of Sprint 2. In the event all eighteen were delivered inside the sprint, together with eighty tests covering their acceptance criteria. See the [Sprint 1 Review](Sprint-1-Review).

The lesson recorded on the [Retrospectives](Retrospectives) page is not that the estimate was pessimistic. It is that the whole sprint's code landed in its final days, which left no room for anything to go wrong. The plan to carry work over was sound; what made it unnecessary was a schedule that should not be repeated.

## Requirements explicitly out of scope

Naming what is not being built prevents scope from creeping back in.

| Item | Reason |
|---|---|
| Running the records on a blockchain | A ledger guarantees a record was not changed, not that it was true when written. The claim enters the system at company verification, which is human either way. Records are signed and chained in the application instead; see the [Domain Model](Domain-Model) |
| Payments or subscription billing | The product is being validated, not commercialised, during this semester |
| A native mobile application | Verification must work in a phone browser with no install, which is the point |
| Automated integration with chamber of commerce registries | Depends on access to systems outside the project |
| Multi-tenant white labelling for certifying bodies | Adds architectural weight without serving the problem being validated |
