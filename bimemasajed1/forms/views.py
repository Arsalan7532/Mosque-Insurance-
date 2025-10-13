from django.shortcuts import render,redirect
from django.contrib import messages
from .forms import SignupForm,LoginForm,MainRegistration_form
from .models import Signup
from django.contrib.auth.hashers import check_password,make_password
from bimemasajed1.decorators import custom_login_required
def signin(request):
    if request.session.get('is_logged_in', False):
        return redirect('home')  # هدایت به صفحه اصلی اگر کاربر لاگین کرده باشد

    if request.method == "POST":
        form=SignupForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.password=make_password(form.cleaned_data['password'])
            user.save()
            return redirect("login")  
    else:
        form=SignupForm()      
    return render(request,'signinpage.html',{'form':form})
def login(request):
    # بررسی وضعیت لاگین
    if request.session.get('is_logged_in', False):
        return redirect('home')  # هدایت به صفحه اصلی اگر کاربر لاگین کرده باشد

    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:
                user = Signup.objects.get(username=username)
                if check_password(password, user.password):
                    request.session['username'] = username
                    request.session['is_logged_in'] = True
                    messages.success(request, "با موفقیت وارد شدید")
                    next_url = request.GET.get('next', 'home')
                    return redirect(next_url)
                else:
                    print (user.password)
                    messages.error(request, "رمز عبور اشتباه است")
            except Signup.DoesNotExist:
                messages.error(request, "نام کاربری وجود ندارد")
                return redirect("signin")
        else:
            print("Form errors:", form.errors)  # دیباگ
    return render(request, 'loginpage.html', {'form': form})
def logout(request):
    if request.session.get ('is_logged_in',False):
        request.session.flush()
        messages.success(request,'با موفقیت خارح شدید')
        return redirect('login')
    else:
        messages.info(request,'شما قبلا خارج شدید')
@custom_login_required
def MainRegistration(request):
    username = request.session.get('username')  # گرفتن یوزرنیم از سشن

    signup = None
    if username:
        try:
            signup = Signup.objects.get(username=username)
        except Signup.DoesNotExist:
            signup = None

    if request.method == 'POST':
        form = MainRegistration_form(request.POST, username=username)
        if form.is_valid():
            mosque = form.save(commit=False)
            mosque.registration = signup
            mosque.save()
            messages.success(request, "اطلاعات مسجد با موفقیت ثبت شد ✅")
            return redirect("/")
        else:
            messages.error(request, "اطلاعات را صحیح وارد نمایید ❌")
    else:
        initial = {}
        if signup:
            initial['registration'] = signup.pk
        form = MainRegistration_form(username=username, initial=initial)

    return render(request, "mainform.html", {"form": form, "signup": signup})
def PersonInfo(request):
    return redirect ('home')
def BuildingInformation(request):
    return redirect ('home')
def TrusteesBoard(request):
    return redirect ('home')
