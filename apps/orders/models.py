from decimal import Decimal

from django.conf import settings
from django.db import models

from apps.menu.models import MenuItem
from apps.tables.models import RestaurantTable


class TableSession(models.Model):

    STATUS_CHOICES = [
        ("open", "Open"),
        ("closed", "Closed"),
    ]

    session_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
    )

    table = models.ForeignKey(
        RestaurantTable,
        on_delete=models.PROTECT,
        related_name="sessions",
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="open",
    )

    notes = models.TextField(
        blank=True,
    )

    opened_at = models.DateTimeField(
        auto_now_add=True,
    )

    closed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-opened_at"]

    def save(self, *args, **kwargs):

        if not self.session_number:

            last = TableSession.objects.order_by("-id").first()

            if last and last.session_number:

                try:
                    number = int(
                        last.session_number.replace("SES", "")
                    ) + 1

                except ValueError:

                    number = 1

            else:

                number = 1

            while TableSession.objects.filter(
                session_number=f"SES{number:06d}"
            ).exists():

                number += 1

            self.session_number = f"SES{number:06d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.session_number} - {self.table}"


class GuestOrder(models.Model):

    STATUS_CHOICES = [
        ("open", "Open"),
        ("preparing", "Preparing"),
        ("ready", "Ready"),
        ("served", "Served"),
        ("paid", "Paid"),
        ("cancelled", "Cancelled"),
    ]

    order_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
    )

    session = models.ForeignKey(
        TableSession,
        on_delete=models.CASCADE,
        related_name="guest_orders",
    )

    guest_number = models.PositiveSmallIntegerField()

    guest_name = models.CharField(
        max_length=100,
        blank=True,
    )

    guest_count = models.PositiveSmallIntegerField(
        default=1,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="open",
    )

    notes = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["guest_number"]

    def save(self, *args, **kwargs):

        if not self.order_number:

            last = GuestOrder.objects.order_by("-id").first()

            if last and last.order_number:

                try:
                    number = int(
                        last.order_number.replace("ORD", "")
                    ) + 1

                except ValueError:

                    number = 1

            else:

                number = 1

            while GuestOrder.objects.filter(
                order_number=f"ORD{number:06d}"
            ).exists():

                number += 1

            self.order_number = f"ORD{number:06d}"

        super().save(*args, **kwargs)

    @property
    def subtotal(self):

        total = Decimal("0.00")

        for item in self.items.all():
            total += item.line_total

        return total

    @property
    def unsent_items(self):
        return self.items.filter(
            kot__isnull=True,
        )

    def __str__(self):
        return self.order_number
    
class KitchenOrderTicket(models.Model):

    STATUS_CHOICES = [
        ("created", "Created"),
        ("printed", "Printed"),
        ("preparing", "Preparing"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    ticket_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
    )

    guest_order = models.ForeignKey(
        GuestOrder,
        on_delete=models.CASCADE,
        related_name="kots",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_kots",
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="created",
    )

    printed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):

        if not self.ticket_number:

            last = KitchenOrderTicket.objects.order_by("-id").first()

            if last and last.ticket_number:

                try:
                    number = int(
                        last.ticket_number.replace("KOT", "")
                    ) + 1

                except ValueError:

                    number = 1

            else:

                number = 1

            while KitchenOrderTicket.objects.filter(
                ticket_number=f"KOT{number:06d}"
            ).exists():

                number += 1

            self.ticket_number = f"KOT{number:06d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.ticket_number


class OrderItem(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("preparing", "Preparing"),
        ("ready", "Ready"),
        ("served", "Served"),
        ("cancelled", "Cancelled"),
    ]

    order = models.ForeignKey(
        GuestOrder,
        on_delete=models.CASCADE,
        related_name="items",
    )

    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.PROTECT,
    )

    kot = models.ForeignKey(
        KitchenOrderTicket,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="items",
    )

    quantity = models.PositiveIntegerField(
        default=1,
    )

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    line_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    notes = models.CharField(
        max_length=255,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["created_at"]

    def save(self, *args, **kwargs):

        self.line_total = self.quantity * self.unit_price

        super().save(*args, **kwargs)

    @property
    def total_price(self):
        return self.line_total

    def __str__(self):
        return f"{self.menu_item} x {self.quantity}"