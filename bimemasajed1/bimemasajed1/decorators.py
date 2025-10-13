from django.shortcuts import redirect
from functools import wraps
def custom_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.session.get('is_logged_in', False):
            return view_func(request, *args, **kwargs)
        else:
            return redirect(f'/account/login/?next={request.path}')
    return wrapper
