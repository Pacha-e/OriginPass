"""Sign the status into every passport, so a status changed in the database shows.

Passports were signed over their identifying fields only. The status a verifier
reads was therefore outside the signature, and a row changed directly in the
database still looked intact. Every row is signed again with the status included.
"""

from django.db import migrations

from audit.integrity import sign


def sign_with_status(apps, schema_editor):
    Product = apps.get_model("products", "Product")

    for product in Product.objects.order_by("id"):
        product.integrity_hash = sign(
            product.passport_code,
            product.company_id,
            product.product_type,
            product.name,
            product.category,
            product.origin,
            product.status,
        )
        product.save(update_fields=["integrity_hash"])


def sign_without_status(apps, schema_editor):
    Product = apps.get_model("products", "Product")

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


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0007_one_open_offer_per_product"),
    ]

    operations = [
        migrations.RunPython(sign_with_status, sign_without_status),
    ]
