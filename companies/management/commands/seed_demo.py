"""Populate the database with a small, believable set of demo records.

Used for the walkthrough recorded for the deliverable video and for looking at
the interface with something in it. Every account it creates shares one
password, which is why it refuses to run outside DEBUG unless forced.
"""

from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from accounts.models import Role, User
from companies.models import Company, CompanyStatus, CompanyType, VerificationTrack
from products.models import (
    PRODUCT_TYPE_BY_COMPANY_TYPE,
    Alert,
    AlertKind,
    CustodyTransfer,
    Product,
    ProductStatus,
)
from verification.models import DeviceCategory, ScanEvent, Verdict

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
            "Distribuidora de artesanías certificadas de Córdoba. Trabaja con doce "
            "talleres de Tuchín y San Andrés de Sotavento."
        ),
        "location": "Montería, Córdoba",
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
            "Taller familiar que teje sombrero vueltiao en caña flecha, "
            "tres generaciones en Tuchín."
        ),
        "location": "Tuchín, Córdoba",
        "website": "",
        "outcome": "approve",
    },
    {
        "email": "info@mochilaswayuu.co",
        "legal_name": "Mochilas Wayuu del Norte",
        "company_type": CompanyType.ARTISAN,
        "verification_track": VerificationTrack.ARTISAN_REVIEW,
        "registry_code": "",
        "description": "Tejedoras wayuu de Uribia que hacen mochilas y chinchorros.",
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
        "description": "Importadora y revendedora de mercancía variada.",
        "location": "Bogotá, Cundinamarca",
        "website": "https://importadoraandina.co",
        "outcome": "reject",
        "reason": (
            "El código de registro no coincide con ningún registro de la Cámara de "
            "Comercio. Envíe el certificado de existencia y vuelva a presentarla."
        ),
    },
    {
        "email": "contacto@ceramicaraquira.co",
        "legal_name": "Ceramica Raquira",
        "company_type": CompanyType.ARTISAN,
        "verification_track": VerificationTrack.ARTISAN_REVIEW,
        "registry_code": "",
        "description": "Taller de alfarería en Ráquira, Boyacá.",
        "location": "Ráquira, Boyacá",
        "website": "",
        "outcome": "suspend",
        "reason": (
            "Tres compradores reportaron piezas vendidas con este nombre que el "
            "taller no hizo. Suspendida mientras se revisan los reportes."
        ),
    },
]


#: Passports for the two approved companies. Sprint 2 is about products, so a
#: demo dataset without them shows none of what the sprint built.
#:
#: `owner_email` names the company that issues each one. The product type is not
#: written here: it follows from the company type (FR23), and stating it a
#: second time would be a chance for the two to disagree.
PASSPORTS = [
    {
        "owner_email": "taller@tuchin.co",
        "name": "Sombrero vueltiao 21 vueltas",
        "description": (
            "Tejido en caña flecha durante tres semanas. Veintiún pares de fibra "
            "en la trenza, la cuenta que marca el grado fino."
        ),
        "category": "Sombreros",
        "origin": "Tuchín, Córdoba",
        "scans": 7,
        "photo": "sombrero-vueltiao-21.jpg",
    },
    {
        "owner_email": "taller@tuchin.co",
        "name": "Sombrero vueltiao 15 vueltas",
        "description": "Grado de diario, tejido en el mismo taller.",
        "category": "Sombreros",
        "origin": "Tuchín, Córdoba",
        "scans": 2,
        "photo": "sombrero-vueltiao-15.jpg",
    },
    {
        "owner_email": "contacto@labonga.co",
        "name": "Mochila wayuu",
        "description": (
            "Mochila tejida en crochet por tejedoras wayuu de Uribia, distribuida desde Montería."
        ),
        "category": "Mochilas",
        "origin": "Uribia, La Guajira",
        "scans": 4,
        "photo": "mochila-wayuu.jpg",
    },
    {
        "owner_email": "contacto@labonga.co",
        "name": "Hamaca de San Jacinto",
        "description": "Hamaca de algodón tejida en telar vertical.",
        "category": "Tejidos",
        "origin": "San Jacinto, Bolívar",
        "scans": 1,
        "photo": "hamaca-san-jacinto.jpg",
        "revoked": (
            "Tres compradores la reportaron como copia hecha a máquina vendida con este nombre."
        ),
    },
]

