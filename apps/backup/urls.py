from django.urls import path

from . import views

app_name = "backup"

urlpatterns = [

    path(
        "",
        views.dashboard,
        name="dashboard",
    ),

    path(
        "create/",
        views.create_backup,
        name="create",
    ),

    path(
        "download/<str:filename>/",
        views.download_backup,
        name="download",
    ),

    path(
        "delete/<str:filename>/",
        views.delete_backup,
        name="delete",
    ),
    path(
    "restore/<str:filename>/",
    views.restore_backup,
    name="restore",
),

]