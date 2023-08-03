from functools import wraps
from django.http import HttpResponseRedirect


def allowed_groups(groups=[], redirect_url=None):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user

            if not user.is_authenticated:
                return HttpResponseRedirect(redirect_url)

            if user.is_superuser or user.groups.filter(name__in=groups).exists():
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseRedirect(redirect_url)

        return _wrapped_view

    return decorator
