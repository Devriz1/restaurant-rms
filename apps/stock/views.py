from datetime import date

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from django.db import transaction
from django.db.models import Count, F, Q, Sum

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView,DetailView

from apps.inventory.models import Material
from apps.purchase.models import Purchase

from .models import StockLedger, StockAdjustment
from .forms import StockAdjustmentForm
from .services import adjust_stock

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
    
# ==========================================================
# STOCK ADJUSTMENT
# ==========================================================

@login_required
@transaction.atomic
def stock_adjustment(request):

    if request.method == "POST":

        form = StockAdjustmentForm(request.POST)

        if form.is_valid():

            adjustment = form.save(commit=False)

            try:

                # ==========================================
                # UPDATE STOCK
                # ==========================================

                adjust_stock(
                    material=adjustment.material,
                    quantity=adjustment.quantity,
                    adjustment_type=adjustment.adjustment_type,
                    reason=adjustment.reason,
                    remarks=adjustment.remarks,
                )

                # ==========================================
                # SAVE ADJUSTMENT RECORD
                # ==========================================

                adjustment.save()

                messages.success(
                    request,
                    "Stock adjustment completed successfully.",
                )

                return redirect(
                    "stock:current-stock"
                )

            except ValueError as error:

                form.add_error(
                    "quantity",
                    str(error),
                )

    else:

        form = StockAdjustmentForm()

    return render(
        request,
        "stock/adjustment_form.html",
        {
            "form": form,
        },
    )
    
    
    
# ==========================================================
# LOW STOCK
# ==========================================================

class LowStockListView(LoginRequiredMixin, ListView):

    model = Material

    template_name = "stock/low_stock.html"

    context_object_name = "materials"

    paginate_by = 20

    def get_queryset(self):

        return (
            Material.objects
            .select_related(
                "category",
                "supplier",
                "unit",
            )
            .filter(
                current_stock__lte=F("minimum_stock"),
                current_stock__gt=0,
                is_active=True,
            )
            .order_by("current_stock", "name")
        )

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["low_stock_count"] = Material.objects.filter(
            current_stock__lte=F("minimum_stock"),
            current_stock__gt=0,
            is_active=True,
        ).count()

        context["out_of_stock_count"] = Material.objects.filter(
            current_stock=0,
            is_active=True,
        ).count()

        return context
    
# ==========================================================
# STOCK MOVEMENT REPORT
# ==========================================================

class StockMovementReportView(LoginRequiredMixin, ListView):

    model = StockLedger

    template_name = "stock/reports/movement_report.html"

    context_object_name = "entries"

    paginate_by = 30

    def get_queryset(self):

        queryset = (
            StockLedger.objects
            .select_related("material")
            .order_by("-created_at", "-id")
        )

        # ==============================================
        # DATE FILTER
        # ==============================================

        date_from = self.request.GET.get("date_from")

        date_to = self.request.GET.get("date_to")

        if date_from:

            queryset = queryset.filter(
                created_at__date__gte=date_from
            )

        if date_to:

            queryset = queryset.filter(
                created_at__date__lte=date_to
            )

        # ==============================================
        # MATERIAL FILTER
        # ==============================================

        material = self.request.GET.get("material")

        if material:

            queryset = queryset.filter(
                material_id=material
            )

        # ==============================================
        # MOVEMENT TYPE FILTER
        # ==============================================

        movement_type = self.request.GET.get(
            "movement_type"
        )

        if movement_type:

            queryset = queryset.filter(
                movement_type=movement_type
            )

        # ==============================================
        # SEARCH
        # ==============================================

        search = self.request.GET.get("q")

        if search:

            queryset = queryset.filter(
                Q(
                    material__name__icontains=search
                )
                |
                Q(
                    material__code__icontains=search
                )
                |
                Q(
                    reference_number__icontains=search
                )
            )

        return queryset

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        queryset = self.get_queryset()

        # ==============================================
        # TOTALS
        # ==============================================

        totals = queryset.aggregate(
            total_in=Sum("quantity_in"),
            total_out=Sum("quantity_out"),
        )

        context["total_in"] = (
            totals["total_in"] or 0
        )

        context["total_out"] = (
            totals["total_out"] or 0
        )

        # ==============================================
        # MATERIALS
        # ==============================================

        context["materials"] = (
            Material.objects
            .filter(is_active=True)
            .order_by("name")
        )

        # ==============================================
        # MOVEMENT TYPES
        # ==============================================

        context["movement_types"] = (
            StockLedger.MovementType.choices
        )

        return context
    
    
# ==========================================================
# STOCK REPORTS DASHBOARD
# ==========================================================

@login_required
def stock_reports(request):

    total_materials = Material.objects.filter(
        is_active=True
    ).count()

    low_stock = Material.objects.filter(
        current_stock__lte=F("minimum_stock"),
        current_stock__gt=0,
        is_active=True,
    ).count()

    out_of_stock = Material.objects.filter(
        current_stock=0,
        is_active=True,
    ).count()

    total_ledger_entries = StockLedger.objects.count()

    purchase_movements = StockLedger.objects.filter(
        movement_type="PURCHASE"
    ).count()

    adjustment_movements = StockLedger.objects.filter(
        movement_type="ADJUSTMENT"
    ).count()

    context = {

        "total_materials": total_materials,

        "low_stock": low_stock,

        "out_of_stock": out_of_stock,

        "total_ledger_entries": total_ledger_entries,

        "purchase_movements": purchase_movements,

        "adjustment_movements": adjustment_movements,

    }

    return render(
        request,
        "stock/reports/dashboard.html",
        context,
    )