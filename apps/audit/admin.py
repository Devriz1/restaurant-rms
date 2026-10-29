from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "user",
        "action",
        "model",
        "object_id",
        "object_repr",
    )
    list_filter = (
        "action",
        "model",
        "created_at",
        "user",
    )
    search_fields = (
        "message",
        "object_repr",
        "user__username",
    )
    date_hierarchy = "created_at"
    readonly_fields = (
        "user",
        "action",
        "model",
        "object_id",
        "object_repr",
        "message",
        "ip_address",
        "user_agent",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False