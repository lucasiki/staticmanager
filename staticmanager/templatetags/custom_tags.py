from django import template
from excelupload.models import *

register = template.Library()

@register.filter()
def get_key(value, arg):
    if arg in value.__dict__:
        return value.__dict__[arg]
    else:
        return ''

@register.filter()
def get_image(value, arg):
    if arg in value:
        return value[arg]['value']
    else:
        return ''