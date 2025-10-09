# service_track_app/decorators.py
from django.http import HttpResponseForbidden
from functools import wraps

def role_required(allowed_roles=[]):
    """
    Декоратор для ограничения доступа по ролям.
    allowed_roles — список, например ['dealer', 'service_center']
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if hasattr(request.user, 'role') and request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("У вас нет доступа к этой странице")
        return wrapper
    return decorator
