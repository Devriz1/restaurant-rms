from django import forms

from apps.core.forms import BaseModelForm

from .models import Bill, Period



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


class PeriodForm(forms.ModelForm):

    class Meta:

        model = Period

        fields = [
            "name",
            "start_date",
            "end_date",
            "period_type",
            "is_active",
        ]

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. FY 2025-26",
                    "autofocus": True,
                }
            ),

            "start_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "end_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "period_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                    "role": "switch",
                }
            ),

        }

        labels = {
            "name": "Period Name",
            "start_date": "Start Date",
            "end_date": "End Date",
            "period_type": "Period Type",
            "is_active": "Set as active period",
        }

        help_texts = {
            "start_date": "First day of the period (e.g. 1 April)",
            "end_date": "Last day of the period (e.g. 31 March)",
            "is_active": "When active, new bills use this period and invoice numbers reset from 1.",
        }

    def clean(self):

        cleaned_data = super().clean()

        start = cleaned_data.get("start_date")
        end = cleaned_data.get("end_date")

        if start and end and end < start:
            self.add_error(
                "end_date",
                "End date must be after start date.",
            )

        return cleaned_data