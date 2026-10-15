# Sprint 1 Review

**Period:** 15 July to 11 August 2026
**Review date:** 11 August 2026
**Sprint goal:** an authenticated user can apply as a company, and the administrator can decide on that application.

## What was committed

Eighteen requirements, all of them Must, taken from the [Requirements Prioritisation](Requirements-Prioritisation) page.

## What was delivered

Eighteen of eighteen. Every issue was closed with a comment naming the commit and the test that verifies its acceptance criteria.

| Requirement | What it does | Where the rule lives |
|---|---|---|
| FR01 | Create an account | `accounts.forms.RegistrationForm` |
| FR02 | Refuse an email address already in use | `RegistrationForm.clean_email` |
| FR03 | Log in with email and password | `accounts.forms.LoginForm` |
| FR04 | One authentication error for any bad credential | `LoginForm.clean` |
| FR05 | Log out and end the session | `accounts.views.log_out`, named `logout_view` when this review was written |
| FR07 | Submit a company application | `companies.views.application_create` |
| FR08 | Require a registry code from commercial companies | `CompanyApplicationForm.clean` |
| FR09 | Accept artisan companies without one | `CompanyApplicationForm.clean` |
| FR10 | Edit while pending or rejected | `Company.is_editable`, `Company.resubmit` |
| FR11 | Refuse edits once approved or suspended | `Company.edit_refusal_reason` |
| FR12 | List applications filtered by status | `companies.views.review_list` |
| FR13 | Approve a pending application | `Company.approve` |
| FR14 | Reject with a written reason | `Company.reject`, `RejectionForm` |
| FR17 | Show status and reason to the owner | `companies.views.application_detail` |
| UR08 | Show the cause beside the refused field | `templates/partials/field.html` |
| DBR01 | Store the company record | `companies.models.Company` |
| DBR11 | Store passwords as salted hashes | Django PBKDF2 through `set_password` |
| DBR12 | Require a reason on negative decisions | Model methods plus database constraints |

## How it was verified

Eighty automated tests, one or more per acceptance criterion, run against PostgreSQL. Where a requirement states a time bound, the test measures the response and asserts it rather than assuming it.

```
Ran 80 tests in 74.880s
OK
```

The requirements that state a rule about data are enforced twice: once in the model, so the application refuses the operation with a message a person can read, and once as a database constraint, so the rule holds even if a future view forgets it. Five constraints do this work: `company_track_matches_type`, `commercial_company_has_registry_code`, `negative_decision_states_a_reason`, `revocation_states_a_reason` and `custody_transfer_changes_holder`.

## Architecture decisions taken during the sprint

**The whole domain model was created now, not only the part Sprint 1 uses.** All six entities and their invariants exist after this sprint. Later sprints add views rather than migrations, and the shape of the data stops being an open question while the features that depend on it are being built.

**The business rules were carried over from the prototype contracts rather than reinvented.** The hackathon version of OriginPass enforced these rules in Solidity, where they had already been thought through: the verification track has to match the company type, a commercial company carries a registry code and an artisan workshop does not, an approved application is no longer editable by its owner, and a negative decision without a stored reason is not a decision. Each of these moved into the Django layer that owns it. The front end was written from scratch, because a React interface for a wallet-based application has nothing to say about a server-rendered one.

**PostgreSQL is required, with no fallback.** Development and deployment run the same engine, so a constraint that holds locally holds in production. The database runs from `docker-compose.yml`, which means no manual installation step.

**The front end uses no CSS framework.** One stylesheet, written for this project, driven by custom properties. This anticipates the HTML and CSS content of Sprint 2 and keeps the dependency list to what the application actually needs.

## What is not done

Product registration, QR codes, the public verification page, custody transfers and the analytics belong to later sprints. Their tables exist and carry their invariants; they have no views yet.

Outside the code, primary research on the [Problem Validation](Problem-Validation) page has still not been run. The instruments are written and the assumptions are stated, but no interview and no survey response has been recorded. This is the largest open item in the project and it does not depend on the code.

## Sprint 2

Twenty-two issues, from 12 August to 8 September 2026. See the [Backlog](https://github.com/users/Pacha-e/projects/1).
