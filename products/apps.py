# ---- External imports ----
from django.apps import AppConfig

# ---- Public API ----


class ProductsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "products"
