from django.shortcuts import render,redirect
from django.contrib import messages
from .forms import SignupForm,LoginForm,MainRegistration_form,PersonInfo_form,BuildingInformation_form,TrusteesBoard_form
from .models import Signup,TrusteesBoard,MainRegistration,PersonInfo,BuildingInformation
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
def get_signup_from_session(request): #get username
    user=request.session.get('username')
    if user:
        try:
            signup=Signup.objects.filter(username=user).first()
        except Signup.DoesNotExist:
            messages.warning(request,"کاربری شما یافت نشد، لطفا دوباره وارد شوید")
            return None
    else:
        messages.warning(request,"ابتدا وارد شوید!")
        return None
    return signup
def save_data(request,getsignup,getform):#save username &form
    if getform.is_valid():
        data=getform.save(commit=False)
        data.registration=getsignup
        data.save()         #not ManyToMany !!!!!!!!!! we dont have try/except
        messages.success(request, "اطلاعات با موفقیت ثبت شد ✅")
        return True 
    else:
        messages.error(request, "اطلاعات را صحیح وارد نمایید ❌")
        return False
def MainRegistration_view(request):
    # گرفتن signup از session
    signup = get_signup_from_session(request)
    if not signup:
        return redirect('login')  # یا مسیر مناسب

    # پیدا کردن MainRegistration مرتبط با این signup (ممکنه None باشه)
    main_reg = MainRegistration.objects.filter(registration=signup).first()

    # آیا کاربر در حالت ویرایش است؟ (با ?edit=true در URL)
    editing = request.GET.get("edit") == "true"

    if request.method == 'POST':
        # هنگام POST، اگر رکورد موجود است از همان برای instance استفاده کن
        form = MainRegistration_form(request.POST, instance=main_reg)
        if form.is_valid():
            obj = form.save(commit=False)
            # اگر رکورد جدید است یا registration تنظیم نشده، حتما registration را ست کن
            obj.registration = signup
            obj.save()
            messages.success(request, "اطلاعات مسجد با موفقیت ذخیره شد ✅")
            return redirect('/')  # یا مسیر دلخواه بعد از ذخیره
        else:
            messages.error(request, "فرم معتبر نیست، لطفا مقادیر را بررسی کنید.")
    else:
        # GET: نمایش فرم با instance (اگر رکورد هست) یا فرم خالی
        form = MainRegistration_form(instance=main_reg)
        # اگر رکورد وجود داره و کاربر در حالت ویرایش نیست → فیلدها را غیرفعال کن
        if main_reg and not editing:
            for field in form.fields.values():
                field.widget.attrs['disabled'] = 'disabled'

    return render(request, 'mainform.html', {
        'form': form,
        'signup': signup,
        'editing': editing,
        'main_reg': main_reg,
    })
@custom_login_required
def PersonInfo_view(request):
    signup = get_signup_from_session(request)
    # پیدا کردن مسجدی که این کاربر ثبت کرده
    main_reg = MainRegistration.objects.filter(registration=signup).first()

    if not main_reg:
        messages.error(request, "ابتدا فرم اطلاعات اصلی مسجد را تکمیل کنید.")
        return redirect('/account/mainform/')  # مسیر فرم مسجد

    editing = request.GET.get("edit") == "true"

    if request.method == 'POST':
        data = PersonInfo.objects.filter(registration=main_reg).first()
        form = PersonInfo_form(request.POST, instance=data)
        if form.is_valid():
            trustees = form.save(commit=False)
            trustees.registration = main_reg
            trustees.save()
            messages.success(request, "اطلاعات هیات امنا ذخیره شد ✅")
            return redirect('/')
    else:
        data = PersonInfo.objects.filter(registration=main_reg).first()
        form = PersonInfo_form(instance=data)
        if not editing:
            for field in form.fields.values():
                field.widget.attrs['disabled'] = 'disabled'

    return render(request, 'personform.html', {
        'form': form,
        'signup': signup,
        'editing': editing
    })
@custom_login_required
def BuildingInformation_view(request):
    signup = get_signup_from_session(request)
    # پیدا کردن مسجدی که این کاربر ثبت کرده
    main_reg = MainRegistration.objects.filter(registration=signup).first()

    if not main_reg:
        messages.error(request, "ابتدا فرم اطلاعات اصلی مسجد را تکمیل کنید.")
        return redirect('/account/mainform/')  # مسیر فرم مسجد

    editing = request.GET.get("edit") == "true"

    if request.method == 'POST':
        data = BuildingInformation.objects.filter(registration=main_reg).first()
        form = BuildingInformation_form(request.POST, instance=data)
        if form.is_valid():
            trustees = form.save(commit=False)
            trustees.registration = main_reg
            trustees.save()
            messages.success(request, "اطلاعات هیات امنا ذخیره شد ✅")
            return redirect('/')
    else:
        data = BuildingInformation.objects.filter(registration=main_reg).first()
        form = BuildingInformation_form(instance=data)
        if not editing:
            for field in form.fields.values():
                field.widget.attrs['disabled'] = 'disabled'

    return render(request, 'buildingform.html', {
        'form': form,
        'signup': signup,
        'editing': editing
    })

@custom_login_required
def trusteesboard_view(request):
    signup = get_signup_from_session(request)
    # پیدا کردن مسجدی که این کاربر ثبت کرده
    main_reg = MainRegistration.objects.filter(registration=signup).first()

    if not main_reg:
        messages.error(request, "ابتدا فرم اطلاعات اصلی مسجد را تکمیل کنید.")
        return redirect('/account/mainform/')  # مسیر فرم مسجد

    editing = request.GET.get("edit") == "true"

    if request.method == 'POST':
        data = TrusteesBoard.objects.filter(registration=main_reg).first()
        form = TrusteesBoard_form(request.POST, instance=data)
        if form.is_valid():
            trustees = form.save(commit=False)
            trustees.registration = main_reg
            trustees.save()
            messages.success(request, "اطلاعات هیات امنا ذخیره شد ✅")
            return redirect('/')
    else:
        data = TrusteesBoard.objects.filter(registration=main_reg).first()
        form = TrusteesBoard_form(instance=data)
        if not editing:
            for field in form.fields.values():
                field.widget.attrs['disabled'] = 'disabled'

    return render(request, 'boardform.html', {
        'form': form,
        'signup': signup,
        'editing': editing
    })
