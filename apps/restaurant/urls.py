from django.urls import path
from .views import RestaurantSettingsView

app_name = "restaurant"

urlpatterns = [
    path(
        "settings/",
        RestaurantSettingsView.as_view(),
        name="settings",
    ),
]