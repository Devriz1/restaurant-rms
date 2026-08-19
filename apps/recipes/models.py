from decimal import Decimal

from django.db import models

from apps.menu.models import MenuItem
from apps.inventory.models import Material


# ==========================================================
# RECIPE
# ==========================================================

class Recipe(models.Model):

    menu_item = models.OneToOneField(
        MenuItem,
        on_delete=models.CASCADE,
        related_name="recipe",
    )

    instructions = models.TextField(
        blank=True,
    )

    preparation_notes = models.TextField(
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

        ordering = [
            "menu_item__name",
        ]

        verbose_name = "Recipe"
        verbose_name_plural = "Recipes"

    def __str__(self):

        return f"Recipe - {self.menu_item.name}"

    @property
    def total_cost(self):

        return sum(
            (
                ingredient.total_cost
                for ingredient in self.ingredients.all()
            ),
            Decimal("0.00"),
        )

    @property
    def selling_price(self):

        return self.menu_item.price

    @property
    def gross_profit(self):

        return (
            self.selling_price
            - self.total_cost
        )

    @property
    def food_cost_percentage(self):

        if self.selling_price <= 0:
            return Decimal("0.00")

        return (
            self.total_cost
            / self.selling_price
        ) * Decimal("100")


# ==========================================================
# RECIPE INGREDIENT
# ==========================================================

class RecipeIngredient(models.Model):

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="ingredients",
    )

    material = models.ForeignKey(
        Material,
        on_delete=models.PROTECT,
        related_name="recipe_ingredients",
    )

    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=0,
    )

    wastage_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )

    remarks = models.CharField(
        max_length=255,
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
            "id",
        ]

        verbose_name = "Recipe Ingredient"
        verbose_name_plural = "Recipe Ingredients"

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "recipe",
                    "material",
                ],
                name="unique_recipe_material",
            ),

        ]

    def __str__(self):

        return (
            f"{self.recipe.menu_item.name} - "
            f"{self.material.name}"
        )

    @property
    def effective_quantity(self):

        wastage = (
            self.quantity
            * self.wastage_percentage
            / Decimal("100")
        )

        return self.quantity + wastage

    @property
    def total_cost(self):

        return (
            self.effective_quantity
            * self.material.cost_price
        )