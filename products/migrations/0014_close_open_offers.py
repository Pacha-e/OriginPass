"""Decline every offer still open from the old way of handing a product over.

Products now change hands in person, with a code that rotates every two minutes;
the old offer, accepted later with a long code, is gone from the interface. An
offer left open would block every new handover of its product (one open offer
per product), so each is declined the way the model declines one: state and
time set, and the decision written into the chained audit trail with its reason.
The offer rows' own signatures do not cover state or time, so they still verify.

Not reversible: an audit entry is never removed.
"""

from django.db import migrations
from django.utils import timezone

from audit.integrity import GENESIS, sign

REASON = "Cerrada al cambiar el sistema de entregas"


def decline_open_offers(apps, schema_editor):
    CustodyTransfer = apps.get_model("products", "CustodyTransfer")
    AuditEntry = apps.get_model("audit", "AuditEntry")

    for offer in CustodyTransfer.objects.filter(state="INITIATED").order_by("id"):
        now = timezone.now()
        CustodyTransfer.objects.filter(pk=offer.pk).update(state="DECLINED", resolved_at=now)

        last = AuditEntry.objects.select_for_update().order_by("-id").first()
        previous = last.entry_hash if last else GENESIS
        entry = AuditEntry(
            actor_id=None,
            action="CUSTODY_DECLINED",
            target_type="products.CustodyTransfer",
            target_id=offer.pk,
            reason=REASON,
            created_at=now,
            previous_hash=previous,
        )
        # The same parts as AuditEntry.signed_parts.
        entry.entry_hash = sign(
            previous,
            entry.actor_id,
            entry.action,
            entry.target_type,
            entry.target_id,
            entry.reason,
            entry.created_at.isoformat(),
        )
        entry.save()


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0013_resign_custody_with_email"),
        ("audit", "0004_auditentry_audit_entry_links_to_one_predecessor"),
    ]

    operations = [
        migrations.RunPython(decline_open_offers, migrations.RunPython.noop),
    ]
