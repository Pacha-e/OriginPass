"""Company applications: the owner's side and the administrator's side.

The views orchestrate and check permission. What a status change means, and
when it is allowed, is decided by the model.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.decorators import admin_required
from accounts.models import Role
from audit.models import Action, AuditEntry

from .forms import CompanyApplicationForm, RejectionForm
from .models import Company, CompanyStatus


# ---------------------------------------------------------------- owner side


@login_required
def application_detail(request):
    """FR17: the owner sees the status and, for a negative decision, the reason."""
    company = Company.objects.filter(owner=request.user).first()
    if company is None:
        return redirect("companies:application_create")
    return render(request, "companies/application_detail.html", {"company": company})


@login_required
def application_create(request):
    """FR07: an authenticated user submits an application, stored as Pending."""
    if Company.objects.filter(owner=request.user).exists():
        return redirect("companies:application_detail")

    if request.method == "POST":
        form = CompanyApplicationForm(request.POST)
        if form.is_valid():
            company = form.save(commit=False)
            company.owner = request.user
            company.status = CompanyStatus.PENDING
            company.save()

            request.user.role = Role.COMPANY
            request.user.save(update_fields=["role"])

            AuditEntry.record(
                actor=request.user, action=Action.COMPANY_SUBMITTED, target=company
            )
            messages.success(
                request,
                "Your application has been submitted and is now pending review.",
            )
            return redirect("companies:application_detail")
    else:
        form = CompanyApplicationForm()

    return render(request, "companies/application_form.html", {"form": form, "company": None})


@login_required
def application_edit(request):
    """FR10 while editable, FR11 once it is not."""
    company = get_object_or_404(Company, owner=request.user)

    if not company.is_editable:
        # FR11: the refusal states why, rather than silently hiding the page.
        return render(
            request,
            "companies/edit_refused.html",
            {"company": company, "reason": company.edit_refusal_reason()},
            status=403,
        )

    if request.method == "POST":
        form = CompanyApplicationForm(request.POST, instance=company)
        if form.is_valid():
            company = form.save()
            company.resubmit(actor=request.user)
            messages.success(
                request, "Your application has been updated and is pending review again."
            )
            return redirect("companies:application_detail")
    else:
        form = CompanyApplicationForm(instance=company)

    return render(
        request, "companies/application_form.html", {"form": form, "company": company}
    )


# ---------------------------------------------------------- administrator side


@admin_required
def review_list(request):
    """FR12: every application, filterable by each of the four statuses."""
    selected = request.GET.get("status", "")
    applications = Company.objects.select_related("owner")

    valid_statuses = {value for value, _ in CompanyStatus.choices}
    if selected not in valid_statuses:
        selected = ""
    else:
        applications = applications.filter(status=selected)

    return render(
        request,
        "companies/review_list.html",
        {
            "applications": applications,
            "statuses": CompanyStatus.choices,
            "selected_status": selected,
        },
    )


@admin_required
def review_detail(request, pk):
    company = get_object_or_404(Company.objects.select_related("owner"), pk=pk)
    return render(
        request,
        "companies/review_detail.html",
        {"company": company, "rejection_form": RejectionForm()},
    )


@admin_required
@require_POST
def review_approve(request, pk):
    """FR13: a pending application becomes Approved."""
    company = get_object_or_404(Company, pk=pk)
    company.approve(actor=request.user)
    messages.success(request, f"{company.legal_name} has been approved.")
    return redirect("companies:review_detail", pk=company.pk)


@admin_required
@require_POST
def review_reject(request, pk):
    """FR14: a rejection is stored together with its written reason."""
    company = get_object_or_404(Company.objects.select_related("owner"), pk=pk)
    form = RejectionForm(request.POST)

    if not form.is_valid():
        return render(
            request,
            "companies/review_detail.html",
            {"company": company, "rejection_form": form},
            status=400,
        )

    company.reject(actor=request.user, reason=form.cleaned_data["reason"])
    messages.success(request, f"{company.legal_name} has been rejected.")
    return redirect("companies:review_detail", pk=company.pk)
