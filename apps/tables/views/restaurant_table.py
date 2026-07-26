from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView

from ..forms import RestaurantTableForm
from ..models import RestaurantTable


class RestaurantTableListView(LoginRequiredMixin, ListView):
    model = RestaurantTable
    template_name = "tables/table_list.html"
    context_object_name = "tables"

    def get_queryset(self):
        return (
            RestaurantTable.objects
            .select_related("area")
            .order_by("area", "table_number")
        )


class RestaurantTableCreateView(LoginRequiredMixin, CreateView):
    model = RestaurantTable
    form_class = RestaurantTableForm
    template_name = "tables/table_form.html"
    success_url = reverse_lazy("tables:table-list")