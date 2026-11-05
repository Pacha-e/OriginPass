# ---- External imports ----
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# ---- Internal imports ----
from .models import User

# ---- Public API ----


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_fieldsets = [
        (None, {"classes": ["wide"], "fields": ["email", "role", "password1", "password2"]}),
    ]
    fieldsets = [
        (None, {"fields": ["email", "password"]}),
        ("Role", {"fields": ["role"]}),
        (
            "Permissions",
            {
                "fields": [
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ]
            },
        ),
        ("Dates", {"fields": ["last_login", "date_joined"]}),
    ]
    list_display = ["email", "role", "is_active", "is_staff", "date_joined"]
    list_filter = ["role", "is_active", "is_staff"]
    ordering = ["email"]
    search_fields = ["email"]
