"""Outbound email through Django's configured backend.

In development these go to the console; in production the settings pick the
SMTP or transactional service, and these helpers do not change. The recipient
sees the same message either way.
"""

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext as _


def notify_company_decision(company):
    """FR53: the applicant is told the outcome with the stored reason."""
    if company.status == "APPROVED":
        subject = _("Your application has been approved")
    elif company.status == "REJECTED":
        subject = _("Your application was reviewed")
    else:
        return
    body = render_to_string(
        "accounts/email/company_decision.txt",
        {"company": company},
    )
    send_mail(
        subject=str(subject),
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[company.owner.email],
        fail_silently=True,
    )


def notify_transfer(transfer):
    """FR54: the receiver is told a transfer is waiting for their answer."""
    subject = _("Someone is offering you a product")
    body = render_to_string(
        "products/email/transfer_offered.txt",
        {"transfer": transfer},
    )
    send_mail(
        subject=str(subject),
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[transfer.to_holder.email],
        fail_silently=True,
    )


def notify_revocation(product):
    """FR55: the current holder is told their product was revoked and why."""
    subject = _("A product you hold has been revoked")
    body = render_to_string(
        "products/email/product_revoked.txt",
        {"product": product},
    )
    send_mail(
        subject=str(subject),
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[product.current_holder.email],
        fail_silently=True,
    )
