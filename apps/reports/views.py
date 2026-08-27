from datetime import date

from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Prefetch, Sum
from django.shortcuts import render
from apps.billing.models import DailyClosing
from apps.billing.models import Bill, Payment
from apps.orders.models import KitchenOrderTicket, OrderItem, TableSession, GuestOrder
from apps.restaurant.models import Restaurant
from apps.tables.models import RestaurantTable
from apps.accounts.decorators import permission_required
from .filters import apply_report_filters
from .export_utils import export_csv, export_excel, export_pdf


def _get_currency_symbol():
    restaurant = Restaurant.objects.first()
    return restaurant.currency_symbol if restaurant else "₹"


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

                "value": f"{_get_currency_symbol()} {total_sales}"

            },

            {

                "title": "Total Bills",

                "value": bills.count()

            },

            {

                "title": "Average Bill",

                "value": f"{_get_currency_symbol()} {average_bill:.2f}"

            },

            {
                "title": "Total Discount",
                "value": f"{_get_currency_symbol()} {total_discount}"
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

                "value": f"{_get_currency_symbol()} {total_amount}"

            },

            {

                "title": "Transactions",

                "value": total_transactions

            },

            {

                "title": "Cash",

                "value": f"{_get_currency_symbol()} {cash}"

            },

            {

                "title": "UPI",

                "value": f"{_get_currency_symbol()} {upi}"

            },

            {

                "title": "Card",

                "value": f"{_get_currency_symbol()} {card}"

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

            "value": f"{_get_currency_symbol()} {summary['sales'] or 0}",

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
                "value": f"{_get_currency_symbol()} {opening_balance}",
            },

            {
                "title": "Today's Sales",
                "value": f"{_get_currency_symbol()} {total_sales}",
            },

            {
                "title": "Cash",
                "value": f"{_get_currency_symbol()} {cash}",
            },

            {
                "title": "UPI",
                "value": f"{_get_currency_symbol()} {upi}",
            },

            {
                "title": "Card",
                "value": f"{_get_currency_symbol()} {card}",
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
                "value": f"{_get_currency_symbol()} {closing_balance}",
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

                "value": f"{_get_currency_symbol()} {sum(t['total_revenue'] for t in report_tables)}",

            },

        ],

    }

    return render(
        request,
        "reports/table_report.html",
        context,
    )


def _export_report(request, report_name, export_format):
    report_map = {
        "sales": _build_sales_export,
        "payments": _build_payment_export,
        "items": _build_item_export,
        "waiters": _build_waiter_export,
        "daily-closing": _build_daily_closing_export,
        "tables": _build_table_export,
    }

    builder = report_map.get(report_name)
    if not builder:
        return render(request, "404.html", status=404)

    data, columns, summary_cards, title, filename_prefix = builder(request)

    symbol = "₹"
    try:
        from apps.restaurant.models import Restaurant
        restaurant = Restaurant.objects.first()
        if restaurant and restaurant.currency_symbol:
            symbol = restaurant.currency_symbol
    except Exception:
        pass

    if summary_cards:
        summary_cards = [
            {
                "title": card["title"],
                "value": card["value"].replace("₹", symbol) if isinstance(card.get("value"), str) else f"{symbol} {card['value']}",
            }
            for card in summary_cards
        ]

    filename = f"{filename_prefix}_{date.today().strftime('%Y%m%d')}"

    if export_format == "csv":
        return export_csv(data, columns, f"{filename}.csv", summary_cards, symbol=symbol)

    if export_format == "xlsx":
        return export_excel(data, columns, f"{filename}.xlsx", summary_cards, symbol=symbol)

    if export_format == "pdf":
        return export_pdf(data, columns, f"{filename}.pdf", title, summary_cards, symbol=symbol)

    return render(request, "404.html", status=404)