#: Enough of a spread that the verification page has something to show and the
#: Sprint 3 analytics have something to read.
#: Photographs of each demonstration product, from Wikimedia Commons under free
#: licences; their authors are named on the credits page (pages.views).
PHOTOS = Path(__file__).parent / "demo_photos"

SCAN_DEVICES = [DeviceCategory.MOBILE, DeviceCategory.MOBILE, DeviceCategory.DESKTOP]

#: Where the scans come from, as a CDN would name the region. Spread so the
#: region chart of the analytics has a shape.
SCAN_REGIONS = ["Córdoba", "Córdoba", "Atlántico", "Bolívar", "Antioquia", "Bogotá D.C."]

#: An account with no company: the buyer at the end of a chain of custody.
BUYER_EMAIL = "comprador@correo.co"

#: The custody story the demo tells, for the passport named here: the workshop
#: hands it to the distributor, the distributor sells it to a buyer. The second
#: passport is left with an open offer, so its transfer code can be shown.
CUSTODY_STORY = {
    "product": "Sombrero vueltiao 21 vueltas",
    "handovers": [
        ("taller@tuchin.co", "contacto@labonga.co", "Entregado al distribuidor en Montería."),
        ("contacto@labonga.co", BUYER_EMAIL, "Vendido en la tienda de Cartagena."),
    ],
}
OPEN_OFFER = ("Sombrero vueltiao 15 vueltas", "taller@tuchin.co", "contacto@labonga.co")


