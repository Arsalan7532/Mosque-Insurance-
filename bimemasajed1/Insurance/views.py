from django.shortcuts import render,redirect
from django.contrib import messages
from django.forms.models import model_to_dict
from django.http import JsonResponse
from forms.models import MainRegistration, question
from .models import Coverage
from .forms import Coverage_Form
from forms.views import get_signup_from_session 
from .services.coverage_calculator import CoverageCalculator
def get_all_data_for_signup(request):
    signup = get_signup_from_session(request)
    try:
        main = MainRegistration.objects.get(registration=signup)
        
        # تبدیل مدل به دیکشنری
        main_dict = model_to_dict(main)
        # حذف فیلدهای id و registration
        main_dict.pop('id', None)
        main_dict.pop('registration', None)
        
        # نگاشت به verbose_name
        main_verbose = {main._meta.get_field(k).verbose_name: v for k, v in main_dict.items()}
        
        # مشابه برای مدل‌های وابسته
        person_list = []
        for p in main.persons.all():
            d = model_to_dict(p)
            d.pop('id', None)
            d.pop('registration', None)
            person_list.append({p._meta.get_field(k).verbose_name: v for k, v in d.items()})
        
        board_list = []
        for b in main.TrusteesBoard.all():
            d = model_to_dict(b)
            d.pop('id', None)
            d.pop('registration', None)
            board_list.append({b._meta.get_field(k).verbose_name: v for k, v in d.items()})

        building_list=[]
        for b in main.building.all():
            d = model_to_dict(b)
            d.pop('id', None)
            d.pop('registration', None)
            building_list.append({b._meta.get_field(k).verbose_name: v for k, v in d.items()})

        return {
            "اطلاعات مسجد": main_verbose,
            "اطلاعات خادمین": person_list,
            "اطلاعات هیات امنا": board_list,
            "اطلاعات ساختمان":building_list,
        }
        
    except MainRegistration.DoesNotExist:
        return None
def alldata_json(request):
    if request.method=='POST':
        signup = get_signup_from_session(request)
        if not signup:
            messages.error(request, "ابتدا وارد شوید!")
            return redirect('login')

        data = get_all_data_for_signup(signup)
        if not data:
            messages.error(request, "ابتدا اطلاعات مسجد را تکمیل کنید")
            return redirect('mainform')
        return JsonResponse(data)
    else:
        return redirect('/')
def newinsurance_view(request):
    signup = get_signup_from_session(request)
    if not signup:
        messages.error(request, "ابتدا وارد شوید!")
        return redirect('login')

    data = get_all_data_for_signup(request)
    if not data:
        messages.error(request, "ابتدا اطلاعات مسجد را تکمیل کنید")
        return redirect('mainform')
    
    coverage_instance = Coverage.objects.filter(signup=signup).first()
    is_endorsement = request.GET.get('endorsement') == 'true' # if ==true ?endorsement=true

    # محاسبه نرخ پوشش‌ها
    calculator = CoverageCalculator(coverage_instance, data['اطلاعات مسجد'])
    detail, total = calculator.calculate()

    if request.method == 'POST':
        form = Coverage_Form(request.POST, instance=coverage_instance)
        if form.is_valid():
            form.save()
            messages.success(request, "اطلاعات با موفقیت ثبت شد")
            return redirect('/')  # یا همان صفحه
    else:
        form = Coverage_Form(instance=coverage_instance)

    return render(request, 'showdata.html', {
        'data': data,
        'form': form,
        'coverage_instance': coverage_instance,
        'is_endorsement': is_endorsement,
        'detail': detail,
        'total': total,
    })
def myinsurance(request):
    return render (request, 'myinsurance.html')