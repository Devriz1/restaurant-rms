from django.contrib import admin
from .models import Restaurant


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "phone",
        "currency",
    )

    def has_add_permission(self, request):
        if Restaurant.objects.exists():
            return False
        return super().has_add_permission(request)