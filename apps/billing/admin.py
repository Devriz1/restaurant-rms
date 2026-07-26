from django.contrib import admin

from .models import Bill
from .models import Payment


class PaymentInline(admin.TabularInline):

    model = Payment

    extra = 0

    readonly_fields = (

        "payment_method",

        "amount",

        "reference_number",

        "received_by",

        "paid_at",

    )



@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):

    list_display = (

        "bill_number",

        "guest_order",

        "session",

        "grand_total",

        "status",

        "created_at",

    )

    list_filter = (

        "status",

        "created_at",

    )

    search_fields = (

        "bill_number",

        "guest_order__order_number",

    )

    readonly_fields = (

        "bill_number",

        "created_at",

        "paid_at",

    )

    inlines = [

        PaymentInline,

    ]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (

        "bill",

        "payment_method",

        "amount",

        "received_by",

        "paid_at",

    )

    list_filter = (

        "payment_method",

        "paid_at",

    )

    search_fields = (

        "bill__bill_number",

        "reference_number",

    )