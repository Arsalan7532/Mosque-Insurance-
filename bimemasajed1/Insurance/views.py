import json
from datetime import timedelta
from django.shortcuts import render,redirect
from django.contrib import messages
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.utils import timezone
from forms.models import MainRegistration, question
from .models import Coverage,Insurance
from .forms import Coverage_Form
from forms.views import get_signup_from_session 
import jalali_utils
from .services.base_calculator import BaseCalculator

INSURANCE_LOCK_DAYS = 365


def get_mosque_policy_lock(signup, mosque):
    policy = Insurance.objects.filter(
        signup=signup,
        coverage__mosque=mosque,
        status__in=['issued', 'payment_completed']
    ).order_by('-issued_at', '-created_at').first()

    if not policy or not policy.issued_at:
        return None, False, None

    lock_until = policy.issued_at + timedelta(days=INSURANCE_LOCK_DAYS)
    is_active = timezone.now() < lock_until
    return policy, is_active, lock_until
def get_all_data_for_main(main):
    if not main:
        return None

    main_dict = model_to_dict(main)
    main_dict.pop('id', None)
    main_dict.pop('registration', None)
    main_verbose = {main._meta.get_field(k).verbose_name: v for k, v in main_dict.items()}

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


def get_all_data_for_signup(request):
    signup = get_signup_from_session(request)
    main = MainRegistration.objects.filter(registration=signup).first()
    if not main:
        return None
    return get_all_data_for_main(main)
    
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
    if not signup:
        return None
    return MainRegistration.objects.filter(registration=signup).first()


def newinsurance_view(request):
    signup = get_signup_from_session(request)
    if not signup:
        messages.error(request, "ابتدا وارد شوید!")
        return redirect('login')

    endorsement_mode = request.GET.get('endorsement') == 'true'
    mains = MainRegistration.objects.filter(registration=signup)
    mosque_id = request.GET.get('mosque_id') or request.POST.get('mosque_id')
    selected = mains.filter(id=mosque_id).first() if mosque_id else mains.first()

    if not selected:
        messages.error(request, "ابتدا یک مسجد را انتخاب کنید")
        return redirect('mainform')

    data = get_all_data_for_main(selected)
    if not data:
        messages.error(request, "ابتدا اطلاعات مسجد را تکمیل کنید")
        return redirect('mainform')

    building = selected.building.first()
    if not building:
        messages.error(request, "اطلاعات ساختمان مسجد انتخاب‌شده تکمیل نشده است")
        return redirect(f'/account/buildform/?mosque_id={selected.id}')

    # قیمت پایه به‌صورت سرویس جدا محاسبه می‌شود.
    # در حالت endorsement فقط باید صفر شود.
    base_price = 0 if endorsement_mode else BaseCalculator().calculate(building)

    coverage_instance = Coverage.objects.filter(signup=signup, mosque=selected).last()

    active_policy, policy_lock_active, policy_lock_until = get_mosque_policy_lock(signup, selected)
    active_insurance = bool(active_policy)

    if active_policy and active_policy.issued_at and active_policy.status in ['issued', 'payment_completed']:
        if not active_policy.valid_until:
            active_policy.valid_until = active_policy.issued_at + timedelta(days=INSURANCE_LOCK_DAYS)
            active_policy.save(update_fields=['valid_until'])

    # منطق قفل‌شدگی: اگر بیمه فعال است و endorsement_mode = false، قفل کن
    form_is_locked = active_insurance and not endorsement_mode

    if request.method == 'POST':
        if policy_lock_active and not endorsement_mode:
            messages.warning(
                request,
                "بیمه این مسجد در بازه 365 روزه فعال است؛ تا پایان این مدت فقط الحاقیه مجاز است ."
            )
            return redirect(f'/insurance/?mosque_id={selected.id}')

        if active_insurance and not endorsement_mode:
            messages.warning(
                request,
                "بیمه‌نامه فعال است. برای تغییر پوشش‌ها باید درخواست الحاقیه ثبت شود."
            )
            return redirect(f'/insurance/?mosque_id={selected.id}')

        post_data = request.POST.copy()
        post_data['signup'] = str(signup.id)
        post_data['mosque'] = str(selected.id)

        form = Coverage_Form(
            post_data,
            instance=coverage_instance,
            signup=signup,
            mosque=selected,
            is_endorsement=form_is_locked
        )
        if form.is_valid():
            coverage = form.save(commit=False)
            coverage.signup = signup
            coverage.mosque = selected
            coverage.pk = None
            coverage.save()

            if endorsement_mode:
                issued_at = timezone.now()
                Insurance.objects.create(
                    signup=signup,
                    coverage=coverage,
                    status='payment_completed',
                    issued_at=issued_at,
                    valid_until=issued_at + timedelta(days=365),
                    premium_quote=None,
                )
                messages.success(request, "الحاقیه با موفقیت ثبت و برای پرداخت آماده شد")
                return redirect(f'/insurance/?mosque_id={selected.id}&endorsement=true')

            issued_at = timezone.now()
            Insurance.objects.create(
                signup=signup,
                coverage=coverage,
                status='issued',
                issued_at=issued_at,
                valid_until=issued_at + timedelta(days=365),
            )
            messages.success(request, "بیمه نامه با موفقیت در صف صدور وارد گردید")
            return redirect(f'/insurance/?mosque_id={selected.id}')
    else:
        form = Coverage_Form(
            instance=coverage_instance,
            signup=signup,
            mosque=selected,
            is_endorsement=form_is_locked
        )

    if endorsement_mode:
        return render(request, 'endorsement_edit.html', {
            'data': data,
            'form': form,
            'coverage_instance': coverage_instance,
            'is_endorsement': active_insurance,
            'endorsement_mode': True,
            'base_price': 0,
            'mains': mains,
            'selected': selected,
            'mosque_name': selected.mosque_name,
            'mosque_id': selected.id,
            'policy_lock_active': policy_lock_active,
            'policy_lock_until': policy_lock_until,
            'policy_lock_until_jalali': jalali_utils.to_jalali_date(policy_lock_until) if policy_lock_until else None,
            'active_policy': active_policy,
        })

    return render(request, 'showdata.html', {
        'data': data,
        'form': form,
        'coverage_instance': coverage_instance,
        'is_endorsement': form_is_locked,
        'endorsement_mode': endorsement_mode,
        'base_price': base_price,
        'mains': mains,
        'selected': selected,
        'mosque_name': selected.mosque_name,
        'mosque_id': selected.id,
        'policy_lock_active': policy_lock_active,
        'policy_lock_until': policy_lock_until,
        'policy_lock_until_jalali': jalali_utils.to_jalali_date(policy_lock_until) if policy_lock_until else None,
        'active_policy': active_policy,
    })

