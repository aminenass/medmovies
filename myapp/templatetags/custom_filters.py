# myapp/templatetags/custom_filters.py
from django import template
import random

register = template.Library()

@register.filter
def get_range(value):
    return range(value)

@register.filter
def get_length(value):
    return len(value)

@register.filter
def get_random(value):
    if isinstance(value, list) and value:  # Check if value is a non-empty list
        return random.choice(value)
    elif isinstance(value, int) and value > 0:  # Check if value is a positive integer
        return random.randrange(value)
    else:
        return None  # Return None for invalid inputs

