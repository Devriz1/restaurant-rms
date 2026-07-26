from django.contrib import admin
from .models import DiningArea, RestaurantTable


@admin.register(DiningArea)
class DiningAreaAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "display_order",
        "is_active",
    )


@admin.register(RestaurantTable)
class RestaurantTableAdmin(admin.ModelAdmin):
    list_display = (
        "table_number",
        "display_name",
        "area",
        "capacity",
        "status",
        "is_active",
    )

    list_filter = (
        "area",
        "status",
        "is_active",
    )

    search_fields = (
        "table_number",
        "display_name",
    )