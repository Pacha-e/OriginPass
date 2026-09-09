"""Builders for the records the tests need, with sensible defaults.

Every factory takes the piece above it and creates one if it is not given, so a
test that only cares about a product writes `make_product()` and a test that
cares about who owns it passes the company in. Anything a test wants to be
specific about is an override; everything else stays out of the way.

The values are the ones the project's own examples use: a workshop in Tuchin
weaving sombrero vueltiao, and a distributor in Monteria.
"""

from accounts.models import User
from companies.models import Company, CompanyStatus, CompanyType, VerificationTrack
from products.models import PRODUCT_TYPE_BY_COMPANY_TYPE, Product

OWNER_PASSWORD = "Vueltiao-2026"
ADMIN_PASSWORD = "Admin-Pass-2026"

#: A status the company did not choose has to say why it holds it, or the
#: database refuses the row.
_DEFAULT_REASON = "Not enough evidence."


def make_user(email="weaver@tuchin.co", password=OWNER_PASSWORD):
    return User.objects.create_user(email, password)


def make_admin(email="admin@originpass.co", password=ADMIN_PASSWORD):
    return User.objects.create_superuser(email, password)


def make_company(
    owner=None,
    *,
    email="weaver@tuchin.co",
    status=CompanyStatus.PENDING,
    company_type=CompanyType.COMMERCIAL,
    **overrides,
):
    """A company in the status asked for, with an owner made if none is given."""
    is_commercial = company_type == CompanyType.COMMERCIAL
    needs_reason = status in (CompanyStatus.REJECTED, CompanyStatus.SUSPENDED)

    fields = {
        "legal_name": "Artesanias La Bonga SAS",
        "company_type": company_type,
        "verification_track": (
            VerificationTrack.CHAMBER_OF_COMMERCE
            if is_commercial
            else VerificationTrack.ARTISAN_REVIEW
        ),
        "registry_code": "NIT-900123456-7" if is_commercial else "",
        "description": "Crafts from Cordoba.",
        "location": "Monteria, Cordoba",
        "status": status,
        "status_reason": _DEFAULT_REASON if needs_reason else "",
    }
    fields.update(overrides)

    return Company.objects.create(owner=owner or make_user(email), **fields)


def make_approved_company(owner=None, **overrides):
    return make_company(owner, status=CompanyStatus.APPROVED, **overrides)


def make_product(company=None, **overrides):
    """A passport for an approved company, made alongside it if none is given.

    The product type follows the company type rather than being defaulted, so a
    factory can never build the crossed pair that FR23 forbids by accident.
    """
    company = company or make_approved_company()

    fields = {
        "product_type": PRODUCT_TYPE_BY_COMPANY_TYPE[company.company_type],
        "name": "Sombrero vueltiao 21 vueltas",
        "description": "Hand woven over three weeks.",
        "category": "Headwear",
        "origin": "Tuchin, Cordoba",
    }
    fields.update(overrides)

    return Product.objects.create(company=company, **fields)
