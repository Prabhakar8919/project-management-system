from functools import wraps
from django.shortcuts import render


def login_required_message(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        return render(request, 'accounts/login_required.html', {'next_url': request.path})
    return _wrapped_view
