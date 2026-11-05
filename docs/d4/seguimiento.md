# Follow-up: Entregable 4

Status on 2026-10-29. The items below were verified with `git` and repository searches. Unverified items are marked.

## How progress is recorded

| Channel | Where | What it records | Evidence |
|---|---|---|---|
| Individual daily log | Wiki, Daily Log page | One daily entry per person; the professor requested it instead of meeting minutes | `README.md:64`; `docs/wiki/Daily-Log.md` |
| Development log | `docs/wiki/Development-Log.md` | What was built each week, what comes next, what blocked it | `docs/wiki/Development-Log.md` |
| Sprint reviews | `docs/wiki/Sprint-1-Review.md`, `Sprint-2-Review.md`, `Sprint-3-Review.md` | Commitments, delivered work, how it was verified | `README.md:83-85` |
| Requirements backlog | Issues in a GitHub project | Requirements tracked as issues | `README.md:90` |
| Retrospectives | `docs/wiki/Retrospectives.md` | What to continue, start and stop | `README.md:88` |
| Commits | Branch history | Changes, with commit messages in English | `README.md:101-104`; `git log` |
| Product Owner meeting | No D4 record | Pending (backlog D4-17) | `docs/GUIA-DEMO.md:67-77` (open question to the professor) |

## Real state

| Item | State | Evidence |
|---|---|---|
| Branch `d4/integracion-20261029` | Points to `81fbe6d`, same as `main`. No commits of its own. The worktree was clean at the start and stopped being clean at about 10:25 (see the next row) | `git log main..HEAD` empty; `git status` empty at the start of the session |
| Uncommitted changes not made by this write-up | Modified: `pages/urls.py`, `pages/views.py`, `requirements.txt`, `README.md` (only the section added here). New: `deploy/`, `delivery/LEEME-PORTATIL-D4.md`, `delivery/build_d4_kit.py`, `delivery/verificar-kit-d4.py`, `pages/tests/test_healthz.py`. Authorship not confirmed | `git status --short`; `git diff --stat` (49 lines added, 31 of them in this README section) |
| `main` | `81fbe6d` (merge of PR #85, 2026-10-15). No Entregable 4 changes | `git log -n 3 main` |
| Subagent branches `d4/design-20261029`, `d4/docs-20261029`, `d4/runtime-20261029` | Their worktrees show `81fbe6d` and are marked "prunable" | `git worktree list` |
| `docs/d4/` | Did not exist when this write-up started. This write-up created the five files listed here. Other agents have since added `analitica.md`, `diagramas.md`, `PREGUNTAS-REVISION.md`, `requisitos-matriz.md`, `usabilidad-protocolo.md` and `vision-board.md` (uncommitted; not reviewed or referenced by this write-up) | `ls docs/d4` |
| AWS deployment | Deployed on 5 November 2026 at https://13-220-96-49.sslip.io. At the time of this update the instance did not answer from outside, which points to a stopped Learner Lab session: start it and check `/healthz/` before the demonstration | `deploy/aws/README-AWS.md`; `README.md` (Entregable 4) |
| Public URL | None | `README.md:139` |
| Health route | Exists in the working tree, uncommitted. Its 200 response against PostgreSQL is not verified | `pages/views.py:122`, `pages/urls.py:10`; docstring at `pages/views.py:123-127` |
| Tests | Not confirmed on this date. Last recorded run: 293 tests passing on 1 October | `docs/GUIA-DEMO.md:91-94` |
| Entregable 4 Wiki entry | Not published | `docs/wiki/` has no Entregable 4 page |
| Infographic | Not in the repository | A search for "infograf" found no matches |
| Interviews and survey | Not done | `docs/wiki/Problem-Validation.md:113` |
| Second-laptop test | Not done | `README.md:42` |
| Monad | Not implemented | `README.md:25-28` |

## Next follow-up steps

0. Agree who confirms the uncommitted worktree changes (D4-18) before running tests.
1. Run D4-06 and save the output with the commit hash.
2. Decide D4-02 and D4-03 before attempting D4-01.
3. Record each interview (D4-04) with date and role on the Problem Validation page.
4. Merge into `main` only with approval (D4-09).

This write-up did not change application code. It added documentation and one README section. No commit, no push.
