"""One record per company that has applied, whatever the outcome.

The rules below are the ones the hackathon prototype enforced on chain in
RegistroEmpresas.sol. Each is stated once, here, so that a view cannot bypass
it, and the ones the database can express are also written as constraints.
"""

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from audit.models import Action, AuditEntry


class CompanyType(models.TextChoices):
    COMMERCIAL = "COMMERCIAL", _("Commercial company")
    ARTISAN = "ARTISAN", _("Artisan workshop")


class VerificationTrack(models.TextChoices):
    CHAMBER_OF_COMMERCE = "CHAMBER_OF_COMMERCE", _("Chamber of Commerce")
    OFFICIAL_REGISTRY = "OFFICIAL_REGISTRY", _("Official registry")
    ARTISAN_REVIEW = "ARTISAN_REVIEW", _("Manual artisan review")


class CompanyStatus(models.TextChoices):
    PENDING = "PENDING", _("Pending")
    APPROVED = "APPROVED", _("Approved")
    REJECTED = "REJECTED", _("Rejected")
    SUSPENDED = "SUSPENDED", _("Suspended")


#: A commercial company is verified through a registry; an artisan workshop is
#: verified by a person. Crossing the two is the ModoVerificacionInvalido error
#: of the prototype contract.
VERIFICATION_TRACKS_BY_COMPANY_TYPE = {
    CompanyType.COMMERCIAL: [
        VerificationTrack.CHAMBER_OF_COMMERCE,
        VerificationTrack.OFFICIAL_REGISTRY,
    ],
    CompanyType.ARTISAN: [VerificationTrack.ARTISAN_REVIEW],
}

COMMERCIAL_TRACKS = VERIFICATION_TRACKS_BY_COMPANY_TYPE[CompanyType.COMMERCIAL]

#: The owner may edit only while the outcome is still open (FR10, FR11).
EDITABLE_STATUSES = (CompanyStatus.PENDING, CompanyStatus.REJECTED)

#: A decision that goes against the applicant has to say why (DBR12).
#: Kept as an ordered tuple: a set iterates in an order that changes between
#: processes, which would make the constraint below differ on every
#: makemigrations run and produce an endless trail of no-op migrations.
STATUSES_REQUIRING_REASON = (CompanyStatus.REJECTED, CompanyStatus.SUSPENDED)


class TransitionNotAllowed(ValueError):
    """A status change asked for from a status it cannot be made from.

    A ValueError, so that callers written before this existed keep working: the
    reason-is-missing refusal is a ValueError too, and both mean the same thing
    to a caller, which is that the change was not made.
    """


class CompanyManager(models.Manager):
    def owned_by(self, user):
        """The company this account owns, or None if it has not applied.

        An account owns at most one company, so this answers with the record
        rather than a queryset. Written once here because three views ask it.
        """
        return self.filter(owner=user).first()


