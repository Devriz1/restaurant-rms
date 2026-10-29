from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import render
from apps.audit.models import AuditLog
from apps.accounts.templatetags.permissions import *  # noqa


@login_required
def audit_log_list(request):
    """Display the audit trail with filtering options.

    Access restricted to users with the 'audit.view' permission (Owner/Manager).
    """

    if not (
        request.user.is_superuser
        or request.user.permissions_list.filter(permission__code="audit.view").exists()
    ):
        return HttpResponseForbidden("You do not have permission to view the audit trail.")

    logs = AuditLog.objects.all().select_related("user")

    # Filtering
    action_filter = request.GET.get("action", "").strip()
    model_filter = request.GET.get("model", "").strip()
    user_filter = request.GET.get("user", "").strip()
    date_from = request.GET.get("date_from", "").strip()
    date_to = request.GET.get("date_to", "").strip()
    search = request.GET.get("q", "").strip()

    if action_filter:
        logs = logs.filter(action=action_filter)

    if model_filter:
        logs = logs.filter(model=model_filter)

    if user_filter:
        logs = logs.filter(user_id=user_filter)

    if date_from:
        logs = logs.filter(created_at__date__gte=date_from)

    if date_to:
        logs = logs.filter(created_at__date__lte=date_to)

    if search:
        logs = logs.filter(
            Q(message__icontains=search)
            | Q(object_repr__icontains=search)
            | Q(user__username__icontains=search)
        )

    # Pagination
    paginator = Paginator(logs, 50)
    page_obj = paginator.get_page(request.GET.get("page", 1))

    # Get unique models for filter dropdown
    unique_models = AuditLog.objects.values_list("model", flat=True).distinct().order_by()

    from django.contrib.auth import get_user_model
    User = get_user_model()
    users = User.objects.filter(audit_logs__isnull=False).distinct().order_by("username")

    context = {
        "page_obj": page_obj,
        "action_filter": action_filter,
        "model_filter": model_filter,
        "user_filter": user_filter,
        "date_from": date_from,
        "date_to": date_to,
        "search": search,
        "unique_models": unique_models,
        "users": users,
        "ACTION_CHOICES": AuditLog.ACTION_CHOICES,
    }

    return render(request, "audit/audit_log_list.html", context)