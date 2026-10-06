"""Input validation for product passports.

The product type is deliberately not a field here. It follows from the type of
the company registering the product (FR23), so offering it would be offering a
choice with exactly one valid answer, and a chance to get it wrong. The passport
code is not a field either: it is generated, never entered (FR21).

What remains is four required fields and one optional image, which is what keeps
registration inside the five that UR10 allows.
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from accounts.models import User

from .models import CustodyTransfer, Product, TransferState


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "description", "category", "origin", "image"]
        labels = {
            "name": _("Product name"),
            "description": _("Description"),
            "category": _("Category"),
            "origin": _("Place of manufacture"),
            "image": _("Photograph"),
        }
        help_texts = {
            "name": _("The name a buyer would recognise, with what makes this one different."),
            "description": _("How it was made, with what material and how long it took."),
            "category": _("The kind of product, in one or two words."),
            "origin": _("The town or region where this product was made."),
            "image": _(
                "Optional. Take it with your phone or choose one from your photos. "
                "Whoever scans the QR sees it."
            ),
        }
        widgets = {
            "name": forms.TextInput(
                attrs={"placeholder": _("For example: Sombrero vueltiao 21 vueltas")}
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": _("For example: Woven in caña flecha over three weeks."),
                }
            ),
            "category": forms.TextInput(attrs={"placeholder": _("For example: Hats")}),
            "origin": forms.TextInput(attrs={"placeholder": _("For example: Tuchín, Córdoba")}),
            # On a phone, image/* offers the camera as well as the gallery.
            "image": forms.ClearableFileInput(attrs={"accept": "image/*"}),
        }

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not name:
            raise forms.ValidationError(_("A product needs a name."))
        return name

    def clean_origin(self):
        origin = self.cleaned_data["origin"].strip()
        if not origin:
            raise forms.ValidationError(_("A passport states where the product was made."))
        return origin


class TransferInitiateForm(forms.Form):
    """FR35: the current holder names the account receiving the product.

    Whether this holder may hand this product over (FR38, FR39, one open offer)
    is the model's rule; the form asks it and puts its answer on the page.
    """

    to_holder_email = forms.EmailField(
        label=_("Email address of the receiver"),
        help_text=_(
            "The email of the person or business receiving the product. "
            "They need an OriginPass account."
        ),
    )
    note = forms.CharField(
        label=_("Note for the chain of custody"),
        widget=forms.Textarea(attrs={"rows": 2}),
        required=False,
        max_length=280,
        help_text=_(
            "Optional. Anyone who scans the product reads it, for example: "
            "Sold at the Cartagena fair."
        ),
    )

    def __init__(self, *args, product, holder, **kwargs):
        super().__init__(*args, **kwargs)
        self.product = product
        self.holder = holder

    def clean_to_holder_email(self):
        email = User.objects.normalize_email(self.cleaned_data["to_holder_email"])
        receiver = User.objects.filter(email__iexact=email, is_active=True).first()
        if receiver is None:
            raise ValidationError(
                _("No account uses that email address. The receiver has to register first.")
            )
        if receiver == self.holder:
            raise ValidationError(_("You already hold this product."))
        return receiver

    def clean(self):
        cleaned = super().clean()
        receiver = cleaned.get("to_holder_email")
        if receiver is not None:
            self.transfer = CustodyTransfer(
                product=self.product,
                from_holder=self.holder,
                to_holder=receiver,
                note=cleaned.get("note", "").strip(),
            )
            self.transfer.clean()
        return cleaned

    def save(self):
        self.transfer.save()
        return self.transfer


class TransferClaimForm(forms.Form):
    """FR40: the buyer proves the handover with the two codes.

    The passport code is on the product; the transfer code is shown only to the
    seller, who hands it over at the sale. Only the account the offer names can
    use them, so codes read over a shoulder move nothing.
    """

    passport_code = forms.CharField(
        label=_("Passport code"),
        max_length=64,
        help_text=_("Printed under the QR code of the product."),
    )
    transfer_code = forms.UUIDField(
        label=_("Transfer code"),
        help_text=_("The seller gives it to you at the moment of the sale."),
        error_messages={"invalid": _("A transfer code looks like 8-4-4-4-12 letters and digits.")},
    )

    def __init__(self, *args, claimant, **kwargs):
        super().__init__(*args, **kwargs)
        self.claimant = claimant

    def clean(self):
        cleaned = super().clean()
        passport_code = (cleaned.get("passport_code") or "").strip()
        transfer_code = cleaned.get("transfer_code")
        if not (passport_code and transfer_code):
            return cleaned

        transfer = (
            CustodyTransfer.objects.select_related("product")
            .filter(
                product__passport_code=passport_code,
                transfer_code=transfer_code,
                state=TransferState.INITIATED,
            )
            .first()
        )
        # One message for every mismatch, including an offer made to someone
        # else: telling them apart would confirm which codes are real.
        if transfer is None or transfer.to_holder_id != self.claimant.pk:
            raise ValidationError(
                _(
                    "No open transfer to your account matches those two codes. "
                    "Check them with the seller."
                )
            )
        cleaned["transfer"] = transfer
        return cleaned


class RevocationForm(forms.Form):
    """FR41, FR42: a revocation states its reason, and the buyer reads it."""

    reason = forms.CharField(
        label=_("Reason for the revocation"),
        widget=forms.Textarea(attrs={"rows": 3}),
        max_length=500,
        help_text=_("Required. A buyer who scans this passport reads exactly this text."),
        error_messages={"required": _("A revocation needs a reason.")},
    )

    def clean_reason(self):
        reason = self.cleaned_data["reason"].strip()
        if not reason:
            raise ValidationError(_("A revocation needs a reason."))
        return reason
