from django.urls import path
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from apps.accounts.decorators import permission_required
from . import views
from .models import Period
from .forms import PeriodForm


app_name = "billing"


@method_decorator(login_required, name="dispatch")
@method_decorator(permission_required("billing.view"), name="dispatch")
class PeriodListView(ListView):
    model = Period
    template_name = "billing/period_list.html"
    context_object_name = "periods"
    ordering = ["-start_date"]


@method_decorator(login_required, name="dispatch")
@method_decorator(permission_required("billing.add"), name="dispatch")
class PeriodCreateView(CreateView):
    model = Period
    form_class = PeriodForm
    template_name = "billing/period_form.html"
    success_url = reverse_lazy("billing:period-list")

    def form_valid(self, form):
        messages.success(self.request, "Financial period created successfully.")
        return super().form_valid(form)


@method_decorator(login_required, name="dispatch")
@method_decorator(permission_required("billing.edit"), name="dispatch")
class PeriodUpdateView(UpdateView):
    model = Period
    form_class = PeriodForm
    template_name = "billing/period_form.html"
    success_url = reverse_lazy("billing:period-list")

    def form_valid(self, form):
        messages.success(self.request, "Financial period updated successfully.")
        return super().form_valid(form)


@method_decorator(login_required, name="dispatch")
@method_decorator(permission_required("billing.delete"), name="dispatch")
class PeriodDeleteView(DeleteView):
    model = Period
    template_name = "billing/period_confirm_delete.html"
    success_url = reverse_lazy("billing:period-list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Financial period deleted successfully.")
        return super().delete(request, *args, **kwargs)


urlpatterns = [

    path(
        "",
        views.dashboard,
        name="dashboard",
    ),

    path(
        "guest/<int:guest_id>/",
        views.billing_screen,
        name="billing-screen",
    ),
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customers/<int:pk>/payment/', views.receive_customer_payment, name='receive_customer_payment'),

    # ---------------- Periods ----------------
    path(
        "periods/",
        PeriodListView.as_view(),
        name="period-list",
    ),
    path(
        "periods/add/",
        PeriodCreateView.as_view(),
        name="period-add",
    ),
    path(
        "periods/<int:pk>/edit/",
        PeriodUpdateView.as_view(),
        name="period-edit",
    ),
    path(
        "periods/<int:pk>/delete/",
        PeriodDeleteView.as_view(),
        name="period-delete",
    ),
    path(
        "periods/<int:pk>/activate/",
        views.activate_period,
        name="period-activate",
    ),

]