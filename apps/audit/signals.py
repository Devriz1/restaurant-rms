from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from apps.audit.utils import audit_log


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    audit_log(
        user=user,
        action="login",
        model_name="User",
        object_id=user.id,
        object_repr=user.username,
        message="User logged in",
        request=request,
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    audit_log(
        user=user,
        action="logout",
        model_name="User",
        object_id=user.id if user else None,
        object_repr=user.username if user else "",
        message="User logged out",
        request=request,
    )