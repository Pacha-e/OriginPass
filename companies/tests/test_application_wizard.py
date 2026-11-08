"""The application asked one question per screen, and the same account comes out of it."""

# ---- External imports ----
from django.test import TestCase
from django.urls import reverse

# ---- Internal imports ----
from companies.models import Company, CompanyStatus, CompanyType, VerificationTrack
from test_support.factories import make_company, make_user

# ---- Constants ----

ARTISAN_STEPS = [
    ("kind", {"company_type": CompanyType.ARTISAN}),
    ("name", {"legal_name": "Taller Tuchin"}),
    ("location", {"location": "Tuchin, Cordoba"}),
    ("description", {"description": "Family workshop weaving sombrero vueltiao."}),
    (
        "evidence",
        {"evidence_notes": "Three generations weaving cana flecha; the association vouches."},
    ),
    ("consent", {"publish_consent": "on"}),
]

COMMERCIAL_STEPS = [
    ("kind", {"company_type": CompanyType.COMMERCIAL}),
    ("name", {"legal_name": "Artesanias La Bonga SAS"}),
    (
        "registry",
        {
            "verification_track": VerificationTrack.CHAMBER_OF_COMMERCE,
            "registry_code": "NIT-900123456-7",
        },
    ),
    ("location", {"location": "Monteria, Cordoba"}),
    ("description", {"description": "Distributor of certified crafts from Cordoba."}),
    ("website", {"website": "https://labonga.co"}),
    ("consent", {"publish_consent": "on"}),
]


# ---- Public API ----
class ApplicationWizardTests(TestCase):
    def setUp(self):
        self.owner = make_user()
        self.client.force_login(self.owner)

    def step_url(self, step):
        return reverse("companies:application_wizard", args=[step])

    def answer(self, step, data):
        return self.client.post(self.step_url(step), data)

    def walk(self, steps):
        for step, data in steps:
            self.answer(step, data)

    def test_artisan_path_skips_registry_fields(self):
        response = self.answer("kind", {"company_type": CompanyType.ARTISAN})

        self.assertRedirects(response, self.step_url("name"))
        self.assertEqual(self.client.get(self.step_url("registry")).status_code, 404)

        self.walk(ARTISAN_STEPS[1:])

        company = Company.objects.get(owner=self.owner)
        self.assertEqual(company.status, CompanyStatus.PENDING)
        self.assertEqual(company.verification_track, VerificationTrack.ARTISAN_REVIEW)
        self.assertEqual(company.registry_code, "")

    def test_commercial_path_asks_registry(self):
        self.answer("kind", {"company_type": CompanyType.COMMERCIAL})

        response = self.answer("name", {"legal_name": "Artesanias La Bonga SAS"})
        self.assertRedirects(response, self.step_url("registry"))

        response = self.answer(
            "registry",
            {"verification_track": VerificationTrack.CHAMBER_OF_COMMERCE, "registry_code": ""},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "companies/wizard_step.html")
        self.assertIn("registry_code", response.context["form"].errors)

    def test_back_keeps_typed_values(self):
        self.answer("kind", {"company_type": CompanyType.ARTISAN})
        self.answer("name", {"legal_name": "Taller Tuchin"})

        response = self.answer("location", {"back": "", "location": "Tuchin"})

        self.assertRedirects(response, self.step_url("name"))
        self.assertContains(self.client.get(self.step_url("name")), 'value="Taller Tuchin"')

    def test_invalid_step_stays_with_message(self):
        self.answer("kind", {"company_type": CompanyType.ARTISAN})

        response = self.answer("name", {"legal_name": ""})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "companies/wizard_step.html")
        self.assertIn("legal_name", response.context["form"].errors)
        self.assertContains(response, "field-error")

    def test_finish_creates_pending_application_once(self):
        self.walk(ARTISAN_STEPS)

        second = self.answer("consent", {"publish_consent": "on"})

        self.assertRedirects(second, reverse("companies:application_detail"))
        self.assertEqual(Company.objects.filter(owner=self.owner).count(), 1)

    def test_progress_label_counts_steps(self):
        self.answer("kind", {"company_type": CompanyType.ARTISAN})

        response = self.client.get(self.step_url("name"))

        self.assertContains(response, "Paso 2 de 6")

    def test_account_with_company_is_sent_to_its_application(self):
        make_company(self.owner)

        response = self.client.get(self.step_url("kind"))

        self.assertRedirects(response, reverse("companies:application_detail"))
