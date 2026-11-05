# Pitch and demo: Entregable 4

> **The demo runs on the public deployment.** It is served at `https://44-206-186-9.sslip.io` (AWS EC2, HTTPS; `docs/d4/backlog.md`, D4-01), with the local server at `http://127.0.0.1:8000/` (`README.md`) as the fallback. Neither the pitch nor the demo claims user results or a validated usability study.

## Preparation

With the virtual environment active (`README.md:128-129`):

```bash
docker compose up -d
python manage.py migrate
python manage.py seed_demo       # requires DEBUG on (README.md:170-171)
python manage.py runserver
```

`seed_demo` prints the passport codes, their verification paths and the transfer code (`README.md:151-153`). Emails appear in the same terminal (`README.md:175-176`), so keep it visible. `seed_demo` prints the demo accounts' shared password; this guide does not record it.

## Pitch (3 minutes)

| Time | Content | Backing |
|---|---|---|
| 0:00-0:30 | Problem: a copied product sells next to the original and the buyer cannot tell them apart. The vueltiao hat from Tuchín is the case. Printed certificates can be photocopied, and brand-owned checkers only serve large brands | `README.md:9-11` |
| 0:30-1:15 | Solution: one passport per unit, with a code that cannot be guessed and a QR that opens a verification page with no account. The page shows the custody trail | `README.md:3`, `README.md:17-18` |
| 1:15-2:00 | What exists today: a Django application on PostgreSQL; informal workshops reviewed by a person; company revocation, suspension and public profile; a signed audit chain | `README.md:15`, `README.md:23`, `README.md:234-239`, `README.md:273-275` |
| 2:00-2:40 | Limits: the QR certifies the registry state, not the physical piece; the signature depends on the server key; Monad is a roadmap item, not implemented | `README.md:25-28`, `README.md:32-38` |
| 2:40-3:00 | Status: deployed on AWS EC2 with HTTPS; no user testing yet. Next: validate with users and anchor the chain outside the server (FR56) | `deploy/aws/README-AWS.md`; `docs/wiki/Problem-Validation.md:113` |

## Demo (5 minutes)

| Time | Action | Route or command | What is shown | Fallback if it fails |
|---|---|---|---|---|
| 0:00-0:30 | Home page and verifier: paste a code from the `seed_demo` output | `/` (`pages/urls.py:8`); `/v/` (`config/urls.py:17`, `verification/urls.py:8`) | Verification field | `docs/brand/screenshots/01-inicio.png` |
| 0:30-1:30 | Authentic passport with its trail | `/v/<code>/` (`verification/urls.py:9`) | Verdict and custody trail, with no emails | `docs/brand/screenshots/05-veredicto-autentico.png` |
| 1:30-2:00 | Revoked passport and unknown code | `/v/<code>/` (`verification/urls.py:9`) | Revoked, with reason; code not found | `06-veredicto-revocado.png`, `07-veredicto-no-encontrado.png` |
| 2:00-3:00 | Workshop account: analytics and copy alert | Login (`accounts/urls.py:14`); analytics (`products/urls.py:13`); CSV (`products/urls.py:14`) | Scans by region and the copy alert | `12-empresa-analitica.png` |
| 3:00-3:40 | Custody: offer a piece and answer the offer | Offer (`products/urls.py:20`); respond (`products/urls.py:12`) | Pending offer and its answer | `13-empresa-custodia.png` |
| 3:40-4:20 | Administrator: dashboard, approval, audit | Dashboard (`products/urls.py:15`); approve (`companies/urls.py:13`); audit (`audit/urls.py:8`) | Totals, approval, audit log | `20-admin-panel.png`, `24-admin-auditoria.png` |
| 4:20-5:00 | Chain integrity | `python manage.py verify_integrity` (`README.md:241-243`) | Verification result | None |

**Notes for the demo**

- The copy alert in the demo is seeded (`companies/management/commands/seed_demo.py:444-465`). Real detection is in `verification/views.py:133-142`, and the region only comes from CDN headers when `TRUST_GEO_HEADERS` is on (`config/settings.py:151`).
- Scan counts are demonstration figures (`README.md:148-153`; `seed_demo.py:153-218`). They are not real usage.
- On the deployed instance new scans record no region (no CDN in front), so the alert does not fire live; show the seeded one and say so.
- If the deployed address does not answer, run the demo locally and say so.

## What is not claimed

- That Monad is implemented (`README.md:25-28`).
- That the deployment is production-grade: one Learner Lab instance, no backup, no outgoing email (`deploy/aws/README-AWS.md`).
- That potential users have validated the product (`docs/wiki/Problem-Validation.md:113`).
