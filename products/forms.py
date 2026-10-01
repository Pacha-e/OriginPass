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

from .models import Product


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
            "category": _("For example Headwear, Basketry, Coffee."),
            "origin": _("The town or region where this unit was made."),
            "image": _("Optional. Shown on the public verification page."),
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
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


# ---- Custody transfer forms (Sprint 3) ----

from django.utils.translation import gettext_lazy as _trans
from .models import CustodyTransfer, TransferState


class TransferInitiateForm(forms.Form):
    """The current holder names the person they are handing the product to,
    and writes a note for the chain. The transfer is written Initiated; the
    receiver's answer (accept or decline) is a separate action.
    """
    to_holder_email = forms.EmailField(label=_trans("Recipient email address"))
    note = forms.CharField(
        label=_trans("Note for the chain of custody"),
        widget=forms.Textarea(attrs={"rows": 2}),
        required=False,
        help_text=_trans("Optional. Shown publicly on the verification page."),
    )

    def __init__(self, *args, product=None, holder=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.product = product
        self.holder = holder

    def clean_to_holder_email(self):
        from accounts.models import User
        email = User.objects.normalize_email(self.cleaned_data["to_holder_email"])
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError(
                _trans("No account uses that email address. The recipient needs to register first.")
            )
        if user == self.holder:
            raise ValidationError(_trans("You cannot transfer to yourself."))
        return user

    def save(self):
        return CustodyTransfer.objects.create(
            product=self.product,
            from_holder=self.holder,
            to_holder=self.cleaned_data["to_holder_email"],
            note=self.cleaned_data.get("note", ""),
        )


class TransferClaimForm(forms.Form):
    """A buyer claims the product with two codes: the passport code on the
    product and the transfer code the seller shared privately. Neither alone
    moves the product.
    """
    passport_code = forms.CharField(
        label=_trans("Passport code"),
        max_length=64,
        help_text=_trans("Printed on the product label or its QR code."),
    )
    transfer_code = forms.UUIDField(
        label=_trans("Transfer code"),
        help_text=_trans("Shared privately by the seller at the moment of the sale."),
    )

    def clean(self):
        cleaned = super().clean()
        passport_code = cleaned.get("passport_code")
        transfer_code = cleaned.get("transfer_code")
        if not (passport_code and transfer_code):
            return cleaned

        try:
            transfer = CustodyTransfer.objects.get(
                product__passport_code=passport_code,
                transfer_code=transfer_code,
                state=TransferState.INITIATED,
            )
        except CustodyTransfer.DoesNotExist:
            raise ValidationError(
                _trans("No pending transfer matches those codes. Ask the seller for the transfer code again.")
            )
        cleaned["transfer"] = transfer
        return cleaned
