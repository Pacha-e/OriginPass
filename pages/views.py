"""Pages that belong to the site itself rather than to any one app.

The landing page is the only one so far. It lives here rather than in `config`
because `config` is configuration, and a page is not configuration.

The error pages have no view: Django's own handlers render `403.html`, `404.html`
and `500.html` from the project template directory, and replacing them with
handlers of our own would add code whose only effect is to move three files.
"""

from django.shortcuts import render


def home(request):
    """The public landing page, reachable without an account."""
    return render(request, "pages/home.html")
