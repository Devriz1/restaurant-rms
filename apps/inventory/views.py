from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from django.db import transaction
from django.db.models import Q,F

from django.shortcuts import (
    render,
    redirect,
)

from django.urls import reverse_lazy

from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)

from .models import (
    Unit,
    Supplier,
    Category,
    Material,
)

from apps.stock.models import StockLedger

from .forms import (
    UnitForm,
    SupplierForm,
    CategoryForm,
    MaterialForm,
)

@login_required
def dashboard(request):

    total_materials = Material.objects.count()

    total_suppliers = Supplier.objects.count()

    low_stock = Material.objects.filter(
        current_stock__gt=0,
        current_stock__lte=F("minimum_stock"),
    ).count()

    out_of_stock = Material.objects.filter(
        current_stock=0,
    ).count()

    low_stock_items = Material.objects.filter(
        current_stock__lte=F("minimum_stock"),
    ).select_related("unit", "category")[:10]

    total_units = Unit.objects.count()

    active_units = Unit.objects.filter(is_active=True).count()

    weight_units = Unit.objects.filter(unit_type="WEIGHT").count()

    volume_units = Unit.objects.filter(unit_type="VOLUME").count()

    recent_activities = StockLedger.objects.select_related(
        "material"
    ).order_by("-created_at")[:10]

    context = {

        "total_materials": total_materials,

        "total_suppliers": total_suppliers,

        "low_stock": low_stock,

        "out_of_stock": out_of_stock,

        "low_stock_items": low_stock_items,

        "total_units": total_units,

        "active_units": active_units,

        "weight_units": weight_units,

        "volume_units": volume_units,

        "recent_activities": recent_activities,

    }

    return render(

        request,

        "inventory/dashboard.html",

        context,

    )



class UnitListView(ListView):

    model = Unit

    template_name = "inventory/units/unit_list.html"

    context_object_name = "units"

    paginate_by = 10
    def get_queryset(self):

        queryset = Unit.objects.all()

        q = self.request.GET.get("q")

        unit_type = self.request.GET.get("type")

        if q:

            queryset = queryset.filter(

                Q(code__icontains=q) |

                Q(name__icontains=q) |

                Q(symbol__icontains=q)

            )

        if unit_type:

            queryset = queryset.filter(

                unit_type=unit_type

            )

        return queryset

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["total_units"] = Unit.objects.count()

        context["active_units"] = Unit.objects.filter(
            is_active=True
        ).count()

        context["weight_units"] = Unit.objects.filter(
            unit_type="WEIGHT"
        ).count()

        context["volume_units"] = Unit.objects.filter(
            unit_type="VOLUME"
        ).count()

        return context


class UnitCreateView(CreateView):

    model = Unit

    form_class = UnitForm

    template_name = "inventory/units/unit_form.html"

    success_url = reverse_lazy("inventory:unit-list")

    def form_valid(self, form):

        messages.success(

            self.request,

            "Unit created successfully."

        )

        return super().form_valid(form)

class UnitUpdateView(UpdateView):

    model = Unit

    form_class = UnitForm

    template_name = "inventory/units/unit_form.html"

    success_url = reverse_lazy("inventory:unit-list")

    def form_valid(self, form):

        messages.success(

            self.request,

            "Unit updated successfully."

        )

        return super().form_valid(form)
    
class UnitDeleteView(DeleteView):

    model = Unit

    template_name = "inventory/units/unit_confirm_delete.html"

    success_url = reverse_lazy("inventory:unit-list")

    def delete(self, request, *args, **kwargs):

        messages.success(

            request,

            "Unit deleted successfully."

        )

        return super().delete(request, *args, **kwargs)

# ==========================================================
# SUPPLIERS
# ==========================================================

class SupplierListView(ListView):

    model = Supplier

    template_name = "inventory/suppliers/supplier_list.html"

    context_object_name = "suppliers"

    paginate_by = 10

    def get_queryset(self):

        queryset = Supplier.objects.all()

        q = self.request.GET.get("q")

        if q:

            queryset = queryset.filter(

                Q(code__icontains=q) |

                Q(name__icontains=q) |

                Q(contact_person__icontains=q) |

                Q(phone__icontains=q)

            )

        return queryset

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["total_suppliers"] = Supplier.objects.count()

        context["active_suppliers"] = Supplier.objects.filter(
            is_active=True
        ).count()

        context["inactive_suppliers"] = Supplier.objects.filter(
            is_active=False
        ).count()

        return context


class SupplierCreateView(CreateView):

    model = Supplier

    form_class = SupplierForm

    template_name = "inventory/suppliers/supplier_form.html"

    success_url = reverse_lazy("inventory:supplier-list")

    def form_valid(self, form):

        messages.success(

            self.request,

            "Supplier created successfully."

        )

        return super().form_valid(form)


