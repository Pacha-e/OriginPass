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
| [Problem Validation](https://github.com/Pacha-e/OriginPass/wiki/Problem-Validation) | Evidence that the problem is real |
| [Requirements Specification](https://github.com/Pacha-e/OriginPass/wiki/Requirements-Specification) | Functional, usability and database requirements |
| [Requirements Prioritisation](https://github.com/Pacha-e/OriginPass/wiki/Requirements-Prioritisation) | MoSCoW prioritisation and sprint assignment |
| [Domain Model](https://github.com/Pacha-e/OriginPass/wiki/Domain-Model) | Entities, relationships and state machines |
| [Deliverable 1](https://github.com/Pacha-e/OriginPass/wiki/Deliverable-1) | Project definition and software requirements specification |

Requirements are tracked as issues in the [Backlog](https://github.com/users/Pacha-e/projects/1).

## Technology

- Python 3.12
- Django 5
- PostgreSQL
- HTML, CSS and Django templates following the MVT pattern

## Running the project locally

The Django project is under development. Once the application package is in place, the steps are:

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then fill in the values
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The application is then served at http://127.0.0.1:8000/.

## Repository layout

```
OriginPass/
├── README.md
└── .gitignore
```

The Django application is added in Sprint 1. Documentation is kept in the Wiki rather than in the repository, so that a single copy stays authoritative.

## Author

Emmanuel Hernández Melo — ehernandem@eafit.edu.co
