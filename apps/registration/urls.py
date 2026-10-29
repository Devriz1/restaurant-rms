from django.urls import path
from .views import activate_key, registration_status

app_name = "registration"

urlpatterns = [
    path(
        "",
        registration_status,
        name="status",
    ),
    path(
        "activate/",
        activate_key,
        name="activate",
    ),
]