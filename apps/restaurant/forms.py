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
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. The Grand Bistro",
                "id": "id_name",
                "autofocus": True,
            }),

            "logo": forms.ClearableFileInput(attrs={
                "class": "form-control",
                "accept": "image/*",
                "id": "id_logo",
            }),

            "phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "+91 98765 43210",
                "id": "id_phone",
            }),

            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "contact@restaurant.com",
                "id": "id_email",
            }),

            "address": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "Street address, building, floor…",
                "id": "id_address",
            }),

            "city": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Mumbai",
                "id": "id_city",
            }),

            "state": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Maharashtra",
                "id": "id_state",
            }),

            "country": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "India",
                "id": "id_country",
            }),

            "pincode": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "400001",
                "id": "id_pincode",
            }),

            "gst_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "27AAPFU0939F1ZV",
                "id": "id_gst_number",
                "style": "text-transform: uppercase; letter-spacing: 0.05em;",
            }),

            "currency": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "INR",
                "id": "id_currency",
                "maxlength": "10",
            }),

            "currency_symbol": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "₹",
                "id": "id_currency_symbol",
                "maxlength": "5",
            }),

            "timezone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Asia/Kolkata",
                "id": "id_timezone",
                "list": "timezone-list",
            }),

            "opening_time": forms.TimeInput(attrs={
                "type": "time",
                "class": "form-control",
                "id": "id_opening_time",
            }),

            "closing_time": forms.TimeInput(attrs={
                "type": "time",
                "class": "form-control",
                "id": "id_closing_time",
            }),

            "receipt_header": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Text printed at the top of every receipt — welcome message, tagline…",
                "id": "id_receipt_header",
            }),

            "receipt_footer": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Text printed at the bottom — thank you message, return policy, social handles…",
                "id": "id_receipt_footer",
            }),
        }

        labels = {
            "name": "Restaurant Name",
            "gst_number": "GST Number",
            "currency_symbol": "Currency Symbol",
            "opening_time": "Opening Time",
            "closing_time": "Closing Time",
            "receipt_header": "Receipt Header",
            "receipt_footer": "Receipt Footer",
        }