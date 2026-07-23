from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum, Count, Avg
from datetime import date

from apps.orders.models import (
    KitchenOrderTicket,
    OrderItem,
)

from apps.billing.models import (
    Bill,
    Payment,
)

from .filters import apply_report_filters



@login_required
def dashboard(request):

    return render(
        request,
        "reports/dashboard.html",
    )



@login_required
def sales_report(request):

    bills = Bill.objects.select_related(
        "guest_order",
        "session",
        "session__table",
        "session__table__area",
        "created_by",
    ).order_by(
        "-created_at"
    )


    bills = apply_report_filters(
        request,
        bills,
    )


    summary = bills.aggregate(

        total_sales=Sum(
            "grand_total"
        ),

        average_bill=Avg(
            "grand_total"
        ),

        total_discount=Sum(
            "discount"
        ),

    )


    total_sales = summary["total_sales"] or 0
    average_bill = summary["average_bill"] or 0
    total_discount = summary["total_discount"] or 0



    context = {


        "bills": bills,


        "total_sales": total_sales,

        "total_bills": bills.count(),

        "average_bill": average_bill,

        "total_discount": total_discount,


        "summary_cards":[


            {
                "title":"Total Sales",
                "value":f"₹ {total_sales}"
            },


            {
                "title":"Total Bills",
                "value":bills.count()
            },


            {
                "title":"Average Bill",
                "value":f"₹ {average_bill:.2f}"
            },


            {
                "title":"Total Discount",
                "value":f"₹ {total_discount}"
            },


        ]

    }


    return render(
        request,
        "reports/sales_report.html",
        context,
    )





@login_required
def payment_report(request):


    payments = Payment.objects.select_related(
        "bill",
        "received_by",
    ).order_by(
        "-paid_at"
    )



    total_amount = payments.aggregate(
        total=Sum("amount")
    )["total"] or 0



    context = {


        "payments": payments,


        "total_amount": total_amount,


        "total_transactions":
            payments.count(),



        "summary_cards":[


            {
                "title":"Total Collection",
                "value":f"₹ {total_amount}"
            },


            {
                "title":"Transactions",
                "value":payments.count()
            },


        ]

    }


    return render(
        request,
        "reports/payment_report.html",
        context,
    )





@login_required
def item_report(request):


    items = OrderItem.objects.select_related(
        "menu_item",
    ).values(

        "menu_item__name"

    ).annotate(

        total_quantity=Sum(
            "quantity"
        ),

        total_sales=Sum(
            "line_total"
        ),

        total_orders=Count(
            "order",
            distinct=True
        )

    ).order_by(
        "-total_quantity"
    )


    total_quantity = items.aggregate(
        total=Sum("total_quantity")
    )["total"] or 0



    total_sales = items.aggregate(
        total=Sum("total_sales")
    )["total"] or 0



    context = {


        "items":items,


        "summary_cards":[


            {
                "title":"Items Sold",
                "value":total_quantity
            },


            {
                "title":"Item Revenue",
                "value":f"₹ {total_sales}"
            },


        ]

    }



    return render(
        request,
        "reports/item_report.html",
        context,
    )





@login_required
def waiter_report(request):


    waiters = KitchenOrderTicket.objects.filter(
        created_by__isnull=False
    ).values(

        "created_by__username"

    ).annotate(

        total_kots=Count(
            "id"
        ),

        total_items=Count(
            "items"
        )

    ).order_by(
        "-total_kots"
    )


    context = {


        "waiters":waiters,


        "summary_cards":[


            {
                "title":"Total Waiters",
                "value":waiters.count()
            },


            {
                "title":"Total KOT",
                "value":
                    sum(
                        w["total_kots"]
                        for w in waiters
                    )
            },


        ]

    }


    return render(
        request,
        "reports/waiter_report.html",
        context,
    )





@login_required
def daily_closing_report(request):


    today = date.today()



    bills = Bill.objects.filter(
        created_at__date=today
    )


    payments = Payment.objects.filter(
        bill__in=bills
    )



    total_sales = bills.aggregate(
        total=Sum("grand_total")
    )["total"] or 0



    cash = payments.filter(
        payment_method="cash"
    ).aggregate(
        total=Sum("amount")
    )["total"] or 0



    upi = payments.filter(
        payment_method="upi"
    ).aggregate(
        total=Sum("amount")
    )["total"] or 0



    card = payments.filter(
        payment_method="card"
    ).aggregate(
        total=Sum("amount")
    )["total"] or 0




    context={


        "today":today,


        "total_sales":total_sales,


        "total_bills":bills.count(),


        "cash":cash,


        "upi":upi,


        "card":card,


        "total_transactions":
            payments.count(),



        "summary_cards":[


            {
                "title":"Today's Sales",
                "value":f"₹ {total_sales}"
            },


            {
                "title":"Bills",
                "value":bills.count()
            },


            {
                "title":"Cash",
                "value":f"₹ {cash}"
            },


            {
                "title":"UPI",
                "value":f"₹ {upi}"
            },


        ]

    }



    return render(
        request,
        "reports/daily_closing.html",
        context
    )