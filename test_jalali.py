import os
import traceback

try:
    import importlib
    m = importlib.import_module('bimemasajed1.jalali_utils')
    from datetime import datetime
    print('jalali_utils imported ->', m.to_jalali_date(datetime.now()))

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bimemasajed1.settings')
    import django
    django.setup()
    from Insurance.models import Insurance
    print('Django setup OK; Insurance model loaded')
    ins = Insurance()
    print('Sample issued_at_jalali:', ins.issued_at_jalali)
except Exception as e:
    traceback.print_exc()
    print('ERROR:', e)
