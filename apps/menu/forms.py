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
        fields = [
            "category",
            "name",
            "description",
            "price",
            "preparation_time",
            "is_veg",
            "is_available",
            "image",
        ]

        widgets = {
            "category": forms.Select(attrs={
                "class": "form-select",
                "id": "id_category",
            }),

            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Margherita Pizza",
                "id": "id_name",
                "autofocus": True,
            }),

            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Describe the dish — ingredients, flavour profile, allergens…",
                "id": "id_description",
            }),

            "price": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "0.00",
                "step": "0.01",
                "min": "0",
                "id": "id_price",
            }),

            "preparation_time": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "10",
                "min": "1",
                "id": "id_preparation_time",
            }),

            "is_veg": forms.CheckboxInput(attrs={
                "class": "form-check-input",
                "role": "switch",
                "id": "id_is_veg",
            }),

            "is_available": forms.CheckboxInput(attrs={
                "class": "form-check-input",
                "role": "switch",
                "id": "id_is_available",
            }),

            "image": forms.ClearableFileInput(attrs={
                "class": "form-control",
                "accept": "image/*",
                "id": "id_image",
            }),
        }

        labels = {
            "is_veg": "Vegetarian",
            "is_available": "Available on Menu",
            "preparation_time": "Prep Time (minutes)",
        }