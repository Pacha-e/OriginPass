"""Outbound email through Django's configured backend.

In development these go to the console; in production the settings pick the
SMTP or transactional service, and these helpers do not change.

A notification is a courtesy on top of a decision that is already stored, so a
mail server that refuses it must not undo the decision or show the actor an
error page. The failure is logged instead of swallowed, so it can be found.
"""

import logging
import smtplib

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)


def _send(subject, template, context, recipient):
    body = render_to_string(template, context)
    try:
        send_mail(
            subject=str(subject),
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
        )
    except (smtplib.SMTPException, OSError):
        logger.exception("Could not send %r to %s", template, recipient)


def notify_company_decision(company):
    """FR53: the applicant is told the outcome with the stored reason."""
    if company.status == "APPROVED":
        subject = _("Your application has been approved")
    elif company.status == "REJECTED":
        subject = _("Your application has been rejected")
    else:
        return
    _send(
        subject,
        "accounts/email/company_decision.txt",
        {
            "company_name": company.legal_name,
            "status": company.get_status_display(),
            "reason": company.status_reason,
        },
        company.owner.email,
    )


def notify_transfer(transfer):
    """FR54: the receiver is told a transfer is waiting for their answer."""
    _send(
        _("A product is waiting for your answer"),
        "products/email/transfer_offered.txt",
        {
            "product_name": transfer.product.name,
            "sender": transfer.from_holder.email,
        },
        transfer.to_holder.email,
    )


def notify_revocation(product, holder):
    """FR55: the holder at the moment of revocation is told why.

    The holder is passed in rather than read from the product, because it has to
    be the one who held the product when it was revoked.
    """
    _send(
        _("A product you hold has been revoked"),
        "products/email/product_revoked.txt",
        {"product_name": product.name, "reason": product.revocation_reason},
        holder.email,
    )
