# Daily Log

The professor asked for an individual, day-by-day log in place of team-meeting minutes,
since the project has one member. Each entry below is a day on which the work left a dated
record: a commit to the [repository](https://github.com/Pacha-e/OriginPass/commits/main),
a change to this wiki, or a session with the professor. A day with no such record is not
listed, rather than filled in from memory. The [Development Log](Development-Log) gives
the same work week by week, with what came next and what was in the way.

| Day | What was done | Evidence |
|---|---|---|
| Tue 14 July | Course presentation, pedagogical agreement and team definition; the project is approved as an individual one. | Course calendar |
| Tue 4 August | Created the repository and published the project documentation for Deliverable 1 to the wiki: product vision, requirements specification, prioritisation and domain model. | `66e6470`, `b6586a7`; wiki `047dfad` |
| Thu 6 August | Wrote the elevator pitch (class activity 9). Deliverable 1 was due that day. | `cd41d32`, `0a646bb`; wiki `c10da1a` |
| Tue 11 August | Built the Sprint 1 application: accounts, company applications and their review, with 80 tests. Added continuous integration, linting and the error pages, and the demonstration dataset. Recorded the Sprint 1 review and retrospective, and planned Sprint 2. | `aaafaab`, `3c4251b`, `c34adf9`; wiki `d20492d`, `896a116`, `3bc269b` |
| Wed 12 August | Replaced the claim that records were immutable with a signed, chained trail and the `verify_integrity` command, and raised FR56 for what it still does not cover. Licensed the project and built the deliverable video from a script. Recorded the desk research and planned the primary research. | `cc40fee`, `aa46733`, `f5290dd`; wiki `494fd18`, `844289a` |
| Thu 27 August | Added a component diagram page to the wiki. | wiki `467b69b` |
| Thu 3 September | Built the Sprint 2 features: product registration, the passport code, the QR and the public verification page. Drew the deployment, component and data models. | `ee82746`, `957a30f`, `18bd5c6` |
| Wed 9 September | Served the whole interface in Spanish (UR04), reorganised the repository, drew the Sprint 2 mockups and seeded passports and scans. Closed Sprint 2 with 179 tests and wrote its review and retrospective. | `ae46b12`, `4d5fbd5`, `d3c1449`, `7b5a827`; wiki `e29ff8d`, `3f2358d` |
| Thu 10 September | Attacked what Sprint 2 had built and fixed seven defects, among them a login that could send the user to another site and a key rotation that accused every older record. Made the database visible with pgAdmin and `describe_schema`, corrected the diagrams against the code, committed the compiled translations, and added FR57 and FR58. Merged Sprint 2 into `main`. | `1233530`, `266dc30`, `2f897fd`, `c67c30f`, `f5933d7`, `12e53ec`, `a344cc2`; wiki `c09cf45`, `ce26dda` |
| Wed 30 September | Built the Sprint 3 features: the duplicate-scan alert, the login lockout, the custody transfers and the claim with two codes, the region and journey on the public page, the scan cap, the analytics, the administrator's overview, revocation and the notification emails. | `c92207c`, `721fdb0`, `f04d52c`, `3cb91a5`, `bdb920a`, `f00eff7`, `185a35d` |
| Thu 1 October | Audited the Sprint 3 work against the requirements and fixed every defect found, each with a regression test. Gave the product its corporate image. In the follow-up with the professor, the rural artisan was named as one of the users; the interface was rewritten in plain language the same day, with an explanation on every action. | `20b9bb3`, `1d7118e`, `1b41862`; the audited work was committed on 6 October |
| Tue 6 October | Committed the audited Sprint 3 work and the plain-language interface, with 306 tests, and closed the Sprint 3 issues in the backlog. Prepared the Deliverable 3 edition of the video pipeline. | `cca4dbb`, `6f8396d` |
| Thu 15 October | Answered the Product Owner's feedback: private evidence of the craft and consent to publish in every application, a product photo editable after registration, and seven demonstration products from formal and informal producers (314 tests). Fixed the lint failures that kept continuous integration red, made the presentation kit run from a plain clone, and merged Sprint 3 into `main` through pull request #82. Reopened FR34, which had been closed without being built. Built the Sprint Review presentation and recorded the walkthrough of the new features; published the launch videos and updated this wiki. | `c60f7ff`, `1d6aa5e`, `ac2da6d`, `823b016`; [PR #82](https://github.com/Pacha-e/OriginPass/pull/82) |

## Presentation preparation, 15 October

The 15 October presentation preparation also replaced the raster slide PDF with vector
text and diagrams, exported each architecture model separately, and packaged the original
screenshots and all five launch videos for offline use. The kit gained `ABRIR-KIT.html`,
file checksums and database-specific demo links. The local 314-test suite, migration check,
lint and formatting passed before publication.

## Days without a record

Between the entries there are long stretches with no commit and no change to the wiki:
5 to 10 August, 13 August to 2 September apart from the 27th, 11 to 29 September, and
2 to 5 and 7 to 14 October. They are left out rather than reconstructed. The two longest,
13 August to 2 September and 11 to 29 September, are recorded on the
[Development Log](Development-Log) as what they were: weeks in which the sprint's work did
not move, and the reason each sprint's code landed in its last days.
