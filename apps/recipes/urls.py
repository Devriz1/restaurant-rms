from django.urls import path

from . import views


app_name = "recipes"


urlpatterns = [

    path(
        "",
        views.RecipeListView.as_view(),
        name="recipe-list",
    ),

    path(
        "add/",
        views.recipe_create,
        name="recipe-add",
    ),

    path(
        "<int:pk>/",
        views.RecipeDetailView.as_view(),
        name="recipe-detail",
    ),

    path(
        "<int:pk>/edit/",
        views.recipe_update,
        name="recipe-edit",
    ),

    path(
        "<int:pk>/delete/",
        views.RecipeDeleteView.as_view(),
        name="recipe-delete",
    ),

]