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
]