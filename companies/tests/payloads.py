"""What a person types into the application form, as the form receives it.

Separate from `testing.factories`, which builds stored records: these are the raw
POST bodies, so a test can start from a valid one and change the single field it
is about with `COMMERCIAL_APPLICATION | {"registry_code": ""}`.
"""

from companies.models import CompanyType, VerificationTrack

COMMERCIAL_APPLICATION = {
    "legal_name": "Artesanias La Bonga SAS",
    "company_type": CompanyType.COMMERCIAL,
    "verification_track": VerificationTrack.CHAMBER_OF_COMMERCE,
    "registry_code": "NIT-900123456-7",
    "description": "Distributor of certified crafts from Cordoba.",
    "location": "Monteria, Cordoba",
    "website": "https://labonga.co",
}

ARTISAN_APPLICATION = {
    "legal_name": "Taller Tuchin",
    "company_type": CompanyType.ARTISAN,
    # Left empty on purpose: the form decides the track for an artisan workshop.
    "verification_track": "",
    "registry_code": "",
    "description": "Family workshop weaving sombrero vueltiao.",
    "location": "Tuchin, Cordoba",
    "website": "",
}
