from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path(
        "floor/",
        views.floor_view,
        name="floor-view",
    ),

    path(
        "table/<int:table_id>/",
        views.open_table,
        name="open-table",
    ),

    path(
        "session/<int:session_id>/",
        views.session_detail,
        name="session-detail",
    ),
    path(
        "session/<int:session_id>/add-guest/",
        views.add_guest,
        name="add-guest",
    ),
    path(
    "guest/<int:guest_id>/",
    views.guest_order,
    name="guest-order",
),
path(
    "add-item/",
    views.add_item,
    name="add-item",
),
path(
    "update-item/",
    views.update_item,
    name="update-item",
),
path(
    "guest/<int:guest_id>/send/",
    views.send_to_kitchen,
    name="send-to-kitchen",
),
path(
    "kot/<int:kot_id>/",
    views.kot_print,
    name="kot-print",
),
    path(
         "live-orders/",
         views.orders_dashboard,
         name="orders-dashboard",
    ),

    # ---------------- Kitchen ----------------
    path(
        "kitchen/",
        views.kitchen_view,
        name="kitchen-view",
    ),
    path(
        "kitchen/refresh/",
        views.kitchen_refresh,
        name="kitchen-refresh",
    ),
    path(
        "kitchen/item/<int:item_id>/update/",
        views.update_kitchen_item,
        name="kitchen-update-item",
    ),
    path(
        "kitchen/item/<int:item_id>/cancel/",
        views.cancel_kitchen_item,
        name="kitchen-cancel-item",
    ),
    path(
        "kitchen/bill/<int:bill_id>/start/",
        views.start_bill,
        name="kitchen-start-bill",
    ),

    # ---------------- Notifications ----------------
    path(
        "notifications/",
        views.notifications_list,
        name="notifications-list",
    ),
    path(
        "notifications/<int:notification_id>/read/",
        views.notification_read,
        name="notification-read",
    ),
    path(
        "notifications/mark-all-read/",
        views.notifications_mark_all_read,
        name="notifications-mark-all-read",
    ),

    # ---------------- Takeaway ----------------

    path(
        "takeaway/",
        views.takeaway_list,
        name="takeaway-list",
    ),

    path(
        "takeaway/new/",
        views.takeaway_create,
        name="takeaway-create",
    ),
]