import datetime
import importlib
import traceback

try:
    m = importlib.import_module('bimemasajed1.jalali_utils')
    print('loaded', hasattr(m, 'to_jalali_date'))
    print('today', m.to_jalali_date(datetime.datetime.now()))
except Exception:
    traceback.print_exc()
