from django.urls import path

from .views import (
    DiningAreaListView,
    DiningAreaCreateView,
    DiningAreaUpdateView,
)

app_name = "tables"

urlpatterns = [
    path("areas/", DiningAreaListView.as_view(), name="area-list"),
    path("areas/add/", DiningAreaCreateView.as_view(), name="area-add"),
    path("areas/<int:pk>/edit/", DiningAreaUpdateView.as_view(), name="area-edit"),
]