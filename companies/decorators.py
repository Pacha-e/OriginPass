"""Access control for views that act on the signed-in account's own company."""

# ---- External imports ----
from functools import wraps

from django.shortcuts import redirect

# ---- Internal imports ----
from .models import Company

# ---- Public API ----


def owned_company_required(view):
    """Pass the view the account's company, or send the account to apply for one.

    Stacked under `login_required`, so that an anonymous request never reaches
    the lookup.
    """

    @wraps(view)
    def wrapper(request, *args, **kwargs):
        company = Company.objects.owned_by(request.user)
        if company is None:
            return redirect("companies:application_create")
        return view(request, company, *args, **kwargs)

    return wrapper
