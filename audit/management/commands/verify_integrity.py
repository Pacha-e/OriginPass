"""Check every signed record and report anything that does not hold up.

    python manage.py verify_integrity

Exits non-zero when something fails, so it can be run on a schedule and have
the failure noticed rather than logged into a file nobody reads.
"""

from django.conf import settings
from django.core.management.base import BaseCommand

from audit.models import AuditEntry
from products.models import CustodyTransfer, Product


class Command(BaseCommand):
    help = "Verify the audit trail, the product signatures and every chain of custody."

    def handle(self, *args, **options):
        problems = []

        ok, problem = AuditEntry.verify_chain()
        count = AuditEntry.objects.count()
        if ok:
            self.stdout.write(self.style.SUCCESS(f"audit trail       {count} entries, intact"))
        else:
            problems.append(problem)
            self.stdout.write(self.style.ERROR(f"audit trail       {problem}"))

        tampered = [p for p in Product.objects.all() if not p.is_intact]
        total = Product.objects.count()
        if tampered:
            for product in tampered:
                problems.append(f"Product #{product.pk} has been altered since registration")
                self.stdout.write(
                    self.style.ERROR(
                        f"product           #{product.pk} {product.name}: "
                        f"altered since registration"
                    )
                )
        else:
            self.stdout.write(self.style.SUCCESS(f"products          {total} signed, intact"))

        with_custody = Product.objects.filter(custody_transfers__isnull=False).distinct()
        broken = 0
        for product in with_custody:
            ok, problem = CustodyTransfer.verify_chain(product)
            if not ok:
                broken += 1
                problems.append(problem)
                self.stdout.write(
                    self.style.ERROR(f"custody chain     {product.passport_code}: {problem}")
                )
        if not broken:
            self.stdout.write(
                self.style.SUCCESS(f"custody chains    {with_custody.count()} chains, intact")
            )

        if problems:
            self.stdout.write("")
            self.stderr.write(f"{len(problems)} problem(s) found.")
            raise SystemExit(1)

        self.stdout.write("")
        keys = 1 + len(settings.SECRET_KEY_FALLBACKS)
        against = "the current signing key" if keys == 1 else f"one of {keys} signing keys"
        self.stdout.write(
            f"Everything verifies against {against}. This proves no record was changed by "
            "anyone holding only the database. It does not cover whoever holds a key as well, "
            "which is what publishing the chain head externally would close."
        )
        if keys > 1:
            self.stdout.write(
                "Retired keys are still accepted, so a record signed under one of them counts "
                "as verified. Drop them from SECRET_KEY_FALLBACKS once nothing needs them."
            )
