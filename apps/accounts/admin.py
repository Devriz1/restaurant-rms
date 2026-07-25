from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    User,
    Permission,
    UserPermission,
)


# ==========================================================
# USER
# ==========================================================

@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = (
        "username",
        "first_name",
        "last_name",
        "role",
        "phone_number",
        "is_active",
        "is_staff",
    )

    list_filter = (
        "role",
        "is_active",
        "is_staff",
    )

    search_fields = (
        "username",
        "first_name",
        "last_name",
        "phone_number",
    )

    ordering = (
        "username",
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            "Restaurant RMS",
            {
                "fields": (
                    "role",
                    "phone_number",
                )
            },
        ),
    )


# ==========================================================
# PERMISSION
# ==========================================================

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "code",
        "category",
    )

    search_fields = (
        "name",
        "code",
    )

    list_filter = (
        "category",
    )


# ==========================================================
# USER PERMISSION
# ==========================================================

@admin.register(UserPermission)
class UserPermissionAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "permission",
    )

    list_filter = (
        "permission__category",
    )

    search_fields = (
        "user__username",
        "permission__name",
    )