from django.shortcuts import render,redirect
from django.contrib import messages
from forms.models import MainRegistration
from Insurance.models import Coverage
from Insurance.views import get_main_for_signup
from Insurance.services.base_calculator import BaseCalculator
from Insurance.services.coverage_calculator import CoverageCalculator

def pay(request):
    signup = getattr(request, 'session', {}).get('username')
    if not signup:
        messages.error(request, "ابتدا وارد شوید")
        return redirect('login')

    from forms.models import Signup
    user = Signup.objects.filter(username=signup).first()
    if not user:
        messages.error(request, "کاربر یافت نشد")
        return redirect('login')

    mosque_id = request.GET.get('mosque_id')
    mains = MainRegistration.objects.filter(registration=user)
    main = mains.filter(id=mosque_id).first() if mosque_id else mains.first()

    if not main:
        messages.error(request, "ابتدا اطلاعات مسجد را وارد نمایید")
        return redirect('mainform')

    coverage = Coverage.objects.filter(signup=user, mosque=main).last()
    if not coverage:
        messages.error(request, "ابتدا پوشش های خود را برای این مسجد انتخاب کنید")
        return redirect(f"/insurance/?mosque_id={main.id}")

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