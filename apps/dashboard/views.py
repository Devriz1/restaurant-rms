from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from apps.tables.models import RestaurantTable
from apps.orders.models import GuestOrder
from apps.billing.models import Bill


class DashboardView(LoginRequiredMixin, TemplateView):

    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["total_tables"] = RestaurantTable.objects.count()

        context["occupied_tables"] = RestaurantTable.objects.filter(
            status="occupied"
        ).count()

        context["available_tables"] = RestaurantTable.objects.filter(
            status="available"
        ).count()

        context["active_guests"] = GuestOrder.objects.filter(
            status="open"
        ).count()

        context["pending_bills"] = Bill.objects.filter(
            status="unpaid"
        ).count()

        context["recent_orders"] = GuestOrder.objects.select_related(
            "session",
            "session__table",
        ).order_by("-created_at")[:8]

        context["recent_bills"] = Bill.objects.select_related(
            "guest_order",
            "session",
            "session__table",
        ).order_by("-created_at")[:8]

        return context