"""Handing a product to a person who has no account yet: by their email address.

The holder types the address twice; the product is recorded as held by that
address and a message carries a signed link. Opening the link signed in with
an account of that same address moves the product to the account.

Registering an account with the address is not enough by itself: OriginPass
does not verify addresses at registration, so anyone could register someone
else's. The link proves the person reads that inbox.

A link names the exact handover it came from. It stops working when that
handover is no longer the latest one for the product: after the claim, after
a correction of the address, or after any later handover.
"""

# ---- External imports ----
from datetime import timedelta

from django import forms
from django.core import signing
from django.utils.translation import gettext_lazy as _

# ---- Constants ----

CLAIM_LINK_LIFETIME = timedelta(days=30)
SALT = "originpass.claim.v1"


# ---- Public API ----


class HandoverEmailForm(forms.Form):
    """The receiver's address, typed twice so a typo is caught before it is sent."""

    email = forms.EmailField(label=_("Email of the person receiving it"))
    email_again = forms.EmailField(label=_("Write it again"))

    def clean(self):
        cleaned = super().clean()
        first = (cleaned.get("email") or "").strip().lower()
        second = (cleaned.get("email_again") or "").strip().lower()
        if first and second and first != second:
            raise forms.ValidationError(_("The two emails are not the same. Check them."))
        cleaned["email"] = first
        return cleaned


def make_claim_token(transfer):
    return signing.TimestampSigner(salt=SALT).sign(f"{transfer.pk}:{transfer.entry_hash}")


def read_claim_token(token):
    """The handover a link was made for, if the link is genuine, recent and still current.

    Raises `signing.BadSignature` (including `SignatureExpired`) for a forged or
    old link, and `LookupError` when the handover is no longer the latest one.
    """
    from products.models import CustodyTransfer, TransferState

    value = signing.TimestampSigner(salt=SALT).unsign(
        token, max_age=CLAIM_LINK_LIFETIME.total_seconds()
    )
    pk, entry_hash = value.split(":", 1)
    transfer = CustodyTransfer.objects.select_related("product").get(pk=pk, entry_hash=entry_hash)
    latest = (
        transfer.product.custody_transfers.filter(state=TransferState.ACCEPTED)
        .order_by("-resolved_at", "-id")
        .first()
    )
    if latest != transfer or not transfer.to_email:
        raise LookupError("This link is no longer the product's latest handover.")
    return transfer
