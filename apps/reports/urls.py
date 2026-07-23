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
        "payments/",
        views.payment_report,
        name="payments",
    ),

    path(
        "items/",
        views.item_report,
        name="items",
    ),

    path(
        "categories/",
        views.category_report,
        name="categories",
    ),

    path(
        "tables/",
        views.table_report,
        name="tables",
    ),

    path(
        "areas/",
        views.dining_area_report,
        name="areas",
    ),

    path(
        "waiters/",
        views.waiter_report,
        name="waiters",
    ),

    path(
        "daily-closing/",
        views.daily_closing_report,
        name="daily-closing",
    ),

]