from django import forms
from .models import Bill


class BillForm(forms.ModelForm):

    class Meta:

        model = Bill

        fields = [
            "discount_type",
            "discount",
            "service_charge",
            "tax",
        ]

        widgets = {

            "discount_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "discount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                }
            ),

            "service_charge": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                }
            ),

            "tax": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                }
            ),

        }