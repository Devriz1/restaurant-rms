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
        "ingredients/",
        views.ingredient_list,
        name="ingredient-list",
    ),

    path(
        "categories/",
        views.category_list,
        name="category-list",
    ),

    path(
        "units/",
        views.unit_list,
        name="unit-list",
    ),

    path(
        "suppliers/",
        views.supplier_list,
        name="supplier-list",
    ),

]