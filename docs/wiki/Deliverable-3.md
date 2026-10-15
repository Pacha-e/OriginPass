# Deliverable 3: MVP

**Course:** ST0251 Proyecto Integrador 1, 2026-2
**Team 1 — OriginPass.** Emmanuel Hernández Melo, carried out individually.
**Sprint covered:** Sprint 3, 9 September to 13 October 2026.

Sprint 3 makes OriginPass work end to end. A workshop issues a passport, the product
changes hands along a signed chain of custody, a buyer scans it and reads a verdict with
the whole journey of the product, and the workshop is warned when one of its codes is
scanned in two places at once. Fourteen of the eighteen requirements planned for Sprint 4
were built in the same sprint.

**Repository:** https://github.com/Pacha-e/OriginPass, branch `main`. Sprint 3 was merged
from `sprint-3-mvp` in [pull request #82](https://github.com/Pacha-e/OriginPass/pull/82)
once continuous integration passed.

**Presentation and video:** the [Sprint Review presentation](https://github.com/Pacha-e/OriginPass/releases/download/originpass-kit-portatil-2026-10-15/OriginPass-Entrega-3-presentacion.pdf)
and the [walkthrough of the new features](https://github.com/Pacha-e/OriginPass/releases/download/originpass-kit-portatil-2026-10-15/OriginPass-Entrega-3-recorrido.mp4); see section 4.

Text and diagrams in the presentation are vectors, so every label stays sharp at any
zoom. Each architecture model also opens on its own:
[deployment PDF](https://github.com/Pacha-e/OriginPass/releases/download/originpass-kit-portatil-2026-10-15/deployment-model-Deployment-model.pdf),
[components PDF](https://github.com/Pacha-e/OriginPass/releases/download/originpass-kit-portatil-2026-10-15/components-model-Component-model.pdf),
[data PDF](https://github.com/Pacha-e/OriginPass/releases/download/originpass-kit-portatil-2026-10-15/data-model-Data-model.pdf).
The kit adds each model as SVG and high-resolution PNG, and the original screenshots.

> **Scope.** OriginPass is an MVP built on Django and PostgreSQL. Its records are signed
> and chained in the application; anchoring the head of that chain on Monad, so that
> verification stops depending on whoever runs the server, is the Sprint 4 goal. A
> photocopied QR resolves the same passport, so a verdict certifies the state of the
> record, not by itself the physical piece: the piece still has to match its photograph
> and description.

---

## 1. Architecture and data

Every diagram is a draw.io file in [`docs/diagrams/`](https://github.com/Pacha-e/OriginPass/tree/main/docs/diagrams),
exported to PNG in [`docs/diagrams/export/`](https://github.com/Pacha-e/OriginPass/tree/main/docs/diagrams/export).
**What changed in Sprint 3 is drawn in orange in each one**, with its own legend entry, so
the change can be read off the diagram as well as from the lists below.

### 1.1. Deployment diagram

[`deployment-model.drawio`](https://github.com/Pacha-e/OriginPass/blob/main/docs/diagrams/deployment-model.drawio) ·
[PNG](https://github.com/Pacha-e/OriginPass/blob/main/docs/diagrams/export/deployment-model-Deployment-model.png)

| Node | Software | Talks to |
|---|---|---|
| Buyer's phone | Any mobile browser, a camera that reads QR codes | Application server, HTTPS |
| Company or administrator workstation | Any desktop browser | Application server, HTTPS |
| Application server | Ubuntu 24.04, Python 3.12, Django 5.2 | Database (TCP 5432), mail service (SMTP 587) |
| Database server | PostgreSQL 17 | — |
| Mail service *(new)* | Any SMTP provider; Django's console backend in development | — |
| GitHub | Repository, wiki, backlog, Actions runner with `postgres:17-alpine` | — |

**Changes in Sprint 3**

- **Mail service.** The notifications (FR53 decisions on an application, FR54 transfer
  offers, FR55 revocations) and the password reset link (FR06) leave the application
  server over SMTP. In development the same calls print the message on the console, so
  the code is the same in both.
- **CDN headers.** The region of a scan (FR33) is read from the geolocation headers a CDN
  adds (`CF-Region`, `CF-IPCountry`). They are trusted only when the deployment declares a
  CDN in front (`TRUST_GEO_HEADERS`), because anywhere else a client could forge them and
  raise false copy alerts against a genuine producer.
- **Database.** Two new tables, two new columns on the company and one on the transfer,
  listed in 1.3.

### 1.2. Component diagram

[`components-model.drawio`](https://github.com/Pacha-e/OriginPass/blob/main/docs/diagrams/components-model.drawio) ·
[PNG](https://github.com/Pacha-e/OriginPass/blob/main/docs/diagrams/export/components-model-Component-model.png)

One component per Django app. Business rules live in the models, validation in the forms,
and the views orchestrate. Each function drawn is a view reachable from the interface.

| Component | Responsibility | Added in Sprint 3 |
|---|---|---|
| `accounts` | Accounts, sessions, roles; outgoing email | Login lockout after five failures in fifteen minutes (FR57); password reset with Django's signed, expiring tokens (FR06); the notification module (FR53–FR55) |
| `companies` | Applications and their review | Suspension and reactivation with a stored reason (FR15, FR16); public profile of an approved company (FR18); private evidence of the craft for workshops without a registry, and consent to publish the profile |
| `products` | Passports, QR, chain of custody, company analytics | Offering, accepting or declining a transfer, and claiming a product with two codes (FR35–FR40); analytics by day, region and product, with the trend against the previous period and a CSV export (FR46–FR49, FR51, FR52); revocation by the company and by the administrator (FR41, FR42); the platform overview (FR50); the photo of a product editable after registration |
| `verification` | The public verdict page | The journey of the product (FR32), the region of each scan (FR33), the duplicate-scan alert (FR49), a cap of 60 recorded scans per address per hour (FR58) |
| `audit` | Signed, chained trail of every status change | The administrator's audit log, filtered by actor, action and date, with the integrity of the whole chain checked on every view (FR44, FR45) |
| `pages` | The landing page and the photo credits | Redesigned with the corporate image |

### 1.3. Data model

[`data-model.drawio`](https://github.com/Pacha-e/OriginPass/blob/main/docs/diagrams/data-model.drawio) ·
[PNG](https://github.com/Pacha-e/OriginPass/blob/main/docs/diagrams/export/data-model-Data-model.png)

Eight tables in PostgreSQL 17. **Changes in Sprint 3:**

| Change | Table | Why |
|---|---|---|
| New table | `accounts_loginattempt` (email, ip_address, failed_count, first_failed_at, locked_until, last_attempt), unique per (email, ip_address) | FR57: a streak of failures per address and origin |
| New table | `products_alert` (product, scan, kind, created_at), unique per (product, scan) | FR49: one alert per suspicious scan |
| New column | `products_custodytransfer.transfer_code` (uuid, unique) | FR40: the code the seller hands over at the sale |
| New constraint | `custody_transfer_one_open_offer`: partial unique index on `product_id` where `state = 'INITIATED'` | A product is offered to one account at a time, so it cannot be sold twice, even under concurrent requests |
| New columns | `companies_company.evidence_notes` (text, private) and `publish_consent` (boolean) | A workshop without a registry describes the evidence of its craft for the reviewer; every applicant agrees to the public profile |

The rules that can be stated in SQL are held by the database as well as by the
application: five check constraints and four unique constraints, all named in the diagram,
so they hold even for a write that never goes through the application.

---

## 2. Corporate image

The full brand sheet, with the reasoning behind each choice, is in
[`docs/brand/`](https://github.com/Pacha-e/OriginPass/tree/main/docs/brand).

**Logo.** A **P** whose bowl is concentric rings. Seen from above, a sombrero vueltiao is
rings of braided caña flecha; read again, the rings are a fingerprint, the identity that
cannot be copied. [`originpass-logo.svg`](https://github.com/Pacha-e/OriginPass/blob/main/static/brand/originpass-logo.svg)

**Slogan.** *El origen no se imita.*

**Palette.**

| Name | Hex | Role |
|---|---|---|
| Añil | `#1E2B58` | Brand, headings, primary actions: the natural dye of the region's textiles and the ink of security printing |
| Caña flecha | `#D9C28A` | The woven thread and the rings; never text |
| Papel | `#F3F4EE` | Page background |
| Sello | `#17694A` | Verdict *Auténtico* |
| Carmín | `#A3253C` | Verdict *Anulado* (revoked) and refusals |
| Ámbar | `#86560A` | Verdict *No encontrado* and pending states |

Every text colour clears a contrast of 4.5 to 1 against its background (UR09).

**Typography.** Headings in Bahnschrift, the DIN of official forms and road signs; body
text in the system face; passport codes in OCR-B where it is installed, the face of a
passport's machine-readable zone.

**Written for the people who use it.** One of the target users is the rural artisan or
farmer, often on a phone. Every action carries a sentence saying what it does: a tooltip
with a mouse, printed under the button on a phone. Every term has a "?" that opens its
meaning in place, every form field explains itself before the input with an example
inside it, and the interface uses one plain word per idea: *producto*, *entregar*,
*código de entrega*, *recibir*, *anular*. A test fails if the technical vocabulary comes
back. Real photographs of the crafts, from Wikimedia Commons, are credited on the site's
credits page.

**The identity in the product.** The public verdict is laid out as the data page of a
passport: a guilloche seal stamped once in the colour of the answer, the product's fields,
and the machine-readable strip at the foot. A strip of the vueltiao's woven zigzag runs
under the header of every page.

| Screen | |
|---|---|
| Landing | ![](https://raw.githubusercontent.com/Pacha-e/OriginPass/main/docs/brand/screenshots/01-inicio.png) |
| Verdict *Auténtico* with the journey of the product | ![](https://raw.githubusercontent.com/Pacha-e/OriginPass/main/docs/brand/screenshots/05-veredicto-autentico.png) |
| Verdict *Anulado* with its reason | ![](https://raw.githubusercontent.com/Pacha-e/OriginPass/main/docs/brand/screenshots/06-veredicto-revocado.png) |
| Verdict on a 360 px phone | ![](https://raw.githubusercontent.com/Pacha-e/OriginPass/main/docs/brand/screenshots/30-movil-veredicto.png) |
| Company analytics and the copy alert | ![](https://raw.githubusercontent.com/Pacha-e/OriginPass/main/docs/brand/screenshots/12-empresa-analitica.png) |
| Passport with an open offer and its transfer code | ![](https://raw.githubusercontent.com/Pacha-e/OriginPass/main/docs/brand/screenshots/11-empresa-detalle-oferta.png) |
| Administrator overview | ![](https://raw.githubusercontent.com/Pacha-e/OriginPass/main/docs/brand/screenshots/20-admin-panel.png) |
| Audit log | ![](https://raw.githubusercontent.com/Pacha-e/OriginPass/main/docs/brand/screenshots/24-admin-auditoria.png) |

---

## 3. Repository

**Repository:** https://github.com/Pacha-e/OriginPass. The project is carried out
individually, so every commit is by Emmanuel Hernández Melo, and each commit message
states what changed and why.

- [`requirements.txt`](https://github.com/Pacha-e/OriginPass/blob/main/requirements.txt)
  lists every library needed to run the program; `requirements-dev.txt` adds the pinned
  linter.
- The [README](https://github.com/Pacha-e/OriginPass/blob/main/README.md) has the commands
  to run it with their parameters, the demonstration accounts and the settings a
  demonstration depends on.
- `python manage.py seed_demo` builds a dataset that shows every Sprint 3 feature: a
  product that travels workshop → distributor → private buyer, an open offer with its
  transfer code, a month of scans from several regions with a duplicate-scan alert, a
  revoked passport, a pending application, and seven products from a formal company and
  an informal workshop.
- The Windows presentation kit is in [`delivery/`](https://github.com/Pacha-e/OriginPass/tree/main/delivery):
  two PowerShell scripts that start the database, install the dependencies, create a
  fresh local key, migrate, load the demonstration data and verify the integrity chains,
  and a [guide](https://github.com/Pacha-e/OriginPass/blob/main/delivery/LEEME-PORTATIL.md)
  listing everything that has to be running and open to present. The scripts run from the
  [kit archive](https://github.com/Pacha-e/OriginPass/releases/tag/originpass-kit-portatil-2026-10-15)
  and from a plain clone.
- The presentation is built from
  [`tools/presentation/`](https://github.com/Pacha-e/OriginPass/tree/main/tools/presentation)
  and the walkthrough is recorded from the running application by
  [`tools/video/record_features.py`](https://github.com/Pacha-e/OriginPass/blob/main/tools/video/record_features.py),
  so both can be rebuilt whenever the product changes.

The [portable kit](https://github.com/Pacha-e/OriginPass/releases/download/originpass-kit-portatil-2026-10-15/OriginPass-Portatil.zip)
works without internet: extract it whole and open `ABRIR-KIT.html`, which links the
presentation, each diagram, the original screenshots, the script, the feature
walkthrough, the five launch videos and a snapshot of this wiki. `Verificar-Kit.ps1`
checks every packaged file against `KIT-MANIFEST.json`, which records the source commit.
`Setup-Portatil.ps1` waits for PostgreSQL, prepares the demonstration data and writes
`ABRIR-DEMO.html` with the passport links of that machine. It needs Python 3.12 and
Docker Desktop installed beforehand.

**Verified.** Continuous integration runs the migration check, the 314 tests against
PostgreSQL 17, the linter and the formatter on every pull request and every push to
`main`, and all four passed on the [run that cleared pull request #82](https://github.com/Pacha-e/OriginPass/actions/runs/38702483356).
`python manage.py verify_integrity` reports every signed chain intact on the demonstration
data.

---

## 4. Video

The Deliverable 3 video is a **walkthrough of every new feature, recorded from the running
application, with a caption on screen for each step** (3:13, 1920×1080):

[![Walkthrough of the Deliverable 3 features](https://raw.githubusercontent.com/wiki/Pacha-e/OriginPass/images/videos/recorrido.jpg)](https://github.com/Pacha-e/OriginPass/releases/download/originpass-kit-portatil-2026-10-15/OriginPass-Entrega-3-recorrido.mp4)

It follows the order of the demonstration: the workshop issues a passport with its photo;
the buyer reads the verdict, the journey and the workshop's public profile; the workshop
hands the product to a distributor, who accepts it, and the distributor sells it to a
buyer, who claims it with the passport code and the transfer code; the journey grows; the
analytics raise the copy alert; the passport is revoked and the QR answers *Anulado*; and
the administrator reads the platform overview, the applications and the signed audit log.

The four parts the template asks for are covered as follows in the Sprint Review:

| Part | Length | Where |
|---|---|---|
| Pitch: team, project, problem, solution, where it is and where it is going | 1:00 | [Presentation](https://github.com/Pacha-e/OriginPass/releases/download/originpass-kit-portatil-2026-10-15/OriginPass-Entrega-3-presentacion.pdf), slides 1 to 3 and 19 |
| Requirements addressed | 1:00 | Presentation, slides 4 and 6 to 12 |
| Evidence of compliance | 2:00 | The walkthrough above, or the same steps live |
| Product Owner perception | 1:00 | Presentation, slide 14: what the Product Owner asked for on 15 October and how it was answered |

The five launch videos, narrated by Emmanuel, are on the [Videos](Videos) page.

---

## 5. Project management

### 5.1. Backlog

The [Backlog](https://github.com/users/Pacha-e/projects/1) holds one issue per requirement,
each with its acceptance criteria, sprint, MoSCoW priority and responsible person. The
full text of every requirement is on the [Requirements Specification](Requirements-Specification)
page.

| Sprint 3 | Status |
|---|---|
| FR18, FR32, FR33, FR35–FR40, FR46–FR50, FR57, FR58 | Done, each closed against its tests |
| UR07, UR09 | Done: every form control is a native element reached with the tab key, with a visible focus style; every text colour of the palette clears 4.5 to 1 |
| DBR05, DBR06, DBR07, DBR09 | Done: custody and scan records stored, accepted transfers unchangeable, no scan record deleted automatically |

Twenty-two of twenty-two.

| Sprint 4 | Status |
|---|---|
| FR06, FR15, FR16, FR41, FR42, FR43, FR44, FR45, FR51, FR52, FR53, FR54, FR55, DBR08 | Done ahead of plan |
| FR27, FR34, FR56, UR05 | Open |

FR34, a per-minute limit on verifications answered with a wait message, was closed by
mistake on 6 October and reopened on 15 October: what exists is FR58, which caps the
scan records and never refuses the verdict.

### 5.2. Individual daily log

The professor asked for a day-by-day individual log in place of team-meeting minutes,
since the project has one member: the [Daily Log](Daily-Log). The [Development Log](Development-Log)
holds the weekly account of what was done, what comes next and what is in the way.

### 5.3. Product Owner feedback

Two rounds of feedback shaped the sprint.

**Follow-up with the professor, 1 October.** One of the target users is the rural artisan
or farmer, so the interface has to be as simple as possible and every action has to say
what it does. Answered the same day with the plain vocabulary, the tooltips, the "?"
explanations and the field help described in section 2.

**Product Owner, 15 October.** Emmanuel, as Product Owner, asked for an obvious way to add
the photograph of a product that is already registered, more variety in the demonstration,
and explicit coverage of both formal companies and informal workshops. Answered with:

- the photo of a product can be added or replaced when it is edited, and a test checks
  that the public page then shows it;
- an artisan workshop without a NIT or a chamber registration describes the evidence of
  its craft, which only the reviewer reads, and every applicant consents to the public
  profile before applying;
- the demonstration data grew to seven products, from a formal textile company and an
  informal basketry workshop as well as the original workshops.

The demonstration businesses and products are fictitious.

### 5.4. Retrospective

The Sprint 3 retrospective is on the [Retrospectives](Retrospectives) page.

---

## 6. Sprint Review

The review is given in class with the [presentation](https://github.com/Pacha-e/OriginPass/releases/download/originpass-kit-portatil-2026-10-15/OriginPass-Entrega-3-presentacion.pdf)
and a live demonstration on the demonstration data, in the order of the walkthrough in
section 4. What was committed, what was delivered and how it was verified is on the
[Sprint 3 Review](Sprint-3-Review) page.
