from django.contrib import admin

from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """Shown here, decided elsewhere.

    The status and the reason stored with it are read-only because this site
    edits fields directly: a status changed here would move without the
    transition being checked and without an entry in the audit trail, and the
    reason for a decision already taken could be rewritten afterwards. The
    review pages are where a decision is made.
    """

    list_display = ["legal_name", "company_type", "status", "owner", "submitted_at"]
    list_filter = ["status", "company_type", "verification_track"]
    search_fields = ["legal_name", "location", "registry_code", "owner__email"]
    readonly_fields = ["status", "status_reason", "submitted_at", "status_changed_at"]
