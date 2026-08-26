from datetime import date

from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Prefetch, Sum
from django.shortcuts import render
from apps.billing.models import DailyClosing
from apps.billing.models import Bill, Payment
from apps.orders.models import KitchenOrderTicket, OrderItem, TableSession, GuestOrder
from apps.tables.models import RestaurantTable
from apps.accounts.decorators import permission_required
from .filters import apply_report_filters


@login_required
@permission_required("reports.view")
def dashboard(request):

    today = date.today()

    today_bills = Bill.objects.filter(
        created_at__date=today,
        status="paid",
    )

    today_sales = today_bills.aggregate(
        total=Sum("grand_total")
    )["total"] or 0

    today_transactions = Payment.objects.filter(
        paid_at__date=today,
    ).count()

    active_staff = KitchenOrderTicket.objects.filter(
        created_at__date=today,
        created_by__isnull=False,
    ).values(
        "created_by"
    ).distinct().count()

    return render(
        request,
        "reports/dashboard.html",
        {
            "today_sales": today_sales,
            "today_bills": today_bills.count(),
            "today_transactions": today_transactions,
            "active_staff": active_staff,
        },
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
    date_field="created_at",
    search_fields=[
        "bill_number",
        "session__table__display_name",
        "guest_order__guest_name",
        "created_by__username",
    ],
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

        "reset_url": "reports:sales",

        "search_placeholder":
            "Search Bill / Table / Guest...",

        "columns": [

            ("bill", "Bill No"),

            ("date", "Date"),

            ("floor", "Floor"),

            ("table", "Table"),

            ("guest", "Guest"),

            ("total", "Total"),

            ("cashier", "Cashier"),

            ("status", "Status"),

        ],

        "summary_cards": [

            {

                "title": "Total Sales",

                "value": f"₹ {total_sales}"

            },

            {

                "title": "Total Bills",

                "value": bills.count()

            },

            {

                "title": "Average Bill",

                "value": f"₹ {average_bill:.2f}"

            },

            {

                "title": "Total Discount",

                "value": f"₹ {total_discount}"

            },

        ],

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

    payments = apply_report_filters(
    request,
    payments,
    date_field="paid_at",
    search_fields=[
        "bill__bill_number",
        "received_by__username",
        "reference_number",
    ],
)
    total_amount = payments.aggregate(
        total=Sum("amount")
    )["total"] or 0

    total_transactions = payments.count()

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

    context = {

        "payments": payments,

        "total_amount": total_amount,

        "total_transactions": total_transactions,

        "cash": cash,

        "upi": upi,

        "card": card,

        "reset_url": "reports:payments",

        "search_placeholder":
            "Search Bill / Payment...",

        "columns": [

            ("bill", "Bill No"),

            ("date", "Date"),

            ("method", "Method"),

            ("amount", "Amount"),

            ("reference", "Reference"),

            ("cashier", "Received By"),

        ],

        "summary_cards": [

            {

                "title": "Collection",

                "value": f"₹ {total_amount}"

            },

            {

                "title": "Transactions",

                "value": total_transactions

            },

            {

                "title": "Cash",

                "value": f"₹ {cash}"

            },

            {

                "title": "UPI",

                "value": f"₹ {upi}"

            },

            {

                "title": "Card",

                "value": f"₹ {card}"

            },

        ],

    }

    return render(
        request,
        "reports/payment_report.html",
        context,
    )


@login_required
def item_report(request):

    items = (
        OrderItem.objects
        .select_related(
            "menu_item",
            "menu_item__category",
        )
        .order_by("-created_at")
    )

    items = apply_report_filters(
        request,
        items,
        date_field="created_at",
        search_fields=[
            "menu_item__name",
            "menu_item__category__name",
        ],
    )

    summary = items.aggregate(

        quantity=Sum("quantity"),

        sales=Sum("line_total"),

        orders=Count(
            "order",
            distinct=True,
        ),

    )

    report_items = (
        items.values(
            "menu_item__name",
            "menu_item__category__name",
        )
        .annotate(
            total_quantity=Sum("quantity"),
            total_sales=Sum("line_total"),
            total_orders=Count(
                "order",
                distinct=True,
            ),
        )
        .order_by("-total_quantity")
    )

    context = {

    "items": report_items,

    # Summary values used by the template
    "total_quantity": summary["quantity"] or 0,

    "total_sales": summary["sales"] or 0,

    "total_orders": summary["orders"] or 0,

    "reset_url": "reports:items",

    "search_placeholder": "Search Menu Item...",

    "columns": [

        ("item", "Item"),

        ("category", "Category"),

        ("quantity", "Quantity"),

        ("orders", "Orders"),

        ("sales", "Revenue"),

    ],

    "summary_cards": [

        {

            "title": "Revenue",

            "value": f"₹ {summary['sales'] or 0}",

        },

        {

            "title": "Items Sold",

            "value": summary["quantity"] or 0,

        },

        {

            "title": "Orders",

            "value": summary["orders"] or 0,

        },

    ],

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
    ).select_related(
        "created_by"
    ).order_by(
        "-created_at"
    )

    waiters = apply_report_filters(
        request,
        waiters,
        date_field="created_at",
        search_fields=[
            "created_by__username",
        ],
    )

    report_waiters = (
        waiters.values(
            "created_by__username",
        )
        .annotate(

            total_kots=Count("id"),

            total_items=Sum("items__quantity"),

        )
        .order_by("-total_kots")
    )

    total_waiters = report_waiters.count()

    total_kots = sum(
        row["total_kots"]
        for row in report_waiters
    )

    total_items = sum(
        row["total_items"]
        for row in report_waiters
    )

    average_kot = round(
        total_kots / total_waiters,
        2
    ) if total_waiters else 0

    context = {

        "waiters": report_waiters,

        "total_waiters": total_waiters,

        "total_kots": total_kots,

        "total_items": total_items,

        "average_kot": average_kot,

        "reset_url": "reports:waiters",

        "search_placeholder": "Search Waiter...",

        "columns": [

            ("waiter", "Waiter"),

            ("kots", "KOT"),

            ("items", "Items"),

        ],

        "summary_cards": [

            {
                "title": "Total Waiters",
                "value": total_waiters,
            },

            {
                "title": "Total KOT",
                "value": total_kots,
            },

            {
                "title": "Items Ordered",
                "value": total_items,
            },

            {
                "title": "Average KOT / Waiter",
                "value": average_kot,
            },

        ],

    }

    return render(
        request,
        "reports/waiter_report.html",
        context,
    )

@login_required
def daily_closing_report(request):

    bills = (
        Bill.objects
        .select_related(
            "guest_order",
            "session",
            "session__table",
            "created_by",
        )
        .order_by("-created_at")
    )

    bills = apply_report_filters(
        request,
        bills,
        date_field="created_at",
        search_fields=[
            "bill_number",
            "guest_order__guest_name",
            "session__table__display_name",
        ],
    )

    payments = Payment.objects.filter(
        bill__in=bills
    )

    # ==========================================
    # TOTALS
    # ==========================================

    total_sales = bills.aggregate(
        total=Sum("grand_total")
    )["total"] or 0

    total_bills = bills.count()

    total_transactions = payments.count()

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

    # ==========================================
    # DAILY CLOSING MODEL INTEGRATION
    # ==========================================

    today = date.today()

    daily_closing = DailyClosing.objects.filter(
        date=today
    ).first()

    if daily_closing:

        opening_balance = daily_closing.opening_balance

        closing_balance = daily_closing.closing_balance

    else:

        previous_closing = (
            DailyClosing.objects
            .order_by("-date")
            .first()
        )

        opening_balance = previous_closing.closing_balance if previous_closing else 0

        closing_balance = opening_balance + cash + upi + card

    context = {

        "bills": bills,

        "cash": cash,
        "upi": upi,
        "card": card,

        "opening_balance": opening_balance,
        "closing_balance": closing_balance,

        "total_sales": total_sales,
        "total_bills": total_bills,
        "total_transactions": total_transactions,

        "reset_url": "reports:daily-closing",

        "search_placeholder": "Search Bill / Table / Guest...",

        "columns": [

            ("bill", "Bill"),

            ("date", "Date"),

            ("table", "Table"),

            ("guest", "Guest"),

            ("cashier", "Cashier"),

            ("total", "Total"),

            ("status", "Status"),

        ],

        "summary_cards": [

            {
                "title": "Opening Balance",
                "value": f"₹ {opening_balance}",
            },

            {
                "title": "Today's Sales",
                "value": f"₹ {total_sales}",
            },

            {
                "title": "Cash",
                "value": f"₹ {cash}",
            },

            {
                "title": "UPI",
                "value": f"₹ {upi}",
            },

            {
                "title": "Card",
                "value": f"₹ {card}",
            },

            {
                "title": "Bills",
                "value": total_bills,
            },

            {
                "title": "Transactions",
                "value": total_transactions,
            },

            {
                "title": "Closing Balance",
                "value": f"₹ {closing_balance}",
            },

        ],

    }

    return render(
        request,
        "reports/daily_closing.html",
        context,
    )


@login_required
def table_report(request):

    tables = (
        RestaurantTable.objects
        .filter(is_active=True)
        .select_related("area")
        .prefetch_related(
            Prefetch(
                "sessions",
                queryset=TableSession.objects.filter(
                    status="open"
                ).prefetch_related(
                    Prefetch(
                        "guest_orders",
                        queryset=GuestOrder.objects.prefetch_related(
                            "items__menu_item"
                        ),
                    )
                ),
            )
        )
        .order_by("area__name", "table_number")
    )

    search_query = request.GET.get("search", "").strip()

    report_tables = []

    for table in tables:

        total_guests = 0

        total_revenue = Decimal("0.00")

        total_items = 0

        for session in table.sessions.all():

            for guest in session.guest_orders.all():

                total_guests += 1

                for item in guest.items.all():

                    total_revenue += item.line_total

                    total_items += item.quantity

        row = {

            "table": table,

            "total_guests": total_guests,

            "total_revenue": total_revenue,

            "total_items": total_items,

        }

        if search_query:

            query = search_query.lower()

            if query in table.display_name.lower() or query in table.area.name.lower():

                report_tables.append(row)

        else:

            report_tables.append(row)

    report_tables.sort(
        key=lambda x: x["total_revenue"],
        reverse=True,
    )

    context = {

        "tables": report_tables,

        "reset_url": "reports:tables",

        "search_placeholder": "Search table or area...",

        "columns": [

            ("table", "Table"),

            ("area", "Area"),

            ("guests", "Guests"),

            ("items", "Items"),

            ("revenue", "Revenue"),

        ],

        "summary_cards": [

            {

                "title": "Active Tables",

                "value": len(report_tables),

            },

            {

                "title": "Total Guests",

                "value": sum(t["total_guests"] for t in report_tables),

            },

            {

                "title": "Total Items",

                "value": sum(t["total_items"] for t in report_tables),

            },

            {

                "title": "Total Revenue",

                "value": f"₹ {sum(t['total_revenue'] for t in report_tables)}",

            },

        ],

    }

    return render(
        request,
        "reports/table_report.html",
        context,
    )

