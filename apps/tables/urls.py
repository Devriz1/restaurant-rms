from django.urls import path

from .views import (
    DiningAreaListView,
    DiningAreaCreateView,
    DiningAreaUpdateView,
    DiningAreaDeleteView,
)

app_name = "tables"

urlpatterns = [
    path("areas/", DiningAreaListView.as_view(), name="area-list"),
    path("areas/add/", DiningAreaCreateView.as_view(), name="area-add"),
    path("areas/<int:pk>/edit/", DiningAreaUpdateView.as_view(), name="area-edit"),
    path("areas/<int:pk>/delete/", DiningAreaDeleteView.as_view(), name="area-delete"),
]