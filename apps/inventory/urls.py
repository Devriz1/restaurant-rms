from django.urls import path

from . import views


app_name = "inventory"


urlpatterns = [

    path(
        "",
        views.dashboard,
        name="dashboard",
    ),

    path(
        "units/",
        views.UnitListView.as_view(),
        name="unit-list",
    ),

    path(
        "units/add/",
        views.UnitCreateView.as_view(),
        name="unit-add",
    ),

    path(
        "units/<int:pk>/edit/",
        views.UnitUpdateView.as_view(),
        name="unit-edit",
    ),

    path(
        "units/<int:pk>/delete/",
        views.UnitDeleteView.as_view(),
        name="unit-delete",
    ),
    path(
    "suppliers/",
    views.SupplierListView.as_view(),
    name="supplier-list",
),

path(
    "suppliers/add/",
    views.SupplierCreateView.as_view(),
    name="supplier-add",
),

path(
    "suppliers/<int:pk>/edit/",
    views.SupplierUpdateView.as_view(),
    name="supplier-edit",
),

path(
    "suppliers/<int:pk>/delete/",
    views.SupplierDeleteView.as_view(),
    name="supplier-delete",
),
path(
    "categories/",
    views.CategoryListView.as_view(),
    name="category-list",
),

path(
    "categories/add/",
    views.CategoryCreateView.as_view(),
    name="category-add",
),

path(
    "categories/<int:pk>/edit/",
    views.CategoryUpdateView.as_view(),
    name="category-edit",
),

path(
    "categories/<int:pk>/delete/",
    views.CategoryDeleteView.as_view(),
    name="category-delete",
),
# ==========================================================
# MATERIALS
# ==========================================================

path(
    "materials/",
    views.MaterialListView.as_view(),
    name="material-list",
),

path(
    "materials/add/",
    views.MaterialCreateView.as_view(),
    name="material-add",
),

path(
    "materials/<int:pk>/edit/",
    views.MaterialUpdateView.as_view(),
    name="material-edit",
),

path(
    "materials/<int:pk>/delete/",
    views.MaterialDeleteView.as_view(),
    name="material-delete",
),
]