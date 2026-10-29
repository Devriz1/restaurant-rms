from apps.audit.models import AuditLog


def audit_log(user, action, model_name, object_id=None, object_repr="", message="", request=None):
    """Create an audit log entry.

    Args:
        user: The user performing the action (or None for system actions).
        action: The action type (e.g., 'create', 'update', 'delete', 'login').
        model_name: The name of the model affected (e.g., 'Bill', 'GuestOrder').
        object_id: The ID of the affected record.
        object_repr: String representation of the affected record.
        message: Additional details about the action.
        request: The HTTP request object (for IP and user agent).
    """
    ip_address = None
    user_agent = ""

    if request:
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(",")[0].strip()
        else:
            ip_address = request.META.get("REMOTE_ADDR")

        user_agent = request.META.get("HTTP_USER_AGENT", "")[:500]

    AuditLog.objects.create(
        user=user,
        action=action,
        model=model_name,
        object_id=object_id,
        object_repr=object_repr[:255] if object_repr else "",
        message=message,
        ip_address=ip_address,
        user_agent=user_agent,
    )