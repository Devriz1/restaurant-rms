from django.urls import path
from . import views

app_name = "stock"

urlpatterns = [

    path(
        "",
        views.dashboard,
        name="dashboard",
    ),
    path(
    "ledger/",
    views.StockLedgerListView.as_view(),
    name="ledger",
),
    path(
    "current-stock/",
    views.CurrentStockListView.as_view(),
    name="current-stock",
),
    path(
    "material/<int:pk>/",
    views.MaterialDetailView.as_view(),
    name="material-detail",
),

]