from django import template

register = template.Library()


@register.filter
def has_permission(user, permission_code):

    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return user.permissions_list.filter(
        permission__code=permission_code
    ).exists()


@register.filter
def has_any_permission(user, permission_codes):

    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    codes = [
        code.strip()
        for code in permission_codes.split(",")
    ]

    return user.permissions_list.filter(
        permission__code__in=codes
    ).exists()