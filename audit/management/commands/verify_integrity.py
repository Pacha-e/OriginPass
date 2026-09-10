"""Check every signed record and report anything that does not hold up.

    python manage.py verify_integrity

Exits non-zero when something fails, so it can be run on a schedule and have
the failure noticed rather than logged into a file nobody reads.
"""

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

from audit.models import AuditEntry
from products.models import CustodyTransfer, Product


class Command(BaseCommand):
    help = "Verify the audit trail, the product signatures and every chain of custody."

    def _refuse_if_the_schema_is_behind(self):
        """Say nothing about a database that is not the one the code describes.

        Everything below reports on what the database holds. A database still
        missing a migration is missing the rules that migration adds, and two
        of them are the constraints that keep each chain linear. Reporting
        "intact" against it would be the most misleading thing this command
        could print: an answer about integrity, given by a database without the
        constraints that defend it.

        This is not hypothetical. Both chain constraints sat unapplied on the
        development database and nothing noticed, because the test suite builds
        its own database from the migrations every run and so never reads the
        one being worked on.
        """
        executor = MigrationExecutor(connection)
        pending = executor.migration_plan(executor.loader.graph.leaf_nodes())
        if not pending:
            return

        self.stderr.write("This database is behind the code. Nothing is verified.")
        self.stderr.write("")
        for migration, _backwards in pending:
            self.stderr.write(f"  unapplied  {migration.app_label}.{migration.name}")
        self.stderr.write("")
        self.stderr.write("Run: python manage.py migrate")
        raise SystemExit(1)

    def handle(self, *args, **options):
        self._refuse_if_the_schema_is_behind()

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
