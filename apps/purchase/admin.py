from django.contrib import admin

from .models import PurchaseItem,Purchase
class PurchaseItemInline(admin.TabularInline):

    model = PurchaseItem

    extra = 1

    fields = (

        "material",

        "quantity",

        "unit_price",

        "gst_percentage",

        "line_total",

    )

    readonly_fields = (

        "line_total",

    )
# ==========================================================
# PURCHASE ADMIN
# ==========================================================

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):

    list_display = (

        "purchase_number",

        "supplier",

        "invoice_number",

        "purchase_date",

        "payment_mode",

        "grand_total",

    )

    search_fields = (

        "purchase_number",

        "invoice_number",

        "supplier__name",

    )

    list_filter = (

        "payment_mode",

        "purchase_date",

        "supplier",

    )

    ordering = (

        "-purchase_date",

        "-id",

    )

    readonly_fields = (

        "purchase_number",

        "created_at",

        "updated_at",

    )

    inlines = [

        PurchaseItemInline,

    ]