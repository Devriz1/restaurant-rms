from functools import wraps

from django.core.exceptions import PermissionDenied


def permission_required(permission_code):

    def decorator(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            has_permission = request.user.permissions_list.filter(
                permission__code=permission_code
            ).exists()

            if not has_permission:
                raise PermissionDenied

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator