"""Product passports: registration, the company's own list, and the QR image.

Every view here starts from the company that owns the request rather than from
the product, because a passport belongs to a company and a company only ever
sees its own. Whether a company may issue passports at all is decided by the
model; these views ask and then explain the answer.
"""

import io

import qrcode
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy

from audit.models import Action, AuditEntry
from companies.models import Company, CompanyStatus

from .forms import ProductForm
from .models import PRODUCT_TYPE_BY_COMPANY_TYPE, Product, ProductStatus

#: Why a company in each non-approving status cannot issue a passport. Kept
#: here rather than in the template so that the view can also refuse a POST.
#: Lazily translated because this is built at import time, before a request has
#: said which language to answer in.
REFUSAL_BY_STATUS = {
    CompanyStatus.PENDING: gettext_lazy(
        "Your application is still being reviewed. Passports can be issued once it "
        "has been approved."
    ),
    CompanyStatus.REJECTED: gettext_lazy(
        "Your application was rejected, so it cannot issue passports. Edit and "
        "resubmit it to be reviewed again."
    ),
    CompanyStatus.SUSPENDED: gettext_lazy(
        "Your company is suspended and cannot issue new passports. Passports "
        "already issued keep working."
    ),
}

REVOKED_PASSPORT_REFUSAL = gettext_lazy(
    "This passport has been revoked. A revoked passport is a record of what was "
    "issued and is not edited."
)


def _refuse(request, company, heading, reason):
    """FR20: a refusal states its cause instead of hiding the page."""
    return render(
        request,
        "products/refusal.html",
        {"company": company, "heading": heading, "reason": reason},
        status=403,
    )


@login_required
def product_list(request):
    """FR24 filtered by status, FR25 searched by name, category or passport code."""
    company = Company.objects.owned_by(request.user)
    if company is None:
        return redirect("companies:application_create")

    products = Product.objects.filter(company=company)

    selected = request.GET.get("status", "")
    if selected in {value for value, label in ProductStatus.choices}:
        products = products.filter(status=selected)
    else:
        selected = ""

    query = request.GET.get("q", "").strip()
    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(category__icontains=query)
            | Q(passport_code__icontains=query)
        )

    return render(
        request,
        "products/product_list.html",
        {
            "company": company,
            "products": products,
            "statuses": ProductStatus.choices,
            "selected_status": selected,
            "query": query,
            "can_register": company.can_register_products,
        },
    )


@login_required
def product_create(request):
    """FR19 for an approved company, FR20 for any other, FR21 and FR23 on save."""
    company = Company.objects.owned_by(request.user)
    if company is None:
        return redirect("companies:application_create")
    if not company.can_register_products:
        return _refuse(
            request,
            company,
            heading=_("This company cannot issue a passport"),
            reason=REFUSAL_BY_STATUS[company.status],
        )

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.company = company
            # FR23: the type follows from the company, so it cannot be crossed.
            product.product_type = PRODUCT_TYPE_BY_COMPANY_TYPE[company.company_type]
            try:
                # The model owns the rule; the view only reports what it says.
                product.full_clean(exclude=["passport_code", "integrity_hash"])
            except ValidationError as error:
                form.add_error(None, error)
            else:
                product.save()
                AuditEntry.record(
                    actor=request.user, action=Action.PRODUCT_REGISTERED, target=product
                )
                messages.success(
                    request,
                    _("%(product)s now has a passport. Its code is %(code)s.")
                    % {"product": product.name, "code": product.passport_code},
                )
                return redirect("products:product_detail", pk=product.pk)
    else:
        form = ProductForm()

    return render(
        request,
        "products/product_form.html",
        {"form": form, "company": company, "product": None},
    )


@login_required
def product_detail(request, pk):
    """The passport as its owner sees it: the code, the QR and the public address."""
    company = Company.objects.owned_by(request.user)
    product = get_object_or_404(Product.objects.select_related("company"), pk=pk, company=company)
    return render(
        request,
        "products/product_detail.html",
        {
            "product": product,
            "verification_url": request.build_absolute_uri(
                reverse("verification:verify", args=[product.passport_code])
            ),
        },
    )


@login_required
def product_edit(request, pk):
    """FR26: the descriptive fields change, the passport code does not."""
    company = Company.objects.owned_by(request.user)
    product = get_object_or_404(Product, pk=pk, company=company)

    if product.status == ProductStatus.REVOKED:
        return _refuse(
            request,
            company,
            heading=_("This passport cannot be edited"),
            reason=REVOKED_PASSPORT_REFUSAL,
        )

    # Asked before the form is built, because the model's rule is that a
    # passport belongs to an approved company, and it states that against the
    # company field, which this form does not have. Left to reach the form, it
    # arrives as an error with nowhere to go and the page fails outright.
    # Suspension is the only way to get here: a company is approved when it
    # registers a passport, and suspension is the only way out of approved.
    if not company.can_register_products:
        return _refuse(
            request,
            company,
            heading=_("This passport cannot be edited"),
            reason=REFUSAL_BY_STATUS[company.status],
        )

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(
                request, _("%(product)s has been updated.") % {"product": product.name}
            )
            return redirect("products:product_detail", pk=product.pk)
    else:
        form = ProductForm(instance=product)

    return render(
        request,
        "products/product_form.html",
        {"form": form, "company": company, "product": product},
    )


