"""The command that reports on integrity, and the two ways its report can lie.

It can say a record is intact when it is not, which the signatures prevent. It
can also say so from a database that is not the one the code describes, which
nothing prevented: both chain constraints sat unapplied on the development
database and no test noticed, because the suite builds its own database from
the migrations every run and so never reads the one being worked on.

A report on integrity given by a database missing the constraints that defend
it is worse than no report, so the command refuses to give one.
"""

from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.db import connection
from django.test import TestCase

from test_support.factories import make_admin, make_approved_company, make_product


class CleanDatabaseTests(TestCase):
    def setUp(self):
        self.admin = make_admin()
        self.product = make_product(make_approved_company(email="weaver@tuchin.co"))

    def _run(self):
        out, err = StringIO(), StringIO()
        call_command("verify_integrity", stdout=out, stderr=err)
        return out.getvalue(), err.getvalue()

    def test_it_reports_the_trail_the_products_and_the_chains(self):
        out, _ = self._run()

        self.assertIn("audit trail", out)
        self.assertIn("products", out)
        self.assertIn("custody chains", out)

    def test_it_says_how_many_keys_it_accepted(self):
        """The closing sentence is the one statement of the security property."""
        out, _ = self._run()

        self.assertIn("the current signing key", out)


class TamperedRecordTests(TestCase):
    def setUp(self):
        self.admin = make_admin()
        self.product = make_product(make_approved_company(email="weaver@tuchin.co"))
        self.product.revoke(actor=self.admin, reason="Reported as a counterfeit.")

    def test_a_rewritten_entry_makes_the_command_fail(self):
        with connection.cursor() as cursor:
            cursor.execute("UPDATE audit_auditentry SET reason = %s", ["Rewritten"])

        out, err = StringIO(), StringIO()
        with self.assertRaises(SystemExit) as exit_code:
            call_command("verify_integrity", stdout=out, stderr=err)

        self.assertEqual(exit_code.exception.code, 1)
        self.assertIn("altered since it was written", out.getvalue())
        self.assertIn("problem(s) found", err.getvalue())


class DatabaseBehindTheCodeTests(TestCase):
    """A migration not yet applied is a rule the database is not enforcing."""

    def setUp(self):
        make_product(make_approved_company(email="weaver@tuchin.co"))

    def _run_with_pending(self, pending):
        out, err = StringIO(), StringIO()
        with patch(
            "django.db.migrations.executor.MigrationExecutor.migration_plan",
            return_value=pending,
        ):
            with self.assertRaises(SystemExit) as exit_code:
                call_command("verify_integrity", stdout=out, stderr=err)
        return exit_code.exception.code, out.getvalue(), err.getvalue()

    def test_it_refuses_to_report_anything(self):
        migration = type("Migration", (), {"app_label": "audit", "name": "0004_a_constraint"})()

        code, out, err = self._run_with_pending([(migration, False)])

        self.assertEqual(code, 1)
        self.assertIn("behind the code", err)
        self.assertNotIn("intact", out)

    def test_it_names_the_migrations_that_are_missing(self):
        first = type("Migration", (), {"app_label": "audit", "name": "0004_a_constraint"})()
        second = type("Migration", (), {"app_label": "products", "name": "0004_another"})()

        _, _, err = self._run_with_pending([(first, False), (second, False)])

        self.assertIn("audit.0004_a_constraint", err)
        self.assertIn("products.0004_another", err)
        self.assertIn("manage.py migrate", err)