class SupplierUpdateView(UpdateView):

    model = Supplier

    form_class = SupplierForm

    template_name = "inventory/suppliers/supplier_form.html"

    success_url = reverse_lazy("inventory:supplier-list")

    def form_valid(self, form):

        messages.success(

            self.request,

            "Supplier updated successfully."

        )

        return super().form_valid(form)


class SupplierDeleteView(DeleteView):

    model = Supplier

    template_name = "inventory/suppliers/supplier_confirm_delete.html"

    success_url = reverse_lazy("inventory:supplier-list")

    def form_valid(self, form):

        messages.success(

            self.request,

            "Supplier deleted successfully."

        )

        return super().form_valid(form)



# ==========================================================
# CATEGORY
# ==========================================================

class CategoryListView(ListView):

    model = Category

    template_name = "inventory/categories/category_list.html"

    context_object_name = "categories"

    paginate_by = 10

    def get_queryset(self):

        queryset = Category.objects.all()

        q = self.request.GET.get("q")

        if q:

            queryset = queryset.filter(

                Q(code__icontains=q) |

                Q(name__icontains=q)

            )

        return queryset

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["total_categories"] = Category.objects.count()

        context["active_categories"] = Category.objects.filter(
            is_active=True
        ).count()

        context["inactive_categories"] = Category.objects.filter(
            is_active=False
        ).count()

        return context


class CategoryCreateView(CreateView):

    model = Category

    form_class = CategoryForm

    template_name = "inventory/categories/category_form.html"

    success_url = reverse_lazy("inventory:category-list")

    def form_valid(self, form):

        messages.success(
            self.request,
            "Category created successfully."
        )

        return super().form_valid(form)


class CategoryUpdateView(UpdateView):

    model = Category

    form_class = CategoryForm

    template_name = "inventory/categories/category_form.html"

    success_url = reverse_lazy("inventory:category-list")

    def form_valid(self, form):

        messages.success(
            self.request,
            "Category updated successfully."
        )

        return super().form_valid(form)


class CategoryDeleteView(DeleteView):

    model = Category

    template_name = "inventory/categories/category_confirm_delete.html"

    success_url = reverse_lazy("inventory:category-list")

    def form_valid(self, form):

        messages.success(
            self.request,
            "Category deleted successfully."
        )

        return super().form_valid(form)



# ==========================================================
# MATERIALS
# ==========================================================

class MaterialListView(ListView):

    model = Material

    template_name = "inventory/materials/material_list.html"

    context_object_name = "materials"

    paginate_by = 15

    def get_queryset(self):

        queryset = Material.objects.select_related(
            "category",
            "supplier",
            "unit",
        )

        q = self.request.GET.get("q")
        category = self.request.GET.get("category")
        supplier = self.request.GET.get("supplier")

        if q:
            queryset = queryset.filter(
                Q(code__icontains=q) |
                Q(name__icontains=q) |
                Q(barcode__icontains=q)
            )

        if category:
            queryset = queryset.filter(
                category_id=category
            )

        if supplier:
            queryset = queryset.filter(
                supplier_id=supplier
            )

        return queryset.order_by("name")

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["categories"] = Category.objects.filter(
            is_active=True
        )

        context["suppliers"] = Supplier.objects.filter(
            is_active=True
        )

        context["total_materials"] = Material.objects.count()

        context["active_materials"] = Material.objects.filter(
            is_active=True
        ).count()

        context["low_stock"] = Material.objects.filter(
            current_stock__lte=F("minimum_stock")
        ).count()

        context["out_of_stock"] = Material.objects.filter(
            current_stock=0
        ).count()

        return context
    

class MaterialCreateView(CreateView):

    model = Material

    form_class = MaterialForm

    template_name = "inventory/materials/material_form.html"

    success_url = reverse_lazy(

        "inventory:material-list"

    )

    def form_valid(self, form):

        messages.success(

            self.request,

            "Material created successfully."

        )

        return super().form_valid(form)


class MaterialUpdateView(UpdateView):

    model = Material

    form_class = MaterialForm

    template_name = "inventory/materials/material_form.html"

    success_url = reverse_lazy(

        "inventory:material-list"

    )

    def form_valid(self, form):

        messages.success(

            self.request,

            "Material updated successfully."

        )

        return super().form_valid(form)


class MaterialDeleteView(DeleteView):

    model = Material

    template_name = "inventory/materials/material_confirm_delete.html"

    success_url = reverse_lazy(

        "inventory:material-list"

    )

    def form_valid(self, form):

        messages.success(

            self.request,

            "Material deleted successfully."

        )

        return super().form_valid(form)


