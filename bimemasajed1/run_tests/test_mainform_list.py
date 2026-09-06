import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE','bimemasajed1.settings')
django.setup()

from django.test import Client
from forms.models import Signup, MainRegistration

signup, _ = Signup.objects.get_or_create(username='testuser2', defaults={'password':'x','email':'test2@example.com'})
# create two mosques
m1, _ = MainRegistration.objects.get_or_create(registration=signup, mosque_id=111, defaults={'mosque_name':'Mosque One','mosque_Capacity':50,'mosque_postalcode':'1111111111','mosque_address':'Addr1','created_phone':'09121111111'})
m2, _ = MainRegistration.objects.get_or_create(registration=signup, mosque_id=222, defaults={'mosque_name':'Mosque Two','mosque_Capacity':100,'mosque_postalcode':'2222222222','mosque_address':'Addr2','created_phone':'09122222222'})

c = Client()
# set session keys
session = c.session
session['username'] = signup.username
session['is_logged_in'] = True
session.save()

resp = c.get('/account/mainform/', HTTP_HOST='localhost')
print('status', resp.status_code)
content = resp.content.decode('utf-8')
print('contains Mosque One?', 'Mosque One' in content)
print('contains Mosque Two?', 'Mosque Two' in content)
