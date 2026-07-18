from django.urls import path

from .views import (
    DiningAreaListView,
    DiningAreaCreateView,
    DiningAreaUpdateView,
    DiningAreaDeleteView,
    RestaurantTableListView,
    RestaurantTableCreateView,
)

app_name = "tables"

urlpatterns = [
    path("areas/", DiningAreaListView.as_view(), name="area-list"),
    path("areas/add/", DiningAreaCreateView.as_view(), name="area-add"),
    path("areas/<int:pk>/edit/", DiningAreaUpdateView.as_view(), name="area-edit"),
    path("areas/<int:pk>/delete/", DiningAreaDeleteView.as_view(), name="area-delete"),
    path(
    "restaurant-tables/",
    RestaurantTableListView.as_view(),
    name="table-list",
),
path(
    "restaurant-tables/add/",
    RestaurantTableCreateView.as_view(),
    name="table-add",
),
]