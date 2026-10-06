"""The filters of the audit log (FR44)."""

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Action


class AuditFilterForm(forms.Form):
    actor = forms.CharField(
        label=_("Actor email"),
        required=False,
        max_length=254,
        widget=forms.TextInput(attrs={"placeholder": _("Part of an email address")}),
    )
    action = forms.ChoiceField(
        label=_("Action"), required=False, choices=[("", _("Any action")), *Action.choices]
    )
    since = forms.DateField(
        label=_("From"), required=False, widget=forms.DateInput(attrs={"type": "date"})
    )
    until = forms.DateField(
        label=_("Until"), required=False, widget=forms.DateInput(attrs={"type": "date"})
    )

    def clean(self):
        cleaned = super().clean()
        since, until = cleaned.get("since"), cleaned.get("until")
        if since and until and since > until:
            raise forms.ValidationError(_("The start date is after the end date."))
        return cleaned
