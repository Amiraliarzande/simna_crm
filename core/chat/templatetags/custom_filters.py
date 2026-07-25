# chat/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """دریافت آیتم از دیکشنری با کلید"""
    if dictionary is None:
        return []
    return dictionary.get(key, [])