from django.db import models
from django.db.models import Max
class MenuCategory(models.Model):

    name = models.CharField(max_length=100, unique=True)

    description = models.TextField(blank=True)

    display_order = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    kitchen_station = models.CharField(
        max_length=100,
        blank=True,
        help_text="Cooking station for kitchen display (e.g. Hot Kitchen, Cold Station, Desserts).",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "name"]
        verbose_name = "Menu Category"
        verbose_name_plural = "Menu Categories"

    def __str__(self):
        return self.name


class MenuItem(models.Model):

    PRICE_NORMAL = "normal"
    PRICE_SPECIAL = "special"
    PRICE_TAKEAWAY = "takeaway"

    PRICE_CHOICES = (
        (PRICE_NORMAL, "Normal Price"),
        (PRICE_SPECIAL, "Special Price"),
        (PRICE_TAKEAWAY, "Takeaway Price"),
    )

    category = models.ForeignKey(
        MenuCategory,
        on_delete=models.CASCADE,
        related_name="items"
    )

    item_code = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
    )

    sub_category = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    name = models.CharField(max_length=150)

    description = models.TextField(blank=True)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Normal Price",
    )

    special_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Special Price",
        help_text="Offer/limited time price. Leave blank to use the normal price.",
    )

    takeaway_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Takeaway Price",
        help_text="Price when the item is packed. Leave blank to use the normal price.",
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
        verbose_name = "Menu Item"
        verbose_name_plural = "Menu Items"

    def __str__(self):
        return self.name

    def get_price(self, price_type=PRICE_NORMAL):
        """Return the price for a given type, falling back to the normal price."""
        value = {
            self.PRICE_SPECIAL: self.special_price,
            self.PRICE_TAKEAWAY: self.takeaway_price,
        }.get(price_type, self.price)

        if value is None:
            return self.price
        return value

    def price_map(self):
        return {
            self.PRICE_NORMAL: self.price,
            self.PRICE_SPECIAL: self.get_price(self.PRICE_SPECIAL),
            self.PRICE_TAKEAWAY: self.get_price(self.PRICE_TAKEAWAY),
        }

    @property
    def has_special_price(self):
        return self.special_price is not None

    @property
    def has_takeaway_price(self):
        return self.takeaway_price is not None

    def save(self, *args, **kwargs):
        if not self.item_code:
            last = MenuItem.objects.aggregate(max_code=Max("item_code"))
            max_num = 0
            if last["max_code"]:
                for code in MenuItem.objects.values_list("item_code", flat=True):
                    if code and code.startswith("I") and code[1:].isdigit():
                        max_num = max(max_num, int(code[1:]))
            self.item_code = f"I{max_num + 1:04d}"
        super().save(*args, **kwargs)