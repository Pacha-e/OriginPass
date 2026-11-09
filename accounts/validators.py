"""Password rules of our own, run by Django with the ones in AUTH_PASSWORD_VALIDATORS."""

# ---- External imports ----
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


# ---- Public API ----
class DifferentFromCurrentValidator:
    """A reset or change happens because the password was forgotten or may be
    known to someone else; in the second case keeping it undoes the change."""

    def validate(self, password, user=None):
        if user is not None and user.pk and user.check_password(password):
            raise ValidationError(
                _("Choose a password different from the one you had."),
                code="password_unchanged",
            )

    def get_help_text(self):
        return _("It must be different from your current password.")
