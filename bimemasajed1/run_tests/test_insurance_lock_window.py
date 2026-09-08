import os
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bimemasajed1.settings')
import django

django.setup()

from django.test import Client
from django.utils import timezone

from forms.models import Signup, MainRegistration, BuildingInformation
from Insurance.models import Coverage, Insurance
from Insurance.views import get_mosque_policy_lock

signup, _ = Signup.objects.get_or_create(
    username='lock_user',
    defaults={'password': 'x', 'email': 'lock_user@example.com'}
)

mosque, _ = MainRegistration.objects.get_or_create(
    registration=signup,
    mosque_id=303,
    defaults={
        'mosque_name': 'Mosque Lock',
        'mosque_Capacity': 50,
        'mosque_postalcode': '303303303',
        'mosque_address': 'Addr3',
        'created_phone': '09120000003',
    },
)

BuildingInformation.objects.get_or_create(
    registration=mosque,
    defaults={
        'total_land_area': 600,
        'total_bulding_area': 400,
        'user_type': 'مسجد',
        'structure_type': 'بتنی',
        'structure_age': 10,
        'structure_meterage': 200,
    },
)

coverage, _ = Coverage.objects.get_or_create(
    signup=signup,
    mosque=mosque,
    defaults={'vahanele_motori': True},
)

Insurance.objects.create(
    signup=signup,
    coverage=coverage,
    status='issued',
    issued_at=timezone.now() - timedelta(days=10),
)

policy, lock_active, _ = get_mosque_policy_lock(signup, mosque)
assert policy is not None
assert lock_active is True

client = Client()
session = client.session
session['username'] = signup.username
session['is_logged_in'] = True
session.save()

resp = client.post(
    f'/insurance/?mosque_id={mosque.id}',
    data={
        'signup': signup.id,
        'mosque': mosque.id,
        'vahanele_motori': 'on',
    },
    HTTP_HOST='localhost',
)

count = Coverage.objects.filter(signup=signup, mosque=mosque).count()
print('lock_active', lock_active)
print('status_code', resp.status_code)
print('coverage_count', count)

assert resp.status_code == 302
assert count == 1
