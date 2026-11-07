"""Sign every chain of custody again, now that its signature covers the email ends.

A handover can now go to, or come from, an email address instead of an account,
so the two email columns joined the signed facts. Existing rows hold "" in both;
each chain is walked in order and every link signed again over the new parts, so
`verify_integrity` keeps reporting it intact. Reversing signs them the old way.
"""

from django.db import migrations

from audit.integrity import GENESIS, sign


def _resign(apps, parts_of):
    CustodyTransfer = apps.get_model("products", "CustodyTransfer")
    product_ids = (
        CustodyTransfer.objects.order_by().values_list("product_id", flat=True).distinct()
    )
    for product_id in product_ids:
        previous = GENESIS
        for transfer in CustodyTransfer.objects.filter(product_id=product_id).order_by("id"):
            transfer.previous_hash = previous
            transfer.entry_hash = sign(previous, *parts_of(transfer))
            transfer.save(update_fields=["previous_hash", "entry_hash"])
            previous = transfer.entry_hash


def with_email(apps, schema_editor):
    _resign(
        apps,
        lambda t: (
            t.product_id,
            t.from_holder_id,
            t.from_email,
            t.to_holder_id,
            t.to_email,
            t.note,
            t.created_at.isoformat(),
        ),
    )


def without_email(apps, schema_editor):
    _resign(
        apps,
        lambda t: (t.product_id, t.from_holder_id, t.to_holder_id, t.note, t.created_at.isoformat()),
    )


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0012_custody_email"),
    ]

    operations = [
        migrations.RunPython(with_email, without_email),
    ]
