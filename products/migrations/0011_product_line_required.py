"""Every passport belongs to a line, now that 0010 gave each one its own."""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0010_lines_for_existing_products"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="line",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="passports",
                to="products.productline",
            ),
        ),
    ]
