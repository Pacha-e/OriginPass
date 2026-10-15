# Development log

A record of how the work actually went, week by week: what was built, what came next, and what stood in the way. The project is carried out individually, so there is no meeting to minute; this is the log a team would otherwise reconstruct from memory, written while it was still true.

Each entry answers the same three questions, so that two weeks can be compared rather than merely read. Where a week produced something that can be pointed at — a commit, a requirement, a test count, a decision — it is named, because an entry that cannot be checked is not a record.

Entries are listed with the most recent first.

---

## Week 15 — 6 to 15 October 2026

**What was done**

- Committed the audited Sprint 3 work and the plain-language interface (`cca4dbb`, 306
  tests), closed the Sprint 3 issues in the backlog, and prepared the Deliverable 3 edition
  of the video pipeline (`6f8396d`).
- Answered the Product Owner's feedback (`c60f7ff`): an artisan workshop without a
  registry now describes the evidence of its craft, which only the reviewer reads, and
  every applicant consents to the public profile before applying (`companies.0002`); the
  photo of a product can be added or replaced after it is registered, with a test that the
  public page then shows it; the demonstration data grew to seven products from a formal
  company and an informal workshop. Eight new tests, 314 in all.
- Found continuous integration red on the Sprint 3 pull request: five runs had failed on
  lint alone, in the video tooling, while the suite itself passed. Fixed it (`1d6aa5e`)
  and merged Sprint 3 into `main` through
  [pull request #82](https://github.com/Pacha-e/OriginPass/pull/82) once the run passed.
- Built the Windows presentation kit: two PowerShell scripts that start the database,
  install the dependencies, create a fresh local key, migrate, load the demonstration data
  and verify the integrity chains, from the kit archive or from a plain clone (`ac2da6d`).
  The archive is published as a release asset rather than committed, since it carries
  rendered video.
- Checked the backlog against the code: FR34, a per-minute limit answered with a wait
  message, had been closed without being built. Reopened it.
- Built the Sprint Review presentation and recorded a walkthrough of every new feature from
  the running application, with a caption per step. Published the five launch videos,
  narrated by Emmanuel, on the [Videos](Videos) page.

**What comes next**

- The Sprint Review in class, and the Sprint 3 retrospective.
- Sprint 4: FR56 (publish the head of the integrity chain, with Monad as the target),
  FR34, FR27 and UR05, and the deployment.
- The primary research.

**What is blocking**

- Nothing technical. The presentation kit has been run on the development PC; it still
  has to be rehearsed on the machine used in class.

---

## Week 14 — 30 September and 1 October 2026

The days before the Deliverable 3 follow-up. The Sprint 3 features were built in two
days and then audited line by line against the requirements before anything was called
done, because the first report on the work said "done" for work that was not.

**What was done**

- Built the chain of custody (FR35–FR40), the company analytics (FR46–FR52), the
  duplicate-scan alert (FR49), the login lockout (FR57) and the scan cap (FR58), and the
  Sprint 4 work that fell out of them: revocation by company and administrator (FR41,
  FR42), suspension and reactivation (FR15, FR16), the public company profile (FR18),
  password reset (FR06), the filtered audit log (FR44) and the notification emails
  (FR53–FR55).
- Audited the result. The suite reported three errors in work reported as green;
  lint went from clean to fifty-four errors; no Sprint 3 issue had been closed. Confirmed
  by tests or live requests, and fixed, each with a regression test:
  - approving or rejecting an application failed with a template error
  - the public verification page showed the email address of every buyer in the chain
  - claiming a piece with the two codes reported success and moved nothing; the
    transfer code was shown nowhere, so the claim could not be made from the interface
  - an administrator's revocation ended on a missing page
  - accepting a transfer emailed the receiver that their product had been revoked
  - an account that no longer held a piece could still offer it, and a piece could have
    two open offers at once, so it could be sold twice
  - a long header on the public page, a long email at login, or `?days=abc` in the
    analytics answered with a server error
  - password reset, the public profile and suspension had code but no address, and the
    audit filters and the trend comparison had no code at all
- Gave the product its corporate image: the logo, the slogan *El origen no se imita*, the
  añil and caña flecha palette, and every page redesigned around it, in Spanish.
- Updated the three diagrams with the Sprint 3 changes marked in orange.

**Feedback from the follow-up (1 October)**

- The professor pointed out that one of the target users is the rural artisan or
  farmer. For them the interface has to be as simple as it can be, and every action
  has to say what it does. Done the same day: one plain word per idea (*entregar*,
  *código de entrega*, *anular*, *producto* instead of custody, transfer, revoke and
  piece), a sentence explaining each button (a tooltip with a mouse, printed under
  the button on a phone), a "?" beside each term that opens its meaning, help above
  every form field with an example inside it, the photo field opening the phone
  camera, 17px text, and real photographs of the crafts with their authors credited.
- Fixed the sample passport on the home page, whose last field spilled over its own
  border: its grid measured itself as two columns and drew one.

**What comes next**

- The Sprint Review and the retrospective.
- Record the video, including the Product Owner and user perceptions it now asks for.
- Close the Sprint 3 issues in the backlog with a reference to the test of each one.
- Sprint 4: FR56 (publish the head of the integrity chain), FR34, FR27, UR05, DBR09.

**What is blocking**

- Nothing technical. The open question for the professor is whether today's follow-up
  counts as the Product Owner meeting section 5.2 asks to be recorded.

---

## Weeks 12 and 13 — 11 to 29 September 2026

**What was done**

Nothing was committed and the wiki did not change. This entry is written rather than
omitted for the same reason as Weeks 7 and 8: the sprint ran for five weeks and its code
landed in the last two days, 30 September and 1 October, which is the pattern the Sprint 1
and Sprint 2 retrospectives both said to stop.

**What is blocking**

- Nothing external. The time was available and was not used.

---

## Week 11 — 9 and 10 September 2026

Two days, after the sprint review, spent attacking what Sprint 2 had built rather than adding to it. The sprint had closed green: twenty-two of twenty-two requirements, a passing suite, passing continuous integration. That is exactly the state in which a defect is least likely to be looked for, which is why it was worth looking.

**What was done**

- Ran an adversarial review loop over the whole codebase, with a second model reading the code independently and every one of its findings verified against the code before being acted on. Seven real defects were found and closed, each with a test written first that fails without the fix:
  - a login followed any address the link asked for, so `?next=https://elsewhere` handed the user to another site one second after they typed their password
  - the documented key-rotation procedure did nothing: after rotating, the integrity report accused every record written beforehand of having been altered
  - two administrators deciding at the same moment both succeeded, leaving two contradictory decisions in the audit trail
  - the administration site could revoke a product and rewrite the stored reason of a suspension, leaving nothing in the trail
  - editing a passport belonging to a suspended company returned a server error, and the demonstration dataset contains exactly that company
  - a double-clicked submit button on the application form returned a server error
  - a stale copy of a custody transfer could write itself over a resolution, putting a resolved handover back to Initiated
- Found that the running database was two migrations behind the code, missing both constraints that keep each chain of signed records linear. Nothing had caught it: the suite builds its own database from the migrations every run and never reads the one being worked in. The integrity command now refuses to report on a database that is behind.
- Made the database visible: a pgAdmin container in `docker-compose`, arriving with its connection already registered, and `manage.py describe_schema`, which reports every table and every rule the database enforces, read from the running database rather than from the models.
- Attacked the four diagrams against the code. The deployment model drew a WSGI server the project does not have and named four library versions it does not install; the component model omitted an entire app and misattributed its landing page; the data model documented five of the seven rules the database holds. All four now describe the system that exists.
- Rehearsed bringing the project up on a machine that has never run it, from a clean clone. It failed: twenty-one tests broke and every page came out in English, because Django reads translations from a compiled catalogue that was not committed and cannot be built without GNU gettext installed. UR04 asks for Spanish. The catalogue is now committed, with tests that fail if it ever drifts from its source.
- Wrote [`docs/ready-to-present.md`](https://github.com/Pacha-e/OriginPass/blob/main/docs/ready-to-present.md), which states what each step should print, and rehearsed it end to end a second time: 224 tests green on a clean clone with no gettext installed.
- Added FR57 and FR58 to the [Requirements Specification](Requirements-Specification), for rate limiting on the credential endpoints and a bound on anonymous scan records. Both are gaps found by attacking the system rather than by describing it, as FR56 was. Neither was implemented, because neither had a requirement behind it until now.
- Merged Sprint 2 into `main`.

**What comes next**

- Record the deliverable video, which is section 4 of Deliverable 2 and the last section still outstanding.
- Start Sprint 3: the chain of custody gets its views, and FR57 and FR58 get built.
- Audit what this week did not reach: the nineteen HTML templates, the stylesheet, the video tooling, and the accessibility and responsive requirements UR01, UR03, UR07 and UR09, none of which has been checked against a browser.

**What is blocking**

- Nothing is blocking. Docker was available again this week, so the suite ran locally as well as in continuous integration, and the single point of verification that closed Sprint 2 is no longer single.
- Primary research still has not started. Third sprint carried, and it is now the oldest open item on this page.

---

## Week 10 — 9 September 2026

Written the day after the sprint review date, which is itself the entry.

**What was done**

- Reorganised the repository: each app now owns its templates and its tests, `config` holds configuration only, the landing page moved to a new `pages` app, and the video tooling moved to `tools/`.
- Replaced five duplicated test factories with one shared `test_support/factories.py`, and the repeated company lookup in three views with a single manager method.
- Served the whole interface in Spanish, closing UR04, the last unstarted requirement of the sprint.
- Found and fixed a bug outside the sprint scope: an approval was applied whatever status the company held, so posting straight to that address could approve a company that had been rejected or suspended.
- Ran the suite green against PostgreSQL 17 through continuous integration: 179 tests, up from 80 at the end of Sprint 1. It stood at 224 by the end of the following week.
- Wrote the [Sprint 2 Review](Sprint-2-Review) and this sprint's retrospective.

**What comes next**

- Produce the Sprint 2 mockups and record the deliverable video, which are sections 2 and 4 of Deliverable 2.
- Export the architecture diagrams to PNG, for use outside the wiki. The wiki itself links the `.drawio` sources rather than attaching images, so that what a reader opens is the file the repository versions.
- Close the twenty-two Sprint 2 issues against the commit and the test that verify each one.

**What is blocking**

- Docker's engine returned an internal error for every API call on this machine, so the test database was unreachable and nothing could be verified locally. Continuous integration was the only thing that ran the suite. It passed, but the sprint closed with a single point of verification and that was not a choice.
- Primary research still has not started. Third sprint carried.

---

## Week 9 — 2 to 8 September 2026

**What was done**

- Built the Sprint 2 features in one pass: product registration with a generated passport code, the company's own product list with its status filter and its search, the passport edit that leaves the code alone, the downloadable QR image, and the public verification page with its three verdicts.
- Wrote a test for each acceptance criterion, including the time bounds UR06, FR24 and DBR10 state.
- Drew the deployment, component and data models required by Deliverable 2, section 1.
- Fixed a bug found by reading the rendered body of a passing test: a comment written across two lines is not stripped by Django and was being served to visitors as text. Added a check over every template so it cannot recur silently.

**What comes next**

- Close UR04, the interface in Spanish, which is the only requirement of the sprint still unstarted.
- Reorganise the repository before it grows any further.

**What is blocking**

- The sprint review is on 8 September and UR04 has not been started, so the sprint will close late.

---

## Weeks 7 and 8 — 19 August to 1 September 2026

**What was done**

No commit was made to the repository in either week. The only recorded work is a
component diagram page added to the wiki on 27 August.

This entry is written rather than omitted because the gap is the fact worth recording: the sprint ran for four weeks and the work landed in two of them. It is the same pattern the [Sprint 1 retrospective](Retrospectives) said to stop, carried into a second sprint.

**What comes next**

- The Sprint 2 features, which at this point have not been started.

**What is blocking**

- Nothing external. The time was available and was not used.

---

## Week 6 — 12 to 18 August 2026

**What was done**

- Replaced the claim that the audit trail was immutable with something true: every record is signed with a key the database does not hold, and each one carries the signature of the one before it, so a rewrite invalidates a signature and a deletion breaks the chain. Neither is prevented; both are detectable.
- Added `verify_integrity`, a command that walks every chain and names the first record that does not hold up, and corrected the documentation that had overstated the guarantee.
- Raised FR56 for the limit that remains: the head of the chain has to be published somewhere the operator does not control. Assigned to Sprint 4.
- Licensed the project under AGPL-3.0 and wrote the reasoning into the README.
- Rebuilt the deliverable video from a script rather than by hand.

**What comes next**

- Start the Sprint 2 features.

**What is blocking**

- Primary research still has not started.

---

## Week 5 — 5 to 11 August 2026

**What was done**

- Published the fourteen documentation pages to the wiki and recorded the seventy-seven requirements as issues in the backlog, one per requirement, with acceptance criteria written for the eighteen in Sprint 1.
- Wrote the elevator pitch.
- Built the Django application: the project skeleton, the whole domain model across five apps, and the views, forms and templates for the eighteen Sprint 1 requirements.
- Wrote eighty tests, one or more per acceptance criterion, and ran them against PostgreSQL.
- Closed the eighteen Sprint 1 issues, each with the commit and the test that verifies it.
- Held the Sprint 1 review and wrote the retrospective. See [Sprint 1 Review](Sprint-1-Review).

**What comes next**

- Run the producer interviews and the buyer survey on the [Problem Validation](Problem-Validation) page.
- Start Sprint 2: product registration, passport codes and QR, and the public verification page.
- Add continuous integration so the test suite runs on every push rather than only when I remember.

**What is blocking**

- Primary research still has not started. It has been on the plan since week 4 and did not move, so the four assumptions behind the product are still untested. Nothing in the code depends on it, which is exactly why it keeps being postponed, and it is the item most likely to invalidate work already done.
- Weeks 1 to 3 of this page are still empty and were not written at the time.

---

## Week 4 — 29 July to 4 August 2026

**What was done**

- Reviewed the hackathon prototype that OriginPass is based on and extracted the domain: actors, state machines and business rules.
- Decided the architecture for the Django rebuild: no blockchain, with the guarantee met by server-side hashing and append-only records.
- Decided to restore the chain of custody, which existed in the first prototype and was dropped in the second for time.
- Wrote the product vision, the product vision board, the requirements specification, the MoSCoW prioritisation and the Deliverable 1 document.
- Set up the repository and the wiki structure.

**What comes next**

- Register the repository link and the product vision board link in the teams spreadsheet.
- Record the Must requirements as issues in the GitHub Backlog with acceptance criteria.
- Run the producer interviews and the buyer survey defined on the [Problem Validation](Problem-Validation) page.
- Record the Deliverable 1 video.
- Scaffold the Django project and the data model.

**What is blocking**

- Deliverable 1 is due on 6 August and the artefacts from earlier weeks were not recorded as they were produced, so several are being written at once. The cause was leaving documentation until the code direction was settled. The fix is to write each artefact in the week it belongs to rather than in a batch.
- Primary research has not started, so the assumptions on the Problem Validation page are still untested.

---

## Week 3 — 22 to 28 July 2026

Not recorded as it passed. The repository did not exist yet — its first commit is dated 4 August — so there is nothing to reconstruct this week from, and it is left as it is rather than filled in from memory. The [retrospective](Retrospectives) treats that as the failure it was.

---

## Week 2 — 15 to 21 July 2026

Not recorded as it passed, and predating the repository in the same way as Week 3. The course work of these weeks survives in its own artefacts — the [Product Vision Board](Product-Vision-Board), the [Elevator Pitch](Elevator-Pitch) and the [Problem Validation](Problem-Validation) — but which of them belongs to which week is no longer knowable, and guessing would make this page less trustworthy rather than more complete.

---

## Week 1 — 14 July 2026

Course presentation, pedagogical agreement, team definition, and the first discussion of the product vision. Recorded afterwards from the course calendar rather than at the time, which is why it names what happened and claims nothing about how it went.
