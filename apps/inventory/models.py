from decimal import Decimal

from django.db import models


class InventoryCategory(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True,
    )

    description = models.TextField(
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        ordering = ["name"]

        verbose_name_plural = "Inventory Categories"

    def __str__(self):

        return self.name


class Unit(models.Model):

    name = models.CharField(
        max_length=50,
        unique=True,
    )

    short_name = models.CharField(
        max_length=10,
        unique=True,
    )

    is_decimal = models.BooleanField(
        default=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:

        ordering = ["name"]

    def __str__(self):

        return self.short_name


class Supplier(models.Model):

    name = models.CharField(
        max_length=200,
    )

    contact_person = models.CharField(
        max_length=100,
        blank=True,
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
    )

    email = models.EmailField(
        blank=True,
    )

    address = models.TextField(
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        ordering = ["name"]

    def __str__(self):

        return self.name


class Ingredient(models.Model):

    code = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
    )

    name = models.CharField(
        max_length=200,
    )

    category = models.ForeignKey(
        InventoryCategory,
        on_delete=models.PROTECT,
        related_name="ingredients",
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ingredients",
    )

    unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
    )

    opening_stock = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    current_stock = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    minimum_stock = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        ordering = ["name"]

    def save(self, *args, **kwargs):

        if not self.code:

            last = Ingredient.objects.order_by("-id").first()

            if last and last.code:

                try:

                    number = int(
                        last.code.replace(
                            "ING",
                            "",
                        )
                    ) + 1

                except ValueError:

                    number = 1

            else:

                number = 1

            while Ingredient.objects.filter(
                code=f"ING{number:05d}"
            ).exists():

                number += 1

            self.code = f"ING{number:05d}"

        if self._state.adding:

            self.current_stock = self.opening_stock

        super().save(*args, **kwargs)

    @property
    def stock_status(self):

        if self.current_stock <= 0:

            return "Out of Stock"

        if self.current_stock <= self.minimum_stock:

            return "Low Stock"

        return "In Stock"

    def __str__(self):

        return self.name