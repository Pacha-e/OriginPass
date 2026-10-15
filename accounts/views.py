"""Authentication flows. Orchestration only; the rules live in the forms."""

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render, resolve_url
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from .forms import AUTHENTICATION_ERROR, LoginForm, RegistrationForm
from .models import LoginAttempt


def _destination_after_login(request):
    """Where the caller asked to go, but only if it is somewhere on this site.

    The address arrives from the query string and is posted back with the form,
    so anyone can put one in a link. Following it unchecked would send the user
    to another site in the one second after they typed their password, which is
    the moment a page pretending to be this one most wants them. An address
    that is not ours is discarded rather than refused: the login itself
    succeeded, and the account's own page is where it belongs.
    """
    target = request.POST.get("next") or ""
    if target and url_has_allowed_host_and_scheme(
        target,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return target
    return resolve_url(settings.LOGIN_REDIRECT_URL)


def _client_ip(request):
    """The address the request came from.

    Django gives the last peer in REMOTE_ADDR. The X-Forwarded-For the
    reverse proxy adds is not trusted here because nothing in the
    development setup guarantees it came from a proxy we control; an
    attacker who can set it can rotate past the per-IP streak.
    """
    return request.META.get("REMOTE_ADDR") or "0.0.0.0"


def register(request):
    """FR01: a visitor creates an account with an email address and a password."""
    if request.user.is_authenticated:
        return redirect("pages:home")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("Your account has been created. You can now log in."))
            return redirect("accounts:login")
    else:
        form = RegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


def log_in(request):
    """FR03: a registered user logs in. FR04: one message for any bad credential.
    FR57: after five failures in fifteen minutes from one IP for one email the
    streak is locked for fifteen minutes, and the locked address still gets the
    same message as a wrong password (FR04), so a crawler cannot tell a locked
    account from one that does not exist.
    """
    if request.user.is_authenticated:
        return redirect("pages:home")

    if request.method == "POST":
        # Normalised and bounded here, before it reaches the table: the streak
        # must not be dodged by changing the case of the address, and an address
        # longer than the column would fail the insert instead of the login.
        email = request.POST.get("email", "").strip().lower()[:254]
        ip = _client_ip(request)

        if email and LoginAttempt.is_locked_out(email, ip):
            form = LoginForm(request, data=request.POST)
            # The lock is not announced: the same error a wrong password would
            # return is shown, so probing cannot enumerate accounts.
            form.add_error(None, AUTHENTICATION_ERROR)
            return render(
                request,
                "accounts/login.html",
                {"form": form, "next": request.GET.get("next", "")},
            )

        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            LoginAttempt.clear(email, ip)
            login(request, form.get_user())
            return redirect(_destination_after_login(request))
        if email:
            LoginAttempt.record_failure(email, ip)
    else:
        form = LoginForm(request)

    return render(
        request,
        "accounts/login.html",
        {"form": form, "next": request.GET.get("next", "")},
    )


@require_POST
def log_out(request):
    """FR05: the session ends and protected pages stop being reachable."""
    logout(request)
    messages.success(request, _("You have been logged out."))
    return redirect("pages:home")
