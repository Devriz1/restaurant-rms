from django.urls import path
from . import views

app_name = "menu"

urlpatterns = [

    path(
        "categories/",
        views.MenuCategoryListView.as_view(),
        name="category-list",
    ),

    path(
        "categories/add/",
        views.MenuCategoryCreateView.as_view(),
        name="category-add",
    ),

    path(
        "categories/<int:pk>/edit/",
        views.MenuCategoryUpdateView.as_view(),
        name="category-edit",
    ),

    path(
        "categories/<int:pk>/delete/",
        views.MenuCategoryDeleteView.as_view(),
        name="category-delete",
    ),
    # Menu Items
path(
    "items/",
    views.MenuItemListView.as_view(),
    name="item-list",
),

path(
    "items/add/",
    views.MenuItemCreateView.as_view(),
    name="item-add",
),

path(
    "items/<int:pk>/edit/",
    views.MenuItemUpdateView.as_view(),
    name="item-edit",
),

path(
    "items/<int:pk>/delete/",
    views.MenuItemDeleteView.as_view(),
    name="item-delete",
),

]