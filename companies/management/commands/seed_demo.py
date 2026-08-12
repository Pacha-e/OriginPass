"""Populate the database with a small, believable set of demo records.

Used for the walkthrough recorded for the deliverable video and for looking at
the interface with something in it. Every account it creates shares one
password, which is why it refuses to run outside DEBUG unless forced.
"""

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from accounts.models import Role, User
from companies.models import Company, CompanyStatus, CompanyType, VerificationTrack

PASSWORD = "OriginPass-2026"

ADMIN_EMAIL = "admin@originpass.co"

APPLICATIONS = [
    {
        "email": "contacto@labonga.co",
        "legal_name": "Artesanias La Bonga SAS",
        "company_type": CompanyType.COMMERCIAL,
        "verification_track": VerificationTrack.CHAMBER_OF_COMMERCE,
        "registry_code": "NIT-900123456-7",
        "description": (
            "Distributor of certified crafts from Cordoba, working with twelve "
            "workshops across Tuchin and San Andres de Sotavento."
        ),
        "location": "Monteria, Cordoba",
        "website": "https://labonga.co",
        "outcome": "approve",
    },
    {
        "email": "taller@tuchin.co",
        "legal_name": "Taller Artesanal Tuchin",
        "company_type": CompanyType.ARTISAN,
        "verification_track": VerificationTrack.ARTISAN_REVIEW,
        "registry_code": "",
        "description": (
            "Family workshop weaving sombrero vueltiao from cana flecha, "
            "three generations in Tuchin."
        ),
        "location": "Tuchin, Cordoba",
        "website": "",
        "outcome": "approve",
    },
    {
        "email": "info@mochilaswayuu.co",
        "legal_name": "Mochilas Wayuu del Norte",
        "company_type": CompanyType.ARTISAN,
        "verification_track": VerificationTrack.ARTISAN_REVIEW,
        "registry_code": "",
        "description": "Wayuu weavers from Uribia producing mochilas and chinchorros.",
        "location": "Uribia, La Guajira",
        "website": "",
        "outcome": "pending",
    },
    {
        "email": "ventas@importadoraandina.co",
        "legal_name": "Importadora Andina SAS",
        "company_type": CompanyType.COMMERCIAL,
        "verification_track": VerificationTrack.OFFICIAL_REGISTRY,
        "registry_code": "NIT-800999111-2",
        "description": "Importer and reseller of assorted goods.",
        "location": "Bogota, Cundinamarca",
        "website": "https://importadoraandina.co",
        "outcome": "reject",
        "reason": (
            "The registry code does not match any record at the Chamber of Commerce. "
            "Send a copy of the certificate of existence and resubmit."
        ),
    },
    {
        "email": "contacto@ceramicaraquira.co",
        "legal_name": "Ceramica Raquira",
        "company_type": CompanyType.ARTISAN,
        "verification_track": VerificationTrack.ARTISAN_REVIEW,
        "registry_code": "",
        "description": "Pottery workshop in Raquira, Boyaca.",
        "location": "Raquira, Boyaca",
        "website": "",
        "outcome": "suspend",
        "reason": (
            "Three buyers reported pieces sold under this name that the workshop "
            "did not make. Suspended while the reports are checked."
        ),
    },
]


class Command(BaseCommand):
    help = "Create a small set of demo accounts and company applications."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Run even when DEBUG is off. These accounts share a known password.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG and not options["force"]:
            raise CommandError(
                "Refusing to run with DEBUG off. Every account created here shares "
                "the same known password. Pass --force if that is what you want."
            )

        admin = self._admin()
        created = 0

        for entry in APPLICATIONS:
            if User.objects.filter(email=entry["email"]).exists():
                self.stdout.write(f"  skipped {entry['email']}, already present")
                continue

            owner = User.objects.create_user(entry["email"], PASSWORD, role=Role.COMPANY)
            company = Company.objects.create(
                owner=owner,
                legal_name=entry["legal_name"],
                company_type=entry["company_type"],
                verification_track=entry["verification_track"],
                registry_code=entry["registry_code"],
                description=entry["description"],
                location=entry["location"],
                website=entry["website"],
                status=CompanyStatus.PENDING,
            )

            outcome = entry["outcome"]
            if outcome == "approve":
                company.approve(actor=admin)
            elif outcome == "reject":
                company.reject(actor=admin, reason=entry["reason"])
            elif outcome == "suspend":
                company.approve(actor=admin)
                company.suspend(actor=admin, reason=entry["reason"])

            created += 1
            self.stdout.write(f"  {company.legal_name} — {company.get_status_display()}")

        self.stdout.write(self.style.SUCCESS(f"\n{created} companies created."))
        self.stdout.write(f"Administrator: {ADMIN_EMAIL}")
        self.stdout.write(f"Password for every demo account: {PASSWORD}")

    def _admin(self):
        admin = User.objects.filter(email=ADMIN_EMAIL).first()
        if admin is None:
            admin = User.objects.create_superuser(ADMIN_EMAIL, PASSWORD)
            self.stdout.write(f"  administrator {ADMIN_EMAIL} created")
        return admin
