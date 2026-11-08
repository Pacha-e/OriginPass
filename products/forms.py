"""Input validation for product passports.

The product type is deliberately not a field here. It follows from the type of
the company registering the product (FR23), so offering it would be offering a
choice with exactly one valid answer, and a chance to get it wrong. The passport
code is not a field either: it is generated, never entered (FR21).

What remains is four required fields and one optional image, which is what keeps
registration inside the five that UR10 allows.
"""

# ---- External imports ----
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

# ---- Internal imports ----
from .models import MAX_PASSPORTS_PER_ISSUE, Product

# ---- Public API ----


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

    def save(self, commit=True):
        """Write only the fields this form owns; the status is read under lock."""
        product = super().save(commit=False)
        if commit:
            product.save_edits(self.Meta.fields)
        return product


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


class IssueForm(forms.Form):
    """How many passports to issue from a line, at once."""

    count = forms.IntegerField(
        label=_("How many passports do you want to issue?"),
        min_value=1,
        max_value=MAX_PASSPORTS_PER_ISSUE,
        widget=forms.NumberInput(attrs={"inputmode": "numeric", "class": "stepper__input"}),
    )
