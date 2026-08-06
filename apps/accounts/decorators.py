from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required

def permission_required(permission_code):

    def decorator(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            if not request.user.is_authenticated:
                raise PermissionDenied

            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            if request.user.permissions_list.filter(
                permission__code=permission_code
            ).exists():
                return view_func(request, *args, **kwargs)

            raise PermissionDenied

        return wrapper

    return decorator