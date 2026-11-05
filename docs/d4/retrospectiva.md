> **Record of 29 October 2026.** This retrospective describes the Entregable 4 working tree on that date. Items that mention uncommitted files, the portable kit or Azure are superseded; see REPORTE-SUPERVISOR-D4.md, section 0, for the current status.

# Retrospective: Entregable 4 (DRAFT)

> **DRAFT.** Every point is PENDING VALIDATION BY EMMANUEL.
> Only facts verifiable in the repository on 2026-10-29 are included. No meetings or third-party opinions are recorded. Anything that could not be verified is marked as such.

## What to continue

| Point | Evidence | Status |
|---|---|---|
| Record progress in the daily log and the weekly development log | `README.md:64`; `docs/wiki/Daily-Log.md`; `docs/wiki/Development-Log.md` | PENDING VALIDATION BY EMMANUEL |
| Automated tests and CI on every push and pull request | `README.md:189-201`; `.github/workflows/ci.yml` (68 lines) | PENDING VALIDATION BY EMMANUEL |
| State what is not implemented instead of simulating it (Monad) | `README.md:25-28` | PENDING VALIDATION BY EMMANUEL |
| Integrity verification as a command that can run on a schedule | `README.md:241-246` | PENDING VALIDATION BY EMMANUEL |

## What to start

| Point | Evidence | Status |
|---|---|---|
| Record each test and deployment run with its date and commit hash before claiming a state | Last recorded run: 1 October, `docs/GUIA-DEMO.md:91-94` | PENDING VALIDATION BY EMMANUEL |
| Validate with users before delivery | `docs/wiki/Problem-Validation.md:113` ("Pending") | PENDING VALIDATION BY EMMANUEL |
| Clean up worktrees of finished tasks | `git worktree list`: three D4 worktrees marked "prunable" | PENDING VALIDATION BY EMMANUEL |
| Publish the deliverable as a Wiki entry, not as an attachment | `enunciado.txt`: "Create GitHub Wiki entry (NOT an attachment)" | PENDING VALIDATION BY EMMANUEL |

## What to stop doing

| Point | Evidence | Status |
|---|---|---|
| Carrying activities from one sprint to the next without a date or owner | Interviews and survey: `docs/wiki/Retrospectives.md:67` ("Third sprint carried."); `docs/wiki/Development-Log.md:261` and `:286` | PENDING VALIDATION BY EMMANUEL |
| Editing the same worktree without coordination | Uncommitted changes by another agent appeared between 10:25 and 10:30 while this documentation was being written (`git status --short`) | PENDING VALIDATION BY EMMANUEL |
| Subagent orchestration with no verifiable trace of its work in the repository | Branches `d4/design-20261029`, `d4/docs-20261029` and `d4/runtime-20261029` point to `81fbe6d`, the same as `main`, with no commits of their own (`git worktree list`). The repository holds no record of what verification was done on them | PENDING VALIDATION BY EMMANUEL: confirm whether that work existed outside the repository |

## Orchestration hypotheses checked against the record

| Hypothesis | Result | Evidence | Status |
|---|---|---|---|
| "Kit without migrations" | Holds only for the new, uncommitted kit script: `delivery/build_d4_kit.py:85` excludes files under `/migrations/`. If that kit's installer does not generate them, `migrate` will not create the app tables; not verified. The committed kit's installer does run `migrate` (`delivery/Setup-Portatil.ps1:41`), and its startup checks `migrate --check` (`delivery/Start-OriginPass.ps1:12`) | `delivery/build_d4_kit.py:85`; `delivery/Setup-Portatil.ps1:41`; `delivery/Start-OriginPass.ps1:12` | PENDING VALIDATION BY EMMANUEL (to be checked in the installation test, D4-05) |
| "Health check mapped wrongly" | Not identified in the record. `/healthz/` exists in the working tree only, uncommitted: view `pages/views.py:122`, route `pages/urls.py:10`; not present in HEAD (`git show HEAD:pages/urls.py`). `config/urls.py:9` includes the `pages` routes at the root. The compose healthchecks are `docker-compose.yml:13-17` and `delivery/docker-compose.kit.yml:12-16`. The published port differs: `docker-compose.yml:10` (5432 on all interfaces) and `delivery/docker-compose.kit.yml:9` (127.0.0.1:55432). Its 200 response against PostgreSQL is not verified | `pages/views.py:122`; `pages/urls.py:10`; `config/urls.py:9`; `docker-compose.yml:10,13-17`; `delivery/docker-compose.kit.yml:9,12-16` | PENDING VALIDATION BY EMMANUEL: state which failure was meant |
| "Diagrams not updated" | Listed as pending on 1 October. Not re-checked against the code in this write-up | `docs/GUIA-DEMO.md:78-84` | PENDING VALIDATION BY EMMANUEL |
