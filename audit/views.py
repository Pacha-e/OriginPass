"""FR44: the administrator reads the audit trail, filtered.

Read-only by construction: this module has no view that writes, and the model
refuses edits anyway. The state of the signed chain is shown above the entries,
because a filtered list of rows says nothing about whether rows were removed.
"""

from datetime import datetime, time

from django.core.paginator import Paginator
from django.shortcuts import render
from django.utils import timezone

from accounts.decorators import admin_required

from .forms import AuditFilterForm
from .models import AuditEntry

PAGE_SIZE = 50


@admin_required
def audit_log(request):
    form = AuditFilterForm(request.GET or None)
    entries = AuditEntry.objects.select_related("actor").order_by("-created_at")

    if form.is_valid():
        data = form.cleaned_data
        if data["actor"]:
            entries = entries.filter(actor__email__icontains=data["actor"].strip())
        if data["action"]:
            entries = entries.filter(action=data["action"])
        zone = timezone.get_current_timezone()
        if data["since"]:
            entries = entries.filter(
                created_at__gte=datetime.combine(data["since"], time.min, tzinfo=zone)
            )
        if data["until"]:
            entries = entries.filter(
                created_at__lte=datetime.combine(data["until"], time.max, tzinfo=zone)
            )

    chain_intact, chain_problem = AuditEntry.verify_chain()
    page = Paginator(entries, PAGE_SIZE).get_page(request.GET.get("page"))
    query = request.GET.copy()
    query.pop("page", None)

    return render(
        request,
        "audit/log.html",
        {
            "form": form,
            "page": page,
            "query": query.urlencode(),
            "chain_intact": chain_intact,
            "chain_problem": chain_problem,
            "total": AuditEntry.objects.count(),
        },
    )
