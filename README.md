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

## Running the project locally

PostgreSQL is required; the application does not fall back to another engine.

```bash
docker compose up -d db          # PostgreSQL 17 on localhost:5432

python -m venv .venv
source .venv/Scripts/activate    # Linux and macOS: source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env             # then fill in SECRET_KEY
python manage.py migrate
python manage.py createsuperuser # this account is the platform administrator
python manage.py runserver
```

The application is then served at http://127.0.0.1:8000/.

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
├── config/           project settings, root URLs, landing page
├── accounts/         User model, registration, login, logout
├── companies/        Company model, applications and the administrator's review
├── products/         Product and CustodyTransfer models
├── verification/     ScanEvent model
├── audit/            append-only AuditEntry
├── templates/        base template, error pages and one folder per app
├── static/           the stylesheet and the favicon, written for this project
├── .github/workflows/ci.yml
├── docker-compose.yml
└── manage.py
```

Business rules live in the models, input validation in the forms, orchestration in the
views and presentation in the templates.

Documentation is kept in the Wiki rather than in the repository, so that a single copy
stays authoritative.

## Status

Sprint 1 delivers accounts, company applications and the administrator's review of them.
Product registration, the public verification page, custody transfers and the analytics
follow in later sprints; their tables already exist.

## Author

Emmanuel Hernández Melo — ehernandem@eafit.edu.co
