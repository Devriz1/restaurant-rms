import json
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.db.models import Count
from django.utils import timezone
from apps.menu.models import MenuCategory, MenuItem
from apps.tables.models import DiningArea, RestaurantTable
from django.db.models import Prefetch
from apps.billing.models import Bill
from apps.audit.utils import audit_log
from .models import (
    GuestOrder,
    KitchenOrderTicket,
    Notification,
    OrderItem,
    TableSession,
)


def purge_empty_guests(session):
    """
    Drop guests on a session that were opened but never ordered from.

    A guest with no order items and no bill carries no information, so it is
    removed automatically instead of needing a manual "clear" action.
    Sessions left with no guests at all are closed.
    """
    session.guest_orders.filter(
        items__isnull=True,
        bill__isnull=True,
    ).delete()

    if not session.guest_orders.exists():

        session.status = "closed"
        session.closed_at = timezone.now()
        session.save()

        return True

    return False


@login_required
def floor_view(request):

    for session in TableSession.objects.filter(
        status="open",
    ):

        purge_empty_guests(session)

    areas = DiningArea.objects.prefetch_related(
        "tables"
    ).filter(
        is_active=True
    ).order_by("display_order", "name")

    active_floor = request.GET.get("floor", "").strip()

    total_tables = sum(area.tables.count() for area in areas)

    return render(
        request,
        "orders/floor_view.html",
        {
            "areas": areas,
            "active_floor": active_floor,
            "total_tables": total_tables,
        },
    )


@login_required
def open_table(request, table_id):

    table = get_object_or_404(
        RestaurantTable,
        pk=table_id,
    )

    session = TableSession.objects.filter(
        table=table,
        status="open",
    ).first()

    if session is None:

        session = TableSession.objects.create(
            table=table,
        )

    return redirect(
        "orders:session-detail",
        session_id=session.id,
    )

@login_required
def session_detail(request, session_id):

    session = get_object_or_404(
        TableSession,
        pk=session_id,
    )

    guests = (
        session.guest_orders
        .annotate(item_count=Count("items"))
        .prefetch_related("items")
        .order_by("guest_number")
    )

    return render(
        request,
        "orders/table_session.html",
        {
            "session": session,
            "table": session.table,
            "guests": guests,
        },
    )
@login_required
def add_guest(request, session_id):

    if request.method != "POST":

        return redirect(
            "orders:session-detail",
            session_id=session_id,
        )

    session = get_object_or_404(
        TableSession,
        pk=session_id,
    )

    last_guest = (
    session.guest_orders
    .order_by("-guest_number")
    .first()
)

    next_guest = 1

    if last_guest:
        next_guest = last_guest.guest_number + 1

    GuestOrder.objects.create(
        session=session,
        guest_number=next_guest,
    )

    return redirect(
        "orders:session-detail",
        session_id=session.id,
    )


@login_required
def guest_order(request, guest_id):

    guest = get_object_or_404(
        GuestOrder,
        pk=guest_id,
    )

    categories = MenuCategory.objects.filter(
        is_active=True,
    ).order_by(
        "display_order",
        "name",
    )

    menu_items = (
        MenuItem.objects.filter(
            is_available=True,
        )
        .select_related(
            "category",
        )
        .order_by(
            "category__display_order",
            "name",
        )
    )

    for menu_item in menu_items:

        menu_item.display_price = menu_item.get_price(
            guest.price_type
        )

    order_items = (
    guest.items
    .select_related("menu_item")
    .order_by("created_at")
)

    pending_total = sum(
        item.line_total
        for item in order_items
        if item.kot is None
    )

    return render(
        request,
        "orders/guest_order.html",
        {
            "guest": guest,
        "session": guest.session,
        "table": guest.table,
        "categories": categories,
        "menu_items": menu_items,
        "order_items": order_items,
        "pending_total": pending_total,
        },
    )


# ==========================================================
# TAKEAWAY
# ==========================================================

@login_required
def takeaway_list(request):

    orders = (
        GuestOrder.objects
        .filter(
            order_type="takeaway",
            status__in=[
                "open",
                "preparing",
                "ready",
                "served",
            ],
        )
        .prefetch_related("items__menu_item")
        .order_by("-created_at")
    )

    for order in orders:

        order.total_items = sum(
            item.quantity for item in order.items.all()
        )

    return render(
        request,
        "orders/takeaway_list.html",
        {
            "takeaway_orders": orders,
        },
    )


@login_required
@require_POST
def takeaway_create(request):

    customer_name = request.POST.get(
        "customer_name",
        "",
    ).strip()

    try:
        guest_count = max(
            1,
            int(request.POST.get("guest_count") or 1),
        )

    except (TypeError, ValueError):

        guest_count = 1

    order = GuestOrder.objects.create(
        session=None,
        order_type="takeaway",
        guest_number=1,
        guest_name=customer_name,
        guest_count=guest_count,
    )

    return redirect(
        "orders:guest-order",
        guest_id=order.id,
    )



