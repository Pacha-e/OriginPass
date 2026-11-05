# ---- External imports ----
from django.apps import AppConfig

# ---- Public API ----


class CompaniesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "companies"
    verbose_name = "Companies"
