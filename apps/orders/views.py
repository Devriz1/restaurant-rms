import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from apps.menu.models import MenuCategory, MenuItem
from apps.tables.models import DiningArea, RestaurantTable

from .models import (
    GuestOrder,
    KitchenOrderTicket,
    OrderItem,
    TableSession,
)


@login_required
def floor_view(request):

    areas = DiningArea.objects.prefetch_related(
        "tables"
    ).filter(
        is_active=True
    )

    return render(
        request,
        "orders/floor_view.html",
        {
            "areas": areas,
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

    return render(
        request,
        "orders/table_session.html",
        {
            "session": session,
            "table": session.table,
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

    last_guest = session.guest_orders.order_by(
        "-guest_number"
    ).first()

    next_guest = (
        1
        if last_guest is None
        else last_guest.guest_number + 1
    )

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

    order_items = guest.items.select_related(
     "menu_item",
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
        "table": guest.session.table,
        "categories": categories,
        "menu_items": menu_items,
        "order_items": order_items,
        "pending_total": pending_total,
        },
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

    order_item = OrderItem.objects.filter(
    order=guest,
    menu_item=menu_item,
    kot__isnull=True,
).first()

    if order_item:

        order_item.quantity += 1
        order_item.save()

    else:

        OrderItem.objects.create(
            order=guest,
            menu_item=menu_item,
            quantity=1,
            unit_price=menu_item.price,
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

    kot = KitchenOrderTicket.objects.create(
        guest_order=guest,
        created_by=request.user,
    )

    unsent_items.update(kot=kot)

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
            "table": kot.guest_order.session.table,
        },
    )