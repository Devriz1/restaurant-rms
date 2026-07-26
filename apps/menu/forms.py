from django import forms
from .models import MenuCategory, MenuItem


class MenuCategoryForm(forms.ModelForm):
    class Meta:
        model = MenuCategory
        fields = [
            "name",
            "description",
            "display_order",
            "is_active",
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Category Name",
            }),

            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Description (Optional)",
            }),

            "display_order": forms.NumberInput(attrs={
                "class": "form-control",
            }),

            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }


class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = "__all__"