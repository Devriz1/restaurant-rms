from decimal import Decimal
from datetime import date

from django.db import models

from apps.inventory.models import Supplier, Material


# ==========================================================
# PURCHASE
# ==========================================================

class Purchase(models.Model):

    PAYMENT_MODE_CHOICES = (

        ("CASH", "Cash"),

        ("UPI", "UPI"),

        ("CARD", "Card"),

        ("BANK", "Bank Transfer"),

        ("CREDIT", "Credit"),

    )

    purchase_number = models.CharField(

        max_length=20,

        unique=True,

        editable=False,

    )

    supplier = models.ForeignKey(

        Supplier,

        on_delete=models.PROTECT,

        related_name="purchase_headers",

    )

    invoice_number = models.CharField(

        max_length=100,

        blank=True,

    )

    purchase_date = models.DateField(

        default=date.today,

    )

    payment_mode = models.CharField(

        max_length=20,

        choices=PAYMENT_MODE_CHOICES,

        default="CASH",

    )

    subtotal = models.DecimalField(

        max_digits=12,

        decimal_places=2,

        default=0,

    )

    gst_total = models.DecimalField(

        max_digits=12,

        decimal_places=2,

        default=0,

    )

    discount = models.DecimalField(

        max_digits=12,

        decimal_places=2,

        default=0,

    )

    other_charges = models.DecimalField(

        max_digits=12,

        decimal_places=2,

        default=0,

    )

    grand_total = models.DecimalField(

        max_digits=12,

        decimal_places=2,

        default=0,

    )

    remarks = models.TextField(

        blank=True,

    )

    created_at = models.DateTimeField(

        auto_now_add=True,

    )

    updated_at = models.DateTimeField(

        auto_now=True,

    )

    class Meta:

        ordering = [

            "-purchase_date",

            "-id",

        ]

        verbose_name = "Purchase"

        verbose_name_plural = "Purchases"

    def save(self, *args, **kwargs):

        if not self.purchase_number:

            last = Purchase.objects.order_by("-id").first()

            if last:

                number = int(

                    last.purchase_number.replace("PUR", "")

                ) + 1

            else:

                number = 1

            self.purchase_number = f"PUR{number:05d}"

        super().save(*args, **kwargs)
        # ==========================================================
    # RECALCULATE PURCHASE TOTALS
    # ==========================================================

    def calculate_totals(self):

        subtotal = Decimal("0.00")

        gst_total = Decimal("0.00")

        for item in self.items.all():

            basic = item.quantity * item.unit_price

            subtotal += basic

            gst_total += item.gst_amount

        self.subtotal = subtotal

        self.gst_total = gst_total

        self.grand_total = (
            subtotal
            + gst_total
            + self.other_charges
            - self.discount
        )

        Purchase.objects.filter(pk=self.pk).update(

            subtotal=self.subtotal,

            gst_total=self.gst_total,

            grand_total=self.grand_total,

        )
    def __str__(self):

        return self.purchase_number

# ==========================================================
# PURCHASE ITEM
# ==========================================================

class PurchaseItem(models.Model):

    purchase = models.ForeignKey(

        Purchase,

        on_delete=models.CASCADE,

        related_name="items",

    )

    material = models.ForeignKey(

        Material,

        on_delete=models.PROTECT,

        related_name="purchase_items",

    )

    quantity = models.DecimalField(

        max_digits=10,

        decimal_places=2,

        default=0,

    )

    unit_price = models.DecimalField(

        max_digits=12,

        decimal_places=2,

        default=0,

    )

    gst_percentage = models.DecimalField(

        max_digits=5,

        decimal_places=2,

        default=0,

    )

    gst_amount = models.DecimalField(

        max_digits=12,

        decimal_places=2,

        default=0,

    )

    line_total = models.DecimalField(

        max_digits=12,

        decimal_places=2,

        default=0,

    )

    class Meta:

        ordering = [

            "id",

        ]

        verbose_name = "Purchase Item"

        verbose_name_plural = "Purchase Items"

    def save(self, *args, **kwargs):

        basic_amount = self.quantity * self.unit_price

        self.gst_amount = (
            basic_amount * self.gst_percentage
    ) / Decimal("100")

        self.line_total = basic_amount + self.gst_amount

        super().save(*args, **kwargs)

        self.purchase.calculate_totals()
        
    def delete(self, *args, **kwargs):

            purchase = self.purchase

            super().delete(*args, **kwargs)

            purchase.calculate_totals()
    def __str__(self):

        return f"{self.purchase.purchase_number} - {self.material.name}"