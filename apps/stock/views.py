from datetime import date
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Count
from django.db.models import F,Q
from apps.inventory.models import Material
from .models import StockLedger
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.purchase.models import Purchase
from django.views.generic import DetailView

@login_required
def dashboard(request):

    inventory_value = 0

    for material in Material.objects.all():

        inventory_value += (
            material.current_stock * material.cost_price
        )

    context = {

        "total_materials":
            Material.objects.count(),

        "low_stock":
            Material.objects.filter(
                current_stock__lte=F("minimum_stock")
            ).count(),

        "out_of_stock":
            Material.objects.filter(
                current_stock=0
            ).count(),

        "ledger_count":
            StockLedger.objects.count(),

        "inventory_value":
            inventory_value,

        "today_purchase":
            Purchase.objects.filter(
                purchase_date=date.today()
            ).count(),

        "recent_movements":
            StockLedger.objects.select_related(
                "material"
            ).order_by(
                "-created_at"
            )[:10],

        "low_stock_materials":
            Material.objects.filter(
                current_stock__lte=F("minimum_stock")
            ).select_related(
                "unit"
            )[:10],

    }

    return render(

        request,

        "stock/dashboard.html",

        context,

    )
    
    
class StockLedgerListView(LoginRequiredMixin, ListView):

    model = StockLedger

    template_name = "stock/ledger.html"

    context_object_name = "entries"

    paginate_by = 30

    def get_queryset(self):

        return (
            StockLedger.objects
            .select_related("material")
            .order_by("-created_at")
        )
        
class CurrentStockListView(LoginRequiredMixin, ListView):

    model = Material

    template_name = "stock/current_stock.html"

    context_object_name = "materials"

    paginate_by = 20

    def get_queryset(self):

        queryset = Material.objects.select_related(

            "category",

            "supplier",

            "unit",

    )

        search = self.request.GET.get("q")

        category = self.request.GET.get("category")

        supplier = self.request.GET.get("supplier")

        status = self.request.GET.get("status")

        if search:

            queryset = queryset.filter(

            Q(name__icontains=search)

            | Q(code__icontains=search)

            | Q(barcode__icontains=search)

        )

        if category:

            queryset = queryset.filter(

            category_id=category

        )

        if supplier:

            queryset = queryset.filter(

            supplier_id=supplier

        )

        if status == "low":

            queryset = queryset.filter(

            current_stock__lte=F("minimum_stock"),

            current_stock__gt=0,

        )

        elif status == "out":

            queryset = queryset.filter(

            current_stock=0,

        )

        elif status == "normal":

            queryset = queryset.filter(

            current_stock__gt=F("minimum_stock")

        )

        return queryset.order_by("name")
    
    
class MaterialDetailView(LoginRequiredMixin, DetailView):

    model = Material

    template_name = "stock/material_detail.html"

    context_object_name = "material"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        material = self.object

        context["ledger"] = (

            StockLedger.objects

            .filter(material=material)

            .order_by("-created_at")[:20]

        )

        context["purchase_items"] = (

            material.purchaseitem_set

            .select_related("purchase")

            .order_by("-purchase__purchase_date")[:10]

        )

        return context