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
from django.core import signing
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_GET, require_POST

# ---- Internal imports ----
from accounts.emails import notify_possession
from companies.models import CompanyStatus

from .email_handover import HandoverEmailForm, make_claim_token, read_claim_token
from .handover import (
    check_handover_code,
    handover_code,
    is_locked,
    product_code_args,
    record_failure,
    seconds_left,
)
from .models import CustodyTransfer, Product, ProductStatus, TransferState
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
def receive_start(request):
    """Where a receiver starts: read the product's QR with the camera, or type its code."""
    typed = request.GET.get("code", "").strip()
    error = None
    if typed:
        # The QR holds the whole verification address; keep only its last part.
        code = typed.rstrip("/").rsplit("/", 1)[-1]
        if Product.objects.filter(passport_code=code).exists():
            return redirect("products:receive", passport_code=code)
        error = _("No product has that code. Check each letter, or read the QR again.")
    return render(request, "products/receive_start.html", {"typed": typed, "error": error})


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


@login_required
def handover_email(request, pk):
    """Hand the product to a person without an account, by their email address."""
    product = _held_by_requester(request, pk)
    form = HandoverEmailForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        transfer = CustodyTransfer.record_handover(
            product, actor=request.user, to_email=form.cleaned_data["email"]
        )
        _send_possession(request, transfer)
        messages.success(
            request,
            _("Done. We sent %(email)s a message with the product.") % {"email": transfer.to_email},
        )
        return redirect("products:custody")
    return render(request, "products/handover_email.html", {"product": product, "form": form})


@login_required
def correct_email(request, pk):
    """Fix a mistyped address, while nobody has claimed the product yet."""
    product, transfer = _given_by_requester(request, pk)
    form = HandoverEmailForm(request.POST or None, initial={"email": transfer.to_email})
    if request.method == "POST" and form.is_valid():
        corrected = CustodyTransfer.record_handover(
            product,
            actor=request.user,
            to_email=form.cleaned_data["email"],
            note=_("Email corrected by whoever handed it over."),
        )
        _send_possession(request, corrected)
        messages.success(
            request,
            _("Corrected. We sent %(email)s a message with the product.")
            % {"email": corrected.to_email},
        )
        return redirect("products:custody")
    return render(
        request,
        "products/handover_email.html",
        {"product": product, "form": form, "correcting": transfer.to_email},
    )


@login_required
@require_POST
def resend_email(request, pk):
    _product, transfer = _given_by_requester(request, pk)
    _send_possession(request, transfer)
    messages.success(request, _("Sent again to %(email)s.") % {"email": transfer.to_email})
    return redirect("products:custody")


def claim_email(request, token):
    """The link in the message: keep the product in the account of that address."""
    try:
        transfer = read_claim_token(token)
    except (signing.BadSignature, LookupError, CustodyTransfer.DoesNotExist, ValueError):
        return render(request, "products/claim_email.html", {"dead": True})

    context = {"transfer": transfer, "product": transfer.product, "next": request.path}
    if not request.user.is_authenticated:
        return render(request, "products/claim_email.html", context)
    if request.user.email.lower() != transfer.to_email.lower():
        context["wrong_account"] = True
        return render(request, "products/claim_email.html", context)

    if request.method == "POST":
        try:
            CustodyTransfer.record_handover(
                transfer.product, actor=request.user, to_holder=request.user
            )
        except ValidationError:
            return render(request, "products/claim_email.html", {"dead": True})
        messages.success(
            request, _("It is yours now: %(product)s.") % {"product": transfer.product.name}
        )
        return redirect("products:custody")
    return render(request, "products/claim_email.html", context)


def waiting_by_email(user):
    """The handovers this account made to an address that has not kept them yet."""
    sent = (
        CustodyTransfer.objects.filter(
            state=TransferState.ACCEPTED, from_holder=user, to_email__gt=""
        )
        .select_related("product")
        .order_by("-resolved_at")
    )
    waiting = []
    for transfer in sent:
        latest = (
            transfer.product.custody_transfers.filter(state=TransferState.ACCEPTED)
            .order_by("-resolved_at", "-id")
            .first()
        )
        # A correction is a later handover from the address to the address:
        # the product still waits, under the corrected address.
        if latest.to_email and _handed_by(latest, user) and latest not in waiting:
            waiting.append(latest)
    return waiting


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


def _given_by_requester(request, pk):
    """The product and its latest handover, if this account handed it to an
    address that has not claimed it yet; otherwise a 404."""
    product = get_object_or_404(Product, pk=pk)
    transfer = (
        product.custody_transfers.filter(state=TransferState.ACCEPTED)
        .order_by("-resolved_at", "-id")
        .first()
    )
    if transfer is None or not transfer.to_email or not _handed_by(transfer, request.user):
        raise Http404
    return product, transfer


def _handed_by(transfer, user):
    """Who handed it over: the account that sent it, or, after corrections,
    the account that sent the first handover to an address."""
    while transfer is not None and transfer.from_holder_id is None:
        transfer = (
            transfer.product.custody_transfers.filter(
                state=TransferState.ACCEPTED, to_email=transfer.from_email, id__lt=transfer.id
            )
            .order_by("-id")
            .first()
        )
    return transfer is not None and transfer.from_holder_id == user.pk


def _send_possession(request, transfer):
    claim_url = request.build_absolute_uri(
        reverse("products:claim_email", args=[make_claim_token(transfer)])
    )
    company = getattr(request.user, "company", None)
    giver = company.legal_name if company is not None else request.user.email
    notify_possession(transfer, claim_url, giver)


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
