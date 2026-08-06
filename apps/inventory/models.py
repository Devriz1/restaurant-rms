from django.db import models


class Unit(models.Model):

    class UnitType(models.TextChoices):
        WEIGHT = "WEIGHT", "Weight"
        VOLUME = "VOLUME", "Volume"
        COUNT = "COUNT", "Count"
        LENGTH = "LENGTH", "Length"
        PACKAGE = "PACKAGE", "Package"
        CUSTOM = "CUSTOM", "Custom"

    code = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
    )

    name = models.CharField(
        max_length=100,
        unique=True,
    )

    symbol = models.CharField(
        max_length=20,
        unique=True,
    )

    unit_type = models.CharField(
        max_length=20,
        choices=UnitType.choices,
        default=UnitType.COUNT,
    )

    decimal_allowed = models.BooleanField(
        default=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = ["name"]

        verbose_name = "Unit"

        verbose_name_plural = "Units"

    def save(self, *args, **kwargs):

        if not self.code:

            last = Unit.objects.order_by("-id").first()

            if last and last.code.startswith("UNT"):

                number = int(last.code[3:]) + 1

            else:

                number = 1

            self.code = f"UNT{number:04d}"

        super().save(*args, **kwargs)

    def __str__(self):

        return f"{self.name} ({self.symbol})"

class Supplier(models.Model):

    code = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
    )

    name = models.CharField(
        max_length=150,
        unique=True,
    )

    contact_person = models.CharField(
        max_length=100,
    )

    phone = models.CharField(
        max_length=20,
        unique=True,
    )

    email = models.EmailField(
        blank=True,
    )

    gst_number = models.CharField(
        max_length=30,
        blank=True,
    )

    address = models.TextField(
        blank=True,
    )

    city = models.CharField(
        max_length=100,
        blank=True,
    )

    state = models.CharField(
        max_length=100,
        blank=True,
    )

    pincode = models.CharField(
        max_length=20,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = ["name"]

        verbose_name = "Supplier"

        verbose_name_plural = "Suppliers"

    def save(self, *args, **kwargs):

        if not self.code:

            last = Supplier.objects.order_by("-id").first()

            if last:

                number = int(last.code.replace("SUP", "")) + 1

            else:

                number = 1

            self.code = f"SUP{number:04d}"

        super().save(*args, **kwargs)

    def __str__(self):

        return self.name

class Category(models.Model):

    code = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
    )

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

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = ["name"]

        verbose_name = "Category"

        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):

        if not self.code:

            last = Category.objects.order_by("-id").first()

            if last:

                number = int(last.code.replace("CAT", "")) + 1

            else:

                number = 1

            self.code = f"CAT{number:04d}"

        super().save(*args, **kwargs)

    def __str__(self):

        return self.name


class Material(models.Model):

    code = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
    )

    name = models.CharField(
        max_length=200,
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="materials",
    )

    unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        related_name="materials",
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name="materials",
    )

    opening_stock = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    current_stock = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    minimum_stock = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    maximum_stock = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    cost_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    last_purchase_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    storage_location = models.CharField(
        max_length=100,
        blank=True,
    )

    barcode = models.CharField(
        max_length=100,
        blank=True,
    )

    expiry_tracking = models.BooleanField(
        default=False,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = ["name"]

        verbose_name = "Material"

        verbose_name_plural = "Materials"

    def save(self, *args, **kwargs):

        if not self.code:

            last = Material.objects.order_by("-id").first()

            if last:

                number = int(last.code.replace("MAT", "")) + 1

            else:

                number = 1

            self.code = f"MAT{number:04d}"

        super().save(*args, **kwargs)

    def __str__(self):

        return self.name

