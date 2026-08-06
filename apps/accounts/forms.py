from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
    
)

from .models import User


# ==========================================================
# LOGIN
# ==========================================================

from django import forms
from django.contrib.auth.forms import AuthenticationForm


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