from django.db.models import Sum, Count
from apps.billing.models import Bill,CustomerPayment


def sales_summary(queryset):
    """
    Returns summary statistics for a queryset of bills.
    """

    total_sales = (
        queryset.aggregate(
            total=Sum("grand_total")
        )["total"] or 0
    )

    total_bills = queryset.count()

    total_discount = (
        queryset.aggregate(
            total=Sum("discount")
        )["total"] or 0
    )

    total_tax = (
        queryset.aggregate(
            total=Sum("tax")
        )["total"] or 0
    )

    total_service_charge = (
        queryset.aggregate(
            total=Sum("service_charge")
        )["total"] or 0
    )

    average_bill = (
        total_sales / total_bills
        if total_bills
        else 0
    )

    return {

        "total_sales": total_sales,

        "total_bills": total_bills,

        "total_discount": total_discount,

        "total_tax": total_tax,

        "total_service_charge": total_service_charge,

        "average_bill": average_bill,

    }
    
def get_daily_financial_summary(target_date):
    # 1. Billed Sales
    bills = Bill.objects.filter(created_at__date=target_date)
    cash_sales = bills.filter(payment_method='CASH').aggregate(s=Sum('total_amount'))['s'] or 0
    upi_sales = bills.filter(payment_method='UPI').aggregate(s=Sum('total_amount'))['s'] or 0
    card_sales = bills.filter(payment_method='CARD').aggregate(s=Sum('total_amount'))['s'] or 0
    credit_sales = bills.filter(payment_method='CREDIT').aggregate(s=Sum('total_amount'))['s'] or 0

    total_sales_volume = cash_sales + upi_sales + card_sales + credit_sales

    # 2. Ledger Repayments Collected Today
    repayments = CustomerPayment.objects.filter(created_at__date=target_date)
    repay_cash = repayments.filter(payment_method='CASH').aggregate(s=Sum('amount'))['s'] or 0
    repay_upi = repayments.filter(payment_method='UPI').aggregate(s=Sum('amount'))['s'] or 0
    repay_card = repayments.filter(payment_method='CARD').aggregate(s=Sum('amount'))['s'] or 0

    # 3. Net Liquidity (Cash-in-hand / Actual money received today)
    actual_cash_collected = cash_sales + repay_cash
    actual_upi_collected = upi_sales + repay_upi
    actual_card_collected = card_sales + repay_card

    return {
        'total_sales': total_sales_volume,
        'credit_sales': credit_sales,
        'actual_money_collected': actual_cash_collected + actual_upi_collected + actual_card_collected,
        'collected_breakdown': {
            'cash': actual_cash_collected,
            'upi': actual_upi_collected,
            'card': actual_card_collected,
        }
    }