def request_endorsement(request):
    signup = get_signup_from_session(request)
    if not signup:
        messages.error(request, 'ابتدا وارد شوید!')
        return redirect('login')

    mosque_id = request.GET.get('mosque_id')
    if not mosque_id:
        messages.warning(request, 'هیچ مسجدی برای درخواست الحاقیه انتخاب نشده است.')
        return redirect('insurance')

    selected = MainRegistration.objects.filter(registration=signup, id=mosque_id).first()
    if not selected:
        messages.error(request, 'مسجد انتخابی پیدا نشد.')
        return redirect('mainform')

    request.session['endorsement_mosque_id'] = selected.id
    return redirect(f'/insurance/?mosque_id={selected.id}&endorsement=true')


def myinsurance(request):
    signup = get_signup_from_session(request)
    if not signup:
        messages.error(request, 'ابتدا وارد شوید!')
        return redirect('login')

    insurances = Insurance.objects.filter(signup=signup).select_related('coverage__mosque').order_by('-created_at')
    rows = []
    for insurance in insurances:
        mosque = None
        if insurance.coverage and insurance.coverage.mosque:
            mosque = insurance.coverage.mosque

        lock_until = None
        locked = False
        remaining_days = None

        if insurance.issued_at:
            lock_until = insurance.issued_at + timedelta(days=INSURANCE_LOCK_DAYS)
            locked = timezone.now() < lock_until
            remaining_days = max(0, (lock_until - timezone.now()).days)

        # jalali representations for templates
        issued_at_jalali = None
        lock_until_jalali = None
        if insurance.issued_at:
            issued_at_jalali = jalali_utils.to_jalali_date(insurance.issued_at)
        if lock_until:
            lock_until_jalali = jalali_utils.to_jalali_date(lock_until)

        rows.append({
            'insurance': insurance,
            'mosque': mosque,
            'lock_until': lock_until,
            'locked': locked,
            'remaining_days': remaining_days,
            'issued_at_jalali': issued_at_jalali,
            'lock_until_jalali': lock_until_jalali,
            'status_label': dict(Insurance.STATUS_CHOICES).get(insurance.status, insurance.status),
            'is_issued': insurance.status in ['issued', 'payment_completed'],
        })

    return render(request, 'myinsurance.html', {'rows': rows})