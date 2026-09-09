"""Access control shared by the apps.

`admin_required` is the counterpart of the soloAdministrador modifier the
prototype contracts put on every administrative call.
"""

from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext as _


def admin_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not request.user.is_platform_admin:
            raise PermissionDenied(_("This page is reserved for the platform administrator."))
        return view(request, *args, **kwargs)

    return wrapper
