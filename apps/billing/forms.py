from django import forms

from apps.core.forms import BaseModelForm

from .models import Bill



class BillForm(BaseModelForm):

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
                    "class":
                    "form-select"
                }
            ),

            "discount": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "placeholder":
                    "Discount",
                }
            ),

            "service_charge": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "placeholder":
                    "Service Charge",
                }
            ),

            "tax": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "placeholder":
                    "Tax",
                }
            ),

        }


    def clean_discount(self):

        discount = self.cleaned_data.get(
            "discount"
        )

        if discount is None:

            discount = 0

        if discount < 0:

            raise forms.ValidationError(
                "Discount cannot be negative."
            )

        return discount