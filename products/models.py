"""One record per physical unit, and the chain of custody that follows it.

A passport that covered a whole batch would legitimise every copy of it, so a
Product is a single unit. The rules here restate what the prototype contracts
PasaporteProductos.sol and PasaporteOrigen.sol enforced on chain.

Sprint 1 creates these tables and their invariants. The views that exercise
them belong to later sprints.
"""

import secrets
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from audit.integrity import GENESIS, matches, sign, verify_chain
from audit.models import Action, AuditEntry
from companies.models import CompanyStatus, CompanyType


class ProductType(models.TextChoices):
    COMMERCIAL_ORIGINAL = "COMMERCIAL_ORIGINAL", _("Commercial original")
    ARTISAN = "ARTISAN", _("Artisan")


class ProductStatus(models.TextChoices):
    ACTIVE = "ACTIVE", _("Active")
    REVOKED = "REVOKED", _("Revoked")


class TransferState(models.TextChoices):
    INITIATED = "INITIATED", _("Initiated")
    ACCEPTED = "ACCEPTED", _("Accepted")
    DECLINED = "DECLINED", _("Declined")


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


class ProductQuerySet(models.QuerySet):
    def held_by(self, user):
        """The products whose current holder is this account, in one query.

        The holder is the receiver of the latest accepted transfer, or the
        company owner while no transfer has been accepted: the same rule as
        `Product.current_holder`, stated for many rows at once.
        """
        last_receiver = (
            CustodyTransfer.objects.filter(
                product=models.OuterRef("pk"), state=TransferState.ACCEPTED
            )
            .order_by("-resolved_at")
            .values("to_holder")[:1]
        )
        return self.annotate(last_receiver=models.Subquery(last_receiver)).filter(
            Q(last_receiver=user.pk) | Q(last_receiver__isnull=True, company__owner=user)
        )


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
    origin = models.CharField(max_length=200, help_text=_("Place of manufacture."))
    image = models.ImageField(upload_to="product-images/", blank=True)
    integrity_hash = models.CharField(max_length=64, blank=True)
    revocation_reason = models.TextField(blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProductQuerySet.as_manager()

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
        """Sign the row, then write it once.

        Every field the signature covers is known before the row reaches the
        database: `passport_code` has a Python-side default, which Django
        applies when the instance is built rather than when it is saved. This
        used to write each row twice, on the stated grounds that the code only
        existed after the first save. That was not true, and it cost every
        registration an extra UPDATE.
        """
        self.integrity_hash = self.compute_integrity_hash()

        # A caller changing one column still needs the signature to follow it,
        # or an edit through `update_fields` would leave the row looking
        # tampered with.
        update_fields = kwargs.get("update_fields")
        if update_fields is not None:
            kwargs["update_fields"] = {*update_fields, "integrity_hash"}

        super().save(*args, **kwargs)

    def clean(self):
        """Only an approved company issues passports, and only of its own kind."""
        if self.company_id is None:
            return
        if self.company.status != CompanyStatus.APPROVED:
            raise ValidationError({"company": _("Only an approved company can register products.")})
        expected = PRODUCT_TYPE_BY_COMPANY_TYPE[self.company.company_type]
        if self.product_type != expected:
            raise ValidationError(
                {
                    "product_type": _(
                        "A %(company_type)s registers products of type %(product_type)s."
                    )
                    % {
                        "company_type": self.company.get_company_type_display().lower(),
                        "product_type": expected.label.lower(),
                    }
                }
            )

    def signed_parts(self):
        """The identifying fields the signature covers."""
        return (
            self.passport_code,
            self.company_id,
            self.product_type,
            self.name,
            self.category,
            self.origin,
        )

    def compute_integrity_hash(self):
        """Sign the identifying fields, so later tampering is detectable.

        Signed rather than hashed. A plain hash over these columns could be
        recomputed by anyone able to write to them, which would let an edited
        row be left looking untouched; the key this uses is not in the database.
        """
        return sign(*self.signed_parts())

    @property
    def is_intact(self):
        # Asked through `matches` rather than compared against a fresh
        # signature, so that a row written before a key rotation is still
        # recognised as ours instead of being reported as altered.
        return matches(self.integrity_hash, *self.signed_parts())

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
        """FR41, FR42: the passport stops being valid and the record says why.

        Asked of the locked row rather than of this copy, so two revocations
        submitted together cannot both pass the check and both write an entry
        to the trail.
        """
        if not reason.strip():
            raise ValueError("A reason is required to revoke a product.")
        with transaction.atomic():
            stored_status = (
                type(self)
                .objects.select_for_update()
                .filter(pk=self.pk)
                .values_list("status", flat=True)
                .first()
            )
            if stored_status == ProductStatus.REVOKED:
                raise ValueError("This product has already been revoked.")
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
    # A random code the seller keeps private and hands over in person. The buyer
    # claims ownership by producing it together with the passport code (FR40).
    transfer_code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
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
            # One chain per product, and a chain is linear: within a product no
            # handover is the predecessor of two others. The lock in `_append`
            # has nothing to hold on a product's first transfer, so the shape of
            # the chain is stated to the database as well.
            models.UniqueConstraint(
                fields=["product", "previous_hash"],
                name="custody_transfer_links_to_one_predecessor",
            ),
            # A product is offered to one account at a time. Two open offers
            # could both be accepted, and the product would have two holders.
            models.UniqueConstraint(
                fields=["product"],
                condition=Q(state="INITIATED"),
                name="custody_transfer_one_open_offer",
            ),
        ]

    def __str__(self):
        return f"{self.product.passport_code}: {self.from_holder} -> {self.to_holder}"

    def save(self, *args, **kwargs):
        if self.pk is None:
            return self._append(*args, **kwargs)

        # Whether this row may still be written is decided by what the database
        # holds, never by what this instance holds. An instance read before the
        # transfer was resolved still carries Initiated, and asking it would let
        # that stale copy write itself over the resolution.
        #
        # Locked and read inside a transaction, because reading it plainly only
        # answers for a copy that was already stale. A resolution committing
        # between the read and the write would still be overwritten: the write
        # waits for the lock it does not hold, then lands on top of what it
        # waited for. The lock makes the answer hold until this row is written.
        with transaction.atomic():
            stored_state = (
                type(self)
                .objects.select_for_update()
                .filter(pk=self.pk)
                .values_list("state", flat=True)
                .first()
            )
            if stored_state != TransferState.INITIATED:
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
        """FR38 and FR39, with the reason a person can act on."""
        if self.product_id and self.product.status == ProductStatus.REVOKED:
            raise ValidationError(_("A revoked product cannot change hands."))
        if self.from_holder_id == self.to_holder_id:
            raise ValidationError(_("A product cannot be transferred to its current holder."))
        if self.product_id and self.from_holder_id != self.product.current_holder.pk:
            raise ValidationError(_("Only the current holder can transfer this product."))
        if (
            self.product_id
            and type(self)
            .objects.filter(product_id=self.product_id, state=TransferState.INITIATED)
            .exclude(pk=self.pk)
            .exists()
        ):
            raise ValidationError(
                _("This product already has an open offer. It has to be answered first.")
            )

    def _resolve(self, state, action, actor):
        with transaction.atomic():
            # Locked and re-read before the question is asked, so that two
            # resolutions of the same transfer cannot both find it open and
            # both append a resolution to the trail.
            stored_state = (
                type(self)
                .objects.select_for_update()
                .filter(pk=self.pk)
                .values_list("state", flat=True)
                .first()
            )
            if stored_state != TransferState.INITIATED:
                raise ValueError("This transfer has already been resolved.")

            self.state = state
            self.resolved_at = timezone.now()
            self.save(update_fields=["state", "resolved_at"])
            # The resolution is not covered by this row's own signature, so it
            # is written into the chained trail instead.
            AuditEntry.record(actor=actor or self.to_holder, action=action, target=self)

    def accept(self, actor=None):
        self._resolve(TransferState.ACCEPTED, Action.CUSTODY_ACCEPTED, actor)

    def decline(self, actor=None):
        self._resolve(TransferState.DECLINED, Action.CUSTODY_DECLINED, actor)


class AlertKind(models.TextChoices):
    DUPLICATE_SCAN = "DUPLICATE_SCAN", _("Duplicate scan")


class Alert(models.Model):
    """Raised when one passport is scanned from distant regions within a window."""

    product = models.ForeignKey("products.Product", on_delete=models.PROTECT, related_name="alerts")
    scan = models.ForeignKey(
        "verification.ScanEvent",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="alerts",
    )
    kind = models.CharField(max_length=32, choices=AlertKind.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["product", "scan"], name="alert_once_per_scan"),
        ]

    def __str__(self):
        return f"{self.get_kind_display()}: {self.product.passport_code}"