@login_required
def qr_download(request, pk):
    """FR22: a PNG encoding the public verification address of this passport."""
    company = Company.objects.owned_by(request.user)
    product = get_object_or_404(Product, pk=pk, company=company)

    address = request.build_absolute_uri(
        reverse("verification:verify", args=[product.passport_code])
    )
    image = qrcode.make(address)

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")

    response = HttpResponse(buffer.getvalue(), content_type="image/png")
    response["Content-Disposition"] = (
        f'attachment; filename="originpass-{product.passport_code}.png"'
    )
    return response


# ---- Custody transfers (Sprint 3, FR35-FR40) ----

from .models import TransferState, CustodyTransfer


@login_required
def transfer_initiate(request, pk):
    """FR35: the current holder offers the product to another account."""
    company = Company.objects.owned_by(request.user)
    product = get_object_or_404(Product, pk=pk, company=company)

    if product.status == ProductStatus.REVOKED:
        return _refuse(
            request,
            company,
            heading=_("This product cannot be transferred"),
            reason=_("A revoked product accepts no custody transfer (FR39)."),
        )

    from .forms import TransferInitiateForm
    if request.method == "POST":
        form = TransferInitiateForm(request.POST, product=product, holder=request.user)
        if form.is_valid():
            transfer = form.save()
            messages.success(
                request,
                _("Transfer offered to %(who)s.") % {"who": transfer.to_holder.email},
            )
            return redirect("products:product_detail", pk=product.pk)
    else:
        form = TransferInitiateForm(product=product, holder=request.user)

    return render(
        request,
        "products/transfer_initiate.html",
        {"form": form, "product": product, "company": company},
    )


@login_required
def transfer_list(request):
    """The incoming transfers waiting for the user's answer."""
    incoming = (
        CustodyTransfer.objects.filter(to_holder=request.user, state=TransferState.INITIATED)
        .select_related("product", "from_holder")
        .order_by("-created_at")
    )
    outgoing = (
        CustodyTransfer.objects.filter(from_holder=request.user, state=TransferState.INITIATED)
        .select_related("product", "to_holder")
        .order_by("-created_at")
    )
    return render(
        request,
        "products/transfer_list.html",
        {"incoming": incoming, "outgoing": outgoing},
    )


@login_required
def transfer_respond(request, pk):
    """FR36: the receiver accepts or declines; the row is locked behind one transaction."""
    transfer = get_object_or_404(
        CustodyTransfer.objects.select_related("product", "to_holder"),
        pk=pk,
        to_holder=request.user,
    )

    if transfer.state != TransferState.INITIATED:
        return _refuse(
            request,
            transfer.product.company,
            heading=_("This transfer has already been resolved"),
            reason=_("A custody transfer cannot be answered twice."),
        )

    if request.method == "POST":
        action = request.POST.get("action")
        try:
            if action == "accept":
                transfer.accept(actor=request.user)
                from accounts.emails import notify_revocation
                notify_revocation(transfer.product)
                messages.success(request, _("You are now the holder of %(product)s.") % {"product": transfer.product.name})
            elif action == "decline":
                transfer.decline(actor=request.user)
                messages.success(request, _("You declined the transfer of %(product)s.") % {"product": transfer.product.name})
            else:
                raise ValueError("Unknown action.")
        except ValueError:
            return _refuse(
                request,
                transfer.product.company,
                heading=_("This transfer has already been resolved"),
                reason=_("A custody transfer cannot be answered twice."),
            )
        return redirect("products:transfer_list")

    return render(
        request,
        "products/transfer_respond.html",
        {"transfer": transfer},
    )


@login_required
def transfer_claim(request):
    """FR40: a buyer claims ownership using the passport code + transfer code.

    The two codes are required together: the passport alone must not transfer
    ownership (that would be one QR worth of phishing), and the transfer code
    alone tells us nothing without knowing which product it belongs to.
    """
    from .forms import TransferClaimForm
    if request.method == "POST":
        form = TransferClaimForm(request.POST)
        if form.is_valid():
            transfer = form.cleaned_data["transfer"]
            # The claim moves the product to the claimant; the original owner
            # remains the from_holder so the chain stays unbroken.
            transfer.to_holder = request.user
            transfer.accept(actor=request.user)
            messages.success(
                request,
                _("You are now the registered holder of %(product)s.") % {"product": transfer.product.name},
            )
            return redirect("products:product_detail", pk=transfer.product.pk)
    else:
        form = TransferClaimForm()

    return render(request, "products/transfer_claim.html", {"form": form})


# ---- Analytics and revocation (Sprint 3+4, FR41-FR50) ----

