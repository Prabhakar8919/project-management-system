from functools import wraps
from django.shortcuts import render

# checking if user is logged in
# if yes, allow access to the view
# if not, show login required page with next URL
def login_required_message(view_func):
    #using decorateer to restrict access to views for logged-in users only
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        return render(request, 'accounts/login_required.html', {'next_url': request.path})
    return _wrapped_view