@require_POST
@login_required
def add_item(request):

    data = json.loads(request.body)

    guest = get_object_or_404(
        GuestOrder,
        pk=data.get("guest_id"),
    )

    menu_item = get_object_or_404(
        MenuItem,
        pk=data.get("menu_item_id"),
    )

    existing_item = (
        guest.items
        .filter(
            menu_item=menu_item,
            kot__isnull=True,
        )
        .first()
    )

    if existing_item:

        existing_item.quantity += 1

        existing_item.save()

        affected_item = existing_item

        order_items = guest.items.select_related(
            "menu_item",
        )

    else:

        affected_item = OrderItem.objects.create(
            order=guest,
            menu_item=menu_item,
            quantity=1,
            unit_price=menu_item.get_price(
                guest.price_type
            ),
        )

        order_items = guest.items.select_related(
            "menu_item",
        )

    pending_total = sum(
        item.line_total
        for item in order_items
        if item.kot is None
    )

    html = render_to_string(
        "orders/partials/current_order.html",
        {
            "order_items": order_items,
         "pending_total": pending_total,
    },
    request=request,
)

    return JsonResponse(
    {
        "success": True,
        "html": html,
        "guest_id": guest.id,
        "order_item_id": affected_item.id,
        "guest_items": guest.items.count(),
        "guest_total": str(guest.subtotal),
    }
)


@require_POST
@login_required
def update_item(request):

    data = json.loads(request.body)

    order_item = get_object_or_404(
        OrderItem,
        pk=data.get("order_item_id"),
    )

    guest = order_item.order

    action = data.get("action")

    if action == "increase":

        order_item.quantity += 1
        order_item.save()

    elif action == "decrease":

        if order_item.quantity > 1:

            order_item.quantity -= 1
            order_item.save()

        else:

            order_item.delete()

    elif action == "remove":

        order_item.delete()

    order_items = guest.items.select_related(
        "menu_item",
    )

    pending_total = sum(
        item.line_total
        for item in order_items
        if item.kot is None and item.status != "cancelled"
    )

    html = render_to_string(
        "orders/partials/current_order.html",
        {
            "order_items": order_items,
            "pending_total": pending_total,
    },
    request=request,
)

    return JsonResponse(
        {
            "success": True,
            "html": html,
        }
    )



@login_required
@require_POST
def send_to_kitchen(request, guest_id):

    guest = get_object_or_404(
        GuestOrder,
        pk=guest_id,
    )

    unsent_items = guest.items.filter(
        kot__isnull=True,
    )

    if not unsent_items.exists():

        return JsonResponse({
            "success": False,
            "message": "No new items to send."
        })

    # Ensure a Bill exists so the kitchen can group items by bill.
    try:
        bill = guest.bill
    except Exception:
        bill = Bill.objects.create(
            guest_order=guest,
            session=guest.session,
            created_by=request.user,
        )

    kot = KitchenOrderTicket.objects.create(
        guest_order=guest,
        created_by=request.user,
    )

    unsent_items.update(kot=kot)

    guest.status = "preparing"
    guest.save()

    audit_log(
        request.user,
        "create",
        "KitchenOrderTicket",
        kot.id,
        str(kot),
        f"KOT #{kot.ticket_number} sent for guest {guest.guest_number} with {unsent_items.count()} item(s).",
        request,
    )

    # Auto-print KOT to configured kitchen printer if enabled
    try:
        from apps.settings.printer import PrinterManager

        settings_obj = PrinterManager.get_settings()
        if settings_obj.auto_print_kot and settings_obj.kitchen_printer:
            order_items = guest.items.select_related("menu_item")
            kot_html = render_to_string(
                "orders/kot_print.html",
                {
                    "kot": kot,
                    "items": order_items,
                    "guest": guest,
                    "table": guest.table,
                },
                request=request,
            )
            PrinterManager.print_kot(kot_html)
    except Exception as e:
        # Log the error but don't fail the request
        audit_log(
            None,
            "view",
            "KitchenOrderTicket",
            kot.id,
            str(kot),
            f"KOT auto-print failed: {str(e)}",
            request,
        )

    order_items = guest.items.select_related("menu_item")

    pending_total = sum(
        item.line_total
        for item in order_items
        if item.kot is None
    )

    html = render_to_string(
        "orders/partials/current_order.html",
        {
            "order_items": order_items,
            "pending_total": pending_total,
        },
        request=request,
    )

    return JsonResponse({
        "success": True,
        "message": f"{kot.ticket_number} sent successfully.",
        "ticket": kot.ticket_number,
        "html": html,
        "kot_url": request.build_absolute_uri(
            reverse("orders:kot-print", kwargs={"kot_id": kot.id})
        ),
    })
