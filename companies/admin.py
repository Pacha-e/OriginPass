from django.contrib import admin

from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ["legal_name", "company_type", "status", "owner", "submitted_at"]
    list_filter = ["status", "company_type", "verification_track"]
    search_fields = ["legal_name", "location", "registry_code", "owner__email"]
    readonly_fields = ["submitted_at", "status_changed_at"]