def _build_sales_export(request):
    bills = Bill.objects.select_related(
        "guest_order",
        "session",
        "session__table",
        "session__table__area",
        "created_by",
    ).order_by("-created_at")

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
        total_sales=Sum("grand_total"),
        average_bill=Avg("grand_total"),
        total_discount=Sum("discount"),
    )

    columns = [
        ("bill_number", "Bill No"),
        ("created_at", "Date"),
        ("session.table.area.name", "Floor"),
        ("session.table.display_name", "Table"),
        ("guest_order.guest_number", "Guest"),
        ("grand_total", "Total"),
        ("created_by.username", "Cashier"),
        ("status", "Status"),
    ]

    return (
        bills,
        columns,
        [
            {"title": "Total Sales", "value": f"{_get_currency_symbol()} {summary['total_sales'] or 0}"},
            {"title": "Total Bills", "value": bills.count()},
            {"title": "Average Bill", "value": f"{_get_currency_symbol()} {summary['average_bill'] or 0:.2f}"},
            {"title": "Total Discount", "value": f"{_get_currency_symbol()} {summary['total_discount'] or 0}"},
        ],
        "Sales Report",
        "sales_report",
    )


def _build_payment_export(request):
    payments = Payment.objects.select_related(
        "bill",
        "received_by",
    ).order_by("-paid_at")

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

    total_amount = payments.aggregate(total=Sum("amount"))["total"] or 0
    total_transactions = payments.count()
    cash = payments.filter(payment_method="cash").aggregate(total=Sum("amount"))["total"] or 0
    upi = payments.filter(payment_method="upi").aggregate(total=Sum("amount"))["total"] or 0
    card = payments.filter(payment_method="card").aggregate(total=Sum("amount"))["total"] or 0

    columns = [
        ("bill.bill_number", "Bill No"),
        ("paid_at", "Date"),
        ("payment_method", "Method"),
        ("amount", "Amount"),
        ("reference_number", "Reference"),
        ("received_by.username", "Received By"),
    ]

    return (
        payments,
        columns,
        [
            {"title": "Collection", "value": f"{_get_currency_symbol()} {total_amount}"},
            {"title": "Transactions", "value": total_transactions},
            {"title": "Cash", "value": f"{_get_currency_symbol()} {cash}"},
            {"title": "UPI", "value": f"{_get_currency_symbol()} {upi}"},
            {"title": "Card", "value": f"{_get_currency_symbol()} {card}"},
        ],
        "Payment Report",
        "payment_report",
    )


def _build_item_export(request):
    items = (
        OrderItem.objects
        .select_related("menu_item", "menu_item__category")
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
        orders=Count("order", distinct=True),
    )

    report_items = (
        items.values("menu_item__name", "menu_item__category__name")
        .annotate(
            total_quantity=Sum("quantity"),
            total_sales=Sum("line_total"),
            total_orders=Count("order", distinct=True),
        )
        .order_by("-total_quantity")
    )

    columns = [
        ("menu_item__name", "Item"),
        ("menu_item__category__name", "Category"),
        ("total_quantity", "Quantity"),
        ("total_orders", "Orders"),
        ("total_sales", "Revenue"),
    ]

    return (
        report_items,
        columns,
        [
            {"title": "Revenue", "value": f"{_get_currency_symbol()} {summary['sales'] or 0}"},
            {"title": "Items Sold", "value": summary["quantity"] or 0},
            {"title": "Orders", "value": summary["orders"] or 0},
        ],
        "Item Report",
        "item_report",
    )


def _build_waiter_export(request):
    waiters = KitchenOrderTicket.objects.filter(
        created_by__isnull=False
    ).select_related("created_by").order_by("-created_at")

    waiters = apply_report_filters(
        request,
        waiters,
        date_field="created_at",
        search_fields=[
            "created_by__username",
        ],
    )

    report_waiters = (
        waiters.values("created_by__username")
        .annotate(
            total_kots=Count("id"),
            total_items=Sum("items__quantity"),
        )
        .order_by("-total_kots")
    )

    total_waiters = report_waiters.count()
    total_kots = sum(row["total_kots"] for row in report_waiters)
    total_items = sum(row["total_items"] for row in report_waiters)
    average_kot = round(total_kots / total_waiters, 2) if total_waiters else 0

    columns = [
        ("created_by__username", "Waiter"),
        ("total_kots", "KOT"),
        ("total_items", "Items"),
    ]

    return (
        report_waiters,
        columns,
        [
            {"title": "Total Waiters", "value": total_waiters},
            {"title": "Total KOT", "value": total_kots},
            {"title": "Items Ordered", "value": total_items},
            {"title": "Average KOT / Waiter", "value": average_kot},
        ],
        "Waiter Report",
        "waiter_report",
    )


