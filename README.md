# OriginPass

A web application that issues a verifiable digital passport for every physical product and records each change of custody along its journey, so that a buyer can confirm a product is genuine without having to trust the seller.

Course project for ST0251 Proyecto Integrador 1, 2026-2, Universidad EAFIT.

## The problem

Counterfeit goods are indistinguishable from genuine ones at the point of sale. This hits protected-origin crafts hardest: a machine-made copy of a sombrero vueltiao sells beside the real thing woven in Tuchín, and the buyer has no way to tell them apart. Producers lose the sale and the reputation, and the denomination of origin loses its meaning.

Printed certificates can be photocopied. Brand-owned checkers only work for large brands that can pay for them. Neither shows where the product has been.

## What OriginPass does

- Verifies companies through two tracks: commercial companies with an official registry code, artisan workshops through manual review.
- Issues one passport per product unit, identified by a code that cannot be guessed from other codes.
- Publishes a verification page reachable by QR that any buyer can open without an account.
- Records the chain of custody from the maker through distributors to the current owner.
- Analyses verification scans to surface signs of QR cloning, such as one passport being scanned in distant places within a short window.

## Documentation

All project documentation lives in the [Wiki](https://github.com/Pacha-e/OriginPass/wiki):

| Page | Contents |
|---|---|
| [Project Overview](https://github.com/Pacha-e/OriginPass/wiki/Project-Overview) | What the product is and how it works |
| [Product Vision Board](https://github.com/Pacha-e/OriginPass/wiki/Product-Vision-Board) | Vision, target group, needs, product, business goals |
| [Elevator Pitch](https://github.com/Pacha-e/OriginPass/wiki/Elevator-Pitch) | The pitch, in one minute |
| [Problem Validation](https://github.com/Pacha-e/OriginPass/wiki/Problem-Validation) | Evidence that the problem is real |
| [Requirements Specification](https://github.com/Pacha-e/OriginPass/wiki/Requirements-Specification) | Functional, usability and database requirements |
| [Requirements Prioritisation](https://github.com/Pacha-e/OriginPass/wiki/Requirements-Prioritisation) | MoSCoW prioritisation and sprint assignment |
| [Domain Model](https://github.com/Pacha-e/OriginPass/wiki/Domain-Model) | Entities, relationships and state machines |
| [Deliverable 1](https://github.com/Pacha-e/OriginPass/wiki/Deliverable-1) | Project definition and software requirements specification |
| [Sprint 1 Review](https://github.com/Pacha-e/OriginPass/wiki/Sprint-1-Review) | What was committed, delivered and how it was verified |

Requirements are tracked as issues in the [Backlog](https://github.com/users/Pacha-e/projects/1).

## Technology

- Python 3.12
- Django 5.2
- PostgreSQL 17, run from `docker-compose.yml`
- HTML, CSS and Django templates following the MVT pattern, with no CSS framework

## Language

The interface is served in **Spanish**; the code, the comments, the commit messages
and the documentation are written in **English**. Both hold at once because the
interface text goes through Django's translation machinery: the source strings are
English and `locale/es/LC_MESSAGES/django.po` is what a visitor actually reads.

Changing interface text means editing the English source string, then:

```bash
python manage.py makemessages -l es    # collect the strings into the .po
python manage.py compilemessages       # build the .mo Django serves
```

Both need GNU gettext installed. The compiled `.mo` is committed beside the `.po`, so a
fresh clone is served in Spanish without gettext; recompile it whenever the `.po` changes.

## Running the project locally

PostgreSQL is required; the application does not fall back to another engine.

To bring the project up on a machine that has never run it, and have it ready to
demonstrate, follow [docs/ready-to-present.md](docs/ready-to-present.md) instead of this
section. It covers the same ground step by step, states what each command should print,
and says what to do when one of them does not.

```bash
docker compose up -d             # PostgreSQL 17 on localhost:5432, pgAdmin on 127.0.0.1:8080

python -m venv .venv
source .venv/Scripts/activate    # Linux and macOS: source .venv/bin/activate
pip install -r requirements-dev.txt   # runtime dependencies plus the linter

cp .env.example .env             # then fill in SECRET_KEY
python manage.py migrate
python manage.py compilemessages # build the Spanish the interface is served in
python manage.py createsuperuser # this account is the platform administrator
python manage.py runserver
```

The application is then served at http://127.0.0.1:8000/.

To look at the interface with something in it, or to record the deliverable
walkthrough, populate a demo dataset:

```bash
python manage.py seed_demo
```

Five company applications, one in each status, and four passports issued by the two
approved ones, with one revoked so that verdict can be shown and a month of scans from
several regions behind them. One passport travels the whole chain of custody, from the
workshop to a distributor to a private buyer, and carries a duplicate-scan alert; another
has an open offer, so its transfer code can be shown. It prints each passport's
verification path and the transfer code, so the walkthrough does not need them looked up.

| Account | Role in the demo |
|---|---|
| `admin@originpass.co` | Platform administrator: overview, applications, audit log |
| `taller@tuchin.co` | Approved artisan workshop: passports, analytics, custody |
| `contacto@labonga.co` | Approved distributor: receives and passes on pieces |
| `comprador@correo.co` | Private buyer with no company: holds a piece |
| `info@mochilaswayuu.co` | Application still pending review |

Running it again adds nothing that is already there, and brings the text of an older
dataset up to date.

The data goes through the same model rules the application does, so it cannot create a
row the application would refuse: the product type is derived from the company rather
than written down, exactly as the registration view derives it.

Every account it creates shares one known password, which it prints, so it refuses
to run unless `DEBUG` is on.

Two settings matter for a demo and default to what development needs:

- Notification emails (FR53 to FR55, the password reset of FR06) are printed in the
  console running the server. A deployment sets `EMAIL_BACKEND` to its SMTP service.
- The region of a scan is read from the geolocation headers of a CDN only when
  `TRUST_GEO_HEADERS` is on, which it is whenever `DEBUG` is. Behind no such proxy a
  client writes those headers itself, so a deployment turns it on only behind one.

Generate a secret key with:

```bash
python -c "from django.core.management.utils import get_random_secret_key as k; print(k())"
```

## Tests and code quality

Every acceptance criterion of the current sprint has a test that asserts it, including
the response-time bounds the requirements state.

```bash
python manage.py test                              # the suite
python manage.py makemigrations --check --dry-run  # no model change left unmigrated
ruff check .                                       # lint
ruff format --check .                              # formatting
```

The same four commands run on every push and pull request through
[GitHub Actions](.github/workflows/ci.yml), against a real PostgreSQL service rather
than a substitute engine.

## Repository layout

```
OriginPass/
├── accounts/         User model, registration, login, logout
├── companies/        Company model, applications and the administrator's review
├── products/         Product and CustodyTransfer models, passports and QR codes
├── verification/     the public verification page and its ScanEvent record
├── audit/            append-only AuditEntry and the integrity checks
├── pages/            the landing page
├── config/           settings, root URLs, WSGI and ASGI entry points
├── templates/        base template, shared partials and the error pages
├── test_support/     factories and helpers shared by the apps' test suites
├── locale/es/        the Spanish the interface is served in
├── static/           the stylesheet, the favicon and the brand marks
├── docs/brand/       logo, slogan, palette and screenshots of the identity
├── docs/diagrams/    deployment, component and data models
├── tools/video/      builds the deliverable presentation video from a script
├── .github/workflows/ci.yml
├── docker-compose.yml
└── manage.py
```

Each app owns everything that belongs to it: its models, its views, its templates
under `<app>/templates/<app>/` and its tests under `<app>/tests/`. `config` holds
configuration and nothing else, which is why the landing page lives in `pages`
rather than there.

Business rules live in the models, input validation in the forms, orchestration in the
views and presentation in the templates.

## Integrity

Products, audit entries and custody records are signed with a key derived from
`SECRET_KEY`, which the database does not hold, and the audit trail and each chain of
custody are linked so that every record carries the signature of the one before it.
Rewriting a row invalidates its signature; removing one leaves a gap in the chain.

```bash
python manage.py verify_integrity
```

Walks everything and names the first record that does not hold up. Exits non-zero on a
failure, so it can be run on a schedule.

This makes tampering by anyone holding **only the database** detectable. It does not cover
whoever runs the server, who holds the key too. Closing that needs the head of the chain
published somewhere the operator does not control, which is a Sprint 4 option. The
reasoning, including why the records are not on a blockchain, is on the
[Domain Model](https://github.com/Pacha-e/OriginPass/wiki/Domain-Model) page.

Documentation is kept in the Wiki rather than in the repository, so that a single copy
stays authoritative.

## Status

Sprint 1 delivered accounts, company applications and the administrator's review of them.

Sprint 2 delivers what the product exists to do: an approved company registers a product,
gets a QR code for it, and any buyer scans that code and reads a verdict without an
account. It also serves the whole interface in Spanish.

Sprint 3 delivers the chain of custody and what the scans say. The current holder of a
piece offers it to another account, which accepts or declines; a buyer can claim it at the
point of sale with the passport code and a transfer code only the seller sees. The public
page shows the journey of each piece without naming anyone by their email. A company sees
its scans by day, region and product, compared with the period before, exports them as CSV
and is alerted when one passport is scanned from two regions within a day. Logins lock
after five failures in fifteen minutes, and scans are capped per address per hour.

Sprint 4 work already in place: revocation by the company and by the administrator with
a stored reason and an email to the holder, suspension and reactivation of a company, a
public profile per approved company, password reset by email and the audit log filtered
by actor, action and date. Bulk registration from CSV, the language switch and publishing
the head of the integrity chain externally remain open.

## Licence

Copyright © 2026 Emmanuel Hernández Melo.

Released under the **GNU Affero General Public License, version 3**. The full text is in
[LICENSE](LICENSE).

The AGPL was chosen over a permissive licence for a specific reason. OriginPass is meant
to be run as a service, and under a permissive licence anyone could take this code, run a
closed competing service on it and give nothing back. Section 13 of the AGPL closes that:
anyone who runs a modified version and lets other people use it over a network has to
offer them its source. Reading the code, learning from it, running it and modifying it are
all allowed; keeping the modifications secret while serving them to the public is not.

As the sole copyright holder I can license the same code differently to anyone who asks,
so this choice does not close any door.

## Author

Emmanuel Hernández Melo — ehernandem@eafit.edu.co
Universidad EAFIT, Medellín, Colombia
