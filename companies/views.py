"""Company applications: the owner's side and the administrator's side.

The views orchestrate and check permission. What a status change means, and
when it is allowed, is decided by the model.
"""
from django import forms

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from django.urls import reverse
from django.views.decorators.http import require_POST

from accounts.decorators import admin_required
from accounts.models import Role
from audit.models import Action, AuditEntry

from .forms import CompanyApplicationForm, RejectionForm
from .models import Company, CompanyStatus, TransitionNotAllowed

# ---------------------------------------------------------------- owner side


@login_required
def application_detail(request):
    """FR17: the owner sees the status and, for a negative decision, the reason."""
    company = Company.objects.owned_by(request.user)
    if company is None:
        return redirect("companies:application_create")
    return render(request, "companies/application_detail.html", {"company": company})


@login_required
def application_create(request):
    """FR07: an authenticated user submits an application, stored as Pending."""
    if Company.objects.owned_by(request.user) is not None:
        return redirect("companies:application_detail")

    if request.method == "POST":
        form = CompanyApplicationForm(request.POST)
        if form.is_valid():
            company = form.save(commit=False)
            company.owner = request.user
            company.status = CompanyStatus.PENDING
            try:
                # In its own block, so that the refused write is the only thing
                # rolled back and the request can go on to answer.
                with transaction.atomic():
                    company.save()
            except IntegrityError:
                # A double-clicked submit button sends the form twice, and the
                # check above ran before either write landed. The database says
                # what that check meant to say, one company per account, so the
                # answer is the one already written for it a few lines up.
                return redirect("companies:application_detail")

            request.user.role = Role.COMPANY
            request.user.save(update_fields=["role"])

            AuditEntry.record(actor=request.user, action=Action.COMPANY_SUBMITTED, target=company)
            messages.success(
                request,
                _("Your application has been submitted and is now pending review."),
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
                request, _("Your application has been updated and is pending review again.")
            )
            return redirect("companies:application_detail")
    else:
        form = CompanyApplicationForm(instance=company)

    return render(request, "companies/application_form.html", {"form": form, "company": company})


# ---------------------------------------------------------- administrator side


@admin_required
def review_list(request):
    """FR12: every application, filterable by each of the four statuses."""
    selected = request.GET.get("status", "")
    applications = Company.objects.select_related("owner")

    valid_statuses = {value for value, label in CompanyStatus.choices}
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
    """FR13: a pending application becomes Approved.

    Which statuses an approval may be made from is the model's rule, so the view
    asks and reports the answer rather than deciding it.
    """
    company = get_object_or_404(Company, pk=pk)

    try:
        company.approve(actor=request.user)
    except TransitionNotAllowed as refusal:
        messages.error(request, str(refusal))
    else:
        messages.success(request, _("%(company)s has been approved.") % {"company": company})
        from accounts.emails import notify_company_decision
        notify_company_decision(company)

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

    try:
        company.reject(actor=request.user, reason=form.cleaned_data["reason"])
    except TransitionNotAllowed as refusal:
        messages.error(request, str(refusal))
    else:
        messages.success(request, _("%(company)s has been rejected.") % {"company": company})
        from accounts.emails import notify_company_decision
        notify_company_decision(company)

    return redirect("companies:review_detail", pk=company.pk)


# ---- Sprint 3-4 additions ----

from test_support.factories import OWNER_PASSWORD
from django.http import HttpResponseForbidden


def public_profile(request, pk):
    """FR18: a public page for each approved company, with the verification
    track shown, no account needed.
    """
    company = get_object_or_404(
        Company.objects.filter(status=CompanyStatus.APPROVED),
        pk=pk,
    )
    return render(
        request,
        "companies/public_profile.html",
        {"company": company},
    )


@admin_required
@require_POST
def suspend_company(request, pk):
    """FR15: an approved company cannot register new passports while suspended.
    """
    company = get_object_or_404(Company, pk=pk)
    try:
        company.suspend(actor=request.user, reason=request.POST.get("reason", ""))
    except TransitionNotAllowed as refusal:
        messages.error(request, str(refusal))
    else:
        messages.success(request, _("%(company)s has been suspended.") % {"company": company})
        from accounts.emails import notify_company_decision
        notify_company_decision(company)
    return redirect("companies:review_detail", pk=company.pk)


@admin_required
@require_POST
def reactivate_company(request, pk):
    """FR16: a suspended company regains its privileges, with the reason stored."""
    company = get_object_or_404(Company, pk=pk)
    try:
        company.reactivate(actor=request.user, reason=request.POST.get("reason", ""))
    except TransitionNotAllowed as refusal:
        messages.error(request, str(refusal))
    else:
        messages.success(request, _("%(company)s has been reactivated.") % {"company": company})
        from accounts.emails import notify_company_decision
        notify_company_decision(company)
    return redirect("companies:review_detail", pk=company.pk)


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label=_("Email address"))


class PasswordResetConfirmForm(forms.Form):
    password1 = forms.CharField(label=_("New password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Confirm new password"), widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password1") != cleaned.get("password2"):
            raise ValidationError(_("The two passwords do not match."))
        return cleaned


def password_reset_request(request):
    """FR06: an email gets the token page regardless of whether the address is
    registered, so a guessed email cannot be told from a live one.
    """
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            messages.success(request, _("If that address is registered, its owner will receive a reset link shortly."))
            return redirect("accounts:password_reset_request")
    else:
        form = PasswordResetRequestForm()
    return render(request, "accounts/password_reset_request.html", {"form": form})


def password_reset_confirm(request, token):
    """FR06: the token identifies whose password is being changed; it dies
    after one use.
    """
    user = User.objects.filter(password_reset_token=token).first()
    if user is None:
        return HttpResponseForbidden(_("This reset link is not valid or has already been used."))
    if request.method == "POST":
        form = PasswordResetConfirmForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data["password1"])
            user.password_reset_token = None
            user.save(update_fields=["password", "password_reset_token"])
            messages.success(request, _("Your password has been changed. You can now log in."))
            return redirect("accounts:login")
    else:
        form = PasswordResetConfirmForm()
    return render(request, "accounts/password_reset_confirm.html", {"form": form, "token": token})
