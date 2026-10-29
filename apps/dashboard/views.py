from decimal import Decimal

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.core.exceptions import PermissionDenied
from django.db.models import Sum

from apps.tables.models import RestaurantTable
from apps.orders.models import GuestOrder
from apps.billing.models import Bill


# A guest counts as active while their order is still being served.
ACTIVE_ORDER_STATUSES = ["open", "preparing", "ready", "served"]

# A bill is pending until it is settled in full.
PENDING_BILL_STATUSES = ["unpaid", "partially_paid"]


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

        today = timezone.localdate()

        # ---------------- TABLES ----------------
        active_tables = RestaurantTable.objects.filter(
            is_active=True
        )

        occupied_table_ids = set(
            RestaurantTable.objects.filter(
                sessions__status="open",
                sessions__guest_orders__status__in=ACTIVE_ORDER_STATUSES,
                sessions__guest_orders__items__isnull=False,
            )
            .values_list("id", flat=True)
            .distinct()
        )

        total_tables = active_tables.count()

        occupied_tables = len(occupied_table_ids)

        context["total_tables"] = total_tables

        context["occupied_tables"] = occupied_tables

        context["available_tables"] = total_tables - occupied_tables

        # ---------------- ACTIVE GUESTS ----------------
        context["active_guests"] = GuestOrder.objects.filter(
            status__in=ACTIVE_ORDER_STATUSES,
            items__isnull=False,
        ).count()

        # ---------------- PENDING BILLS ----------------
        context["pending_bills"] = Bill.objects.filter(
            status__in=PENDING_BILL_STATUSES,
        ).count()

        # ---------------- TODAY'S REVENUE ----------------
        # Same basis as the reports app: fully paid bills raised today.
        today_revenue = Bill.objects.filter(
            created_at__date=today,
            status="paid",
        ).aggregate(
            total=Sum("grand_total")
        )["total"] or Decimal("0.00")

        context["today_revenue"] = today_revenue

        # ---------------- TOTAL REVENUE ----------------
        # Cumulative revenue from all paid bills.
        total_revenue = Bill.objects.filter(
            status="paid",
        ).aggregate(
            total=Sum("grand_total")
        )["total"] or Decimal("0.00")

        context["total_revenue"] = total_revenue

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