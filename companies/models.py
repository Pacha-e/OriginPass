"""One record per company that has applied, whatever the outcome.

The rules below are the ones the hackathon prototype enforced on chain in
RegistroEmpresas.sol. Each is stated once, here, so that a view cannot bypass
it, and the ones the database can express are also written as constraints.
"""

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone

from audit.models import Action, AuditEntry


class CompanyType(models.TextChoices):
    COMMERCIAL = "COMMERCIAL", "Commercial company"
    ARTISAN = "ARTISAN", "Artisan workshop"


class VerificationTrack(models.TextChoices):
    CHAMBER_OF_COMMERCE = "CHAMBER_OF_COMMERCE", "Chamber of Commerce"
    OFFICIAL_REGISTRY = "OFFICIAL_REGISTRY", "Official registry"
    ARTISAN_REVIEW = "ARTISAN_REVIEW", "Manual artisan review"


class CompanyStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"
    SUSPENDED = "SUSPENDED", "Suspended"


#: A commercial company is verified through a registry; an artisan workshop is
#: verified by a person. Crossing the two is the ModoVerificacionInvalido error
#: of the prototype contract.
TRACKS_BY_TYPE = {
    CompanyType.COMMERCIAL: [
        VerificationTrack.CHAMBER_OF_COMMERCE,
        VerificationTrack.OFFICIAL_REGISTRY,
    ],
    CompanyType.ARTISAN: [VerificationTrack.ARTISAN_REVIEW],
}

#: The owner may edit only while the outcome is still open (FR10, FR11).
EDITABLE_STATUSES = (CompanyStatus.PENDING, CompanyStatus.REJECTED)

#: A decision that goes against the applicant has to say why (DBR12).
#: Kept as an ordered tuple: a set iterates in an order that changes between
#: processes, which would make the constraint below differ on every
#: makemigrations run and produce an endless trail of no-op migrations.
STATUSES_REQUIRING_REASON = (CompanyStatus.REJECTED, CompanyStatus.SUSPENDED)


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
        help_text="Official registry code. Required for a commercial company (FR08).",
    )
    status_reason = models.TextField(
        blank=True,
        help_text="Why the application was rejected or the company suspended (DBR12).",
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    status_changed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-submitted_at"]
        verbose_name_plural = "companies"
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(
                        company_type=CompanyType.COMMERCIAL,
                        verification_track__in=TRACKS_BY_TYPE[CompanyType.COMMERCIAL],
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
        return (
            f"This application cannot be edited because it is {self.get_status_display().lower()}. "
            "Contact the administrator if the details need to change."
        )

    # ---- transitions ----

    def _set_status(self, status, *, reason=""):
        if status in STATUSES_REQUIRING_REASON and not reason.strip():
            raise ValueError(f"A reason is required to set the status to {status}.")
        self.status = status
        self.status_reason = reason.strip()
        self.status_changed_at = timezone.now()
        self.save(update_fields=["status", "status_reason", "status_changed_at"])

    def approve(self, actor):
        self._set_status(CompanyStatus.APPROVED)
        AuditEntry.record(actor=actor, action=Action.COMPANY_APPROVED, target=self)

    def reject(self, actor, reason):
        self._set_status(CompanyStatus.REJECTED, reason=reason)
        AuditEntry.record(
            actor=actor, action=Action.COMPANY_REJECTED, target=self, reason=self.status_reason
        )

    def suspend(self, actor, reason):
        self._set_status(CompanyStatus.SUSPENDED, reason=reason)
        AuditEntry.record(
            actor=actor, action=Action.COMPANY_SUSPENDED, target=self, reason=self.status_reason
        )

    def reactivate(self, actor):
        self._set_status(CompanyStatus.APPROVED)
        AuditEntry.record(actor=actor, action=Action.COMPANY_REACTIVATED, target=self)

    def resubmit(self, actor):
        """An edited application goes back into the queue (FR10)."""
        self._set_status(CompanyStatus.PENDING)
        AuditEntry.record(actor=actor, action=Action.COMPANY_RESUBMITTED, target=self)
