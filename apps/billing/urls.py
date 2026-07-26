from django.urls import path

from . import views


app_name = "billing"


urlpatterns = [

    path(
        "",
        views.dashboard,
        name="dashboard",
    ),

    path(
        "guest/<int:guest_id>/",
        views.billing_screen,
        name="billing-screen",
    ),

]