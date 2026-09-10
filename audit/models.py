"""Append-only trail of every status change of a company or a product.

The value of an audit record is that it cannot be rewritten after the fact. The
model refuses updates, but a model can only refuse what goes through it: raw SQL
does not call `save()`. So each entry is also signed with a key the database does
not hold, and carries the signature of the entry before it. Rewriting a row
invalidates its own signature; removing one breaks the link for every row after
it. Neither is prevented, both are detectable.

What remains open is the operator, who holds the key as well as the database.
See `audit/integrity.py`.
"""

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone

from .integrity import GENESIS, sign, verify_chain


class Action(models.TextChoices):
    COMPANY_SUBMITTED = "COMPANY_SUBMITTED", "Company application submitted"
    COMPANY_RESUBMITTED = "COMPANY_RESUBMITTED", "Company application resubmitted"
    COMPANY_APPROVED = "COMPANY_APPROVED", "Company approved"
    COMPANY_REJECTED = "COMPANY_REJECTED", "Company rejected"
    COMPANY_SUSPENDED = "COMPANY_SUSPENDED", "Company suspended"
    COMPANY_REACTIVATED = "COMPANY_REACTIVATED", "Company reactivated"
    PRODUCT_REGISTERED = "PRODUCT_REGISTERED", "Product registered"
    PRODUCT_REVOKED = "PRODUCT_REVOKED", "Product revoked"
    CUSTODY_ACCEPTED = "CUSTODY_ACCEPTED", "Custody transfer accepted"
    CUSTODY_DECLINED = "CUSTODY_DECLINED", "Custody transfer declined"


class AuditEntry(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="audit_entries",
        null=True,
        blank=True,
    )
    action = models.CharField(max_length=32, choices=Action.choices)
    #: What the entry is about, as `app_label.ModelName`, and its primary key.
    #:
    #: Deliberately a string rather than a GenericForeignKey. Two of that
    #: field's properties are wrong for a trail whose whole job is to outlive
    #: what it describes: it cascades, so deleting the target would delete the
    #: evidence of what happened to it, and it identifies the model by a
    #: ContentType row whose id the database assigns. This entry's signature
    #: covers `target_type`, so an id that differs between two databases would
    #: make the same event sign differently in each, and a restore would
    #: invalidate every signature. A label is stable everywhere.
    target_type = models.CharField(max_length=32)
    target_id = models.PositiveIntegerField()
    reason = models.TextField(blank=True)
    # Set before the row is written rather than by the database, because the
    # signature covers it and cannot be computed after the fact.
    created_at = models.DateTimeField(default=timezone.now)

    previous_hash = models.CharField(max_length=64, default=GENESIS, editable=False)
    entry_hash = models.CharField(max_length=64, blank=True, editable=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "audit entries"
        indexes = [models.Index(fields=["target_type", "target_id"])]
        constraints = [
            # The chain is linear, so no entry is the predecessor of two
            # others. Saying that to the database closes the one gap the lock
            # in `record` cannot: an empty table has no row to lock, so two
            # writers racing to append the first entry would both read GENESIS
            # and both link to it. They still race; now the loser is rejected
            # instead of forking the chain in silence.
            models.UniqueConstraint(
                fields=["previous_hash"],
                name="audit_entry_links_to_one_predecessor",
            ),
        ]

    def __str__(self):
        return f"{self.action} on {self.target_type}#{self.target_id}"

    def save(self, *args, **kwargs):
        if self.pk is not None:
            raise ValueError("Audit entries are append-only and cannot be edited.")
        return super().save(*args, **kwargs)

    def signed_parts(self):
        """The values this entry's signature covers."""
        return (
            self.actor_id,
            self.action,
            self.target_type,
            self.target_id,
            self.reason,
            self.created_at.isoformat(),
        )

    @property
    def is_intact(self):
        """Whether this entry still matches its own signature, ignoring the chain."""
        from .integrity import matches

        return matches(self.entry_hash, self.previous_hash, *self.signed_parts())

    @classmethod
    def record(cls, *, actor, action, target, reason=""):
        """Append one entry, linked to the one before it.

        Where the call belongs, so that adding an action does not start with
        working it out again:

        - **A status change records itself, inside the model method that makes
          it**, within the same transaction. `Company._set_status` and
          `Product.revoke` do this. A decision and its record are one act: a
          refused transition must leave nothing behind, and one that went
          through must never be left without its entry.
        - **A creation records in the view**, after the object is saved. There
          is no model method to put it in — a form built the object — and there
          is nothing to be inconsistent with, because a row that does not exist
          yet has no state for the trail to disagree with.

        Both are used here on purpose. If an action ever has both a model
        method and a view, it goes in the model method.
        """
        with transaction.atomic():
            # Locks the current last entry so two writers cannot both link to
            # it. An empty table has no row to lock, which is why the linearity
            # of the chain is also a database constraint: see Meta.
            last = cls.objects.select_for_update().order_by("-id").first()
            previous = last.entry_hash if last else GENESIS

            entry = cls(
                actor=actor,
                action=action,
                # The app label is part of it: a bare class name would let two
                # models of the same name in different apps share a row in the
                # trail, which is the one place an ambiguity must not exist.
                target_type=target._meta.label,
                target_id=target.pk,
                reason=reason,
                created_at=timezone.now(),
                previous_hash=previous,
            )
            entry.entry_hash = sign(previous, *entry.signed_parts())
            entry.save()
            return entry

    @classmethod
    def verify_chain(cls):
        """Walk the whole trail. Returns (ok, problem)."""
        return verify_chain(cls.objects.order_by("id"), lambda entry: entry.signed_parts())
