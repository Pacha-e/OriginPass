# Deliverable 4

Status on 5 November 2026. This page reports what is built and running, and what is still open. It records no review, interview or result that has not happened.

## Deployment

- The application runs on AWS EC2 (AWS Academy Learner Lab), Ubuntu 26.04.1 LTS, behind nginx with gunicorn and PostgreSQL on the instance.
- HTTPS with a Let's Encrypt certificate. HTTP redirects to HTTPS.
- The public address is in the README (section "Entregable 4"). It changes when the instance is restarted, so check that section before a demonstration.
- Installation and update steps: `deploy/aws/README-AWS.md`.

## What changed since Deliverable 3

- Password change for signed-in accounts.
- Printable QR codes at 300 dpi on US Letter sheets, twelve per page, with the OriginPass mark.
- The claim page reads the passport QR from the camera (HTTPS) or from an uploaded photo.
- Uploaded images are served by nginx on the instance.
- Five defects from the audit fixed, each with a regression test: locked login, offers on revoked passports, stale company edits, the demonstration seed outside DEBUG, and altered passports.

## Evidence

- Automated tests: 349 passed on PostgreSQL 17 in the last full run (commit `047089f`).
- The public health check answered `{"status": "ok"}` over HTTPS on 5 November 2026.

## Open items

- Usability validation with real users: not done.
- PVB validation: not done.
- External audit findings still open (custody signatures, concurrency, installer): listed in the project's audit notes.
- The remote CI run has not been checked from the development environment.
- The update script has not yet been run on the instance.