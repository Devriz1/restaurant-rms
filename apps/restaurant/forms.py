from django import forms
from .models import Restaurant


class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = [
            "name",
            "logo",
            "phone",
            "email",
            "address",
            "city",
            "state",
            "country",
            "pincode",
            "gst_number",
            "currency",
            "currency_symbol",
            "timezone",
            "opening_time",
            "closing_time",
            "receipt_header",
            "receipt_footer",
        ]

        widgets = {
            "opening_time": forms.TimeInput(attrs={"type": "time"}),
            "closing_time": forms.TimeInput(attrs={"type": "time"}),
        }