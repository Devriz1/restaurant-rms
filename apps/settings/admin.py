from django.contrib import admin
from .models import PrinterSetting


@admin.register(PrinterSetting)
class PrinterSettingAdmin(admin.ModelAdmin):

    list_display = (
        "billing_printer",
        "kitchen_printer",
        "report_printer",
        "updated_at",
    )