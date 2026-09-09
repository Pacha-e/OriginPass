"""Input validation for the authentication flows."""

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import User

#: One message for both an unknown address and a wrong password, so that the
#: form never reveals which of the two failed (FR04).
AUTHENTICATION_ERROR = _("The email address or password is incorrect.")


class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput, strip=False)
    password2 = forms.CharField(
        label=_("Confirm password"), widget=forms.PasswordInput, strip=False
    )

    class Meta:
        model = User
        fields = ["email"]
        labels = {"email": _("Email address")}

    def clean_email(self):
        email = User.objects.normalize_email(self.cleaned_data["email"])
        if User.objects.filter(email__iexact=email).exists():
            # Stated on the email field so it renders beside it (FR02, UR08).
            raise ValidationError(_("This email address is already in use."))
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(_("The two passwords do not match."))
        return password2

    def _post_clean(self):
        super()._post_clean()
        password = self.cleaned_data.get("password2")
        if password:
            try:
                validate_password(password, self.instance)
            except ValidationError as error:
                self.add_error("password2", error)

    def save(self, commit=True):
        user = super().save(commit=False)
        # Hashed with a per-record salt; the plain text is never stored (DBR11).
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(label=_("Email address"))
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput, strip=False)

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get("email")
        password = cleaned.get("password")

        if email and password:
            self.user = authenticate(self.request, username=email, password=password)
            if self.user is None:
                # Raised on the form, not on a field, so neither input is
                # singled out as the failing one (FR04).
                raise ValidationError(AUTHENTICATION_ERROR)
            if not self.user.is_active:
                raise ValidationError(AUTHENTICATION_ERROR)
        return cleaned

    def get_user(self):
        return self.user
