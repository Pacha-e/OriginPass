"""Handing a piece over in person: the holder's screen and the receiver's screen.

The holder opens "Entregar" on their phone: it shows the piece's QR, which only
identifies the piece, and the six-digit code that authorises the handover,
renewed every two minutes (products.handover). The receiver reads the QR, sees
the piece they are about to receive, types the code the holder says aloud, and
the piece is theirs.
"""

# ---- External imports ----
import base64
import io

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_GET

# ---- Internal imports ----
from companies.models import CompanyStatus

from .handover import (
    check_handover_code,
    handover_code,
    is_locked,
    product_code_args,
    record_failure,
    seconds_left,
)
from .models import CustodyTransfer, Product, ProductStatus
from .qr import passport_qr_image

# ---- Public API ----


@login_required
def handover(request, pk):
    """The holder's screen: the piece's QR and the code to say aloud."""
    product = _held_by_requester(request, pk)
    now = timezone.now()
    address = request.build_absolute_uri(
        reverse("verification:verify", args=[product.passport_code])
    )
    return render(
        request,
        "products/handover.html",
        {
            "product": product,
            "qr_data_uri": _png_data_uri(passport_qr_image(address)),
            "code": handover_code(*product_code_args(product), now),
            "seconds_left": seconds_left(now),
            "code_url": reverse("products:handover_code", args=[product.pk]),
        },
    )


@login_required
@require_GET
def handover_code_json(request, pk):
    """The code in force now, for the holder's screen to refresh itself."""
    product = _held_by_requester(request, pk)
    now = timezone.now()
    response = JsonResponse(
        {
            "code": handover_code(*product_code_args(product), now),
            "seconds_left": seconds_left(now),
        }
    )
    response["Cache-Control"] = "no-store"
    return response


@login_required
def receive(request, passport_code):
    """The receiver's screen: the piece they are about to receive, and the code box."""
    product = get_object_or_404(
        Product.objects.select_related("company", "line"), passport_code=passport_code
    )

    if product.current_holder == request.user:
        messages.info(request, _("It is yours already: %(product)s.") % {"product": product.name})
        return redirect("products:custody")

    error = None
    if product.status == ProductStatus.REVOKED:
        error = _("This passport was revoked, so this piece cannot change hands.")
    elif request.method == "POST":
        error = _receive(request, product)
        if error is None:
            messages.success(
                request, _("It is yours now: %(product)s.") % {"product": product.name}
            )
            return redirect("products:custody")

    return render(
        request,
        "products/receive.html",
        {"product": product, "error": error, "holder_name": _holder_name(product)},
        status=200,
    )


# ---- Private helpers ----


def _held_by_requester(request, pk):
    """The product, only if the signed-in account holds it now; otherwise a 404.

    A 404 rather than a refusal: whether someone else's piece exists is not
    this account's business, and the code must never be shown to it.
    """
    product = get_object_or_404(Product.objects.select_related("company"), pk=pk)
    if product.status == ProductStatus.REVOKED or product.current_holder != request.user:
        raise Http404
    return product


def _receive(request, product):
    """Check the typed code and record the handover. Returns an error, or None."""
    now = timezone.now()
    if is_locked("product", product.pk, now):
        return _("Too many wrong codes for this piece. Try again in 15 minutes.")

    typed = request.POST.get("code", "")
    with transaction.atomic():
        # Locked before the code is checked: the code is made from the holder
        # and the handover count, so it is checked against the ones that will
        # be written over. A second receiver typing the same code waits here
        # and then finds it dead, instead of taking the piece from the first.
        locked = Product.objects.select_for_update().get(pk=product.pk)
        valid = check_handover_code(*product_code_args(locked), typed, now)
        if valid:
            try:
                CustodyTransfer.record_handover(locked, actor=request.user, to_holder=request.user)
            except ValidationError:
                valid = False
    if valid:
        return None

    # Recorded outside the transaction, so a refused attempt is still counted.
    record_failure("product", product.pk, now)
    return _(
        "That code does not work. Ask for the code shown right now on the screen "
        "of whoever is giving you the piece."
    )


def _holder_name(product):
    """Who holds it now, named the way the public page names them."""
    holder = product.current_holder
    company = getattr(holder, "company", None) if holder is not None else None
    if company is not None and company.status == CompanyStatus.APPROVED:
        return company.legal_name
    return _("A person")


def _png_data_uri(image):
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")
