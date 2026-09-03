"""Input validation for product passports.

The product type is deliberately not a field here. It follows from the type of
the company registering the product (FR23), so offering it would be offering a
choice with exactly one valid answer, and a chance to get it wrong. The passport
code is not a field either: it is generated, never entered (FR21).

What remains is four required fields and one optional image, which is what keeps
registration inside the five that UR10 allows.
"""

from django import forms

from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "description", "category", "origin", "image"]
        labels = {
            "name": "Product name",
            "description": "Description",
            "category": "Category",
            "origin": "Place of manufacture",
            "image": "Photograph",
        }
        help_texts = {
            "category": "For example Headwear, Basketry, Coffee.",
            "origin": "The town or region where this unit was made.",
            "image": "Optional. Shown on the public verification page.",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not name:
            raise forms.ValidationError("A product needs a name.")
        return name

    def clean_origin(self):
        origin = self.cleaned_data["origin"].strip()
        if not origin:
            raise forms.ValidationError("A passport states where the product was made.")
        return origin
