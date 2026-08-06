from django import forms

from .models import PrinterSetting


class PrinterSettingForm(forms.ModelForm):

    class Meta:

        model = PrinterSetting

        fields = [

            "billing_printer",

            "kitchen_printer",

            "report_printer",

            "receipt_printer",

            "auto_print_kot",

            "auto_print_bill",

            "bill_copies",

            "kot_copies",

        ]

        widgets = {

            "billing_printer": forms.TextInput(

                attrs={

                    "class": "form-control",

                    "placeholder": "Example: EPSON TM-T82III",

                }

            ),

            "kitchen_printer": forms.TextInput(

                attrs={

                    "class": "form-control",

                    "placeholder": "Kitchen Printer",

                }

            ),

            "report_printer": forms.TextInput(

                attrs={

                    "class": "form-control",

                    "placeholder": "Report Printer",

                }

            ),

            "receipt_printer": forms.TextInput(

                attrs={

                    "class": "form-control",

                    "placeholder": "Receipt Printer",

                }

            ),

            "bill_copies": forms.NumberInput(

                attrs={

                    "class": "form-control",

                    "min": 1,

                }

            ),

            "kot_copies": forms.NumberInput(

                attrs={

                    "class": "form-control",

                    "min": 1,

                }

            ),

        }