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
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customers/<int:pk>/payment/', views.receive_customer_payment, name='receive_customer_payment'),

]