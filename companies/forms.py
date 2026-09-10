"""Input validation for company applications.

The rules in `clean` are the ones RegistroEmpresas._validarSolicitud enforced in
the prototype: the verification track has to match the company type, a
commercial company has to carry a registry code, and an artisan workshop does
not. Each failure is attached to the field that caused it so that the template
renders the cause next to that input (UR08).
"""

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import COMMERCIAL_TRACKS, Company, CompanyType, VerificationTrack

#: Stated once because the form raises it twice: as the required-field message
#: and again when the submitted reason turns out to be only whitespace.
REJECTION_REASON_REQUIRED = _("A reason is required to reject an application.")


class CompanyApplicationForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            "legal_name",
            "company_type",
            "verification_track",
            "description",
            "location",
            "website",
            "registry_code",
        ]
        labels = {
            "legal_name": _("Legal name"),
            "company_type": _("Company type"),
            "verification_track": _("Verification track"),
            "description": _("Description"),
            "location": _("Location"),
            "website": _("Contact website"),
            "registry_code": _("Official registry code"),
        }
        help_texts = {
            "verification_track": _(
                "A commercial company chooses one. An artisan workshop is reviewed by a person."
            ),
            "website": _("Optional."),
            "registry_code": _(
                "Required for a commercial company, for example a NIT "
                "or a Chamber of Commerce code."
            ),
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # The track is decided in clean() for an artisan workshop, so the field
        # is optional at the widget level and validated by company type below.
        self.fields["verification_track"].required = False
        self.fields["company_type"].choices = CompanyType.choices

    def clean(self):
        cleaned = super().clean()
        company_type = cleaned.get("company_type")
        track = cleaned.get("verification_track")
        registry_code = (cleaned.get("registry_code") or "").strip()

        if company_type == CompanyType.COMMERCIAL:
            # FR08: the registry code is what makes the commercial track verifiable.
            if not registry_code:
                self.add_error(
                    "registry_code",
                    _("A commercial company must provide an official registry code."),
                )
            if track not in COMMERCIAL_TRACKS:
                self.add_error(
                    "verification_track",
                    _(
                        "A commercial company is verified through the Chamber of Commerce "
                        "or an official registry."
                    ),
                )

        elif company_type == CompanyType.ARTISAN:
            # FR09: accepted with no registry code and marked for manual review.
            cleaned["verification_track"] = VerificationTrack.ARTISAN_REVIEW
            if registry_code:
                self.add_error(
                    "registry_code",
                    _(
                        "An artisan workshop is verified by manual review and does not "
                        "use a registry code."
                    ),
                )
            else:
                cleaned["registry_code"] = ""

        return cleaned


class RejectionForm(forms.Form):
    """A rejection carries a written reason, or it is not a rejection (FR14, DBR12)."""

    reason = forms.CharField(
        label=_("Reason for the rejection"),
        widget=forms.Textarea(attrs={"rows": 3}),
        error_messages={"required": REJECTION_REASON_REQUIRED},
    )

    def clean_reason(self):
        reason = self.cleaned_data["reason"].strip()
        if not reason:
            raise forms.ValidationError(REJECTION_REASON_REQUIRED)
        return reason
