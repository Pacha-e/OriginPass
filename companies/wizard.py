"""The application asked one question per screen.

CompanyApplicationForm stays the only judge of what is valid. This module decides
which fields each screen asks, in which order, and which screens a company type
gets; the answers wait in the session until the last screen sends them.
"""

# ---- External imports ----
from django.utils.translation import gettext_lazy as _

# ---- Internal imports ----
from .forms import CompanyApplicationForm
from .models import COMMERCIAL_TRACKS, CompanyType

# ---- Constants ----

#: Where the answers wait between screens: form field to text, so that leaving
#: the wizard and coming back does not lose what was typed.
SESSION_KEY = "application_wizard"

ARTISAN_STEPS = ["kind", "name", "location", "description", "evidence", "consent"]
COMMERCIAL_STEPS = ["kind", "name", "registry", "location", "description", "website", "consent"]

STEP_FIELDS = {
    "kind": ["company_type"],
    "name": ["legal_name"],
    "registry": ["verification_track", "registry_code"],
    "location": ["location"],
    "description": ["description"],
    "evidence": ["evidence_notes"],
    "website": ["website"],
    "consent": ["publish_consent"],
}

#: The form names its fields after the model ("verification track"). A buyer or an
#: artisan reads these instead, so the screens carry their own words.
LABELS = {
    "legal_name": _("Name of your workshop or business"),
    "verification_track": _("Where your company is registered"),
    "registry_code": _("Number (NIT or Chamber of Commerce code)"),
    "location": _("Town and department"),
    "description": _("What you make and since when"),
    "evidence_notes": _("How you work"),
    "website": _("Web page or social network"),
}

#: The form's help speaks to the long form, where both paths share the screen
#: ("only for a commercial company..."). Each wizard screen is already one path.
HELP = {
    "legal_name": _("As the people who buy from you know it."),
    "verification_track": "",
    "registry_code": _("For example, your NIT."),
    "location": _("For example: Tuchín, Córdoba."),
    "description": _("The people who buy read this."),
    "evidence_notes": _(
        "Your materials, where you work and who knows your work. "
        "Only the person who reviews it reads this; it is never published."
    ),
    "website": _("You can leave it empty."),
    "publish_consent": "",
}

# ---- Public API ----


def steps_for(company_type):
    """The screens a company type goes through. Before the kind is chosen, the workshop's."""
    if company_type == CompanyType.COMMERCIAL:
        return COMMERCIAL_STEPS
    return ARTISAN_STEPS


def build_form(data=None, initial=None):
    form = CompanyApplicationForm(data, initial=initial)
    for name, label in LABELS.items():
        form.fields[name].label = label
    for name, help_text in HELP.items():
        form.fields[name].help_text = help_text
    track = form.fields["verification_track"]
    track.choices = [("", _("Choose one"))] + [
        (value, label) for value, label in track.choices if value in COMMERCIAL_TRACKS
    ]
    return form


def step_errors(data, step):
    """The errors of this screen's fields only, so a later screen does not complain early."""
    form = build_form(data)
    form.is_valid()
    return {name: list(form.errors[name]) for name in STEP_FIELDS[step] if name in form.errors}
