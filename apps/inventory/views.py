from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import F
from .models import (
    Ingredient,
    InventoryCategory,
    Supplier,
    Unit,
)


@login_required
def dashboard(request):

    context = {

        "ingredient_count": Ingredient.objects.count(),

        "category_count": InventoryCategory.objects.count(),

        "supplier_count": Supplier.objects.count(),

        "unit_count": Unit.objects.count(),

        "low_stock": Ingredient.objects.filter(
    current_stock__lte=F("minimum_stock")
).count(),

    }

    return render(
        request,
        "inventory/dashboard.html",
        context,
    )


@login_required
def ingredient_list(request):

    return render(
        request,
        "inventory/ingredient_list.html",
        {
            "ingredients": Ingredient.objects.all(),
        },
    )


@login_required
def category_list(request):

    return render(
        request,
        "inventory/category_list.html",
        {
            "categories": InventoryCategory.objects.all(),
        },
    )


@login_required
def unit_list(request):

    return render(
        request,
        "inventory/unit_list.html",
        {
            "units": Unit.objects.all(),
        },
    )


@login_required
def supplier_list(request):

    return render(
        request,
        "inventory/supplier_list.html",
        {
            "suppliers": Supplier.objects.all(),
        },
    )