@login_required
def kot_print(request, kot_id):

    kot = get_object_or_404(
        KitchenOrderTicket,
        pk=kot_id,
    )

    items = kot.items.select_related(
        "menu_item",
    )

    return render(
        request,
        "orders/kot_print.html",
        {
            "kot": kot,
            "items": items,
            "guest": kot.guest_order,
            "table": kot.guest_order.table,
        },
    )

@login_required
def orders_dashboard(request):

    sessions = (
        TableSession.objects
        .filter(status="open")
        .select_related("table")
        .prefetch_related(
            Prefetch(
                "guest_orders",
                queryset=GuestOrder.objects.prefetch_related(
                    "items__menu_item",
                    "bill",
                ),
            )
        )
        .order_by("table__display_name")
    )

    active_tables = sessions.count()

    total_guests = 0

    total_items = 0

    for session in sessions:

        guest_count = session.guest_orders.count()

        session.total_guests = guest_count

        total_guests += guest_count

        item_count = 0

        last_updated = None

        for guest in session.guest_orders.all():

            for item in guest.items.all():

                item_count += item.quantity

                if (
                    last_updated is None
                    or item.created_at > last_updated
                ):
                    last_updated = item.created_at

        session.total_items = item_count

        session.last_updated = last_updated

        total_items += item_count

    context = {

        "sessions": sessions,

        "active_tables": active_tables,

        "total_guests": total_guests,

        "total_items": total_items,

    }

    return render(
        request,
        "orders/orders_dashboard.html",
        context,
    )


# ==========================================================
# KITCHEN DISPLAY
# ==========================================================

KITCHEN_ITEM_STATUSES = ["pending", "preparing", "ready"]


def _kitchen_bills():
    """Return items currently in the kitchen, grouped by bill.

    Used by both the full kitchen view and the AJAX refresh endpoint.
    """

    items = (
        OrderItem.objects
        .select_related(
            "menu_item",
            "menu_item__category",
            "order",
            "order__session",
            "order__session__table",
            "order__session__table__area",
            "kot",
        )
        .filter(
            kot__isnull=False,
            status__in=KITCHEN_ITEM_STATUSES,
            order__bill__isnull=False,
        )
        .order_by(
            "order__bill__bill_number",
            "created_at",
        )
    )

    bills = {}

    for item in items:
        bill = item.order.bill
        bill_key = bill.id

        if bill_key not in bills:
            bills[bill_key] = {
                "bill": bill,
                "order": item.order,
                "items": [],
            }

        bills[bill_key]["items"].append(item)

    return bills


@login_required
def kitchen_view(request):
    """Kitchen display screen showing all items sent to the kitchen.

    Items are grouped by their associated bill.
    """

    bills = _kitchen_bills()

    return render(
        request,
        "orders/kitchen.html",
        {
            "bills": bills,
            "bill_count": len(bills),
        },
    )


@login_required
def kitchen_refresh(request):
    """AJAX endpoint returning just the bills grid for live updates."""

    bills = _kitchen_bills()

    html = render_to_string(
        "orders/partials/kitchen_bills.html",
        {
            "bills": bills,
            "bill_count": len(bills),
        },
        request=request,
    )
    
    from django.utils import timezone
    now = timezone.now().strftime("%I:%M %p").lstrip("0")

    return JsonResponse({
        "html": html,
        "last_updated": now,
    })


@require_POST
@login_required
def start_bill(request, bill_id):
    """Handle bill-level kitchen actions.

    When the bill has pending items, this starts them all (sets to ``preparing``).
    When all items are ``ready``, this serves them all (sets to ``served``).
    """

    bill = get_object_or_404(Bill, pk=bill_id)

    bill_items = bill.guest_order.items.filter(
        kot__isnull=False,
        status__in=KITCHEN_ITEM_STATUSES,
    )

    pending_items = bill_items.filter(status="pending")
    ready_items = bill_items.filter(status="ready")
    not_ready_count = bill_items.exclude(status="ready").count()

    if pending_items.exists():
        pending_items.update(status="preparing")
        audit_log(
            request.user,
            "status_change",
            "Bill",
            bill.id,
            str(bill),
            f"Started preparing {pending_items.count()} item(s) on bill {bill.bill_number}.",
            request,
        )
        return JsonResponse({
            "success": True,
            "action": "started",
            "bill_id": bill_id,
            "message": f"{pending_items.count()} item(s) moved to preparing.",
        })

    elif ready_items.exists() and not_ready_count == ready_items.count():
        ready_items.update(status="served")

        # Create notification for the waiter who created the KOT
        kot = bill.guest_order.kots.first()
        if kot and kot.created_by:
            Notification.objects.create(
                recipient=kot.created_by,
                bill=bill,
                message=f"Bill {bill.bill_number} is ready to be served",
                notification_type="order_served",
            )

        audit_log(
            request.user,
            "status_change",
            "Bill",
            bill.id,
            str(bill),
            f"Served {ready_items.count()} item(s) on bill {bill.bill_number}.",
            request,
        )

        return JsonResponse({
            "success": True,
            "action": "served",
            "bill_id": bill_id,
            "served_count": ready_items.count(),
            "message": f"{ready_items.count()} item(s) served.",
        })

    else:
        return JsonResponse({
            "success": False,
            "message": "No action possible on this bill right now.",
        })