def _build_daily_closing_export(request):
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

    payments = Payment.objects.filter(bill__in=bills)

    total_sales = bills.aggregate(total=Sum("grand_total"))["total"] or 0
    total_bills = bills.count()
    total_transactions = payments.count()
    cash = payments.filter(payment_method="cash").aggregate(total=Sum("amount"))["total"] or 0
    upi = payments.filter(payment_method="upi").aggregate(total=Sum("amount"))["total"] or 0
    card = payments.filter(payment_method="card").aggregate(total=Sum("amount"))["total"] or 0

    today = date.today()
    daily_closing = DailyClosing.objects.filter(date=today).first()

    if daily_closing:
        opening_balance = daily_closing.opening_balance
        closing_balance = daily_closing.closing_balance
    else:
        previous_closing = DailyClosing.objects.order_by("-date").first()
        opening_balance = previous_closing.closing_balance if previous_closing else 0
        closing_balance = opening_balance + cash + upi + card

    columns = [
        ("bill_number", "Bill"),
        ("created_at", "Date"),
        ("session.table.display_name", "Table"),
        ("guest_order.guest_name", "Guest"),
        ("created_by.username", "Cashier"),
        ("grand_total", "Total"),
        ("status", "Status"),
    ]

    return (
        bills,
        columns,
        [
            {"title": "Opening Balance", "value": f"{_get_currency_symbol()} {opening_balance}"},
            {"title": "Today's Sales", "value": f"{_get_currency_symbol()} {total_sales}"},
            {"title": "Cash", "value": f"{_get_currency_symbol()} {cash}"},
            {"title": "UPI", "value": f"{_get_currency_symbol()} {upi}"},
            {"title": "Card", "value": f"{_get_currency_symbol()} {card}"},
            {"title": "Bills", "value": total_bills},
            {"title": "Transactions", "value": total_transactions},
            {"title": "Closing Balance", "value": f"{_get_currency_symbol()} {closing_balance}"},
        ],
        "Daily Closing Report",
        "daily_closing_report",
    )


def _build_table_export(request):
    tables = (
        RestaurantTable.objects
        .filter(is_active=True)
        .select_related("area")
        .prefetch_related(
            Prefetch(
                "sessions",
                queryset=TableSession.objects.filter(status="open").prefetch_related(
                    Prefetch(
                        "guest_orders",
                        queryset=GuestOrder.objects.prefetch_related("items__menu_item"),
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

    report_tables.sort(key=lambda x: x["total_revenue"], reverse=True)

    columns = [
        ("table.display_name", "Table"),
        ("table.area.name", "Area"),
        ("total_guests", "Guests"),
        ("total_items", "Items"),
        ("total_revenue", "Revenue"),
    ]

    return (
        report_tables,
        columns,
        [
            {"title": "Active Tables", "value": len(report_tables)},
            {"title": "Total Guests", "value": sum(t["total_guests"] for t in report_tables)},
            {"title": "Total Items", "value": sum(t["total_items"] for t in report_tables)},
            {"title": "Total Revenue", "value": f"{_get_currency_symbol()} {sum(t['total_revenue'] for t in report_tables)}"},
        ],
        "Table Report",
        "table_report",
    )


# ==========================================================
# EXPORT VIEWS
# ==========================================================

@login_required
@permission_required("reports.view")
def export_sales(request, export_format):
    return _export_report(request, "sales", export_format)


@login_required
@permission_required("reports.view")
def export_payments(request, export_format):
    return _export_report(request, "payments", export_format)


@login_required
@permission_required("reports.view")
def export_items(request, export_format):
    return _export_report(request, "items", export_format)


@login_required
@permission_required("reports.view")
def export_waiters(request, export_format):
    return _export_report(request, "waiters", export_format)


@login_required
@permission_required("reports.view")
def export_daily_closing(request, export_format):
    return _export_report(request, "daily-closing", export_format)


@login_required
@permission_required("reports.view")
def export_tables(request, export_format):
    return _export_report(request, "tables", export_format)

