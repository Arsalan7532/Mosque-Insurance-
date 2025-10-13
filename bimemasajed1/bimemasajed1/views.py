from django.shortcuts import render,redirect
from django.shortcuts import render, redirect
from functools import wraps
from forms.models import MainRegistration
from django.contrib import messages

def custom_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.session.get('is_logged_in', False):
            return view_func(request, *args, **kwargs)
        else:
            return redirect(f'/account/login/?next={request.path}')
    return wrapper

@custom_login_required
def home(request):
    mosque = None  
    try:
        mosque = MainRegistration.objects.filter(
            registration__username=request.session.get("username")
        ).values(
            'mosque_name', 'mosque_id', 'mosque_Capacity', 'created_phone', 'create_date'
        ).first()
    except Exception as e:
        messages.warning(request, f"مشکل در دریافت اطلاعات با پشتیبانی تماس بگیرید: {e}")
    return render(request, 'homepage.html', {"mosque": mosque})