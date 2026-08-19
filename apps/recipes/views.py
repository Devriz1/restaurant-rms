from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView

from .forms import RecipeForm, RecipeIngredientFormSet
from .models import Recipe
# ==========================================================
# RECIPE LIST
# ==========================================================

class RecipeListView(LoginRequiredMixin, ListView):

    model = Recipe

    template_name = "recipes/recipe_list.html"

    context_object_name = "recipes"

    paginate_by = 20

    def get_queryset(self):

        queryset = (
            Recipe.objects
            .select_related(
                "menu_item",
                "menu_item__category",
            )
            .prefetch_related(
                "ingredients",
                "ingredients__material",
                "ingredients__material__unit",
            )
            .order_by(
                "menu_item__category__display_order",
                "menu_item__name",
            )
        )

        search = self.request.GET.get("q", "").strip()

        if search:

            queryset = queryset.filter(
                menu_item__name__icontains=search
            )

        return queryset


# ==========================================================
# RECIPE CREATE
# ==========================================================

@login_required
@transaction.atomic
def recipe_create(request):

    if request.method == "POST":

        form = RecipeForm(request.POST)

        if form.is_valid():

            recipe = form.save()

            formset = RecipeIngredientFormSet(
                request.POST,
                instance=recipe,
            )

            if formset.is_valid():

                formset.save()

                messages.success(
                    request,
                    "Recipe created successfully.",
                )

                return redirect(
                    "recipes:recipe-detail",
                    pk=recipe.pk,
                )

            recipe.delete()

        else:

            formset = RecipeIngredientFormSet(
                request.POST,
            )

    else:

        form = RecipeForm()

        formset = RecipeIngredientFormSet()

    return render(
        request,
        "recipes/recipe_form.html",
        {
            "form": form,
            "formset": formset,
            "title": "New Recipe",
        },
    )


# ==========================================================
# RECIPE UPDATE
# ==========================================================

@login_required
@transaction.atomic
def recipe_update(request, pk):

    recipe = get_object_or_404(
        Recipe,
        pk=pk,
    )

    if request.method == "POST":

        form = RecipeForm(
            request.POST,
            instance=recipe,
        )

        formset = RecipeIngredientFormSet(
            request.POST,
            instance=recipe,
        )

        if form.is_valid() and formset.is_valid():

            form.save()

            formset.save()

            messages.success(
                request,
                "Recipe updated successfully.",
            )

            return redirect(
                "recipes:recipe-detail",
                pk=recipe.pk,
            )

    else:

        form = RecipeForm(
            instance=recipe,
        )

        formset = RecipeIngredientFormSet(
            instance=recipe,
        )

    return render(
        request,
        "recipes/recipe_form.html",
        {
            "form": form,
            "formset": formset,
            "recipe": recipe,
            "title": "Edit Recipe",
        },
    )


# ==========================================================
# RECIPE DETAIL
# ==========================================================

class RecipeDetailView(
    LoginRequiredMixin,
    DetailView,
):

    model = Recipe

    template_name = "recipes/recipe_detail.html"

    context_object_name = "recipe"

    def get_queryset(self):

        return (
            Recipe.objects
            .select_related(
                "menu_item",
                "menu_item__category",
            )
            .prefetch_related(
                "ingredients",
                "ingredients__material",
                "ingredients__material__unit",
            )
        )


# ==========================================================
# RECIPE DELETE
# ==========================================================

class RecipeDeleteView(
    LoginRequiredMixin,
    DeleteView,
):

    model = Recipe

    template_name = "recipes/recipe_confirm_delete.html"

    success_url = reverse_lazy(
    "recipes:recipe-list"
)

    def form_valid(self, form):

        messages.success(
            self.request,
            "Recipe deleted successfully.",
        )

        return super().form_valid(form)