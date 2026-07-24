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