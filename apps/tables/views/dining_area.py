from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from ..forms import DiningAreaForm
from ..models import DiningArea


class DiningAreaListView(LoginRequiredMixin, ListView):
    model = DiningArea
    template_name = "tables/dining_area_list.html"
    context_object_name = "areas"


class DiningAreaCreateView(LoginRequiredMixin, CreateView):
    model = DiningArea
    form_class = DiningAreaForm
    template_name = "tables/dining_area_form.html"
    success_url = reverse_lazy("tables:area-list")


class DiningAreaUpdateView(LoginRequiredMixin, UpdateView):
    model = DiningArea
    form_class = DiningAreaForm
    template_name = "tables/dining_area_form.html"
    success_url = reverse_lazy("tables:area-list")


class DiningAreaDeleteView(LoginRequiredMixin, DeleteView):
    model = DiningArea
    template_name = "tables/dining_area_confirm_delete.html"
    success_url = reverse_lazy("tables:area-list")