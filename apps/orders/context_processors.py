from apps.orders.models import Notification


def notification_context(request):
    if not request.user.is_authenticated:
        return {"unread_notifications": 0}

    unread_count = Notification.objects.filter(
        recipient=request.user,
        is_read=False,
    ).count()

    return {
        "unread_notifications": unread_count,
    }