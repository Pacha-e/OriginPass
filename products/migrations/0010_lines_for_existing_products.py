"""Give every passport that predates lines a line of its own.

Each existing product becomes a line of one unit with the same identifying
fields and photo, so nothing a buyer reads changes and every signature stays as
it was. Reversing removes the lines and leaves the passports untouched.
"""

from django.db import migrations


def one_line_per_product(apps, schema_editor):
    Product = apps.get_model("products", "Product")
    ProductLine = apps.get_model("products", "ProductLine")

    for product in Product.objects.filter(line__isnull=True).order_by("id"):
        line = ProductLine.objects.create(
            company_id=product.company_id,
            product_type=product.product_type,
            name=product.name,
            description=product.description,
            category=product.category,
            origin=product.origin,
            image=product.image,
        )
        # Only the foreign key is written: the signed columns are not touched.
        Product.objects.filter(pk=product.pk).update(line=line)


def drop_lines(apps, schema_editor):
    Product = apps.get_model("products", "Product")
    ProductLine = apps.get_model("products", "ProductLine")
    Product.objects.update(line=None)
    ProductLine.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0009_productline"),
    ]

    operations = [
        migrations.RunPython(one_line_per_product, drop_lines),
    ]
