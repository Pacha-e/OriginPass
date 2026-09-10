"""Root URL configuration."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("pages.urls")),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("companies/", include("companies.urls")),
    path("products/", include("products.urls")),
    # Kept short on purpose: this path is what the QR code encodes, and a
    # shorter address is a less dense image to scan.
    path("v/", include("verification.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
