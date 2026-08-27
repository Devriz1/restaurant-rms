from django.urls import path
from . import views

app_name = "reports"


urlpatterns = [

    path(
        "",
        views.dashboard,
        name="dashboard",
    ),

    path(
        "sales/",
        views.sales_report,
        name="sales",
    ),

    path(
        "sales/export/<str:export_format>/",
        views.export_sales,
        name="export-sales",
    ),

    path(
        "payments/",
        views.payment_report,
        name="payments",
    ),

    path(
        "payments/export/<str:export_format>/",
        views.export_payments,
        name="export-payments",
    ),

    path(
        "items/",
        views.item_report,
        name="items",
    ),

    path(
        "items/export/<str:export_format>/",
        views.export_items,
        name="export-items",
    ),

    path(
        "waiters/",
        views.waiter_report,
        name="waiters",
    ),

    path(
        "waiters/export/<str:export_format>/",
        views.export_waiters,
        name="export-waiters",
    ),

    path(
        "tables/",
        views.table_report,
        name="tables",
    ),

    path(
        "tables/export/<str:export_format>/",
        views.export_tables,
        name="export-tables",
    ),

    path(
        "daily-closing/",
        views.daily_closing_report,
        name="daily-closing",
    ),

    path(
        "daily-closing/export/<str:export_format>/",
        views.export_daily_closing,
        name="export-daily-closing",
    ),

]