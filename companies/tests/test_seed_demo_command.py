"""The demo dataset used for the deliverable walkthrough."""

from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

from companies.models import Company, CompanyStatus


class SeedDemoCommandTests(TestCase):
    @override_settings(DEBUG=True)
    def test_it_creates_one_company_in_each_status(self):
        call_command("seed_demo", stdout=StringIO())

        statuses = set(Company.objects.values_list("status", flat=True))

        self.assertEqual(statuses, {value for value, _ in CompanyStatus.choices})

    @override_settings(DEBUG=True)
    def test_running_it_twice_creates_nothing_new(self):
        call_command("seed_demo", stdout=StringIO())
        before = Company.objects.count()

        call_command("seed_demo", stdout=StringIO())

        self.assertEqual(Company.objects.count(), before)

    @override_settings(DEBUG=False)
    def test_it_refuses_to_run_with_debug_off(self):
        """Every account it creates shares one known password."""
        with self.assertRaises(CommandError):
            call_command("seed_demo", stdout=StringIO())

        self.assertFalse(Company.objects.exists())
