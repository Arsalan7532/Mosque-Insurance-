from django.shortcuts import render,redirect
from django.contrib import messages
from .forms import SignupForm,LoginForm,MainRegistration_form,PersonInfo_form,BuildingInformation_form,TrusteesBoard_form
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
def MainRegistration(request):
    signup= get_signup_from_session(request)
    if not signup: #you can use decorator
        return redirect('login') 
    if request.method == 'POST':
        form = MainRegistration_form(request.POST, username=signup.username)
        if save_data(request,signup,form):
            return redirect("/")
        else:
            pass
    else:
        form = MainRegistration_form(username=signup.username)
    return render(request, "mainform.html", {"form": form, "signup": signup})
@custom_login_required
def PersonInfo(request):
    signup=get_signup_from_session(request)
    if request.method == "POST":
        form=PersonInfo_form(request.POST)
        if save_data(request,signup,form):
            return redirect("/")
        else:
            pass
    else:
        form=PersonInfo_form()
    return render(request,"personform.html",{"form":form,"signup":signup})
@custom_login_required
def BuildingInformation(request):
    signup=get_signup_from_session(request)
    if request.method == 'POST':
        form=BuildingInformation_form(request.POST)
        if save_data(request,signup,form):
            return redirect('/')
        else:
            pass
    else:
        form=BuildingInformation_form()
    return render(request,'buildingform.html',{'form':form,'signup':signup})

@custom_login_required
def TrusteesBoard(request):
    signup=get_signup_from_session(request)
    if request.method =='POST':
        form= TrusteesBoard_form(request.POST)
        if save_data(request,signup,form):
            return redirect("/")
        else:
            pass
    else:
        form=TrusteesBoard_form()
    return render (request,'boardform.html',{'form':form,'signup':signup})