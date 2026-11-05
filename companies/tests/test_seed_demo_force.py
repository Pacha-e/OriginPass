"""The demo seed must never create accounts with a known password outside DEBUG.

It used to accept --force for this, and --force also overwrote existing rows
that matched demo emails. The option is gone, so the refusal has no way round.
"""

# ---- External imports ----
from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

# ---- Internal imports ----
from companies.models import Company


# ---- Public API ----
class SeedDemoRefusalTests(TestCase):
    @override_settings(DEBUG=False)
    def test_force_is_no_longer_an_option(self):
        with self.assertRaises(CommandError):
            call_command("seed_demo", "--force", stdout=StringIO())

        self.assertFalse(Company.objects.exists())

    @override_settings(DEBUG=False)
    def test_it_refuses_outside_debug_without_any_option(self):
        with self.assertRaises(CommandError):
            call_command("seed_demo", stdout=StringIO())

        self.assertFalse(Company.objects.exists())
