from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ActivateKeyForm
from .models import LicenseKey, Registration


@login_required
def registration_status(request):
    """Show whether the installation is currently unlocked."""

    reg = Registration.get_active()
    return render(
        request,
        "registration/status.html",
        {
            "registration": reg,
            "is_registered": Registration.is_registered(),
            "active_key": LicenseKey.get_active_key(),
        },
    )


@login_required
def activate_key(request):
    """Activate a license key against this installation."""

    if request.method == "POST":
        form = ActivateKeyForm(request.POST)
        if form.is_valid():
            key_code = form.cleaned_data["key"]
            key = LicenseKey.objects.filter(key=key_code).first()
            if key is None or not key.is_valid:
                messages.error(request, "Invalid or expired license key.")
                return render(request, "registration/activate.html", {"form": form})

            Registration.objects.filter(is_active=True).update(is_active=False)
            Registration.objects.create(
                license_key=key,
                is_active=True,
            )
            messages.success(
                request,
                f"License key '{key.key}' activated successfully.",
            )
            return redirect("registration:status")
    else:
        form = ActivateKeyForm()

    return render(request, "registration/activate.html", {"form": form})