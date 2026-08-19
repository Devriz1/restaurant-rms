from django import forms
from django.forms import inlineformset_factory

from .models import Recipe, RecipeIngredient


# ==========================================================
# RECIPE FORM
# ==========================================================

class RecipeForm(forms.ModelForm):

    class Meta:

        model = Recipe

        fields = (
            "menu_item",
            "instructions",
            "preparation_notes",
            "is_active",
        )

        widgets = {

            "menu_item": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "instructions": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": (
                        "Enter preparation instructions..."
                    ),
                }
            ),

            "preparation_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": (
                        "Additional preparation notes..."
                    ),
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),

        }


# ==========================================================
# RECIPE INGREDIENT FORM
# ==========================================================

class RecipeIngredientForm(forms.ModelForm):

    class Meta:

        model = RecipeIngredient

        fields = (
            "material",
            "quantity",
            "wastage_percentage",
            "remarks",
        )

        widgets = {

            "material": forms.Select(
                attrs={
                    "class": "form-select ingredient-material",
                }
            ),

            "quantity": forms.NumberInput(
                attrs={
                    "class": "form-control ingredient-quantity",
                    "step": "0.001",
                    "min": "0",
                }
            ),

            "wastage_percentage": forms.NumberInput(
                attrs={
                    "class": "form-control ingredient-wastage",
                    "step": "0.01",
                    "min": "0",
                }
            ),

            "remarks": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Optional",
                }
            ),

        }

    # ======================================================
    # QUANTITY VALIDATION
    # ======================================================

    def clean_quantity(self):

        quantity = self.cleaned_data.get("quantity")

        if quantity is not None and quantity <= 0:

            raise forms.ValidationError(
                "Quantity must be greater than zero."
            )

        return quantity

    # ======================================================
    # WASTAGE VALIDATION
    # ======================================================

    def clean_wastage_percentage(self):

        wastage = self.cleaned_data.get(
            "wastage_percentage"
        )

        if wastage is not None:

            if wastage < 0:

                raise forms.ValidationError(
                    "Wastage cannot be negative."
                )

            if wastage > 100:

                raise forms.ValidationError(
                    "Wastage cannot exceed 100%."
                )

        return wastage


# ==========================================================
# RECIPE INGREDIENT FORMSET
# ==========================================================

RecipeIngredientFormSet = inlineformset_factory(

    Recipe,

    RecipeIngredient,

    form=RecipeIngredientForm,

    extra=1,

    can_delete=True,

)