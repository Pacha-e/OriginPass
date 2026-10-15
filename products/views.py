"""Product passports: registration, the company's own list, and the QR image.

Every view here starts from the company that owns the request rather than from
the product, because a passport belongs to a company and a company only ever
sees its own. Whether a company may issue passports at all is decided by the
model; these views ask and then explain the answer.
"""

import csv
import io
from datetime import timedelta

import qrcode
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Count, Q
from django.db.models.functions import TruncDay
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy

from accounts.decorators import admin_required
from accounts.emails import notify_revocation, notify_transfer
from audit.models import Action, AuditEntry
from companies.models import Company, CompanyStatus
from verification.models import ScanEvent

from .forms import ProductForm, RevocationForm, TransferClaimForm, TransferInitiateForm
from .models import (
    PRODUCT_TYPE_BY_COMPANY_TYPE,
    Alert,
    CustodyTransfer,
    Product,
    ProductStatus,
    TransferState,
)

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
    holder = product.current_holder
    open_offer = (
        product.custody_transfers.filter(state=TransferState.INITIATED)
        .select_related("to_holder")
        .first()
    )
    return render(
        request,
        "products/product_detail.html",
        {
            "product": product,
            "holder": holder,
            "is_holder": holder == request.user,
            "open_offer": open_offer,
            "scan_count": product.scan_events.count(),
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


# ------------------------------------------------------------ custody (FR35-FR40)


@login_required
def custody(request):
    """Everything about custody for one account: what it holds, what is offered
    to it, and what it is offering. Open to every account, with or without a
    company, because a distributor or a buyer holds products too.
    """
    held = Product.objects.held_by(request.user).select_related("company").order_by("name")
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
        "products/custody.html",
        {"held": held, "incoming": incoming, "outgoing": outgoing},
    )


@login_required
def transfer_initiate(request, pk):
    """FR35: the current holder offers the product to another account.

    FR38 and FR39 are refusals with a reason, so a holder who cannot transfer
    gets a page that says why rather than a missing page.
    """
    product = get_object_or_404(Product.objects.select_related("company"), pk=pk)

    if product.status == ProductStatus.REVOKED:
        return _refuse(
            request,
            None,
            heading=_("This product cannot change hands"),
            reason=_("Its passport was revoked, and a revoked product accepts no transfer."),
        )
    if product.current_holder != request.user:
        return _refuse(
            request,
            None,
            heading=_("This product cannot change hands"),
            reason=_(
                "Only the current holder can transfer it, and your account does not hold it now."
            ),
        )

    if request.method == "POST":
        form = TransferInitiateForm(request.POST, product=product, holder=request.user)
        if form.is_valid():
            try:
                transfer = form.save()
            except IntegrityError:
                # Another offer for this product was saved between the check and
                # this write; the database constraint is what caught it.
                form.add_error(
                    None,
                    _("This product already has an open offer. It has to be answered first."),
                )
            else:
                notify_transfer(transfer)
                messages.success(
                    request,
                    _(
                        "Offer sent to %(who)s. Give them the transfer code when you hand "
                        "the product over."
                    )
                    % {"who": transfer.to_holder.email},
                )
                return redirect("products:custody")
    else:
        form = TransferInitiateForm(product=product, holder=request.user)

    return render(
        request,
        "products/transfer_initiate.html",
        {"form": form, "product": product},
    )


@login_required
def transfer_respond(request, pk):
    """FR36: the receiver accepts or declines. FR37: an acceptance joins the chain."""
    transfer = get_object_or_404(
        CustodyTransfer.objects.select_related("product__company", "from_holder"),
        pk=pk,
        to_holder=request.user,
    )

    if transfer.state != TransferState.INITIATED:
        messages.info(request, _("This transfer had already been answered."))
        return redirect("products:custody")

    if request.method == "POST":
        action = request.POST.get("action")
        if action not in {"accept", "decline"}:
            return redirect("products:transfer_respond", pk=transfer.pk)
        try:
            if action == "accept":
                transfer.accept(actor=request.user)
            else:
                transfer.decline(actor=request.user)
        except ValueError:
            # Answered meanwhile, possibly in another tab: that answer stands.
            messages.info(request, _("This transfer had already been answered."))
        else:
            template = (
                _("You now hold %(product)s.")
                if action == "accept"
                else _("You declined %(product)s.")
            )
            messages.success(request, template % {"product": transfer.product.name})
        return redirect("products:custody")

    return render(request, "products/transfer_respond.html", {"transfer": transfer})


@login_required
def transfer_claim(request):
    """FR40: the buyer claims the product with its passport code and the transfer code."""
    if request.method == "POST":
        form = TransferClaimForm(request.POST, claimant=request.user)
        if form.is_valid():
            transfer = form.cleaned_data["transfer"]
            try:
                transfer.accept(actor=request.user)
            except ValueError:
                messages.info(request, _("This transfer had already been answered."))
            else:
                messages.success(
                    request, _("You now hold %(product)s.") % {"product": transfer.product.name}
                )
            return redirect("products:custody")
    else:
        form = TransferClaimForm(claimant=request.user)

    return render(request, "products/transfer_claim.html", {"form": form})


# ------------------------------------------------------- analytics (FR46-FR52)

#: The ranges a company can pick, in days. Anything else falls back to 30.
ANALYTICS_RANGES = (7, 30, 90, 365)


def _selected_range(request):
    """The range asked for in the query string, if it is one on offer."""
    try:
        days = int(request.GET.get("days", 30))
    except ValueError:
        return 30
    return days if days in ANALYTICS_RANGES else 30


@login_required
def company_analytics(request):
    """FR46 counts over a range, FR47 regions, FR48 ranking, FR49 alerts and
    FR52 the change against the period of equal length before it. A company
    only ever sees scans of its own products.
    """
    company = Company.objects.owned_by(request.user)
    if company is None:
        return redirect("companies:application_create")

    days = _selected_range(request)
    since = timezone.now() - timedelta(days=days)
    scans = ScanEvent.objects.filter(product__company=company)
    current = scans.filter(scanned_at__gte=since)
    total = current.count()
    previous_total = scans.filter(
        scanned_at__gte=since - timedelta(days=days), scanned_at__lt=since
    ).count()

    by_day = list(
        current.annotate(day=TruncDay("scanned_at"))
        .values("day")
        .order_by("day")
        .annotate(count=Count("id"))
    )
    by_region = list(
        current.values("region").order_by().annotate(count=Count("id")).order_by("-count")
    )
    by_product = list(
        current.values("product__name", "product__passport_code")
        .annotate(count=Count("id"))
        .order_by("-count")[:10]
    )
    alerts = (
        Alert.objects.filter(product__company=company)
        .select_related("product", "scan")
        .order_by("-created_at")[:10]
    )

    # Bar lengths as percentages, worked out here so the template only draws.
    peak = max([row["count"] for row in by_day] + [1])
    for row in by_day:
        row["share"] = round(row["count"] * 100 / peak)
    for row in by_region:
        row["share"] = round(row["count"] * 100 / total) if total else 0
    top = max([row["count"] for row in by_product] + [1])
    for row in by_product:
        row["share"] = round(row["count"] * 100 / top)

    change = None
    if previous_total:
        change = round((total - previous_total) * 100 / previous_total)

    return render(
        request,
        "products/analytics.html",
        {
            "company": company,
            "days": days,
            "ranges": ANALYTICS_RANGES,
            "total": total,
            "previous_total": previous_total,
            "change": change,
            "by_day": by_day,
            "by_region": by_region,
            "by_product": by_product,
            "alerts": alerts,
        },
    )


#: A cell starting with one of these is run as a formula by spreadsheets.
_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def _csv_cell(value):
    """A cell a spreadsheet shows as text instead of running it (CSV injection)."""
    text = "" if value is None else str(value)
    return "'" + text if text.startswith(_FORMULA_PREFIXES) else text


@login_required
def company_analytics_csv(request):
    """FR51: the scans of the selected range, one row per day, product and region."""
    company = Company.objects.owned_by(request.user)
    if company is None:
        return redirect("companies:application_create")

    days = _selected_range(request)
    since = timezone.now() - timedelta(days=days)
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="originpass-analytics-{days}d.csv"'
    writer = csv.writer(response)
    writer.writerow(["day", "product", "passport_code", "region", "scans"])
    rows = (
        ScanEvent.objects.filter(product__company=company, scanned_at__gte=since)
        .annotate(day=TruncDay("scanned_at"))
        .values("day", "product__name", "product__passport_code", "region")
        .annotate(count=Count("id"))
        .order_by("day", "product__name")
    )
    for row in rows:
        writer.writerow(
            [
                row["day"].date().isoformat(),
                _csv_cell(row["product__name"]),
                row["product__passport_code"],
                _csv_cell(row["region"]),
                row["count"],
            ]
        )
    return response


# -------------------------------------------------------- revocation (FR41, FR42)


def _revoke(request, product, form):
    """Revoke, tell the holder (FR55) and report. Shared by company and admin."""
    holder = product.current_holder
    try:
        product.revoke(actor=request.user, reason=form.cleaned_data["reason"])
    except ValueError:
        messages.info(request, _("This passport had already been revoked."))
        return
    notify_revocation(product, holder)
    messages.success(request, _("%(product)s has been revoked.") % {"product": product.name})


@login_required
def product_revoke(request, pk):
    """FR41: the company that registered a product revokes it, stating why."""
    company = Company.objects.owned_by(request.user)
    product = get_object_or_404(Product, pk=pk, company=company)

    if product.status == ProductStatus.REVOKED:
        return _refuse(
            request,
            company,
            heading=_("This passport has already been revoked"),
            reason=REVOKED_PASSPORT_REFUSAL,
        )

    form = RevocationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        _revoke(request, product, form)
        return redirect("products:product_detail", pk=product.pk)

    return render(
        request,
        "products/product_revoke.html",
        {
            "product": product,
            "form": form,
            "cancel_url": reverse("products:product_detail", args=[product.pk]),
        },
    )


@admin_required
def admin_revoke_product(request, pk):
    """FR42: the administrator revokes any passport, under the same obligation
    to state the reason. The administrator has no product pages of their own,
    so the decision lands on the public page, which now shows it.
    """
    product = get_object_or_404(Product.objects.select_related("company"), pk=pk)
    if product.status == ProductStatus.REVOKED:
        messages.info(request, _("This passport had already been revoked."))
        return redirect("verification:verify", code=product.passport_code)

    form = RevocationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        _revoke(request, product, form)
        return redirect("verification:verify", code=product.passport_code)

    return render(
        request,
        "products/product_revoke.html",
        {
            "product": product,
            "form": form,
            "by_admin": True,
            "cancel_url": reverse("products:admin_overview"),
        },
    )


# --------------------------------------------------------------- admin (FR50)


@admin_required
def admin_overview(request):
    """FR50: the platform totals by status, with the latest alerts and passports."""
    companies = {
        row["status"]: row["count"]
        for row in Company.objects.values("status").order_by().annotate(count=Count("id"))
    }
    products = {
        row["status"]: row["count"]
        for row in Product.objects.values("status").order_by().annotate(count=Count("id"))
    }
    return render(
        request,
        "products/admin_overview.html",
        {
            "company_totals": [
                (value, label, companies.get(value, 0)) for value, label in CompanyStatus.choices
            ],
            "product_totals": [
                (value, label, products.get(value, 0)) for value, label in ProductStatus.choices
            ],
            "company_count": sum(companies.values()),
            "product_count": sum(products.values()),
            "scan_count": ScanEvent.objects.count(),
            "recent_alerts": Alert.objects.select_related("product__company", "scan")[:10],
            "recent_products": Product.objects.select_related("company").order_by("-registered_at")[
                :8
            ],
        },
    )
