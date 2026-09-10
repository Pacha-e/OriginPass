from django.contrib import admin

from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """Shown here, decided elsewhere.

    The status and the reason stored with it are read-only because this site
    edits fields directly: a status changed here would move without the
    transition being checked and without an entry in the audit trail, and the
    reason for a decision already taken could be rewritten afterwards.

    Where each decision is made instead:

    - approve and reject have review pages, built for FR13 and FR14
    - suspend and reactivate have `Company.suspend` and `Company.reactivate`
      and no page yet, because FR15 and FR16 belong to Sprint 4

    Until those pages exist, suspending a company is something only code does.
    That is deliberate: this site could do it before, without a reason being
    required and without leaving a trail, which is not a decision, it is an
    edit wearing the clothes of one.
    """

    list_display = ["legal_name", "company_type", "status", "owner", "submitted_at"]
    list_filter = ["status", "company_type", "verification_track"]
    search_fields = ["legal_name", "location", "registry_code", "owner__email"]
    readonly_fields = ["status", "status_reason", "submitted_at", "status_changed_at"]
