import uuid

from django.db import migrations, models


def give_each_transfer_its_own_code(apps, schema_editor):
    # A callable default on AddField is evaluated once, so every existing row
    # would get the same code and the unique index below would refuse it.
    CustodyTransfer = apps.get_model("products", "CustodyTransfer")
    for transfer in CustodyTransfer.objects.filter(transfer_code__isnull=True).only("pk"):
        CustodyTransfer.objects.filter(pk=transfer.pk).update(transfer_code=uuid.uuid4())


class Migration(migrations.Migration):
    """Add, fill, then constrain: a database that already has transfers migrates too."""

    dependencies = [
        ("products", "0005_sprint3_alert"),
    ]

    operations = [
        migrations.AddField(
            model_name="custodytransfer",
            name="transfer_code",
            field=models.UUIDField(null=True, editable=False),
        ),
        migrations.RunPython(give_each_transfer_its_own_code, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="custodytransfer",
            name="transfer_code",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
