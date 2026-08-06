from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, DeleteView

from .models import Purchase
from .forms import PurchaseForm, PurchaseItemFormSet


# ==========================================================
# PURCHASE LIST
# ==========================================================

class PurchaseListView(LoginRequiredMixin, ListView):

    model = Purchase

    template_name = "inventory/purchases/purchase_list.html"

    context_object_name = "purchases"

    paginate_by = 15

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["total_purchases"] = Purchase.objects.count()

        return context


# ==========================================================
# PURCHASE CREATE
# ==========================================================

@login_required
def purchase_create(request):

    if request.method == "POST":

        form = PurchaseForm(request.POST)

        formset = PurchaseItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():

            purchase = form.save()

            items = formset.save(commit=False)

            subtotal = Decimal("0.00")

            for item in items:

                item.purchase = purchase

                item.save()

                subtotal += item.line_total

            purchase.subtotal = subtotal

            purchase.grand_total = (
                subtotal
                - purchase.discount
                + purchase.other_charges
            )

            purchase.save()

            messages.success(
                request,
                "Purchase created successfully.",
            )

            return redirect(
                "purchase:purchase-detail",
                pk=purchase.pk,
            )

    else:

        form = PurchaseForm()

        formset = PurchaseItemFormSet()

    return render(
        request,
        "inventory/purchases/purchase_form.html",
        {
            "form": form,
            "formset": formset,
            "title": "New Purchase",
        },
    )


# ==========================================================
# PURCHASE UPDATE
# ==========================================================

@login_required
def purchase_update(request, pk):

    purchase = get_object_or_404(
        Purchase,
        pk=pk,
    )

    if request.method == "POST":

        form = PurchaseForm(
            request.POST,
            instance=purchase,
        )

        formset = PurchaseItemFormSet(
            request.POST,
            instance=purchase,
        )

        if form.is_valid() and formset.is_valid():

            purchase = form.save()

            items = formset.save(commit=False)

            for obj in formset.deleted_objects:

                obj.delete()

            subtotal = Decimal("0.00")

            for item in items:

                item.purchase = purchase

                item.save()

            for item in purchase.items.all():

                subtotal += item.line_total

            purchase.subtotal = subtotal

            purchase.grand_total = (
                subtotal
                - purchase.discount
                + purchase.other_charges
            )

            purchase.save()

            messages.success(
                request,
                "Purchase updated successfully.",
            )

            return redirect(
                "purchase:purchase-detail",
                pk=purchase.pk,
            )

    else:

        form = PurchaseForm(
            instance=purchase,
        )

        formset = PurchaseItemFormSet(
            instance=purchase,
        )

    return render(
        request,
        "inventory/purchases/purchase_form.html",
        {
            "form": form,
            "formset": formset,
            "purchase": purchase,
            "title": "Edit Purchase",
        },
    )


# ==========================================================
# PURCHASE DETAIL
# ==========================================================

class PurchaseDetailView(LoginRequiredMixin, DetailView):

    model = Purchase

    template_name = "inventory/purchases/purchase_detail.html"

    context_object_name = "purchase"


# ==========================================================
# PURCHASE DELETE
# ==========================================================

class PurchaseDeleteView(LoginRequiredMixin, DeleteView):

    model = Purchase

    template_name = "inventory/purchases/purchase_confirm_delete.html"

    success_url = reverse_lazy(
        "purchase:purchase-list"
    )

    def delete(self, request, *args, **kwargs):

        messages.success(
            request,
            "Purchase deleted successfully.",
        )

        return super().delete(
            request,
            *args,
            **kwargs,
        )