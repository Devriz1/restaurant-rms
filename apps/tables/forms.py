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