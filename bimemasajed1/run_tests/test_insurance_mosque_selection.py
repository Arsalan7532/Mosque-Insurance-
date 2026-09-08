import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bimemasajed1.settings')
django.setup()

from django.test import Client
from forms.models import Signup, MainRegistration
from Insurance.models import Coverage

signup, _ = Signup.objects.get_or_create(
    username='insurance_user',
    defaults={'password': 'x', 'email': 'insurance_user@example.com'}
)

m1, _ = MainRegistration.objects.get_or_create(
    registration=signup,
    mosque_id=101,
    defaults={
        'mosque_name': 'Mosque Alpha',
        'mosque_Capacity': 60,
        'mosque_postalcode': '1111111111',
        'mosque_address': 'Addr1',
        'created_phone': '09120000001',
    },
)

m2, _ = MainRegistration.objects.get_or_create(
    registration=signup,
    mosque_id=202,
    defaults={
        'mosque_name': 'Mosque Beta',
        'mosque_Capacity': 80,
        'mosque_postalcode': '2222222222',
        'mosque_address': 'Addr2',
        'created_phone': '09120000002',
    },
)

# create building records so the insurance page can proceed
from forms.models import BuildingInformation
BuildingInformation.objects.get_or_create(
    registration=m1,
    defaults={
        'total_land_area': 600,
        'total_bulding_area': 400,
        'user_type': 'مسجد',
        'structure_type': 'بتنی',
        'structure_age': 10,
        'structure_meterage': 200,
    },
)
BuildingInformation.objects.get_or_create(
    registration=m2,
    defaults={
        'total_land_area': 700,
        'total_bulding_area': 500,
        'user_type': 'مسجد',
        'structure_type': 'بتنی',
        'structure_age': 8,
        'structure_meterage': 250,
    },
)

client = Client()
session = client.session
session['username'] = signup.username
session['is_logged_in'] = True
session.save()

resp = client.get(f'/insurance/?mosque_id={m2.id}', HTTP_HOST='localhost')
print('status', resp.status_code)
content = resp.content.decode('utf-8')
print('contains selected mosque?', 'Mosque Beta' in content)
print('contains other mosque?', 'Mosque Alpha' in content)
print('contains coverage form?', 'انتخاب پوشش‌های بیمه' in content)

post_resp = client.post(
    f'/insurance/?mosque_id={m2.id}',
    data={
        'signup': signup.id,
        'mosque': m2.id,
        'vahanele_motori': 'on',
        'masouliat_ashkhas_sevom': 'on',
    },
    HTTP_HOST='localhost',
)
print('post status', post_resp.status_code)
print('coverage count for selected mosque', Coverage.objects.filter(signup=signup, mosque=m2).count())
print('coverage count for other mosque', Coverage.objects.filter(signup=signup, mosque=m1).count())

coverage = Coverage.objects.filter(signup=signup, mosque=m2).last()
print('selected mosque coverage attached?', bool(coverage and coverage.mosque_id == m2.id))
