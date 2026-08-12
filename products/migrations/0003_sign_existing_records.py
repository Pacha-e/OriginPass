"""Sign the products and custody records that existed before signing was introduced.

Products carried an unsigned hash, which anyone holding the database could
recompute. Those values are replaced with signed ones. Custody transfers carried
no chain at all and are linked up here, one chain per product.
"""

from django.db import migrations

from audit.integrity import GENESIS, sign


def sign_existing(apps, schema_editor):
    Product = apps.get_model("products", "Product")
    CustodyTransfer = apps.get_model("products", "CustodyTransfer")

    for product in Product.objects.order_by("id"):
        product.integrity_hash = sign(
            product.passport_code,
            product.company_id,
            product.product_type,
            product.name,
            product.category,
            product.origin,
        )
        product.save(update_fields=["integrity_hash"])

    # One chain per product, not one across the table: a chain of custody
    # belongs to the thing being handed over.
    product_ids = CustodyTransfer.objects.values_list("product_id", flat=True).distinct()
    for product_id in product_ids:
        previous = GENESIS
        transfers = CustodyTransfer.objects.filter(product_id=product_id).order_by("id")
        for transfer in transfers:
            parts = (
                transfer.product_id,
                transfer.from_holder_id,
                transfer.to_holder_id,
                transfer.note,
                transfer.created_at.isoformat(),
            )
            transfer.previous_hash = previous
            transfer.entry_hash = sign(previous, *parts)
            transfer.save(update_fields=["previous_hash", "entry_hash"])
            previous = transfer.entry_hash


def unsign(apps, schema_editor):
    CustodyTransfer = apps.get_model("products", "CustodyTransfer")
    CustodyTransfer.objects.update(previous_hash=GENESIS, entry_hash="")


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0002_custodytransfer_entry_hash_and_more"),
        ("audit", "0003_sign_existing_records"),
    ]

    operations = [
        migrations.RunPython(sign_existing, unsign),
    ]
