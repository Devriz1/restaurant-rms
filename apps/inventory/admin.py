from django.contrib import admin

from .models import (
    Ingredient,
    InventoryCategory,
    Supplier,
    Unit,
)


@admin.register(InventoryCategory)
class InventoryCategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
    )

    ordering = (
        "name",
    )


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "short_name",
        "is_decimal",
        "is_active",
    )

    list_filter = (
        "is_decimal",
        "is_active",
    )

    search_fields = (
        "name",
        "short_name",
    )

    ordering = (
        "name",
    )


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "contact_person",
        "phone",
        "is_active",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "phone",
        "email",
    )

    ordering = (
        "name",
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):

    list_display = (
        "code",
        "name",
        "category",
        "unit",
        "current_stock",
        "minimum_stock",
        "cost_price",
        "stock_status",
        "is_active",
    )

    list_filter = (
        "category",
        "unit",
        "is_active",
    )

    search_fields = (
        "code",
        "name",
    )

    ordering = (
        "name",
    )