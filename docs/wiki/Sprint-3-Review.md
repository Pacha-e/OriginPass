# Sprint 3 Review

**Period:** 9 September to 13 October 2026
**Sprint goal:** a product changes hands along a signed chain of custody that any buyer can
read, and the company sees where its products are verified and when one of its codes is
being copied.

## What was committed

Twenty-two requirements: the chain of custody, the journey on the public page, the scan
record and its analytics, the duplicate-scan alert, the administrator's totals, the two
limits found by attacking the system (FR57 and FR58), keyboard access and contrast, and
the records they rest on. The scope and the reasoning are on the
[Requirements Prioritisation](Requirements-Prioritisation) page.

## What was delivered

Twenty-two of twenty-two, and fourteen of the eighteen requirements planned for Sprint 4.

| Requirement | What it does | Where the rule lives |
|---|---|---|
| FR18 | Public profile of an approved company | `companies.views.public_profile` |
| FR32 | The journey of the product on the public page, without anyone's email | `verification.views._public_chain` |
| FR33 | Record each scan with its region and device | `verification.views._region_for`, `ScanEvent` |
| FR35 | The current holder offers the product to another account | `products.views.transfer_initiate`, `TransferInitiateForm` |
| FR36 | The receiver accepts or declines | `products.views.transfer_respond` |
| FR37 | An accepted transfer joins the chain, signed and linked to the previous one | `CustodyTransfer` |
| FR38 | Refuse an offer from an account that does not hold the product, with the reason | `TransferInitiateForm.clean`, `ProductQuerySet.held_by` |
| FR39 | Refuse any transfer of a revoked product | `CustodyTransfer.clean` |
| FR40 | A buyer claims the product with the passport code and the transfer code | `products.views.transfer_claim`, `TransferClaimForm` |
| FR46–FR48 | Scans by day, by region and by product | `products.views.company_analytics` |
| FR49 | Alert when one passport is scanned in two regions within 24 hours | `verification.views`, `products.models.Alert` |
| FR50 | Companies and products by status, for the administrator | `products.views.admin_overview` |
| FR57 | Lock an email and origin for 15 minutes after five failures | `accounts.models.LoginAttempt` |
| FR58 | Record at most 60 scans per address per hour, always answering the verdict | `verification.views._under_scan_cap` |
| UR07 | Reach every form control with the tab key | Native controls, `static/css/originpass.css` focus styles |
| UR09 | Keep text contrast at 4.5 to 1 or more | The palette in `static/css/originpass.css` |
| DBR05, DBR06 | Store the transfers, and keep an accepted one unchanged | `products.models.CustodyTransfer` |
| DBR07, DBR09 | Store every scan, and delete none automatically | `verification.models.ScanEvent` |

| Built ahead of Sprint 4 | Where |
|---|---|
| FR06 password reset | `accounts/urls.py`, Django's signed, expiring tokens |
| FR15, FR16 suspension and reactivation | `companies.views.suspend_company`, `reactivate_company` |
| FR41, FR42 revocation by the company and by the administrator | `products.views.product_revoke`, `admin_revoke_product` |
| FR44 the filtered audit log | `audit.views.audit_log` |
| FR51, FR52 CSV export and the trend against the previous period | `products.views.company_analytics_csv`, `company_analytics` |
| FR53–FR55 the notification emails | `accounts.emails` |

FR43, FR45 and DBR08, the audit trail itself, were in place since Sprint 1, signed and
chained since 12 August.

## How it was verified

Three hundred and fourteen automated tests, run against PostgreSQL 17 through
[continuous integration](https://github.com/Pacha-e/OriginPass/actions) together with the
migration check, the linter and the formatter. Sprint 2 ended with one hundred and
seventy-nine.

Before anything was called done, the work was audited against the requirements, by tests
and by live requests. That audit found and fixed, each with a regression test written
first: an approval that failed with a template error, a public page that showed the email
of every buyer in the chain, a claim that reported success and moved nothing, a revocation
that ended on a missing page, an email that told a receiver their product had been
revoked, a product that could be offered twice at once, and three inputs that answered
with a server error.

Sprint 3 was merged into `main` through
[pull request #82](https://github.com/Pacha-e/OriginPass/pull/82) once the integration run
passed, and `verify_integrity` reports every signed chain intact on the demonstration data.

## Decisions taken during the sprint

**Who holds a product is derived, not stored.** The holder is the receiver of the last
accepted transfer, or the owner of the registering company when there is none. A stored
holder would be a second copy of a fact the chain already records, and the two could
disagree.

**One open offer per product, in the database.** A partial unique index allows a single
`INITIATED` transfer per product. Checked only in the view, two requests at the same
moment could both pass and sell the same product twice.

**The region of a scan is trusted only behind a declared CDN.** Anywhere else the
geolocation headers come from the client, and a forged region would raise false copy
alerts against a genuine producer.

**The public page names companies, never people.** The journey shows each business and
date; a private buyer appears without their email.

**The interface speaks the user's words.** After the follow-up on 1 October, every action
explains itself and the technical vocabulary was replaced by one plain word per idea,
guarded by a test.

## Feedback received

- **1 October, follow-up with the professor:** the rural artisan or farmer is one of the
  users, so the interface has to be as simple as possible. Answered the same day.
- **15 October, Product Owner:** a photo editable after registration, more variety in the
  demonstration, and formal and informal producers both covered. Answered with
  `companies.0002`, an edit-photo test and seven demonstration products.

## What is not done

FR27 (bulk registration from CSV), FR34 (a per-minute limit with a wait message), FR56
(publishing the head of the integrity chain outside the server) and UR05 (an English
interface) remain for Sprint 4.

Outside the code, the primary research on the [Problem Validation](Problem-Validation)
page has still not been run.

## Sprint 4

From 14 October to 10 November 2026. See the [Backlog](https://github.com/users/Pacha-e/projects/1).
