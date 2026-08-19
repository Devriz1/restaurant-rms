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
     path(
        "adjustment/",
        views.stock_adjustment,
        name="stock-adjustment",
    ),
     path(
    "low-stock/",
    views.LowStockListView.as_view(),
    name="low-stock",
),
     path(
    "reports/movement/",
    views.StockMovementReportView.as_view(),
    name="movement-report",
),
     path(
    "reports/",
    views.stock_reports,
    name="reports",
),

]