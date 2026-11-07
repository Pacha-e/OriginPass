"""Batches: several products handed over at once, with one QR and one code.

A company selling twenty hats to a shop shows one QR and says one code instead
of twenty. The batch only exists for the handover: once received, every
product is held on its own again, can be handed over or revoked alone, and a
buyer scans the product's own QR, never the batch's.

All the products pass or none does. A person's account hands over batches of
PERSON_BATCH_LIMIT products at most; a company's has no limit; receiving has
none. The code is the same rotating code as for one product (products.handover),
made from the batch, its owner and its state, so it dies once the batch is
handed over or cancelled.
"""

# ---- External imports ----
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils.translation import gettext as _

# ---- Internal imports ----
from .handover import check_handover_code, is_locked, record_failure
from .models import (
    BatchState,
    CustodyTransfer,
    Product,
    ProductStatus,
    TransferBatch,
    TransferBatchItem,
)

# ---- Constants ----

PERSON_BATCH_LIMIT = 5


# ---- Public API ----


def batch_code_args(batch):
    return ("batch", batch.pk, str(batch.owner_id), batch.state)


def create_batch(owner, products):
    """An open batch of `products`, which `owner` must hold now and which must be active."""
    products = list(products)
    if not products:
        raise ValidationError(_("Choose at least one product."))
    if not is_company_account(owner) and len(products) > PERSON_BATCH_LIMIT:
        raise ValidationError(
            _("A personal account hands over at most %(limit)s products at a time.")
            % {"limit": PERSON_BATCH_LIMIT}
        )
    with transaction.atomic():
        locked = list(Product.objects.select_for_update().filter(pk__in=[p.pk for p in products]))
        _check_all_handed_by(locked, owner)
        batch = TransferBatch.objects.create(owner=owner)
        try:
            with transaction.atomic():
                TransferBatchItem.objects.bulk_create(
                    TransferBatchItem(batch=batch, product=product) for product in locked
                )
        except IntegrityError:
            raise ValidationError(
                _("Some of these products are already in another open batch.")
            ) from None
    return batch


def receive_batch(batch, receiver, typed, at):
    """Move every product of the open batch to `receiver`, all or none."""
    if is_locked("batch", batch.pk, at):
        raise ValidationError(_("Too many wrong codes for this batch. Try again in 15 minutes."))
    with transaction.atomic():
        batch = TransferBatch.objects.select_for_update().get(pk=batch.pk)
        valid = batch.state == BatchState.OPEN and check_handover_code(
            *batch_code_args(batch), typed, at
        )
        if valid:
            products = list(
                Product.objects.select_for_update().filter(batch_items__batch=batch).order_by("pk")
            )
            _check_all_handed_by(products, batch.owner)
            for product in products:
                CustodyTransfer.record_handover(product, actor=receiver, to_holder=receiver)
            batch.state = BatchState.HANDED
            batch.save(update_fields=["state"])
            batch.items.update(is_open=False)
            return products
    record_failure("batch", batch.pk, at)
    raise ValidationError(
        _(
            "That code does not work. Ask for the code shown right now on the screen "
            "of whoever is giving you the products."
        )
    )


def cancel_batch(batch, user):
    if batch.owner_id != user.pk or batch.state != BatchState.OPEN:
        raise ValidationError(_("This batch can no longer be cancelled."))
    with transaction.atomic():
        batch.state = BatchState.CANCELLED
        batch.save(update_fields=["state"])
        batch.items.update(is_open=False)


def is_company_account(user):
    """A company account hands over batches of any size; a personal one does not."""
    return getattr(user, "company", None) is not None


# ---- Private helpers ----


def _check_all_handed_by(products, owner):
    """Every product active and held by `owner`; otherwise name the first that is not."""
    for product in products:
        if product.status == ProductStatus.REVOKED:
            raise ValidationError(
                _("%(product)s was revoked, so the batch cannot be handed over.")
                % {"product": product.name}
            )
        if product.current_holder != owner:
            raise ValidationError(
                _("%(product)s is not in the name of whoever is handing over the batch.")
                % {"product": product.name}
            )
