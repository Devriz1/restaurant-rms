from django.db import models


class MenuCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    display_order = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "name"]
        verbose_name = "Menu Category"
        verbose_name_plural = "Menu Categories"

    def __str__(self):
        return self.name


class MenuItem(models.Model):

    category = models.ForeignKey(
        MenuCategory,
        on_delete=models.CASCADE,
        related_name="items"
    )

    name = models.CharField(max_length=150)

    description = models.TextField(blank=True)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    preparation_time = models.PositiveSmallIntegerField(
        default=10,
        help_text="Preparation time in minutes"
    )

    is_veg = models.BooleanField(default=False)

    is_available = models.BooleanField(default=True)

    image = models.ImageField(
        upload_to="menu/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category", "name"]

    def __str__(self):
        return self.name