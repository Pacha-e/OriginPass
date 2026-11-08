"""Product passports: registration, the company's own list, and the QR image.

Every view here starts from the company that owns the request rather than from
the product, because a passport belongs to a company and a company only ever
sees its own. Whether a company may issue passports at all is decided by the
model; these views ask and then explain the answer.
"""

# ---- External imports ----
import csv
import io
from datetime import timedelta
from itertools import groupby
from operator import attrgetter

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Count, Exists, OuterRef, Prefetch, Q
from django.db.models.functions import TruncDay
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy
from django.views.decorators.http import require_POST

# ---- Internal imports ----
from accounts.decorators import admin_required
from accounts.emails import notify_revocation
from audit.models import Action, AuditEntry
from companies.decorators import owned_company_required
from companies.models import Company, CompanyStatus
from verification.models import ScanEvent

from .forms import IssueForm, ProductForm, RevocationForm
from .handover_views import waiting_by_email
from .models import (
    MAX_PASSPORTS_PER_ISSUE,
    PRODUCT_TYPE_BY_COMPANY_TYPE,
    Alert,
    CustodyTransfer,
    Product,
    ProductLine,
    ProductStatus,
    TransferState,
)
from .qr import PRINT_DPI, passport_qr_image
from .sheets import qr_sheets_pdf

# ---- Constants ----

#: Fifty Letter sheets of twelve: more than any workshop prints at once.
MAX_PRINT_PER_REQUEST = 600

#: The ranges a company can pick, in days. Anything else falls back to 30.
ANALYTICS_RANGES = (7, 30, 90, 365)

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

#: A cell starting with one of these is run as a formula by spreadsheets.
_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")

# ---- Public API ----


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


@login_required
@owned_company_required
def company_analytics(request, company):
    """FR46 counts over a range, FR47 regions, FR48 ranking, FR49 alerts and
    FR52 the change against the period of equal length before it. A company
    only ever sees scans of its own products.
    """
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


@login_required
@owned_company_required
def company_analytics_csv(request, company):
    """FR51: the scans of the selected range, one row per day, product and region."""
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


@login_required
def custody(request):
    """What one account holds now, with the ways to receive and hand over.

    Open to every account, with or without a company, because a distributor or
    a buyer holds products too.
    """
    held = Product.objects.held_by(request.user).select_related("company").order_by("name")
    return render(
        request,
        "products/custody.html",
        {"held": held, "waiting_by_email": waiting_by_email(request.user)},
    )


