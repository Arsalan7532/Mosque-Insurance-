import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bimemasajed1.settings')
import django

django.setup()

from django.test import Client

from forms.models import Signup, MainRegistration


def make_client(username):
    signup, _ = Signup.objects.get_or_create(
        username=username,
        defaults={'password': 'x', 'email': f'{username}@example.com'}
    )
    mosque, _ = MainRegistration.objects.get_or_create(
        registration=signup,
        mosque_id=8900 + len(Signup.objects.filter(username=username)),
        defaults={
            'mosque_name': 'Mosque Edit Test',
            'mosque_Capacity': 60,
            'mosque_postalcode': '1111111111',
            'mosque_address': 'Addr',
            'created_phone': '09120000000',
        },
    )
    client = Client()
    session = client.session
    session['username'] = signup.username
    session['is_logged_in'] = True
    session.save()
    return client, mosque


client, mosque = make_client('edit_user_no_policy')
resp = client.get(f'/account/mainform/?mosque_id={mosque.id}', HTTP_HOST='localhost')
content = resp.content.decode('utf-8')
assert f'?mosque_id={mosque.id}&edit=true' in content, 'No-policy mosque should expose direct edit link'
assert '/insurance/request-endorsement/' not in content, 'No-policy mosque should not force endorsement flow'

print('no_policy_edit_link_ok')
