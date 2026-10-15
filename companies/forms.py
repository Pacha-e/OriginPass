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
SUSPENSION_REASON_REQUIRED = _("A reason is required to suspend a company.")


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
            "evidence_notes",
            "publish_consent",
        ]
        labels = {
            "legal_name": _("Legal name"),
            "company_type": _("Company type"),
            "verification_track": _("Verification track"),
            "description": _("Description"),
            "location": _("Location"),
            "website": _("Contact website"),
            "registry_code": _("Official registry code"),
            "evidence_notes": _("Evidence of your craft"),
            "publish_consent": _("Consent to publish"),
        }
        help_texts = {
            "legal_name": _("The name of your workshop or business, as buyers know it."),
            "company_type": _(
                "Artisan workshop: you make products by hand and have no commercial "
                "registry. Commercial company: you have a NIT or a Chamber of Commerce record."
            ),
            "verification_track": _(
                "Only for a commercial company: where your registry comes from. "
                "An artisan workshop is reviewed by a person and leaves this empty."
            ),
            "description": _("What you make and since when. Buyers read this."),
            "location": _("Town and department, for example: Tuchín, Córdoba."),
            "website": _("Optional. A page or social network where buyers find you."),
            "registry_code": _(
                "Required for a commercial company, for example a NIT "
                "or a Chamber of Commerce code."
            ),
            "evidence_notes": _(
                "Required for an artisan workshop without a registry: how you work, "
                "your materials, your workspace, and anyone who can vouch for you. "
                "Only the reviewer reads this; it is never published."
            ),
            "publish_consent": _(
                "Once approved, your name, town and description are shown on a public "
                "profile so buyers can find you. Tick to agree."
            ),
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "evidence_notes": forms.Textarea(attrs={"rows": 4}),
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
            # FR09: a human decides from real evidence, so the application has to
            # carry it; a blank note leaves the reviewer nothing to work with.
            if not (cleaned.get("evidence_notes") or "").strip():
                self.add_error(
                    "evidence_notes",
                    _(
                        "Describe the evidence of your craft so a person can review "
                        "your workshop without a registry code."
                    ),
                )

        # FR18: an approved company gets a public profile, whoever it is, so
        # applying without consenting to it cannot succeed.
        if not cleaned.get("publish_consent"):
            self.add_error(
                "publish_consent",
                _("Your consent is needed to publish your profile once approved."),
            )

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


class SuspensionForm(forms.Form):
    """A suspension is a negative decision too, so it carries its reason (FR15, DBR12)."""

    reason = forms.CharField(
        label=_("Reason for the suspension"),
        widget=forms.Textarea(attrs={"rows": 3}),
        error_messages={"required": SUSPENSION_REASON_REQUIRED},
    )

    def clean_reason(self):
        reason = self.cleaned_data["reason"].strip()
        if not reason:
            raise forms.ValidationError(SUSPENSION_REASON_REQUIRED)
        return reason
