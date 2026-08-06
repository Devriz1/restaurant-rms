from django.contrib import admin

from .models import Unit, Supplier, Category, Material


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):

    list_display = (
        "code",
        "name",
        "symbol",
        "unit_type",
        "decimal_allowed",
        "is_active",
        "created_at",
    )

    list_filter = (
        "unit_type",
        "decimal_allowed",
        "is_active",
    )

    search_fields = (
        "code",
        "name",
        "symbol",
    )

    readonly_fields = (
        "code",
        "created_at",
        "updated_at",
    )

    ordering = (
        "name",
    )

    fieldsets = (

        (
            "Unit Details",
            {
                "fields": (
                    "code",
                    "name",
                    "symbol",
                    "unit_type",
                )
            },
        ),

        (
            "Settings",
            {
                "fields": (
                    "decimal_allowed",
                    "is_active",
                )
            },
        ),

        (
            "System Information",
            {
                "classes": (
                    "collapse",
                ),
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),

    )

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):

    list_display = (

        "code",

        "name",

        "contact_person",

        "phone",

        "city",

        "is_active",

    )

    search_fields = (

        "code",

        "name",

        "contact_person",

        "phone",

        "gst_number",

    )

    list_filter = (

        "city",

        "state",

        "is_active",

    )

    ordering = (

        "name",

    )

    readonly_fields = (

        "code",

        "created_at",

        "updated_at",

    )

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (

        "code",

        "name",

        "is_active",

        "created_at",

    )

    search_fields = (

        "code",

        "name",

    )

    list_filter = (

        "is_active",

    )

    ordering = (

        "name",

    )


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):

    list_display = (

        "code",

        "name",

        "category",

        "unit",

        "supplier",

        "current_stock",

        "cost_price",

        "is_active",

    )

    search_fields = (

        "code",

        "name",

    )

    list_filter = (

        "category",

        "supplier",

        "is_active",

    )

    ordering = (

        "name",

    )


# ==========================================================
# PURCHASE ITEM INLINE
# ==========================================================

