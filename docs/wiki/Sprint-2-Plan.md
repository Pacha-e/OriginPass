# Sprint 2 Plan

**Period:** 12 August to 8 September 2026
**Review date:** 8 September 2026

## Sprint goal

An approved company registers a product and gets a QR code for it, and any buyer scans that code and sees a verdict without an account. This is the sprint in which OriginPass first does the thing it exists to do.

## Scope

Twenty-two requirements: sixteen Must, three Should and three usability requirements that constrain how the verification page is built rather than what it does.

| Group | Requirements |
|---|---|
| Product registration | FR19, FR20, FR21, FR23, UR10, DBR02, DBR03, DBR04 |
| A company's own products | FR24, FR25, FR26 |
| QR code | FR22 |
| Public verification | FR28, FR29, FR30, FR31, DBR10 |
| Interface constraints | UR01, UR02, UR03, UR04, UR06 |

Acceptance criteria for all twenty-two are now written on their issues in the [Backlog](https://github.com/users/Pacha-e/projects/1).

## What Sprint 1 already paid for

Sprint 1 created the whole domain model rather than only the part it needed. Seven of this sprint's requirements are therefore already satisfied in the database layer, and their remaining work is the view that exercises them.

| Requirement | State after Sprint 1 | What is left |
|---|---|---|
| DBR02 Store the product record | Model holds every documented field | Nothing; confirm against the domain model |
| DBR03 Passport code uniqueness | `unique=True`, covered by a test | Nothing |
| DBR04 Product to company reference | Foreign key with `PROTECT`, covered by a test | Nothing |
| DBR10 Index the passport code | `db_index=True` | Measure the lookup and record the figure |
| FR21 Non-derivable passport code | `secrets.token_urlsafe`, covered by a test | Nothing |
| FR23 Match product type to company type | `Product.clean`, covered by a test | Surface it in the registration form |
| FR20 Refuse unapproved companies | `Product.clean`, covered by a test | Refuse at the view, with the reason |

## The interface language

UR04 asks for the interface in Spanish. The course asks for every deliverable and artefact in English. Both hold at once: **code, comments, commit messages and documentation stay in English; interface text goes through Django's translation machinery and is served in Spanish by default.**

```
LANGUAGE_CODE = "es-co"
LANGUAGES = [("es", "Español"), ("en", "English")]
MIDDLEWARE  += django.middleware.locale.LocaleMiddleware
locale/es/LC_MESSAGES/django.po
```

This is a retrofit as well as a rule for new work: the interface strings written in Sprint 1 have to be wrapped and translated too. Doing it in this sprint, while the interface is still small, costs less than doing it in Sprint 3 when it is not.

## Build order

The order follows what each step unblocks, not the numbering of the requirements.

1. **Internationalisation first.** Configure it, then retrofit the Sprint 1 templates and forms. Everything written afterwards is written translated, instead of being revisited a second time. Covers UR04.
2. **Product registration.** The form, the view and the company-side guard, with the type rule surfaced where the user can see it. Covers FR19, FR20, FR23, UR10, and confirms DBR02, DBR03, DBR04.
3. **A company's own products.** The list with its status filter, then the search, then the edit that leaves the passport code alone. Covers FR24, FR25, FR26.
4. **The public verification page.** The three verdicts, reachable with no session, recording a `ScanEvent` on each visit. This is the part a stranger sees, so it carries the usability requirements: UR01, UR02, UR03 and UR06. Covers FR28, FR29, FR30, FR31.
5. **The QR code.** Generated from the verification address, downloadable as PNG. It comes last because it encodes an address that has to exist first. Covers FR22.
6. **Measurement.** Record the passport-code lookup time and the verification page load over throttled 3G, with the tool and settings used. Covers DBR10 and UR06.

## Capacity

The course budgets six hours a week outside class, so about twenty-four hours across the four weeks. Twenty-two requirements in that budget is roughly an hour each, which is only realistic because seven of them are largely done and several others are small variations of work already in place.

The three Should requirements, FR25, FR26 and UR10, are the ones to drop first if the budget runs out. Everything else is Must.

## Risks

**The retrofit of Sprint 1 strings is larger than it looks.** Roughly one hundred and twenty strings across templates, form labels, help texts and validation messages. Mitigated by doing it first, in one pass, before the interface grows.

**A new dependency for the QR code.** It needs a library, which is the first runtime dependency added for a feature rather than for the framework. Choose one that generates PNG without a system package, so the setup steps in the README stay true.

**The verification page has no account behind it.** It is the only page a stranger can reach, which makes it the one place where rate limiting matters. FR34 covers this and belongs to Sprint 3, so this sprint should not assume the page is protected.

**The primary research is still not done.** It has now been carried for two sprints. It does not block any requirement here, which is exactly why it keeps slipping, and it is the item most likely to invalidate work already built.

## Definition of done

A requirement is done when its acceptance criteria are each covered by a test, the suite is green against PostgreSQL, continuous integration passes, and the issue is closed with a comment naming the commit and the test.
