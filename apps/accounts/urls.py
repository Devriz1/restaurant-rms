from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import UserLoginView
from . import views

app_name = "accounts"


urlpatterns = [
    path("login/", UserLoginView.as_view(), name="login"),
    path(
    "logout/",
    views.user_logout,
    name="logout",
),
    path(
        "",
        views.user_list,
        name="user-list",
    ),

    path(
        "add/",
        views.user_add,
        name="user-add",
    ),

    path(
        "<int:pk>/edit/",
        views.user_edit,
        name="user-edit",
    ),

    path(
        "<int:pk>/delete/",
        views.user_delete,
        name="user-delete",
    ),

path(
    "logout/",
    LogoutView.as_view(),
    name="logout",
),
path(
    "<int:pk>/change-password/",
    views.change_user_password,
    name="user-change-password",
),
]