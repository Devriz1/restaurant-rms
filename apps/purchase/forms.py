from django import forms
from django.forms import inlineformset_factory

from .models import Purchase, PurchaseItem


# ==========================================================
# PURCHASE FORM
# ==========================================================

class PurchaseForm(forms.ModelForm):

    purchase_date = forms.DateField(

        widget=forms.DateInput(

            attrs={

                "type": "date",

                "class": "form-control",

            }

        )

    )

    class Meta:

        model = Purchase

        fields = (

            "supplier",

            "invoice_number",

            "purchase_date",

            "payment_mode",

            "discount",

            "other_charges",

            "remarks",

        )

        widgets = {

            "supplier": forms.Select(

                attrs={

                    "class": "form-select",

                }

            ),

            "invoice_number": forms.TextInput(

                attrs={

                    "class": "form-control",

                    "placeholder": "Supplier Invoice Number",

                }

            ),

            "payment_mode": forms.Select(

                attrs={

                    "class": "form-select",

                }

            ),

            "discount": forms.NumberInput(

                attrs={

                    "class": "form-control",

                    "step": "0.01",

                    "min": "0",

                }

            ),

            "other_charges": forms.NumberInput(

                attrs={

                    "class": "form-control",

                    "step": "0.01",

                    "min": "0",

                }

            ),

            "remarks": forms.Textarea(

                attrs={

                    "class": "form-control",

                    "rows": 3,

                }

            ),

        }


# ==========================================================
# PURCHASE ITEM FORM
# ==========================================================

class PurchaseItemForm(forms.ModelForm):

    class Meta:

        model = PurchaseItem

        fields = (

            "material",

            "quantity",

            "unit_price",

            "gst_percentage",

        )

        widgets = {

            "material": forms.Select(

                attrs={

                    "class": "form-select material",

                }

            ),

            "quantity": forms.NumberInput(

                attrs={

                    "class": "form-control qty",

                    "step": "0.01",

                }

            ),

            "unit_price": forms.NumberInput(

                attrs={

                    "class": "form-control rate",

                    "step": "0.01",

                }

            ),

            "gst_percentage": forms.NumberInput(

                attrs={

                    "class": "form-control gst",

                    "step": "0.01",

                }

            ),

        }


# ==========================================================
# FORMSET
# ==========================================================

PurchaseItemFormSet = inlineformset_factory(

    Purchase,

    PurchaseItem,

    form=PurchaseItemForm,

    extra=1,

    can_delete=True,

)