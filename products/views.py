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
