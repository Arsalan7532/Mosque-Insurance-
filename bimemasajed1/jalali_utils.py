import datetime


def to_jalali_date(dt):
    """Convert a datetime/date to Jalali `YYYY/MM/DD` string.

    If `jdatetime` is not available, fall back to Gregorian `YYYY/MM/DD`.
    This avoids import-time failures when the dependency isn't installed.
    """
    if not dt:
        return None
    try:
        import jdatetime
        try:
            return jdatetime.datetime.fromgregorian(datetime=dt).strftime('%Y/%m/%d')
        except Exception:
            try:
                return jdatetime.date.fromgregorian(date=dt).strftime('%Y/%m/%d')
            except Exception:
                return None
    except Exception:
        # fallback: return Gregorian date string
        try:
            return dt.strftime('%Y/%m/%d')
        except Exception:
            return None