@require_POST
@login_required
def update_kitchen_item(request, item_id):
    """Advance an order-item's kitchen status.

    Accepts ``status`` in the JSON body.  Valid transitions:
    pending → preparing → ready → served
    Any item can also be set back to ``cancelled``.
    """

    item = get_object_or_404(OrderItem, pk=item_id)

    data = json.loads(request.body)
    new_status = data.get("status", "").strip()

    if new_status not in dict(OrderItem.STATUS_CHOICES):
        return JsonResponse(
            {"success": False, "message": "Invalid status value."},
            status=400,
        )

    previous_status = item.status
    item.status = new_status

    item.save()

    audit_log(
        request.user,
        "status_change",
        "OrderItem",
        item.id,
        str(item),
        f"Status changed from '{previous_status}' to '{new_status}' for {item.menu_item.name}.",
        request,
    )

    if new_status == "served":
        if not item.order.items.filter(
            status__in=KITCHEN_ITEM_STATUSES,
        ).exists():
            item.order.status = "served"
            item.order.save()

        # Create notification for the waiter who created the KOT
        kot = item.order.kots.first()
        if kot and kot.created_by:
            Notification.objects.create(
                recipient=kot.created_by,
                order=item.order,
                message=f"{item.menu_item.name} is ready to be served",
                notification_type="item_served",
            )

    html = render_to_string(
        "orders/partials/kitchen_item_row.html",
        {"item": item},
        request=request,
    )

    return JsonResponse({
        "success": True,
        "item_id": item_id,
        "old_status": previous_status,
        "new_status": new_status,
        "order_id": item.order_id,
        "html": html,
    })


@require_POST
@login_required
def cancel_kitchen_item(request, item_id):
    """Cancel a single order item from the kitchen screen."""

    item = get_object_or_404(OrderItem, pk=item_id)

    if item.status in ("served", "cancelled"):
        return JsonResponse(
            {
                "success": False,
                "message": "This item can no longer be cancelled.",
            },
            status=400,
        )

    item.status = "cancelled"
    item.save()

    audit_log(
        request.user,
        "status_change",
        "OrderItem",
        item.id,
        str(item),
        f"Item '{item.menu_item.name}' cancelled.",
        request,
    )

    guest = item.order

    if not guest.items.filter(
        status__in=KITCHEN_ITEM_STATUSES,
    ).exists():
        if guest.items.filter(status="cancelled").count() == guest.items.count():
            guest.status = "cancelled"
        else:
            guest.status = "ready"
        guest.save()

    html = render_to_string(
        "orders/partials/kitchen_item_row.html",
        {"item": item},
        request=request,
    )

    return JsonResponse({
        "success": True,
        "item_id": item_id,
        "guest_id": guest.id,
        "html": html,
    })


@login_required
def notifications_list(request):
    """Return the list of notifications for the current user as HTML."""

    notifications = Notification.objects.filter(
        recipient=request.user,
        is_read=False,
    ).select_related(
        "order",
        "order__session",
        "order__session__table",
        "bill",
    )[:20]

    unread_count = notifications.count()

    html = render_to_string(
        "orders/partials/notifications_dropdown.html",
        {
            "notifications": notifications,
        },
        request=request,
    )

    return JsonResponse({
        "html": html,
        "count": unread_count,
    })


@require_POST
@login_required
def notification_read(request, notification_id):
    """Mark a single notification as read."""

    notification = get_object_or_404(
        Notification,
        pk=notification_id,
        recipient=request.user,
    )

    notification.is_read = True
    notification.save()

    unread_count = Notification.objects.filter(
        recipient=request.user,
        is_read=False,
    ).count()

    return JsonResponse({
        "success": True,
        "unread_count": unread_count,
    })


@require_POST
@login_required
def notifications_mark_all_read(request):
    """Mark all notifications for the current user as read."""

    Notification.objects.filter(
        recipient=request.user,
        is_read=False,
    ).update(is_read=True)

    return JsonResponse({
        "success": True,
        "message": "All notifications marked as read.",
    })
