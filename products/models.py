"""One record per physical unit, and the chain of custody that follows it.

A passport that covered a whole batch would legitimise every copy of it, so a
Product is a single unit. The rules here restate what the prototype contracts
PasaporteProductos.sol and PasaporteOrigen.sol enforced on chain.

Sprint 1 creates these tables and their invariants. The views that exercise
them belong to later sprints.
"""

import secrets

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.crypto import constant_time_compare

from audit.integrity import GENESIS, sign, verify_chain
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
                condition=(~Q(status=ProductStatus.REVOKED) | ~Q(revocation_reason="")),
                name="revocation_states_a_reason",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.passport_code})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # The hash covers the passport code, which a new row only has after the
        # first save, so it is written on a second pass.
        expected = self.compute_integrity_hash()
        if self.integrity_hash != expected:
            self.integrity_hash = expected
            super().save(update_fields=["integrity_hash"])

    def clean(self):
        """Only an approved company issues passports, and only of its own kind."""
        if self.company_id is None:
            return
        if self.company.status != CompanyStatus.APPROVED:
            raise ValidationError({"company": "Only an approved company can register products."})
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
        """Sign the identifying fields, so later tampering is detectable.

        Signed rather than hashed. A plain hash over these columns could be
        recomputed by anyone able to write to them, which would let an edited
        row be left looking untouched; the key this uses is not in the database.
        """
        return sign(
            self.passport_code,
            self.company_id,
            self.product_type,
            self.name,
            self.category,
            self.origin,
        )

    @property
    def is_intact(self):
        return constant_time_compare(self.integrity_hash, self.compute_integrity_hash())

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

    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="custody_transfers")
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
    # Set before the row is written rather than by the database, because the
    # signature covers it and cannot be computed after the fact.
    created_at = models.DateTimeField(default=timezone.now)
    resolved_at = models.DateTimeField(null=True, blank=True)

    previous_hash = models.CharField(max_length=64, default=GENESIS, editable=False)
    entry_hash = models.CharField(max_length=64, blank=True, editable=False)

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

    def save(self, *args, **kwargs):
        if self.pk is None:
            return self._append(*args, **kwargs)

        if self.state != TransferState.INITIATED:
            existing = type(self).objects.get(pk=self.pk)
            if existing.state != TransferState.INITIATED:
                raise ValueError("A resolved custody transfer cannot be edited.")
        return super().save(*args, **kwargs)

    def _append(self, *args, **kwargs):
        """Link this handover to the previous one for the same product."""
        with transaction.atomic():
            last = (
                type(self)
                .objects.select_for_update()
                .filter(product_id=self.product_id)
                .order_by("-id")
                .first()
            )
            self.previous_hash = last.entry_hash if last else GENESIS
            self.entry_hash = sign(self.previous_hash, *self.signed_parts())
            return super().save(*args, **kwargs)

    def signed_parts(self):
        """The facts of the handover itself.

        The state and the time it was resolved are deliberately outside the
        signature, because they change once when the transfer is accepted or
        declined and that is a legitimate change. Those two are evidenced
        instead by the entry the resolution appends to the audit trail, which
        is chained.
        """
        return (
            self.product_id,
            self.from_holder_id,
            self.to_holder_id,
            self.note,
            self.created_at.isoformat(),
        )

    @classmethod
    def verify_chain(cls, product):
        """Walk one product's chain of custody. Returns (ok, problem)."""
        return verify_chain(
            cls.objects.filter(product=product).order_by("id"),
            lambda transfer: transfer.signed_parts(),
        )

    def clean(self):
        if self.product_id and self.product.status == ProductStatus.REVOKED:
            raise ValidationError("A revoked product accepts no custody transfer.")
        if self.from_holder_id == self.to_holder_id:
            raise ValidationError("A product cannot be transferred to its current holder.")
        if self.product_id and self.from_holder_id != self.product.current_holder.pk:
            raise ValidationError("Only the current holder can transfer this product.")

    def _resolve(self, state, action, actor):
        if self.state != TransferState.INITIATED:
            raise ValueError("This transfer has already been resolved.")
        self.state = state
        self.resolved_at = timezone.now()
        self.save(update_fields=["state", "resolved_at"])
        # The resolution is not covered by this row's own signature, so it is
        # written into the chained trail instead.
        AuditEntry.record(actor=actor or self.to_holder, action=action, target=self)

    def accept(self, actor=None):
        self._resolve(TransferState.ACCEPTED, Action.CUSTODY_ACCEPTED, actor)

    def decline(self, actor=None):
        self._resolve(TransferState.DECLINED, Action.CUSTODY_DECLINED, actor)
