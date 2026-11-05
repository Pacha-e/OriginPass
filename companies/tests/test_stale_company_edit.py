"""An edit must not write back a status it read before someone else changed it.

The owner's edit form loads the company, then saves every field. If an admin
suspends the company in between, saving the whole row would restore the old
status and undo the suspension without a trace.
"""

# ---- External imports ----
from django.test import TestCase

# ---- Internal imports ----
from companies.forms import CompanyApplicationForm
from companies.models import Company, CompanyStatus
from test_support.factories import make_admin, make_company, make_user


# ---- Public API ----
class StaleCompanyEditTests(TestCase):
    def setUp(self):
        self.owner = make_user(email="maker@tuchin.co")
        self.company = make_company(owner=self.owner, status=CompanyStatus.APPROVED)
        self.admin = make_admin()

    def test_a_suspension_made_during_the_edit_survives_the_save(self):
        loaded = Company.objects.get(pk=self.company.pk)
        other = Company.objects.get(pk=self.company.pk)
        other.suspend(actor=self.admin, reason="Under review")

        form = CompanyApplicationForm(
            data={
                "legal_name": "Artesanias La Bonga SAS",
                "company_type": loaded.company_type,
                "verification_track": loaded.verification_track,
                "registry_code": loaded.registry_code,
                "publish_consent": True,
                "description": "Crafts from Cordoba, updated.",
                "location": "Monteria, Cordoba",
                "website": "",
            },
            instance=loaded,
        )
        self.assertTrue(form.is_valid(), form.errors)
        form.save()

        self.company.refresh_from_db()
        self.assertEqual(self.company.status, CompanyStatus.SUSPENDED)
        self.assertEqual(self.company.description, "Crafts from Cordoba, updated.")
