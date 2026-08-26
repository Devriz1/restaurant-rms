from django.contrib import admin

from .models import Bill
from .models import Payment,Customer, CreditLedgerEntry, CustomerPayment, BillPaymentAllocation


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
    

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_number', 'name', 'phone', 'credit_limit', 'current_outstanding', 'is_active')
    search_fields = ('name', 'phone', 'customer_number')
    readonly_fields = ('customer_number',)

@admin.register(CreditLedgerEntry)
class CreditLedgerEntryAdmin(admin.ModelAdmin):
    list_display = ('customer', 'transaction_type', 'entry_type', 'amount', 'created_by', 'created_at')
    list_filter = ('transaction_type', 'entry_type', 'created_at')
    search_fields = ('customer__name', 'reference_number')

    def has_delete_permission(self, request, obj=None):
        # Prevent accidental deletion of ledger history
        return False

@admin.register(CustomerPayment)
class CustomerPaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_number', 'customer', 'amount', 'payment_method', 'received_by', 'created_at')
    readonly_fields = ('payment_number',)