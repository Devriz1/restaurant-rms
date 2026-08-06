from django import forms

from .models import Unit,Supplier, Category, Material


class UnitForm(forms.ModelForm):

    class Meta:

        model = Unit

        fields = [

            "name",

            "symbol",

            "unit_type",

            "decimal_allowed",

            "is_active",

        ]

        widgets = {

            "name": forms.TextInput(

                attrs={

                    "class": "form-control",

                    "placeholder": "Enter Unit Name",

                }

            ),

            "symbol": forms.TextInput(

                attrs={

                    "class": "form-control",

                    "placeholder": "Kg, L, Pcs...",

                }

            ),

            "unit_type": forms.Select(

                attrs={

                    "class": "form-select",

                }

            ),

            "decimal_allowed": forms.CheckboxInput(

                attrs={

                    "class": "form-check-input",

                }

            ),

            "is_active": forms.CheckboxInput(

                attrs={

                    "class": "form-check-input",

                }

            ),

        }


class SupplierForm(forms.ModelForm):

    class Meta:

        model = Supplier

        fields = [

            "name",

            "contact_person",

            "phone",

            "email",

            "gst_number",

            "address",

            "city",

            "state",

            "pincode",

            "is_active",

        ]

        widgets = {

            "name": forms.TextInput(

                attrs={

                    "class": "form-control",

                }

            ),

            "contact_person": forms.TextInput(

                attrs={

                    "class": "form-control",

                }

            ),

            "phone": forms.TextInput(

                attrs={

                    "class": "form-control",

                }

            ),

            "email": forms.EmailInput(

                attrs={

                    "class": "form-control",

                }

            ),

            "gst_number": forms.TextInput(

                attrs={

                    "class": "form-control",

                }

            ),

            "address": forms.Textarea(

                attrs={

                    "class": "form-control",

                    "rows": 3,

                }

            ),

            "city": forms.TextInput(

                attrs={

                    "class": "form-control",

                }

            ),

            "state": forms.TextInput(

                attrs={

                    "class": "form-control",

                }

            ),

            "pincode": forms.TextInput(

                attrs={

                    "class": "form-control",

                }

            ),

            "is_active": forms.CheckboxInput(

                attrs={

                    "class": "form-check-input",

                }

            ),

        }

class CategoryForm(forms.ModelForm):

    class Meta:

        model = Category

        fields = [

            "name",

            "description",

            "is_active",

        ]

        widgets = {

            "name": forms.TextInput(

                attrs={

                    "class": "form-control",

                    "placeholder": "Enter Category Name",

                }

            ),

            "description": forms.Textarea(

                attrs={

                    "class": "form-control",

                    "rows": 3,

                    "placeholder": "Enter Description",

                }

            ),

            "is_active": forms.CheckboxInput(

                attrs={

                    "class": "form-check-input",

                }

            ),

        }


# ==========================================================
# MATERIAL FORM
# ==========================================================

class MaterialForm(forms.ModelForm):

    class Meta:

        model = Material

        fields = [

            "name",

            "category",

            "supplier",

            "unit",

            "opening_stock",

            "current_stock",

            "minimum_stock",

            "maximum_stock",

            "cost_price",

            "last_purchase_price",

            "storage_location",

            "barcode",

            "expiry_tracking",

            "is_active",

        ]

        widgets = {

            "name": forms.TextInput(

                attrs={

                    "class": "form-control",

                    "placeholder": "Material Name",

                }

            ),

            "category": forms.Select(

                attrs={

                    "class": "form-select",

                }

            ),

            "supplier": forms.Select(

                attrs={

                    "class": "form-select",

                }

            ),

            "unit": forms.Select(

                attrs={

                    "class": "form-select",

                }

            ),

            "opening_stock": forms.NumberInput(

                attrs={

                    "class": "form-control",

                    "step": "0.01",

                }

            ),

            "current_stock": forms.NumberInput(

                attrs={

                    "class": "form-control",

                    "step": "0.01",

                    "readonly": True,

                }

            ),

            "minimum_stock": forms.NumberInput(

                attrs={

                    "class": "form-control",

                    "step": "0.01",

                }

            ),

            "maximum_stock": forms.NumberInput(

                attrs={

                    "class": "form-control",

                    "step": "0.01",

                }

            ),

            "cost_price": forms.NumberInput(

                attrs={

                    "class": "form-control",

                    "step": "0.01",

                }

            ),

            "last_purchase_price": forms.NumberInput(

                attrs={

                    "class": "form-control",

                    "step": "0.01",

                }

            ),

            "storage_location": forms.TextInput(

                attrs={

                    "class": "form-control",

                    "placeholder": "Rack / Freezer / Shelf",

                }

            ),

            "barcode": forms.TextInput(

                attrs={

                    "class": "form-control",

                    "placeholder": "Barcode (Optional)",

                }

            ),

            "expiry_tracking": forms.CheckboxInput(

                attrs={

                    "class": "form-check-input",

                }

            ),

            "is_active": forms.CheckboxInput(

                attrs={

                    "class": "form-check-input",

                }

            ),

        }

    def save(self, commit=True):

        material = super().save(commit=False)

        if not material.pk:

            material.current_stock = material.opening_stock

        if commit:

            material.save()

        return material

