from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse


class RegistrationLockMiddleware:
    """Lock the app when no valid license key is active.

    Only the Registration and Activate pages remain accessible.
    """

    EXEMPT_PREFIXES = (
        "/registration/",
        "/static/",
        "/admin/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from apps.registration.models import Registration

        path = request.path

        # Allow exempt paths through
        if any(path.startswith(prefix) for prefix in self.EXEMPT_PREFIXES):
            return self.get_response(request)

        # Allow logout/login through
        if path.startswith("/accounts/login") or path.startswith("/accounts/logout"):
            return self.get_response(request)

        if not Registration.is_registered():
            messages.error(
                request,
                "Software is locked. Activate a license key to continue.",
            )
            return redirect("registration:status")

        return self.get_response(request)