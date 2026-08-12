"""Views that belong to the project rather than to any single app."""

from django.shortcuts import render


def home(request):
    """Public landing page. Reachable without an account."""
    return render(request, "home.html")
