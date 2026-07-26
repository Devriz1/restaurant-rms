from django.db.models import Sum, Count
from apps.billing.models import Bill


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