import csv
from datetime import timedelta

from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, F, Sum, Avg
from django.db.models.functions import TruncDay
from django.http import HttpResponse
from django.utils import timezone

from verification.models import ScanEvent, Verdict
from .models import Alert


def _is_admin(user):
    return user.is_authenticated and user.is_platform_admin


@login_required
def company_analytics(request):
    """FR46-49: scan counts over a chosen range, region distribution, and the
    ranked list of products. The company only ever sees its own data.
    """
    company = Company.objects.owned_by(request.user)
    if company is None:
        return redirect("companies:application_create")

    days = int(request.GET.get("days", "30"))
    if days not in (7, 30, 90, 365):
        days = 30
    since = timezone.now() - timedelta(days=days)

    scans_qs = ScanEvent.objects.filter(product__company=company, scanned_at__gte=since)
    by_day = (
        scans_qs.annotate(day=TruncDay("scanned_at"))
        .values("day")
        .order_by("day")
        .annotate(count=Count("id"))
    )
    by_region = (
        scans_qs.values("region").order_by().annotate(count=Count("id")).order_by("-count")
    )
    by_product = (
        scans_qs.values("product__name", "product__passport_code")
        .annotate(count=Count("id"))
        .order_by("-count")[:20]
    )
    alerts = (
        company.products.prefetch_related("alerts")
        .filter(alerts__isnull=False)
        .distinct()
        .order_by("-alerts__created_at")[:10]
    )

    return render(
        request,
        "products/analytics.html",
        {
            "company": company,
            "days": days,
            "by_day": list(by_day),
            "by_region": list(by_region),
            "by_product": list(by_product),
            "alerts": alerts,
        },
    )


@login_required
def company_analytics_csv(request):
    """FR51: a CSV export of the same numbers, one row per day."""
    company = Company.objects.owned_by(request.user)
    if company is None:
        return redirect("companies:application_create")

    days = int(request.GET.get("days", "30"))
    if days not in (7, 30, 90, 365):
        days = 30
    since = timezone.now() - timedelta(days=days)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        f'attachment; filename="originpass-analytics-{company.pk}-{days}d.csv"'
    )
    writer = csv.writer(response)
    writer.writerow(["day", "product", "region", "scans"])
    scans = (
        ScanEvent.objects.filter(product__company=company, scanned_at__gte=since)
        .annotate(day=TruncDay("scanned_at"))
        .values("day", "product__name", "region")
        .annotate(count=Count("id"))
        .order_by("day", "product__name")
    )
    for row in scans:
        writer.writerow([row["day"], row["product__name"], row["region"], row["count"]])
    return response


@login_required
def product_revoke(request, pk):
    """FR41: a company revokes one of its passports; the row says why."""
    company = Company.objects.owned_by(request.user)
    product = get_object_or_404(Product, pk=pk, company=company)

    if product.status == ProductStatus.REVOKED:
        return _refuse(
            request,
            company,
            heading=_("This passport has already been revoked"),
            reason=_("A revoked passport is a record of what was issued and cannot be revoked again."),
        )

    if request.method == "POST":
        reason = request.POST.get("reason", "").strip()
        try:
            product.revoke(actor=request.user, reason=reason)
            messages.success(
                request, _("%(product)s has been revoked.") % {"product": product.name}
            )
            return redirect("products:product_detail", pk=product.pk)
        except ValueError as exc:
            messages.error(request, str(exc))

    return render(
        request,
        "products/product_revoke.html",
        {"product": product, "company": company},
    )


@user_passes_test(_is_admin)
def admin_overview(request):
    """FR50: the platform totals, grouped by status, with the alerts."""
    from companies.models import CompanyStatus

    by_company_status = (
        Company.objects.values("status").annotate(count=Count("id")).order_by("status")
    )
    by_product_status = (
        Product.objects.values("status").annotate(count=Count("id")).order_by("status")
    )
    recent_alerts = (
        Alert.objects.select_related("product", "scan")
        .order_by("-created_at")[:20]
    )
    return render(
        request,
        "products/admin_overview.html",
        {
            "by_company_status": by_company_status,
            "by_product_status": by_product_status,
            "recent_alerts": recent_alerts,
        },
    )


@user_passes_test(_is_admin)
def admin_revoke_product(request, pk):
    """FR42: the administrator revokes any passport, with the same obligation
    to state the reason as a company has.
    """
    product = get_object_or_404(Product.objects.select_related("company"), pk=pk)
    if request.method == "POST":
        reason = request.POST.get("reason", "").strip()
        try:
            product.revoke(actor=request.user, reason=reason)
            messages.success(request, _("%(product)s has been revoked.") % {"product": product.name})
            from accounts.emails import notify_revocation
            notify_revocation(product)
            return redirect("products:product_detail", pk=product.pk)
        except ValueError as exc:
            messages.error(request, str(exc))
    return render(
        request,
        "products/product_revoke.html",
        {"product": product, "company": product.company, "by_admin": True},
    )
