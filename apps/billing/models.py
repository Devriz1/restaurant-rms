from decimal import Decimal

from django.conf import settings
from django.db import models

from apps.orders.models import GuestOrder, TableSession


class Bill(models.Model):

    STATUS_CHOICES = [
        ("unpaid", "Unpaid"),
        ("paid", "Paid"),
        ("cancelled", "Cancelled"),
    ]

    DISCOUNT_TYPE_CHOICES = [
        ("amount", "Amount"),
        ("percent", "Percentage"),
    ]

    bill_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
    )

    guest_order = models.OneToOneField(
        GuestOrder,
        on_delete=models.PROTECT,
        related_name="bill",
    )

    session = models.ForeignKey(
        TableSession,
        on_delete=models.PROTECT,
        related_name="bills",
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    discount_type = models.CharField(
        max_length=10,
        choices=DISCOUNT_TYPE_CHOICES,
        default="amount",
    )

    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    service_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    tax = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    grand_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="unpaid",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_bills",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-id"]

    def calculate_totals(self):

        subtotal = Decimal("0.00")

        for item in self.items.all():
            subtotal += item.line_total

        self.subtotal = subtotal

        if self.discount_type == "percent":

            discount_amount = (
                subtotal * self.discount
            ) / Decimal("100")

        else:

            discount_amount = self.discount

        if discount_amount > subtotal:
            discount_amount = subtotal

        self.grand_total = (
            subtotal
            - discount_amount
            + self.service_charge
            + self.tax
        )

        if self.grand_total < Decimal("0.00"):
            self.grand_total = Decimal("0.00")

    def save(self, *args, **kwargs):

        if not self.bill_number:

            last = Bill.objects.order_by("-id").first()

            if last and last.bill_number:

                try:
                    number = int(
                        last.bill_number.replace("BILL", "")
                    ) + 1

                except ValueError:

                    number = 1

            else:

                number = 1

            while Bill.objects.filter(
                bill_number=f"BILL{number:06d}"
            ).exists():

                number += 1

            self.bill_number = f"BILL{number:06d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.bill_number


class BillItem(models.Model):

    bill = models.ForeignKey(
        Bill,
        on_delete=models.CASCADE,
        related_name="items",
    )

    menu_item_name = models.CharField(
        max_length=150,
    )

    quantity = models.PositiveIntegerField()

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    line_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    notes = models.CharField(
        max_length=255,
        blank=True,
    )

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.menu_item_name


class Payment(models.Model):

    METHOD_CHOICES = [
        ("cash", "Cash"),
        ("upi", "UPI"),
        ("card", "Card"),
    ]

    bill = models.ForeignKey(
        Bill,
        on_delete=models.CASCADE,
        related_name="payments",
    )

    payment_method = models.CharField(
        max_length=20,
        choices=METHOD_CHOICES,
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    reference_number = models.CharField(
        max_length=100,
        blank=True,
    )

    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )

    paid_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-paid_at"]

    def __str__(self):
        return f"{self.bill.bill_number} - {self.payment_method}"