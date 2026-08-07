from django.db import models

from apps.inventory.models import Material


class StockLedger(models.Model):

    class MovementType(models.TextChoices):

        OPENING = "OPENING", "Opening Stock"

        PURCHASE = "PURCHASE", "Purchase"

        SALE = "SALE", "Sale"

        ADJUSTMENT = "ADJUSTMENT", "Adjustment"

        WASTE = "WASTE", "Waste"

        RETURN = "RETURN", "Purchase Return"

    material = models.ForeignKey(
        Material,
        on_delete=models.PROTECT,
        related_name="stock_ledger",
    )

    movement_type = models.CharField(
        max_length=20,
        choices=MovementType.choices,
    )

    reference_number = models.CharField(
        max_length=100,
        blank=True,
    )

    quantity_in = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    quantity_out = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    remarks = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        ordering = [
            "-created_at",
            "-id",
        ]

        verbose_name = "Stock Ledger"

        verbose_name_plural = "Stock Ledger"

    def __str__(self):

        return (
            f"{self.material.name} - "
            f"{self.movement_type}"
        )