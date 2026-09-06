import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE','bimemasajed1.settings')
django.setup()

from forms.models import Signup, MainRegistration
from Insurance.models import Coverage
from api.views import RequestQuoteAPIView
from rest_framework.test import APIRequestFactory
import json

# create or get signup
signup, _ = Signup.objects.get_or_create(username='testuser', defaults={'password':'x','email':'test@example.com'})
# create main registration
main, _ = MainRegistration.objects.get_or_create(registration=signup, defaults={'mosque_name':'Test Mosque','mosque_id':12345,'mosque_Capacity':50,'mosque_postalcode':'1234567890','mosque_address':'Test Addr','created_phone':'09120000000'})
# create coverage
coverage, _ = Coverage.objects.get_or_create(signup=signup)

factory = APIRequestFactory()
view = RequestQuoteAPIView.as_view()

# prepare request data
data = {'mosque_id': main.mosque_id}
request = factory.post('/api/RequestBime/', data, format='json')
response = view(request)

print('Status code:', response.status_code)
try:
    print(json.dumps(response.data, ensure_ascii=False, indent=2))
except Exception:
    print(response.data)