class Command(BaseCommand):
    help = "Create a small set of demo accounts, company applications and passports."

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
                # Descriptive text only, written by an older version of this command.
                Company.objects.filter(owner__email=entry["email"]).update(
                    description=entry["description"], location=entry["location"]
                )
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

        issued = self._issue_passports(admin)
        self._tell_the_custody_story()
        self._raise_a_duplicate_scan_alert()

        self.stdout.write(self.style.SUCCESS(f"\n{issued} passports issued."))
        self.stdout.write(f"Administrator: {ADMIN_EMAIL}")
        self.stdout.write(f"Password for every demo account: {PASSWORD}")

    def _admin(self):
        admin = User.objects.filter(email=ADMIN_EMAIL).first()
        if admin is None:
            admin = User.objects.create_superuser(ADMIN_EMAIL, PASSWORD)
            self.stdout.write(f"  administrator {ADMIN_EMAIL} created")
        return admin

    def _issue_passports(self, admin):
        """One passport per entry, for the companies that are approved."""
        issued = 0

        for entry in PASSPORTS:
            company = Company.objects.filter(owner__email=entry["owner_email"]).first()
            if company is None or not company.can_register_products:
                continue
            existing = Product.objects.filter(company=company, name=entry["name"]).first()
            if existing is not None:
                self._refresh(existing, entry)
                self._attach_photo(existing, entry)
                self.stdout.write(f"  skipped {entry['name']}, already present")
                continue

            product = Product.objects.create(
                company=company,
                # FR23: the type follows from the company rather than being chosen.
                product_type=PRODUCT_TYPE_BY_COMPANY_TYPE[company.company_type],
                name=entry["name"],
                description=entry["description"],
                category=entry["category"],
                origin=entry["origin"],
            )

            if entry.get("revoked"):
                product.revoke(actor=admin, reason=entry["revoked"])

            self._attach_photo(product, entry)
            self._record_scans(product, entry.get("scans", 0))

            issued += 1
            self.stdout.write(
                f"  {product.name} — {product.get_status_display()} — /v/{product.passport_code}"
            )

        return issued

    def _attach_photo(self, product, entry):
        """Give the passport its photograph, once."""
        name = entry.get("photo")
        if not name or product.image:
            return
        with (PHOTOS / name).open("rb") as photo:
            product.image.save(name, File(photo), save=True)

    def _refresh(self, product, entry):
        """Bring a passport created by an older version of this command up to date.

        Only the descriptive text: its code and its company never change. A
        revoked passport is left as it is: it is a record, and the public page
        reads the date of its revocation from its last change.
        """
        if product.status == ProductStatus.REVOKED:
            return
        fields = {key: entry[key] for key in ("description", "category", "origin")}
        if any(getattr(product, key) != value for key, value in fields.items()):
            for key, value in fields.items():
                setattr(product, key, value)
            product.save()

    def _record_scans(self, product, how_many):
        """A history of verifications over the last month, so the page and the
        analytics have data.

        Written straight to the table rather than through the view: this is a
        record of visits that already happened, not a visit being made now.
        """
        verdict = Verdict.REVOKED if product.revocation_reason else Verdict.GENUINE
        now = timezone.now()

        scans = ScanEvent.objects.bulk_create(
            ScanEvent(
                product=product,
                verdict=verdict,
                device_category=SCAN_DEVICES[number % len(SCAN_DEVICES)],
                region=SCAN_REGIONS[number % len(SCAN_REGIONS)],
            )
            for number in range(how_many)
        )
        # The time is set by the database on insert, so it is moved back after.
        for number, scan in enumerate(scans):
            ScanEvent.objects.filter(pk=scan.pk).update(
                scanned_at=now - timedelta(days=3 + number * 4, hours=number)
            )

    def _tell_the_custody_story(self):
        """Hand one passport along a chain, and leave another with an open offer."""
        product = Product.objects.filter(name=CUSTODY_STORY["product"]).first()
        if product is not None and not product.custody_transfers.exists():
            buyer = User.objects.filter(email=BUYER_EMAIL).first()
            if buyer is None:
                buyer = User.objects.create_user(BUYER_EMAIL, PASSWORD, role=Role.HOLDER)
            for giver, receiver, note in CUSTODY_STORY["handovers"]:
                transfer = CustodyTransfer.objects.create(
                    product=product,
                    from_holder=User.objects.get(email=giver),
                    to_holder=User.objects.get(email=receiver),
                    note=note,
                )
                transfer.accept(actor=transfer.to_holder)
            self.stdout.write(f"  custody chain of {product.name}: workshop, distributor, buyer")

        name, giver, receiver = OPEN_OFFER
        offered = Product.objects.filter(name=name).first()
        if offered is not None and not offered.custody_transfers.exists():
            transfer = CustodyTransfer.objects.create(
                product=offered,
                from_holder=User.objects.get(email=giver),
                to_holder=User.objects.get(email=receiver),
                note="Lote para la feria de Cartagena.",
            )
            self.stdout.write(
                f"  open offer of {offered.name}, transfer code {transfer.transfer_code}"
            )

    def _raise_a_duplicate_scan_alert(self):
        """Two scans of one passport from distant regions an hour apart (FR49)."""
        product = Product.objects.filter(name=CUSTODY_STORY["product"]).first()
        if product is None or product.alerts.exists():
            return
        now = timezone.now()
        first = ScanEvent.objects.create(
            product=product,
            verdict=Verdict.GENUINE,
            region="Córdoba",
            device_category=DeviceCategory.MOBILE,
        )
        second = ScanEvent.objects.create(
            product=product,
            verdict=Verdict.GENUINE,
            region="Bogotá D.C.",
            device_category=DeviceCategory.MOBILE,
        )
        ScanEvent.objects.filter(pk=first.pk).update(scanned_at=now - timedelta(hours=3))
        ScanEvent.objects.filter(pk=second.pk).update(scanned_at=now - timedelta(hours=2))
        Alert.objects.create(product=product, scan=second, kind=AlertKind.DUPLICATE_SCAN)
        self.stdout.write(f"  duplicate-scan alert on {product.name}")
