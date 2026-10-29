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
            "kitchen_station",
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

            "kitchen_station": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Hot Kitchen, Cold Station, Desserts",
                "id": "id_kitchen_station",
            }),
        }


class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = [
            "item_code",
            "category",
            "sub_category",
            "name",
            "description",
            "price",
            "special_price",
            "takeaway_price",
            "preparation_time",
            "is_veg",
            "is_available",
            "image",
        ]

        widgets = {
            "item_code": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. PIZ-001",
                "id": "id_item_code",
            }),

            "category": forms.Select(attrs={
                "class": "form-select",
                "id": "id_category",
            }),

            "sub_category": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Thin Crust",
                "id": "id_sub_category",
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

            "special_price": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Same as normal",
                "step": "0.01",
                "min": "0",
                "id": "id_special_price",
            }),

            "takeaway_price": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Same as normal",
                "step": "0.01",
                "min": "0",
                "id": "id_takeaway_price",
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
            "price": "Normal Price",
            "special_price": "Special Price",
            "takeaway_price": "Takeaway Price",
            "is_veg": "Vegetarian",
            "is_available": "Available on Menu",
            "preparation_time": "Prep Time (minutes)",
        }

    def clean(self):
        cleaned_data = super().clean()

        for field in ("special_price", "takeaway_price"):

            value = cleaned_data.get(field)

            if value is not None and value < 0:
                self.add_error(
                    field,
                    f"{self.fields[field].label} cannot be negative.",
                )

        return cleaned_data