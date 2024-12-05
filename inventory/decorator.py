from django.http import JsonResponse
from functools import wraps

def role_required(allowed_roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({'error': 'Authentication required'}, status=401)

            if request.user.groups.filter(name__in=allowed_roles).exists():
                return view_func(request, *args, **kwargs)
            else:
                return JsonResponse({'error': 'Permission denied'}, status=403)
        return wrapper
    return decorator
