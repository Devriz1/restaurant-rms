from django import forms
from .models import DiningArea
from .models import RestaurantTable


class DiningAreaForm(forms.ModelForm):
    class Meta:
        model = DiningArea
        fields = [
            "name",
            "description",
            "display_order",
            "is_active",
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Main Hall, Rooftop, Private Room",
                "id": "id_name",
                "autofocus": True,
            }),

            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Brief description of this dining area (optional)",
                "id": "id_description",
            }),

            "display_order": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0",
                "placeholder": "0",
                "id": "id_display_order",
            }),

            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input",
                "role": "switch",
                "id": "id_is_active",
            }),
        }

        labels = {
            "is_active": "Active",
            "display_order": "Display Order",
        }


class RestaurantTableForm(forms.ModelForm):
    class Meta:
        model = RestaurantTable
        fields = [
            "area",
            "table_number",
            "display_name",
            "capacity",
            "status",
            "is_active",
        ]

        widgets = {
            "area": forms.Select(attrs={
                "class": "form-select",
                "id": "id_area",
            }),

            "table_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. T1, A-01, VIP-3",
                "id": "id_table_number",
                "autofocus": True,
            }),

            "display_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Window Table (optional)",
                "id": "id_display_name",
            }),

            "capacity": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "1",
                "max": "50",
                "placeholder": "2",
                "id": "id_capacity",
            }),

            "status": forms.Select(attrs={
                "class": "form-select",
                "id": "id_status",
            }),

            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input",
                "role": "switch",
                "id": "id_is_active",
            }),
        }

        labels = {
            "table_number": "Table Number / ID",
            "display_name": "Display Name",
            "is_active": "Active",
        }