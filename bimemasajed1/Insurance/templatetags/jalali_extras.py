from django import template
from django.utils.safestring import mark_safe
import jalali_utils

register = template.Library()


@register.filter
def jalali(value):
    """Convert a datetime/date to Jalali `YYYY/MM/DD` string or return None."""
    if not value:
        return None
    s = jalali_utils.to_jalali_date(value)
    return s
