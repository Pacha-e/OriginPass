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

from audit.models import Action, AuditEntry
from companies.models import Company, CompanyStatus

from .forms import ProductForm
from .models import PRODUCT_TYPE_BY_COMPANY_TYPE, Product, ProductStatus

#: Why a company in each non-approving status cannot issue a passport. Kept
#: here rather than in the template so that the view can also refuse a POST.
REFUSAL_BY_STATUS = {
    CompanyStatus.PENDING: (
        "Your application is still being reviewed. Passports can be issued once it "
        "has been approved."
    ),
    CompanyStatus.REJECTED: (
        "Your application was rejected, so it cannot issue passports. Edit and "
        "resubmit it to be reviewed again."
    ),
    CompanyStatus.SUSPENDED: (
        "Your company is suspended and cannot issue new passports. Passports "
        "already issued keep working."
    ),
}


def _company_of(request):
    return Company.objects.filter(owner=request.user).first()


def _refuse(request, company):
    """FR20: the refusal states its cause instead of hiding the page."""
    return render(
        request,
        "products/registration_refused.html",
        {"company": company, "reason": REFUSAL_BY_STATUS[company.status]},
        status=403,
    )


@login_required
def product_list(request):
    """FR24 filtered by status, FR25 searched by name, category or passport code."""
    company = _company_of(request)
    if company is None:
        return redirect("companies:application_create")

    products = Product.objects.filter(company=company)

    selected = request.GET.get("status", "")
    if selected in {value for value, _ in ProductStatus.choices}:
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
    company = _company_of(request)
    if company is None:
        return redirect("companies:application_create")
    if not company.can_register_products:
        return _refuse(request, company)

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
                    f"{product.name} now has a passport. Its code is {product.passport_code}.",
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
    company = _company_of(request)
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
    company = _company_of(request)
    product = get_object_or_404(Product, pk=pk, company=company)

    if product.status == ProductStatus.REVOKED:
        return render(
            request,
            "products/registration_refused.html",
            {
                "company": company,
                "reason": (
                    "This passport has been revoked. A revoked passport is a record of "
                    "what was issued and is not edited."
                ),
            },
            status=403,
        )

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f"{product.name} has been updated.")
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
    company = _company_of(request)
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
