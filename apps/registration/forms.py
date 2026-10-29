from django import forms
from .models import LicenseKey, Registration


class LicenseKeyForm(forms.ModelForm):

    key = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter license key",
                "autofocus": True,
            }
        ),
    )

    expires_at = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(
            attrs={
                "class": "form-control",
                "type": "datetime-local",
            },
            format="%Y-%m-%dT%H:%M",
        ),
        label="Expires At",
        help_text="Leave blank for lifetime keys.",
    )

    class Meta:
        model = LicenseKey
        fields = [
            "key",
            "status",
            "plan",
            "max_users",
            "expires_at",
            "note",
        ]
        widgets = {
            "status": forms.Select(
                attrs={"class": "form-select"}
            ),
            "plan": forms.Select(
                attrs={"class": "form-select"}
            ),
            "max_users": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                }
            ),
            "note": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Optional note…",
                }
            ),
        }
        labels = {
            "key": "License Key",
            "status": "Status",
            "plan": "Plan",
            "max_users": "Max Users",
            "note": "Note",
        }


class ActivateKeyForm(forms.Form):
    key = forms.CharField(
        max_length=128,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Paste license key here",
                "autofocus": True,
            }
        ),
        label="License Key",
    )

    def clean_key(self):
        key = self.cleaned_data.get("key", "").strip().upper()
        if not key:
            raise forms.ValidationError("Please enter a license key.")
        return key