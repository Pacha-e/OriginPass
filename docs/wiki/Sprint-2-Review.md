# Sprint 2 Review

**Period:** 12 August to 8 September 2026
**Review date:** 8 September 2026
**Sprint goal:** an approved company registers a product and gets a QR code for it, and any buyer scans that code and sees a verdict without an account.

This is the sprint in which OriginPass first does the thing it exists to do.

## What was committed

Twenty-two requirements: sixteen Must, three Should and three usability requirements that constrain how the verification page is built rather than what it does. The scope is on the [Sprint 2 Plan](Sprint-2-Plan) page.

## What was delivered

Twenty-two of twenty-two.

| Requirement | What it does | Where the rule lives |
|---|---|---|
| FR19 | Register a product as an approved company | `products.views.product_create` |
| FR20 | Refuse registration from an unapproved company, with the cause | `products.views.REFUSAL_BY_STATUS`, `Product.clean` |
| FR21 | Generate a passport code that cannot be derived from another | `products.models.generate_passport_code` |
| FR22 | Offer the QR as a downloadable PNG | `products.views.qr_download` |
| FR23 | Match the product type to the company type | `Product.clean`, `PRODUCT_TYPE_BY_COMPANY_TYPE` |
| FR24 | List a company's own products, filtered by status | `products.views.product_list` |
| FR25 | Search by name, category or passport code | `products.views.product_list` |
| FR26 | Edit the descriptive fields, never the passport code | `products.views.product_edit`, `ProductForm` |
| FR28 | Open the verification page with no session | `verification.views.verify` |
| FR29 | State the verdict Genuine | `verification.models.Verdict`, `verdict.html` |
| FR30 | State the verdict Revoked, with the date | `verification.views.verify` |
| FR31 | State the verdict Not found, identically for every unmatched code | `verification.views.verify` |
| UR01 | Fit the verification result on a 360 pixel screen | `static/css/originpass.css` |
| UR02 | Reach the verdict in at most two interactions | one GET from the scanned address |
| UR03 | State the verdict in words, not only in colour | `verification/verdict.html` |
| UR04 | Render the interface in Spanish | `locale/es/LC_MESSAGES/django.po` |
| UR06 | Load the verification page within 3 seconds on 3G | no script, one stylesheet, one query |
| UR10 | Keep product registration to five required fields | `products.forms.ProductForm` |
| DBR02 | Store the product record | `products.models.Product` |
| DBR03 | Enforce passport code uniqueness | `unique=True` on `passport_code` |
| DBR04 | Enforce the product to company reference | foreign key with `on_delete=PROTECT` |
| DBR10 | Index the passport code for fast lookup | `db_index=True` on `passport_code` |

## How it was verified

One hundred and seventy-nine automated tests, one or more per acceptance criterion, run against PostgreSQL 17 through [continuous integration](https://github.com/Pacha-e/OriginPass/actions). Sprint 1 ended with eighty.

```
Ran 179 tests in 77.723s
OK
```

Where a requirement states a time bound, the test measures the response and asserts it rather than assuming it: the verification page against the three seconds of UR06, the product list against the three seconds of FR24, and the passport-code lookup against a two hundred millisecond bound for DBR10.

The tests assert the Spanish a visitor reads, not the English source, because the requirement is about what reaches the reader. Continuous integration installs gettext and compiles the catalogue before running the suite; without that step every assertion about Spanish would pass against English and prove nothing.

## Architecture decisions taken during the sprint

**The interface is Spanish, the source is English.** UR04 asks for a Spanish interface; the course asks for every artefact in English. Rather than choose, the interface text goes through Django's translation machinery: the source strings stay English and `locale/es` holds what a visitor reads. This also cost nothing to extend — a visitor whose browser asks for English gets English, because the source strings are already that.

The one exception is `templates/500.html`, whose Spanish is written directly in the file. That page renders when something has just failed, which is exactly the moment not to depend on the translation machinery. The reason is stated in the template.

**The verification page was built by taking things away.** UR06 gives it a budget on 3G. It is met by not spending it: no script, one stylesheet, one indexed query and one row written. The page is the only one a stranger reaches, and it is the smallest.

**An unmatched code is answered with 200, not 404.** The page is a valid answer to a valid question. A 404 would let a browser or a QR scanner replace it with an error screen of its own, and the one thing this page cannot afford is to be replaced by something that does not say what it means.

**Every visit is recorded, including the ones that matched nothing.** A run of unmatched codes is somebody probing the code space, which is the signal that would be lost by recording only the successes. It is what the Sprint 3 analytics will read.

## Work done that the sprint did not ask for

**The repository was reorganised.** Each app now owns its own templates and its own tests; `config` holds configuration and nothing else, so the landing page moved to a `pages` app; the video tooling moved to `tools/`. Five near-identical company and product factories, one per test module, became one `test_support/factories.py`.

**A status change is now checked against the status it is made from.** `review_approve` approved whatever company it was given, so an administrator posting straight to that address could approve a company that had been rejected or suspended, with no record of the decision in between. Each transition now names the statuses it may be made from, the view reports the refusal instead of failing, and the review page stops offering a decision that has already been taken.

**Two checks were added that hold for the whole project rather than for one feature.** Every template is now compiled by the suite, so a tag typed wrong on a page no test opens is found by the suite rather than by a visitor. And every entry of the translation catalogue is checked for an empty translation, which gettext treats as a fall back to English rather than as an error.

## What is not done

Custody transfers and the analytics belong to later sprints. Their tables exist and carry their invariants; they have no views yet.

FR56, publishing the head of the integrity chain somewhere the operator does not control, remains open and belongs to Sprint 4.

Outside the code, the primary research on the [Problem Validation](Problem-Validation) page has now been carried for three sprints. The instruments are written and the assumptions are stated, but no interview and no survey response has been recorded. It does not block any requirement, which is exactly why it keeps slipping, and it is still the item most likely to invalidate work already built.

## Sprint 3

From 9 September to 13 October 2026. See the [Backlog](https://github.com/users/Pacha-e/projects/1).
