import json
from django.shortcuts import render,redirect
from django.contrib import messages
from django.forms.models import model_to_dict
from django.http import JsonResponse
from forms.models import MainRegistration, question
from .models import Coverage,Insurance
from .forms import Coverage_Form
from forms.views import get_signup_from_session 
from .services.coverage_calculator import CoverageCalculator
from .services.base_calculator import BaseCalculator
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
        #main_verbose = [(main._meta.get_field(k).verbose_name, v) for k, v in main_dict.items()]
        main_verbose = {main._meta.get_field(k).verbose_name: v for k, v in main_dict.items()}   

        # مشابه برای مدل‌های وابسته
        person_list = []
        for p in main.persons.all():
            d = model_to_dict(p)
            d.pop('id', None)
            d.pop('registration', None)

            person_list.append({
                p._meta.get_field(k).verbose_name: v
                for k, v in d.items()
            })
            
        
        board_list = []
        for b in main.TrusteesBoard.all():
            d = model_to_dict(b)
            d.pop('id', None)
            d.pop('registration', None)

            board_list.append({
                b._meta.get_field(k).verbose_name: v
                for k, v in d.items()
            })

        building_list = []
        for b in main.building.all():
            d = model_to_dict(b)
            d.pop('id', None)
            d.pop('registration', None)

            building_list.append({
                b._meta.get_field(k).verbose_name: v
                for k, v in d.items()
            })

        return {
            "data": {
                "اطلاعات مسجد": main_verbose,
                "اطلاعات خادمین": person_list,
                "اطلاعات هیات امنا": board_list,
                "اطلاعات ساختمان": building_list,
            },
            "objects": {
                "main": main,
                "buildings": main.building.all(),
            }
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

def get_main_for_signup(request):
    signup = get_signup_from_session(request)
    try:
        return MainRegistration.objects.get(registration=signup)
    except MainRegistration.DoesNotExist:
        return None
    
#def newinsurance_view(request):
    signup = get_signup_from_session(request)
    if not signup:
        messages.error(request, "ابتدا وارد شوید!")
        return redirect('login')

    data = get_all_data_for_signup(request)
    if not data:
        messages.error(request, "ابتدا اطلاعات مسجد را تکمیل کنید")
        return redirect('mainform')

    main = get_main_for_signup(request)
    if not main:
        messages.error(request, "اطلاعات مسجد ناقص است")
        return redirect('mainform')

    building = main.building.first()
    if not building:
        messages.error(request, "اطلاعات ساختمان تکمیل نشده")
        return redirect('buildform')

    base_price = BaseCalculator().calculate(building)

    # ✅ خیلی مهم: اول coverage_instance
    coverage_instance = Coverage.objects.filter(signup=signup).first()

    # آیا بیمه فعال یا صادر شده داریم؟
    active_insurance = Insurance.objects.filter(
        signup=signup,
        status__in=['active', 'issued']
    ).exists()

    # محاسبه پوشش‌ها (فقط اگر قبلاً انتخاب شده باشند)
    detail, total = {}, 0
    if coverage_instance:
        calculator = CoverageCalculator(base_price, coverage_instance)
        detail, total = calculator.calculate()

    # -------------------------
    # POST
    # -------------------------
    if request.method == 'POST':
        form = Coverage_Form(
            request.POST,
            instance=coverage_instance,
            signup=signup,
            is_endorsement=active_insurance
        )

        if form.is_valid():
            coverage = form.save(commit=False)
            coverage.signup = signup
            coverage.save()

            # ساخت یا بروزرسانی Insurance
            insurance, created = Insurance.objects.get_or_create(
                signup=signup,
                defaults={
                    'coverage': coverage,
                    'status': 'draft'
                }
            )
            if not created:
                insurance.coverage = coverage
                insurance.save()

            messages.success(request, "اطلاعات با موفقیت ثبت شد")
            return redirect('/')

    # -------------------------
    # GET
    # -------------------------
    else:
        form = Coverage_Form(
            instance=coverage_instance,
            signup=signup,
            is_endorsement=active_insurance
        )
    rates = {
        'vahanele_motori': 0.05,  # 5%
        'hazine_pezezhki': 0.07,  # 7%
        'jange_az_sanavi': 0.03,  # 3%
        'masouliat_ashkhas_sevom': 0.06,  # 6%
        'tedad_diyat': 0.04,  # 4%
        'masouliat_mojri': 0.02,  # 2%
        'tabareh_66': 0.001,  # 0.1%
        'mamooriat_kharej': 0.0012,  # 0.12%
        'gharamat_roozane': 0.002,  # 0.2%
        'hazine_kargoshay': 0.0015,  # 0.15%
        'die_increase_multipliers': {
            '1': 0.03,  # حداکثر یکسال
            '2': 0.05,  # حداکثر دو سال
            '3': 0.08,  # حداکثر سه سال
        }
    }
    return render(request, 'showdata.html', {
        'data': data,
        'form': form,
        'coverage_instance': coverage_instance,
        'detail': detail,
        'total': total,
        'base_price': base_price,
        'rate': rates,
        'is_endorsement': active_insurance,
    })

def newinsurance_view(request):
    signup = get_signup_from_session(request)
    if not signup:
        messages.error(request, "ابتدا وارد شوید!")
        return redirect('login')

    data = get_all_data_for_signup(request)
    
    if not data:
        messages.error(request, "ابتدا اطلاعات مسجد را تکمیل کنید")
        return redirect('mainform')
    
    # محاسبه نرخ پوشش‌ها
    main=get_main_for_signup(request)
    if not main :
        messages.error(request,"اطلاعات مسجد را تکمیل نمایید")
    building=main.building.first()
    base_price = BaseCalculator().calculate(building)

    coverage_instance = Coverage.objects.filter(signup=signup).first()
    detail, total = {}, 0
    if coverage_instance:
        calculator = CoverageCalculator(base_price, coverage_instance)
        detail, total = calculator.calculate()


    active_insurance = Insurance.objects.filter(
        signup=signup, 
        status__in=['active', 'issued']
    ).exists()  # آیا بیمه فعال/صادره وجود دارد؟

    # ثبت اطلاعات
    # ثبت اطلاعات
    if request.method == 'POST':

        # ❌ اگر بیمه فعال است → اجازه ویرایش نداریم
        if active_insurance:
            messages.warning(
                request,
                "بیمه‌نامه فعال است. برای تغییر پوشش‌ها باید درخواست الحاقیه ثبت شود."
            )
            return redirect('insurance')  # یا همان صفحه

        form = Coverage_Form(
            request.POST,
            instance=coverage_instance,
            signup=signup,
            is_endorsement=active_insurance
        )
        if active_insurance:
            messages.warning(request, "برای تغییر پوشش‌ها باید الحاقیه ثبت کنید")
            return redirect('insurance')

        if form.is_valid():
            coverage = form.save(commit=False)
            coverage.signup = signup
            coverage.save()

            insurance, created = Insurance.objects.get_or_create(
                signup=signup,
                defaults={
                    'coverage': coverage,
                    'status': 'draft'
                }
            )
            if not created:
                insurance.coverage = coverage
                insurance.status = 'draft'
                insurance.save()
                messages.success(request, "پوشش‌ها با موفقیت ثبت شد")
                return redirect('/')
    else:
        form = Coverage_Form(
            instance=coverage_instance,
            signup=signup,
            is_endorsement=active_insurance
        )

    # نرخ‌های پوشش‌ها برای محاسبه سمت کلاینت
    rates = {
        'vahanele_motori': 0.05,  # 5%
        'hazine_pezezhki': 0.07,  # 7%
        'jange_az_sanavi': 0.03,  # 3%
        'masouliat_ashkhas_sevom': 0.06,  # 6%
        'tedad_diyat': 0.04,  # 4%
        'masouliat_mojri': 0.02,  # 2%
        'tabareh_66': 0.001,  # 0.1%
        'mamooriat_kharej': 0.0012,  # 0.12%
        'gharamat_roozane': 0.002,  # 0.2%
        'hazine_kargoshay': 0.0015,  # 0.15%
        'die_increase_multipliers': {
            '1': 0.03,  # حداکثر یکسال
            '2': 0.05,  # حداکثر دو سال
            '3': 0.08,  # حداکثر سه سال
        }
    }

    return render(request, 'showdata.html', {
        'data': data,
        'form': form,
        'coverage_instance': coverage_instance,
        'is_endorsement': active_insurance,
        'detail': detail,
        'total': total,
        'base_price': base_price if base_price > 0 else 1000000,
        'rates': rates,
    })
def myinsurance(request):
    return render (request, 'myinsurance.html')