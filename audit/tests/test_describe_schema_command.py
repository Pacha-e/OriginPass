"""The report of what the database enforces, and what would make it useless.

Two things would: describing the models instead of the database, which is what
hid two unapplied constraints for days, and rendering a rule as the definition
Postgres prints, which is faithful and unreadable. So the tests hold it to
reading from the database and to naming each rule the way it was named.
"""

from io import StringIO

from django.core.management import call_command
from django.db import connection
from django.test import TestCase


def report():
    out = StringIO()
    call_command("describe_schema", stdout=out)
    return out.getvalue()


class TablesTests(TestCase):
    def test_it_covers_the_six_tables_this_project_designed(self):
        text = report()

        for table in [
            "accounts_user",
            "companies_company",
            "products_product",
            "products_custodytransfer",
            "verification_scanevent",
            "audit_auditentry",
        ]:
            self.assertIn(table, text)

    def test_it_leaves_out_the_tables_django_keeps_for_itself(self):
        text = report()

        for table in ["django_migrations", "django_session", "auth_permission"]:
            self.assertNotIn(table, text)

    def test_it_lists_the_columns_of_a_table(self):
        text = report()

        self.assertIn("passport_code", text)
        self.assertIn("integrity_hash", text)


class RulesTests(TestCase):
    """Every rule the database holds has to appear, named as it was named."""

    def test_each_check_constraint_appears_as_the_sentence_it_was_named(self):
        text = report()

        for rule in [
            "commercial company has registry code",
            "company track matches type",
            "negative decision states a reason",
            "revocation states a reason",
            "custody transfer changes holder",
        ]:
            self.assertIn(rule, text)

    def test_the_two_rules_that_keep_a_chain_linear_appear(self):
        text = report()

        self.assertIn("audit entry links to one predecessor", text)
        self.assertIn("custody transfer links to one predecessor", text)

    def test_a_check_carries_the_definition_that_proves_it(self):
        """The name states the intent; the definition is the evidence for it."""
        text = report()

        self.assertIn("CHECK (", text)

    def test_a_name_django_generated_is_shown_as_its_definition_instead(self):
        """A generated name says less than the definition, so it does not lead."""
        text = report()

        self.assertNotIn("companies company owner id", text)
        self.assertIn("(owner_id) -> accounts_user(id)", text)


class ReadFromTheDatabaseTests(TestCase):
    """Not from the models. A model says what should be there; only the database says what is."""

    def test_a_constraint_dropped_behind_the_models_back_stops_being_reported(self):
        with connection.cursor() as cursor:
            cursor.execute(
                "ALTER TABLE products_product DROP CONSTRAINT revocation_states_a_reason"
            )

        text = report()

        self.assertNotIn("revocation states a reason", text)

    def test_it_says_which_database_it_read(self):
        text = report()

        self.assertIn("PostgreSQL", text)
        self.assertIn("read from the running database", text)


class OutputTests(TestCase):
    def test_it_stays_within_the_characters_a_windows_console_can_print(self):
        """This runs on whatever console the machine has, and one cannot encode an arrow."""
        report().encode("cp1252")