class Company(models.Model):
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="company",
    )
    legal_name = models.CharField(max_length=200)
    company_type = models.CharField(max_length=16, choices=CompanyType.choices)
    verification_track = models.CharField(max_length=32, choices=VerificationTrack.choices)
    status = models.CharField(
        max_length=16, choices=CompanyStatus.choices, default=CompanyStatus.PENDING
    )
    description = models.TextField()
    location = models.CharField(max_length=200)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to="company-logos/", blank=True)
    registry_code = models.CharField(
        max_length=64,
        blank=True,
        help_text=_("Official registry code. Required for a commercial company (FR08)."),
    )
    status_reason = models.TextField(
        blank=True,
        help_text=_("Why the application was rejected or the company suspended (DBR12)."),
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    status_changed_at = models.DateTimeField(default=timezone.now)

    objects = CompanyManager()

    class Meta:
        ordering = ["-submitted_at"]
        verbose_name_plural = "companies"
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(
                        company_type=CompanyType.COMMERCIAL,
                        verification_track__in=COMMERCIAL_TRACKS,
                    )
                    | Q(
                        company_type=CompanyType.ARTISAN,
                        verification_track=VerificationTrack.ARTISAN_REVIEW,
                    )
                ),
                name="company_track_matches_type",
            ),
            models.CheckConstraint(
                condition=(
                    (Q(company_type=CompanyType.COMMERCIAL) & ~Q(registry_code=""))
                    | Q(company_type=CompanyType.ARTISAN, registry_code="")
                ),
                name="commercial_company_has_registry_code",
            ),
            models.CheckConstraint(
                condition=(~Q(status__in=STATUSES_REQUIRING_REASON) | ~Q(status_reason="")),
                name="negative_decision_states_a_reason",
            ),
        ]

    def __str__(self):
        return self.legal_name

    # ---- queries the templates and views ask ----

    @property
    def is_editable(self):
        """False once a decision has been taken that the owner cannot undo."""
        return self.status in EDITABLE_STATUSES

    @property
    def requires_manual_review(self):
        """An artisan application is reviewed by a person, not by a registry (FR09)."""
        return self.verification_track == VerificationTrack.ARTISAN_REVIEW

    @property
    def can_register_products(self):
        return self.status == CompanyStatus.APPROVED

    def edit_refusal_reason(self):
        """Why an edit is being refused, worded for the owner (FR11)."""
        if self.is_editable:
            return None
        return _(
            "This application cannot be edited because it is %(status)s. "
            "Contact the administrator if the details need to change."
        ) % {"status": self.get_status_display().lower()}

    # ---- transitions ----

    #: Each transition names the statuses it may be made from, so that a
    #: decision already taken is not taken a second time and a company is not
    #: suspended before it has been approved. Checked here rather than in the
    #: view, because the view is not the only caller.
    APPROVE_FROM = (CompanyStatus.PENDING,)
    REJECT_FROM = (CompanyStatus.PENDING,)
    SUSPEND_FROM = (CompanyStatus.APPROVED,)
    REACTIVATE_FROM = (CompanyStatus.SUSPENDED,)

    @property
    def can_be_approved(self):
        return self.status in self.APPROVE_FROM

    @property
    def can_be_rejected(self):
        return self.status in self.REJECT_FROM

    @property
    def can_be_suspended(self):
        return self.status in self.SUSPEND_FROM

    @property
    def can_be_reactivated(self):
        return self.status in self.REACTIVATE_FROM

    def _set_status(self, status, *, allowed_from, reason=""):
        if self.status not in allowed_from:
            raise TransitionNotAllowed(
                _("%(company)s is %(current)s, so it cannot become %(wanted)s.")
                % {
                    "company": self.legal_name,
                    "current": self.get_status_display().lower(),
                    "wanted": CompanyStatus(status).label.lower(),
                }
            )
        if status in STATUSES_REQUIRING_REASON and not reason.strip():
            raise ValueError(f"A reason is required to set the status to {status}.")
        self.status = status
        self.status_reason = reason.strip()
        self.status_changed_at = timezone.now()
        self.save(update_fields=["status", "status_reason", "status_changed_at"])

    def approve(self, actor):
        """FR13: a pending application becomes approved."""
        self._set_status(CompanyStatus.APPROVED, allowed_from=self.APPROVE_FROM)
        AuditEntry.record(actor=actor, action=Action.COMPANY_APPROVED, target=self)

    def reject(self, actor, reason):
        """FR14: a pending application is refused, with the reason recorded."""
        self._set_status(CompanyStatus.REJECTED, allowed_from=self.REJECT_FROM, reason=reason)
        AuditEntry.record(
            actor=actor, action=Action.COMPANY_REJECTED, target=self, reason=self.status_reason
        )

    def suspend(self, actor, reason):
        """An approved company stops issuing passports; the ones it issued keep working."""
        self._set_status(CompanyStatus.SUSPENDED, allowed_from=self.SUSPEND_FROM, reason=reason)
        AuditEntry.record(
            actor=actor, action=Action.COMPANY_SUSPENDED, target=self, reason=self.status_reason
        )

    def reactivate(self, actor):
        """A suspension is lifted and the company is approved again."""
        self._set_status(CompanyStatus.APPROVED, allowed_from=self.REACTIVATE_FROM)
        AuditEntry.record(actor=actor, action=Action.COMPANY_REACTIVATED, target=self)

    def resubmit(self, actor):
        """An edited application goes back into the queue (FR10)."""
        self._set_status(CompanyStatus.PENDING, allowed_from=EDITABLE_STATUSES)
        AuditEntry.record(actor=actor, action=Action.COMPANY_RESUBMITTED, target=self)
