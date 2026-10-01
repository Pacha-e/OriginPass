"""The account behind every authenticated action.

A buyer verifying a product is not a User: verification is anonymous by design.
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Role(models.TextChoices):
    ADMIN = "ADMIN", _("Administrator")
    COMPANY = "COMPANY", _("Company")
    HOLDER = "HOLDER", _("Holder")


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("An email address is required.")
        extra_fields.setdefault("role", Role.HOLDER)
        user = self.model(email=self.normalize_email(email), **extra_fields)
        # set_password hashes with PBKDF2 and a salt unique to this record
        # (DBR11). The plain text is never assigned to a field.
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields["role"] = Role.ADMIN

        if extra_fields.get("is_staff") is not True:
            raise ValueError("A superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("A superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=16, choices=Role.choices, default=Role.HOLDER)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    password_reset_token = models.UUIDField(null=True, blank=True, unique=True, editable=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ["email"]

    def __str__(self):
        return self.email

    @property
    def is_platform_admin(self):
        """Mirrors the soloAdministrador modifier of the prototype contracts."""
        return self.role == Role.ADMIN or self.is_superuser


class LoginAttempt(models.Model):
    """One row per (IP, email) failure streak.

    FR57 caps at five failures in fifteen minutes and answers every further
    attempt with the same message a wrong password returns (FR04), so the lock
    never announces itself. The same message keeps it impossible to tell a
    blocked address from an unknown one.
    """
    MAX_FAILURES = 5
    WINDOW_MINUTES = 15
    LOCK_MINUTES = 15

    email = models.EmailField()
    ip_address = models.GenericIPAddressField()
    failed_count = models.PositiveIntegerField(default=0)
    first_failed_at = models.DateTimeField(default=timezone.now)
    locked_until = models.DateTimeField(null=True, blank=True)
    last_attempt = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("email", "ip_address")]
        indexes = [
            models.Index(fields=["email", "-last_attempt"], name="login_attempt_email_time"),
        ]

    def __str__(self):
        return f"{self.email} from {self.ip_address}: {self.failed_count} failures"

    def is_locked(self):
        """The streak is in its cool-off period."""
        return self.locked_until is not None and self.locked_until > timezone.now()

    def reset(self):
        """Successful login wipes the streak."""
        self.failed_count = 0
        self.first_failed_at = timezone.now()
        self.locked_until = None
        self.save(update_fields=["failed_count", "first_failed_at", "locked_until", "last_attempt"])

    def register_failure(self):
        """A failed attempt increments the streak and locks after the cap."""
        now = timezone.now()
        window_start = now - timezone.timedelta(minutes=self.WINDOW_MINUTES)
        if self.first_failed_at < window_start:
            # Streak expired; start over.
            self.failed_count = 1
            self.first_failed_at = now
        else:
            self.failed_count += 1
        if self.failed_count >= self.MAX_FAILURES:
            self.locked_until = now + timezone.timedelta(minutes=self.LOCK_MINUTES)
        self.save(update_fields=["failed_count", "first_failed_at", "locked_until", "last_attempt"])

    @classmethod
    def get_or_create_for_ip(cls, email, ip):
        return cls.objects.get_or_create(
            email=email, ip_address=ip,
            defaults={"first_failed_at": timezone.now()},
        )[0]
