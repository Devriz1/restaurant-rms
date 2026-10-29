from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from apps.accounts.decorators import permission_required

from ..forms import RestaurantTableForm
from ..models import RestaurantTable


@method_decorator(login_required, name="dispatch")
@method_decorator(permission_required("tables.view"), name="dispatch")
class RestaurantTableListView(ListView):
    model = RestaurantTable
    template_name = "tables/table_list.html"
    context_object_name = "tables"

    def get_queryset(self):
        return (
            RestaurantTable.objects
            .select_related("area")
            .order_by("area", "table_number")
        )


@method_decorator(login_required, name="dispatch")
@method_decorator(permission_required("tables.add"), name="dispatch")
class RestaurantTableCreateView(CreateView):
    model = RestaurantTable
    form_class = RestaurantTableForm
    template_name = "tables/table_form.html"
    success_url = reverse_lazy("tables:table-list")


@method_decorator(login_required, name="dispatch")
@method_decorator(permission_required("tables.edit"), name="dispatch")
class RestaurantTableUpdateView(UpdateView):
    model = RestaurantTable
    form_class = RestaurantTableForm
    template_name = "tables/table_form.html"
    success_url = reverse_lazy("tables:table-list")


@method_decorator(login_required, name="dispatch")
@method_decorator(permission_required("tables.delete"), name="dispatch")
class RestaurantTableDeleteView(DeleteView):
    model = RestaurantTable
    template_name = "tables/table_confirm_delete.html"
    success_url = reverse_lazy("tables:table-list")