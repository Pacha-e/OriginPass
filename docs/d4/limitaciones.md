# Limitations and future work: Entregable 4

Verified on 2026-10-29 on `d4/integracion-20261029`. Each limitation cites the file and line that support it. Items that could not be verified are marked. Where a fact depends on uncommitted worktree changes, it says so.

## 1. Technical

| ID | Limitation | Evidence |
|---|---|---|
| T1 | MVP on Django 5.2 and PostgreSQL 17. PostgreSQL is mandatory: the application does not fall back to another engine | `README.md:94-96`, `README.md:118`, `config/settings.py:87-89`, `requirements.txt:1-6` |
| T2 | Production configuration: gunicorn, WhiteNoise and HTTPS are in place on the AWS instance. Limits: the instance disk holds the database and media with no backup, and the sslip.io name and the IP depend on the instance running | `requirements.txt`; `config/settings.py:63`; `deploy/aws/README-AWS.md` |
| T3 | Email: in development, messages print to the server console; a deployment must configure an SMTP backend | `config/settings.py:143`; `README.md:175-176` |
| T4 | Scan region: taken from CDN headers only when `TRUST_GEO_HEADERS` is on; in development it is on whenever `DEBUG` is on | `config/settings.py:151`; `README.md:177-179` |
| T5 | Integrity: signatures use a server key derived from `SECRET_KEY`. Detects tampering by someone who holds only the database, not by whoever runs the server | `README.md:36-38`, `README.md:248-250`, `config/settings.py:33` |
| T6 | Fixed development credentials in the Docker files. The development compose publishes PostgreSQL on all interfaces; the kit binds it to loopback | `docker-compose.yml:8`, `docker-compose.yml:10`; `delivery/docker-compose.kit.yml:7`, `delivery/docker-compose.kit.yml:9` |
| T7 | Response times are checked in the test suite, not in a deployed environment | `README.md:189-190` |
| T8 | Health route: `/healthz/` exists in the working tree only, uncommitted. It is meant to return 200 when PostgreSQL answers a query and 503 when it does not. Neither result is verified against a live database | `pages/views.py:122-127`; `pages/urls.py:10` (working tree); `pages/tests/test_healthz.py` (uncommitted) |

## 2. Functional

| ID | Limitation | Evidence |
|---|---|---|
| F1 | Monad is not implemented. It is a roadmap goal; there is no contract and no testnet | `README.md:21-28`. A search for "monad" found no matches in the application modules (`accounts`, `companies`, `products`, `verification`, `audit`, `pages`, `config`); it appears only in the README, `docs/wiki/` and `tools/presentation/deck_content.py` |
| F2 | The QR resolves a registry entry. A photocopied label resolves the same passport; the verdict certifies the state of the record, not the physical piece | `README.md:32-35`; `config/urls.py:15` (comment on the path the QR encodes); `products/urls.py:19` (QR download) |
| F3 | Two verification routes: companies with an official registration code, and informal workshops verified by manual review of evidence of the craft. A person decides | `README.md:15`; `docs/wiki/Home.md:40`; `companies/urls.py:13-14` (approve, reject) |
| F4 | One image per product; no gallery | `README.md:16` |
| F5 | Demo photographs are illustrative and do not prove the product's origin | `README.md:16` |
| F6 | No bulk CSV registration (FR27) and no language switch (UR05) | `README.md:276` |
| F7 | No external publication of the integrity-chain head (FR56) | `README.md:276-277`, `README.md:248-252` |
| F8 | The per-minute request limit (FR34) is listed as pending in the Entregable 3 guide; the README describes only the per-hour scan limit | `docs/GUIA-DEMO.md:78-84`; `README.md:270-271` |

## 3. Validation and evidence

| ID | Limitation | Evidence |
|---|---|---|
| V1 | No usability or user-validation results with potential users | `docs/wiki/Problem-Validation.md:113` ("Pending"); `docs/wiki/Retrospectives.md:113`. A search for "usability test", "user test", "interview" and "usability" in `docs/wiki/` found no recorded results |
| V2 | No testimonials | A search for "testimon" in `docs/wiki/` found no matches |
| V3 | Demo figures are not real usage data. `seed_demo` fixes the scan counts per product, generates dates by formula, and creates the duplicate-scan alert | `companies/management/commands/seed_demo.py:153-218` (fixed counts), `:409-411` (dates by formula), `:444-465` (seeded alert); `README.md:148-153` |
| V4 | The copy alert shown in the demo is seeded data. Real detection is in `verification/views.py:133-142` and depends on the region (T4) | `verification/views.py:37`, `verification/views.py:133-142` |
| V5 | No production or real-user data. The kit includes no live database and no user uploads | `README.md:42`; `README.md:141-146` |

## 4. Deployment and status

| ID | Limitation | Evidence |
|---|---|---|
| D1 | Public URL: deployed at https://44-206-186-9.sslip.io (5 November 2026). It depends on the Learner Lab instance: while the instance is stopped, the URL does not answer | `deploy/aws/README-AWS.md`; `docs/d4/seguimiento.md` |
| D2 | No first-run test on a second laptop | `README.md:42` |
| D3 | Tests have not been re-run on this date | `docs/GUIA-DEMO.md:91-94` ("Estado verificado", 1 October) |
| D4 | The portable kit contains Sprint 3 code and demo; no live database, no user uploads, no personal signing key | `README.md:42` |

## 5. Future work (not committed)

- Publish the integrity-chain head outside the server (FR56). Monad is the planned target of that goal, not an implemented component (`README.md:25-28`, `README.md:276-277`).
- Bulk CSV registration (FR27) and language switch (UR05) (`README.md:276`).
- A per-product image gallery; currently one image per product (`README.md:16`).
- Validate with users and adjust to their findings (`docs/d4/backlog.md`, D4-04).
