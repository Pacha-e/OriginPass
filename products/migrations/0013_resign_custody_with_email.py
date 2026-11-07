"""Sign every chain of custody again, now that its signature covers the email ends.

A handover can now go to, or come from, an email address instead of an account,
so the two email columns joined the signed facts. Existing rows hold "" in both;
each chain is walked in order and every link signed again over the new parts, so
`verify_integrity` keeps reporting it intact. Reversing signs them the old way.

A link is signed again only after its old signature has been checked: re-signing
an altered row would launder the alteration, so the migration stops and names
the row instead. Run it with the application stopped, so no handover is appended
to a chain while its links are being rewritten.
"""

from django.db import migrations

from audit.integrity import GENESIS, matches, sign


def _parts_with_email(t):
    return (
        t.product_id,
        t.from_holder_id,
        t.from_email,
        t.to_holder_id,
        t.to_email,
        t.note,
        t.created_at.isoformat(),
    )


def _parts_without_email(t):
    return (t.product_id, t.from_holder_id, t.to_holder_id, t.note, t.created_at.isoformat())


def _resign(apps, old_parts, new_parts):
    CustodyTransfer = apps.get_model("products", "CustodyTransfer")
    product_ids = (
        CustodyTransfer.objects.order_by().values_list("product_id", flat=True).distinct()
    )
    for product_id in product_ids:
        old_previous = new_previous = GENESIS
        for transfer in CustodyTransfer.objects.filter(product_id=product_id).order_by("id"):
            if transfer.previous_hash != old_previous or not matches(
                transfer.entry_hash, transfer.previous_hash, *old_parts(transfer)
            ):
                raise RuntimeError(
                    f"CustodyTransfer #{transfer.pk} does not verify under its current "
                    "signature; it is not signed again. Investigate before migrating."
                )
            old_previous = transfer.entry_hash
            transfer.previous_hash = new_previous
            transfer.entry_hash = sign(new_previous, *new_parts(transfer))
            transfer.save(update_fields=["previous_hash", "entry_hash"])
            new_previous = transfer.entry_hash


def with_email(apps, schema_editor):
    _resign(apps, _parts_without_email, _parts_with_email)


def without_email(apps, schema_editor):
    _resign(apps, _parts_with_email, _parts_without_email)


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0012_custody_email"),
    ]

    operations = [
        migrations.RunPython(with_email, without_email),
    ]
