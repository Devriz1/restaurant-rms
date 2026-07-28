from django import forms

from .models import (
    Ingredient,
    InventoryCategory,
    Supplier,
    Unit,
)


class InventoryCategoryForm(forms.ModelForm):

    class Meta:

        model = InventoryCategory

        fields = "__all__"


class UnitForm(forms.ModelForm):

    class Meta:

        model = Unit

        fields = "__all__"


class SupplierForm(forms.ModelForm):

    class Meta:

        model = Supplier

        fields = "__all__"


class IngredientForm(forms.ModelForm):

    class Meta:

        model = Ingredient

        fields = "__all__"