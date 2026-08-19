from django import forms

from apps.inventory.models import Material

from .models import StockAdjustment


class StockAdjustmentForm(forms.ModelForm):

    class Meta:

        model = StockAdjustment

        fields = (
            "material",
            "adjustment_type",
            "quantity",
            "reason",
            "remarks",
        )

        widgets = {

            "material": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "adjustment_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "quantity": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0.01",
                    "placeholder": "Enter quantity",
                }
            ),

            "reason": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Reason for adjustment",
                }
            ),

            "remarks": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Additional remarks",
                }
            ),
        }

    def clean_quantity(self):

        quantity = self.cleaned_data["quantity"]

        if quantity <= 0:

            raise forms.ValidationError(
                "Adjustment quantity must be greater than zero."
            )

        return quantity