"""Append-only trail of every status change of a company or a product.

The value of an audit record is that it cannot be rewritten after the fact, so
the model refuses updates outright. A correction is made by appending a new
entry, never by editing an old one.
"""

from django.conf import settings
from django.db import models


class Action(models.TextChoices):
    COMPANY_SUBMITTED = "COMPANY_SUBMITTED", "Company application submitted"
    COMPANY_RESUBMITTED = "COMPANY_RESUBMITTED", "Company application resubmitted"
    COMPANY_APPROVED = "COMPANY_APPROVED", "Company approved"
    COMPANY_REJECTED = "COMPANY_REJECTED", "Company rejected"
    COMPANY_SUSPENDED = "COMPANY_SUSPENDED", "Company suspended"
    COMPANY_REACTIVATED = "COMPANY_REACTIVATED", "Company reactivated"
    PRODUCT_REGISTERED = "PRODUCT_REGISTERED", "Product registered"
    PRODUCT_REVOKED = "PRODUCT_REVOKED", "Product revoked"


class AuditEntry(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="audit_entries",
        null=True,
        blank=True,
    )
    action = models.CharField(max_length=32, choices=Action.choices)
    target_type = models.CharField(max_length=32)
    target_id = models.PositiveIntegerField()
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "audit entries"
        indexes = [models.Index(fields=["target_type", "target_id"])]

    def __str__(self):
        return f"{self.action} on {self.target_type}#{self.target_id}"

    def save(self, *args, **kwargs):
        if self.pk is not None:
            raise ValueError("Audit entries are append-only and cannot be edited.")
        return super().save(*args, **kwargs)

    @classmethod
    def record(cls, *, actor, action, target, reason=""):
        """Append one entry for a change applied to `target`."""
        return cls.objects.create(
            actor=actor,
            action=action,
            target_type=target.__class__.__name__,
            target_id=target.pk,
            reason=reason,
        )
