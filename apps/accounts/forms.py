from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
)

from .models import User
from apps.billing.models import Period


# ==========================================================
# LOGIN
# ==========================================================

class LoginForm(AuthenticationForm):

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Username",
                "autocomplete": "off",
                "autocapitalize": "off",
                "autocorrect": "off",
                "spellcheck": "false",
            }
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Password",
                "autocomplete": "new-password",
            }
        )
    )

    period = forms.ModelChoiceField(
        queryset=Period.objects.none(),
        required=False,
        empty_label="Select financial period…",
        widget=forms.Select(
            attrs={
                "class": "form-select",
                "id": "id_login_period",
            }
        ),
        label="Financial Period",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Active periods first, then inactive — all ordered by start date desc
        active = Period.objects.filter(is_active=True).order_by("-start_date")
        inactive = Period.objects.filter(is_active=False).order_by("-start_date")
        ids = list(active.values_list("id", flat=True)) + list(inactive.values_list("id", flat=True))
        self.fields["period"].queryset = Period.objects.filter(id__in=ids)

        # Default to the last created period
        last = Period.objects.order_by("-start_date").first()
        if last and not self.is_bound:
            self.fields["period"].initial = last.id


# ==========================================================
# CREATE USER
# ==========================================================

class UserCreateForm(UserCreationForm):

    class Meta:

        model = User

        fields = [
            "username",
            "first_name",
            "last_name",
            "phone_number",
            "email",
            "role",
            "is_active",
        ]


# ==========================================================
# EDIT USER
# ==========================================================

class UserEditForm(forms.ModelForm):

    class Meta:

        model = User

        fields = [
            "username",
            "first_name",
            "last_name",
            "phone_number",
            "email",
            "role",
            "is_active",
        ]