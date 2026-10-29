from django.db import models
from django.conf import settings


class AuditLog(models.Model):

    ACTION_CHOICES = [
        ("login", "User Login"),
        ("logout", "User Logout"),
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Delete"),
        ("view", "View"),
        ("print", "Print (KOT/Receipt)"),
        ("payment", "Payment"),
        ("status_change", "Status Change"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )

    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
    )

    model = models.CharField(
        max_length=100,
        help_text="The model that was affected (e.g., 'Bill', 'GuestOrder', 'OrderItem').",
    )

    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="The ID of the affected record.",
    )

    object_repr = models.CharField(
        max_length=255,
        blank=True,
        help_text="A string representation of the affected record.",
    )

    message = models.TextField(
        blank=True,
        help_text="Additional details about the action.",
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
    )

    user_agent = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["action", "model"]),
        ]

    def __str__(self):
        return f"{self.action} on {self.model} #{self.object_id} by {self.user}"