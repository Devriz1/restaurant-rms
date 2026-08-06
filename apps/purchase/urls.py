from django.urls import path

from . import views

app_name = "purchase"

urlpatterns = [

    # ==========================================
    # PURCHASE LIST
    # ==========================================

    path(
        "",
        views.PurchaseListView.as_view(),
        name="purchase-list",
    ),

    # ==========================================
    # CREATE PURCHASE
    # ==========================================

    path(
        "add/",
        views.purchase_create,
        name="purchase-add",
    ),

    # ==========================================
    # PURCHASE DETAIL
    # ==========================================

    path(
        "<int:pk>/",
        views.PurchaseDetailView.as_view(),
        name="purchase-detail",
    ),

    # ==========================================
    # EDIT PURCHASE
    # ==========================================

    path(
        "<int:pk>/edit/",
        views.purchase_update,
        name="purchase-edit",
    ),

    # ==========================================
    # DELETE PURCHASE
    # ==========================================

    path(
        "<int:pk>/delete/",
        views.PurchaseDeleteView.as_view(),
        name="purchase-delete",
    ),

]