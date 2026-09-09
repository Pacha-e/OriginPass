"""Written on every verification, holding no personal data.

The region is coarse on purpose: it is enough to notice the same passport being
scanned in distant places within a short window, which is what the analytics of
a later sprint look for, and not enough to locate a buyer.

Sprint 1 creates this table. The public verification page belongs to Sprint 2.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class DeviceCategory(models.TextChoices):
    MOBILE = "MOBILE", _("Mobile")
    TABLET = "TABLET", _("Tablet")
    DESKTOP = "DESKTOP", _("Desktop")
    UNKNOWN = "UNKNOWN", _("Unknown")


class Verdict(models.TextChoices):
    GENUINE = "GENUINE", _("Genuine")
    REVOKED = "REVOKED", _("Revoked")
    NOT_FOUND = "NOT_FOUND", _("Not found")


class ScanEvent(models.Model):
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="scan_events",
        null=True,
        blank=True,
        help_text=_("Null when the scanned code matched no product."),
    )
    scanned_at = models.DateTimeField(auto_now_add=True)
    region = models.CharField(max_length=100, blank=True)
    device_category = models.CharField(
        max_length=16, choices=DeviceCategory.choices, default=DeviceCategory.UNKNOWN
    )
    verdict = models.CharField(max_length=16, choices=Verdict.choices)

    class Meta:
        ordering = ["-scanned_at"]
        indexes = [models.Index(fields=["product", "scanned_at"])]

    def __str__(self):
        return f"{self.verdict} at {self.scanned_at:%Y-%m-%d %H:%M}"
