from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
)

from .models import MenuCategory,MenuItem
from .forms import MenuCategoryForm,MenuItemForm


class MenuCategoryListView(ListView):
    model = MenuCategory
    template_name = "menu/category_list.html"
    context_object_name = "categories"


class MenuCategoryCreateView(CreateView):
    model = MenuCategory
    form_class = MenuCategoryForm
    template_name = "menu/category_form.html"
    success_url = reverse_lazy("menu:category-list")

    def form_valid(self, form):
        messages.success(self.request, "Category added successfully.")
        return super().form_valid(form)


class MenuCategoryUpdateView(UpdateView):
    model = MenuCategory
    form_class = MenuCategoryForm
    template_name = "menu/category_form.html"
    success_url = reverse_lazy("menu:category-list")

    def form_valid(self, form):
        messages.success(self.request, "Category updated successfully.")
        return super().form_valid(form)


class MenuCategoryDeleteView(DeleteView):
    model = MenuCategory
    template_name = "menu/category_confirm_delete.html"
    success_url = reverse_lazy("menu:category-list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Category deleted successfully.")
        return super().delete(request, *args, **kwargs)
    
class MenuItemListView(ListView):
    model = MenuItem
    template_name = "menu/item_list.html"
    context_object_name = "items"


class MenuItemCreateView(CreateView):
    model = MenuItem
    form_class = MenuItemForm
    template_name = "menu/item_form.html"
    success_url = reverse_lazy("menu:item-list")

    def form_valid(self, form):
        messages.success(self.request, "Menu item added successfully.")
        return super().form_valid(form)


class MenuItemUpdateView(UpdateView):
    model = MenuItem
    form_class = MenuItemForm
    template_name = "menu/item_form.html"
    success_url = reverse_lazy("menu:item-list")

    def form_valid(self, form):
        messages.success(self.request, "Menu item updated successfully.")
        return super().form_valid(form)


class MenuItemDeleteView(DeleteView):
    model = MenuItem
    template_name = "menu/item_confirm_delete.html"
    success_url = reverse_lazy("menu:item-list")

    def form_valid(self, form):
        messages.success(self.request, "Menu item deleted successfully.")
        return super().form_valid(form)