@login_required
@owned_company_required
def product_create(request, company):
    """FR19 for an approved company, FR20 for any other, FR21 and FR23 on save."""
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
                product.full_clean(exclude=["passport_code", "integrity_hash", "line"])
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
                return redirect("products:line_detail", pk=product.line_id)
    else:
        form = ProductForm(initial={"origin": company.location})

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
    return render(
        request,
        "products/product_detail.html",
        {
            "product": product,
            "holder": holder,
            "is_holder": holder == request.user,
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
@owned_company_required
def product_list(request, company):
    """The company's lines, one card each, filtered by a passport's status and searched
    by line name, category or any passport code.
    """
    lines = ProductLine.objects.filter(company=company)

    selected = request.GET.get("status", "")
    if selected in {value for value, label in ProductStatus.choices}:
        lines = lines.filter(Exists(Product.objects.filter(line=OuterRef("pk"), status=selected)))
    else:
        selected = ""

    query = request.GET.get("q", "").strip()
    if query:
        lines = lines.filter(
            Q(name__icontains=query)
            | Q(category__icontains=query)
            | Q(Exists(Product.objects.filter(line=OuterRef("pk"), passport_code__icontains=query)))
        )

    lines = lines.annotate(
        passport_count=Count("passports", distinct=True),
        handed_count=Count(
            "passports",
            filter=Q(passports__custody_transfers__state=TransferState.ACCEPTED),
            distinct=True,
        ),
    )

    return render(
        request,
        "products/product_list.html",
        {
            "company": company,
            "lines": lines,
            "statuses": ProductStatus.choices,
            "selected_status": selected,
            "query": query,
            "can_register": company.can_register_products,
        },
    )


@login_required
@owned_company_required
def line_detail(request, company, pk):
    """A line as its company sees it: its passports, and the form to issue more."""
    line = get_object_or_404(ProductLine, pk=pk, company=company)
    passports = line.passports.prefetch_related(
        Prefetch(
            "custody_transfers",
            queryset=CustodyTransfer.objects.filter(state=TransferState.ACCEPTED)
            .select_related("to_holder")
            .order_by("-resolved_at"),
            to_attr="accepted_transfers",
        )
    )
    return render(
        request,
        "products/line_detail.html",
        {
            "company": company,
            "line": line,
            "passports": passports,
            "issue_form": IssueForm(initial={"count": 1}),
        },
    )


@login_required
@owned_company_required
@require_POST
def line_issue(request, company, pk):
    """FR19 for a whole line: issue between 1 and MAX_PASSPORTS_PER_ISSUE passports."""
    line = get_object_or_404(ProductLine, pk=pk, company=company)
    form = IssueForm(request.POST)
    if not form.is_valid():
        messages.error(
            request,
            _("Choose between 1 and %(max)s passports at a time.")
            % {"max": MAX_PASSPORTS_PER_ISSUE},
        )
        return redirect("products:line_detail", pk=line.pk)

    try:
        passports = line.issue_passports(form.cleaned_data["count"], request.user)
    except ValueError:
        messages.error(request, REFUSAL_BY_STATUS[company.status])
        return redirect("products:line_detail", pk=line.pk)

    messages.success(
        request,
        _("Done: %(count)s new passports.") % {"count": len(passports)},
    )
    return redirect("products:line_detail", pk=line.pk)


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


@login_required
def qr_download(request, pk):
    """FR22: a PNG encoding the public verification address of this passport."""
    company = Company.objects.owned_by(request.user)
    product = get_object_or_404(Product, pk=pk, company=company)

    address = request.build_absolute_uri(
        reverse("verification:verify", args=[product.passport_code])
    )
    image = passport_qr_image(address)

    buffer = io.BytesIO()
    image.save(buffer, format="PNG", dpi=(PRINT_DPI, PRINT_DPI))

    response = HttpResponse(buffer.getvalue(), content_type="image/png")
    response["Content-Disposition"] = (
        f'attachment; filename="originpass-{product.passport_code}.png"'
    )
    return response


@login_required
def print_qr(request):
    """The active passports grouped by line; the chosen ones come back as a PDF of QR sheets."""
    products = _printable_products(request.user)
    error = ""

    if request.method == "POST":
        # Bounded: a primary key fits in 18 digits, and one request prints at
        # most MAX_PRINT_PER_REQUEST passports.
        ids = [
            value
            for value in request.POST.getlist("product")[:MAX_PRINT_PER_REQUEST]
            if value.isdigit() and len(value) <= 18
        ]
        chosen = list(products.filter(pk__in=ids))
        if chosen:
            base_url = request.build_absolute_uri("/").rstrip("/")
            response = HttpResponse(qr_sheets_pdf(chosen, base_url), content_type="application/pdf")
            response["Content-Disposition"] = 'attachment; filename="originpass-qr.pdf"'
            return response
        error = _("Choose at least one product to print.")

    return render(
        request,
        "products/print_qr.html",
        {
            "groups": _groups_by_line(products),
            "error": error,
            "preselect_line": _line_from_query(request),
        },
    )


# ---- Private helpers ----


def _csv_cell(value):
    """A cell a spreadsheet shows as text instead of running it (CSV injection)."""
    text = "" if value is None else str(value)
    return "'" + text if text.startswith(_FORMULA_PREFIXES) else text


def _groups_by_line(products):
    """(line, its products) pairs, lines in name order, so each line is one heading."""
    ordered = products.order_by("line__name", "line_id", "pk")
    return [(line, list(items)) for line, items in groupby(ordered, key=attrgetter("line"))]


def _line_from_query(request):
    """The line the page was asked to preselect, if the query names one."""
    value = request.GET.get("line", "")
    return int(value) if value.isdigit() and len(value) <= 18 else None


def _printable_products(user):
    """The active passports the account may print: its company's, or else those it holds."""
    company = Company.objects.owned_by(user)
    if company is None:
        products = Product.objects.held_by(user)
    else:
        products = Product.objects.filter(company=company)
    return products.filter(status=ProductStatus.ACTIVE).select_related("line")


def _refuse(request, company, heading, reason):
    """FR20: a refusal states its cause instead of hiding the page."""
    return render(
        request,
        "products/refusal.html",
        {"company": company, "heading": heading, "reason": reason},
        status=403,
    )


def _revoke(request, product, form):
    """Revoke, tell the holder (FR55) and report. Shared by company and admin."""
    holder = product.current_holder
    holder_email = holder.email if holder else product.holder_email
    try:
        product.revoke(actor=request.user, reason=form.cleaned_data["reason"])
    except ValueError:
        messages.info(request, _("This passport had already been revoked."))
        return
    notify_revocation(product, holder_email)
    messages.success(request, _("%(product)s has been revoked.") % {"product": product.name})


def _selected_range(request):
    """The range asked for in the query string, if it is one on offer."""
    try:
        days = int(request.GET.get("days", 30))
    except ValueError:
        return 30
    return days if days in ANALYTICS_RANGES else 30
