from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.dashboard.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("restaurant/", include("apps.restaurant.urls")),
    path("tables/", include("apps.tables.urls")),
    path("menu/", include("apps.menu.urls")),
    path("orders/", include("apps.orders.urls")),
    path("billing/",include("apps.billing.urls"),),
    path("reports/",include("apps.reports.urls"),),
    path("settings/",include("apps.settings.urls"),),
    path("users/",include("apps.accounts.urls"),),
    path("backup/",include("apps.backup.urls"),),
    path("inventory/",include("apps.inventory.urls"),),
    path("",include("pwa.urls"),),
    path("purchase/",include("apps.purchase.urls"),),
    path("stock/",include("apps.stock.urls"),),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)