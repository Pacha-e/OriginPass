"""Sign and chain the records that existed before signing was introduced.

Rows written before this migration carry no signature, so `verify_chain` would
report the trail as broken from its first entry. This walks what is already
there in order and links it up.

Signing an old row does not prove it was never touched; nothing can prove that
after the fact. It establishes the chain from here on, which is what the
mechanism is for.
"""

from django.db import migrations

from audit.integrity import GENESIS, sign


def sign_existing(apps, schema_editor):
    AuditEntry = apps.get_model("audit", "AuditEntry")

    previous = GENESIS
    for entry in AuditEntry.objects.order_by("id"):
        parts = (
            entry.actor_id,
            entry.action,
            entry.target_type,
            entry.target_id,
            entry.reason,
            entry.created_at.isoformat(),
        )
        entry.previous_hash = previous
        entry.entry_hash = sign(previous, *parts)
        # The model refuses updates; the historical model this migration sees
        # does not carry that guard, which is why the backfill is possible here
        # and nowhere else.
        entry.save(update_fields=["previous_hash", "entry_hash"])
        previous = entry.entry_hash


def unsign(apps, schema_editor):
    AuditEntry = apps.get_model("audit", "AuditEntry")
    AuditEntry.objects.update(previous_hash=GENESIS, entry_hash="")


class Migration(migrations.Migration):
    dependencies = [
        ("audit", "0002_auditentry_entry_hash_auditentry_previous_hash_and_more"),
    ]

    operations = [
        migrations.RunPython(sign_existing, unsign),
    ]
