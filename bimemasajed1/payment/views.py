from django.shortcuts import render,redirect
from django.contrib import messages
from Insurance.models import Coverage
from Insurance.views import get_main_for_signup
from Insurance.services.base_calculator import BaseCalculator
from Insurance.services.coverage_calculator import CoverageCalculator

def pay(request):
    main=get_main_for_signup(request) #گرفتن signup و MainRegistration  -  none برمیگردونه
    if not main:
        messages.error(request, "ابتدا اطلاعات مسجد را وارد نمایید")
        return redirect('mainform')
    try:
        coverage=Coverage.objects.get(signup=main.registration)
    except Coverage.DoesNotExist:
        messages.error(request,"ابتدا پوشش های خود را انتخاب کنید")
        return redirect("insurance")# url بررسی شوددددددددددددددد
    
    building = main.building.first()
    if not building:
        messages.error(
            request,
            "اطلاعات ساختمان (زیربنا) تکمیل نشده و امکان محاسبه وجود ندارد"
        )
        return redirect("buildform")
    
    basePrice=BaseCalculator().calculate(building) #قیمت پایه
    calculator = CoverageCalculator(basePrice, coverage)
    detail, coverage_total = calculator.calculate()
    final_total = basePrice + coverage_total

    return render(request,"payment.html",{"detail_coverage":detail,"coverage_total":coverage_total,"final_total":final_total,"base_price": basePrice,"coverage":coverage})