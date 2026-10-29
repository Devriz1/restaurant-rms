from django.contrib import admin
from .models import MenuCategory, MenuItem


@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "display_order",
        "kitchen_station",
        "is_active",
    )

    list_editable = (
        "display_order",
        "kitchen_station",
        "is_active",
    )

    search_fields = ("name",)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):

    list_display = (
        "item_code",
        "name",
        "category",
        "sub_category",
        "price",
        "special_price",
        "takeaway_price",
        "is_available",
    )

    list_filter = (
        "category",
        "sub_category",
        "is_available",
        "is_veg",
    )

    search_fields = (
        "item_code",
        "sub_category",
        "name",
        "description",
    )