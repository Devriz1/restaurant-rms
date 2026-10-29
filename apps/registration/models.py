from django.conf import settings
from django.db import models
from django.utils import timezone


class LicenseKey(models.Model):
    """Software registration / license key.

    A key can either unlock the software fully (one-time purchase) or be
    set as a recurring subscription that expires on a given date.
    """

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        REVOKED = "revoked", "Revoked"

    class Plan(models.TextChoices):
        LIFETIME = "lifetime", "Lifetime"
        MONTHLY = "monthly", "Monthly"
        YEARLY = "yearly", "Yearly"

    key = models.CharField(
        max_length=128,
        unique=True,
        db_index=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    plan = models.CharField(
        max_length=20,
        choices=Plan.choices,
        default=Plan.LIFETIME,
    )

    max_users = models.PositiveIntegerField(
        default=1,
        help_text="Maximum number of user accounts allowed.",
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Leave blank for lifetime keys.",
    )

    note = models.TextField(
        blank=True,
        default="",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "License Key"
        verbose_name_plural = "License Keys"

    def __str__(self):
        return f"{self.key} ({self.status})"

    @property
    def is_valid(self):
        if self.status != self.Status.ACTIVE:
            return False
        if self.plan != self.Plan.LIFETIME and self.expires_at:
            if timezone.now() > self.expires_at:
                return False
        return True

    @property
    def is_expired(self):
        if self.plan == self.Plan.LIFETIME or not self.expires_at:
            return False
        return timezone.now() > self.expires_at

    @property
    def time_remaining(self):
        """Human-readable time remaining until expiry."""
        if self.plan == self.Plan.LIFETIME or not self.expires_at:
            return "Lifetime"
        if self.is_expired:
            return "Expired"
        delta = self.expires_at - timezone.now()
        days = delta.days
        seconds = delta.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if days > 0:
            return f"{days} days, {hours} hours left"
        if hours > 0:
            return f"{hours} hours, {minutes} minutes left"
        return f"{minutes} minutes left"

    @classmethod
    def get_active_key(cls):
        """Return the first currently-valid license key, if any."""
        now = timezone.now()
        return (
            cls.objects.filter(status=cls.Status.ACTIVE)
            .filter(
                models.Q(plan=cls.Plan.LIFETIME)
                | models.Q(expires_at__gt=now)
            )
            .order_by("-created_at")
            .first()
        )

    @classmethod
    def is_unlocked(cls):
        """True when at least one valid license key exists."""
        return cls.get_active_key() is not None


class Registration(models.Model):
    """Tracks which license key is currently applied to this installation."""

    license_key = models.ForeignKey(
        LicenseKey,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="registrations",
    )

    registered_at = models.DateTimeField(auto_now_add=True)

    last_checked_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-registered_at"]
        verbose_name = "Registration"
        verbose_name_plural = "Registrations"

    def __str__(self):
        return f"{self.license_key} ({self.registered_at:%Y-%m-%d})"

    def save(self, *args, **kwargs):
        # Only one active registration at a time
        if self.is_active:
            Registration.objects.filter(is_active=True).exclude(
                pk=self.pk
            ).update(is_active=False)
        super().save(*args, **kwargs)

    @classmethod
    def get_active(cls):
        return cls.objects.filter(is_active=True).first()

    @classmethod
    def is_registered(cls):
        reg = cls.get_active()
        return reg is not None and reg.license_key is not None and reg.license_key.is_valid