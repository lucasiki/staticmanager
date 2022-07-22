from django import template
from django.conf import settings
from staticmanager.models import staticManager

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
    
@register.filter()
def staticmanager(value, arg):
    try:
        arg = arg.split(':')
        obj = staticManager.objects.filter(keyobj=arg[0])[0]
        returner=''
        if obj.type == 1:
            returner = obj.textobj
        if obj.type == 2:
            returner = obj.textareaobj
        if obj.type == 3:
            returner = settings.MEDIA_URL + obj.fileobj
        if obj.type == 4:
            if arg[1] == 'h':
                returner = obj.linkobjh

            else:
                returner = obj.linkobjb


        return returner
    except:
        try: 
            value2 = value.split(':')
            if value2[1] == 'static':
                value = settings.STATIC_URL + value2[0]
                print(value)
        except:
            pass
    return value

@register.inclusion_tag('staticmanager/image.html', takes_context = True)
def staticPhoto(context, obj):

    obj = staticManager.objects.filter(keyobj=obj)
    if len(obj) == 0:
        return
    obj = obj[0]
    dimension = ''
    width = ''
    height = ''
    try:
        if obj.dimension != '':
            newdimension = obj.dimension.split(' ')
            width = newdimension[0]
            height = newdimension[1]
    except:
        dimension = ''

    imageSrc = settings.MEDIA_URL + obj.fileobj
    
    try:
        enabled = context['session']['staticmanager']
    except:
        enabled = False
    return{
        'width':width,
        'height':height,
        'imageSrc':imageSrc,
        'imageAlt': obj.keyobj,
        'user':context['user'],
        'enabled':enabled
    }

@register.inclusion_tag('staticmanager/texts.html', takes_context = True)
def staticText(context, obj):

    obj = staticManager.objects.filter(keyobj=obj)
    if len(obj) == 0:
        return
    obj = obj[0]

    returner = ''
    if obj.type == 1:
        returner = obj.textobj
    if obj.type == 2:
        returner = obj.textareaobj


    try:
        enabled = context['session']['staticmanager']
    except:
        enabled = False
    return{
        'text':returner,
        'key': obj.keyobj,
        'user':context['user'],
        'enabled':enabled
    }

@register.inclusion_tag('staticmanager/links.html', takes_context = True)
def staticLink(context, obj):

    obj = staticManager.objects.filter(keyobj=obj)
    if len(obj) == 0:
        return
    obj = obj[0]

    if obj.type == 1:
        returnerLink = obj.textobj
        returnerText = obj.textobj
    if obj.type == 2:
        returnerLink = obj.textareaobj
        returnerText = obj.textareaobj
    if obj.type == 4:
        returnerLink = obj.linkobjb
        returnerText = obj.linkobjh

    try:
        enabled = context['session']['staticmanager']
    except:
        enabled = False
    return{
        'link':returnerLink,
        'text':returnerText,
        'key': obj.keyobj,
        'user':context['user'],
        'enabled':enabled
    }
