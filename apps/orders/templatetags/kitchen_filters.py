from django import template

register = template.Library()


@register.filter
def filter_status(items, status):
    """Count items with a specific status."""
    if not items:
        return 0
    return sum(1 for item in items if item.status == status)


@register.filter
def filter_not_ready(items):
    """Count items that are not ready (i.e., pending or preparing)."""
    if not items:
        return 0
    return sum(1 for item in items if item.status not in ("ready", "served", "cancelled"))


@register.filter
def filter_pending(items):
    """Check if any items in a list have 'pending' status."""
    if not items:
        return False
    return any(item.status == "pending" for item in items)


@register.filter
def get_bill(guest):
    """Safely get the bill related object for a GuestOrder.

    Returns the Bill instance if it exists, None otherwise.
    """
    try:
        return guest.bill
    except Exception:
        return None