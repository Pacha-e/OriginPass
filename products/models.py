"""One record per physical unit, and the chain of custody that follows it.

A passport that covered a whole batch would legitimise every copy of it, so a
Product is a single unit. The rules here restate what the prototype contracts
PasaporteProductos.sol and PasaporteOrigen.sol enforced on chain.

Sprint 1 creates these tables and their invariants. The views that exercise
them belong to later sprints.
"""

import hashlib
import secrets

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone

from audit.models import Action, AuditEntry
from companies.models import CompanyStatus, CompanyType


class ProductType(models.TextChoices):
    COMMERCIAL_ORIGINAL = "COMMERCIAL_ORIGINAL", "Commercial original"
    ARTISAN = "ARTISAN", "Artisan"


class ProductStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    REVOKED = "REVOKED", "Revoked"


class TransferState(models.TextChoices):
    INITIATED = "INITIATED", "Initiated"
    ACCEPTED = "ACCEPTED", "Accepted"
    DECLINED = "DECLINED", "Declined"


#: A commercial company issues commercial originals, an artisan workshop issues
#: artisan pieces. Crossing them is the TipoProductoInvalido error of the
#: prototype contract.
PRODUCT_TYPE_BY_COMPANY_TYPE = {
    CompanyType.COMMERCIAL: ProductType.COMMERCIAL_ORIGINAL,
    CompanyType.ARTISAN: ProductType.ARTISAN,
}


def generate_passport_code():
    """A code drawn from a cryptographically secure source.

    A sequential or otherwise derivable code would let anyone holding one
    genuine code produce codes that look valid, which defeats the purpose.
    """
    return secrets.token_urlsafe(24)


class Product(models.Model):
    company = models.ForeignKey(
        "companies.Company", on_delete=models.PROTECT, related_name="products"
    )
    passport_code = models.CharField(
        max_length=64, unique=True, db_index=True, default=generate_passport_code
    )
    product_type = models.CharField(max_length=32, choices=ProductType.choices)
    status = models.CharField(
        max_length=16, choices=ProductStatus.choices, default=ProductStatus.ACTIVE
    )
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=100)
    origin = models.CharField(max_length=200, help_text="Place of manufacture.")
    image = models.ImageField(upload_to="product-images/", blank=True)
    integrity_hash = models.CharField(max_length=64, blank=True)
    revocation_reason = models.TextField(blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-registered_at"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    ~Q(status=ProductStatus.REVOKED) | ~Q(revocation_reason="")
                ),
                name="revocation_states_a_reason",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.passport_code})"

    def clean(self):
        """Only an approved company issues passports, and only of its own kind."""
        if self.company_id is None:
            return
        if self.company.status != CompanyStatus.APPROVED:
            raise ValidationError(
                {"company": "Only an approved company can register products."}
            )
        expected = PRODUCT_TYPE_BY_COMPANY_TYPE[self.company.company_type]
        if self.product_type != expected:
            raise ValidationError(
                {
                    "product_type": (
                        f"A {self.company.get_company_type_display().lower()} registers "
                        f"products of type {expected.label.lower()}."
                    )
                }
            )

    def compute_integrity_hash(self):
        """Hash over the identifying fields, so later tampering is detectable."""
        identity = "|".join(
            [
                self.passport_code,
                str(self.company_id),
                self.product_type,
                self.name,
                self.category,
                self.origin,
            ]
        )
        return hashlib.sha256(identity.encode("utf-8")).hexdigest()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        expected = self.compute_integrity_hash()
        if self.integrity_hash != expected:
            self.integrity_hash = expected
            super().save(update_fields=["integrity_hash"])

    @property
    def is_intact(self):
        return self.integrity_hash == self.compute_integrity_hash()

    @property
    def current_holder(self):
        """The to_holder of the most recent accepted transfer, or the company owner."""
        last = (
            self.custody_transfers.filter(state=TransferState.ACCEPTED)
            .order_by("-resolved_at")
            .first()
        )
        return last.to_holder if last else self.company.owner

    def revoke(self, actor, reason):
        if self.status == ProductStatus.REVOKED:
            raise ValueError("This product has already been revoked.")
        if not reason.strip():
            raise ValueError("A reason is required to revoke a product.")
        self.status = ProductStatus.REVOKED
        self.revocation_reason = reason.strip()
        self.save(update_fields=["status", "revocation_reason"])
        AuditEntry.record(
            actor=actor,
            action=Action.PRODUCT_REVOKED,
            target=self,
            reason=self.revocation_reason,
        )


class CustodyTransfer(models.Model):
    """An append-only chain. Once resolved, a row is never edited (DBR06).

    Corrections are made by appending a new transfer, never by rewriting an old
    one: that is the whole value of a custody record.
    """

    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="custody_transfers"
    )
    from_holder = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="transfers_sent"
    )
    to_holder = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="transfers_received"
    )
    state = models.CharField(
        max_length=16, choices=TransferState.choices, default=TransferState.INITIATED
    )
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["created_at"]
        constraints = [
            models.CheckConstraint(
                condition=~Q(from_holder=models.F("to_holder")),
                name="custody_transfer_changes_holder",
            ),
        ]

    def __str__(self):
        return f"{self.product.passport_code}: {self.from_holder} -> {self.to_holder}"

    def clean(self):
        if self.product_id and self.product.status == ProductStatus.REVOKED:
            raise ValidationError("A revoked product accepts no custody transfer.")
        if self.from_holder_id == self.to_holder_id:
            raise ValidationError("A product cannot be transferred to its current holder.")
        if self.product_id and self.from_holder_id != self.product.current_holder.pk:
            raise ValidationError("Only the current holder can transfer this product.")

    def save(self, *args, **kwargs):
        if self.pk is not None and self.state != TransferState.INITIATED:
            existing = type(self).objects.get(pk=self.pk)
            if existing.state != TransferState.INITIATED:
                raise ValueError("A resolved custody transfer cannot be edited.")
        return super().save(*args, **kwargs)

    def _resolve(self, state):
        if self.state != TransferState.INITIATED:
            raise ValueError("This transfer has already been resolved.")
        self.state = state
        self.resolved_at = timezone.now()
        self.save(update_fields=["state", "resolved_at"])

    def accept(self):
        self._resolve(TransferState.ACCEPTED)

    def decline(self):
        self._resolve(TransferState.DECLINED)
