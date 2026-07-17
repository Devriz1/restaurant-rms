from django import forms
from .models import DiningArea


class DiningAreaForm(forms.ModelForm):
    class Meta:
        model = DiningArea
        fields = [
            "name",
            "description",
            "display_order",
            "is_active",
        ]