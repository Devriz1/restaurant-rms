from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.core.exceptions import PermissionDenied

from apps.tables.models import RestaurantTable
from apps.orders.models import GuestOrder
from apps.billing.models import Bill


@method_decorator(never_cache, name="dispatch")
class DashboardView(LoginRequiredMixin, TemplateView):

    template_name = "dashboard/index.html"

    login_url = "/accounts/login/"
    redirect_field_name = "next"

    def dispatch(self, request, *args, **kwargs):

        # Let LoginRequiredMixin redirect anonymous users first
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        print("=" * 60)
        print("Dashboard Access")
        print("User:", request.user.username)
        print("ID:", request.user.id)
        print("Authenticated:", request.user.is_authenticated)
        print("Superuser:", request.user.is_superuser)
        print("Role:", request.user.role)
        print("Session:", request.session.session_key)
        print("=" * 60)

        # Permission check
        if not request.user.is_superuser:

            has_permission = request.user.permissions_list.filter(
                permission__code="dashboard.view"
            ).exists()

            print("Dashboard Permission:", has_permission)

            if not has_permission:
                raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

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
            status="status"
        ).count()

        context["recent_orders"] = (
            GuestOrder.objects.select_related(
                "session",
                "session__table",
            )
            .order_by("-created_at")[:8]
        )

        context["recent_bills"] = (
            Bill.objects.select_related(
                "guest_order",
                "session",
                "session__table",
            )
            .order_by("-created_at")[:8]
        )

        return context