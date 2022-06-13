from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from srcResearch import settings
import os
from .models import staticManager 
from django.core.paginator import Paginator
from datetime import datetime
from django.db.models import Q

# Create your views here.

def deletefile(f):
    try:
        path = settings.MEDIA_ROOT
        fullpath = path + '\\' + str(f)    
        os.remove(fullpath) 
    except Exception as Err:
        print(Err)
        return 0
    return 1

def handle_uploaded_file(f, staticpath):
    formateddate = datetime.strftime(datetime.today(), "%Y%m%d%h%M%S")
    path = settings.MEDIA_ROOT + '\\' + staticpath
    fullpath = path + '\\' + formateddate + '-' +str(f)

    if not os.path.exists(path):
        os.makedirs(path)

    with open(fullpath, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return (staticpath + '\\' + formateddate + '-' + str(f))

def processObjects(objects):
    newobj = {}
    for object in objects:
        newobj[object.keyobj] = {}
        if object.type==3:
            newobj[object.keyobj]['value'] = settings.MEDIA_URL + object.fileobj
        elif object.type==2:
            newobj[object.keyobj]['value'] = object.textareaobj
        else:
            newobj[object.keyobj]['value'] = object.textobj
        newobj[object.keyobj]['id'] = object.id
        newobj[object.keyobj]['type'] = object.type 

    return newobj

    


class staticManagerView(View):
    def get(self,request, Slug = None):
        objects = staticManager.objects.all().order_by('id')
        if Slug != None:
            objects = objects.filter(
            Q(keyobj__contains=Slug) 
            | Q(textobj__contains=Slug) 
            | Q(textareaobj__contains=Slug) 
            | Q(fileobj__contains=Slug) 
            | Q(linkobjh__contains=Slug) 
            | Q(linkobjb__contains=Slug) 
            )

        newobj = processObjects(objects)


        paginator = Paginator(objects, 20)
        page_number = request.GET.get('page')
        objects = paginator.get_page(page_number)

        keys = ['keyobj', 'type', 'textobj', 'textareaobj', 'fileobj']


        context={
            "objects":objects,
            "keys" : keys,
            "newobj": newobj
            }
        return render(request, 'staticmanager/index.html', context)

    def post(self,request):
        texts = request.POST
        files = request.FILES

        if texts['key'] == 'newlink':
            obj = staticManager.objects.filter(id = texts['value'])
            obj = obj[0]
            obj.linkobjh = texts['newlinkh']
            obj.linkobjb = texts['newlinkb']
            obj.save()
            return JsonResponse({})

        if texts['key'] == 'newtext':
            obj = staticManager.objects.filter(id = texts['value'])
            obj = obj[0]
            obj.textobj = texts['newtext']
            obj.save()
            return JsonResponse({})

        if texts['key'] == 'newarea':
            obj = staticManager.objects.filter(id = texts['value'])
            obj = obj[0]
            obj.textareaobj = texts['newarea']
            obj.save()
            return JsonResponse({})

        if texts['key'] == 'newfile':
            obj = staticManager.objects.filter(id = texts['value'])
            deletefile(obj[0].fileobj)
            ret = handle_uploaded_file(files['file'], 'staticfiles')
            obj = obj[0]
            obj.fileobj = ret
            obj.save()

            return JsonResponse({})

        if texts['key'] == 'delete':
            obj = staticManager.objects.filter(id = texts['value'])
            if obj[0].type == 3:
                deletefile(obj[0].fileobj)
            obj.delete()
            return JsonResponse({})

        if texts['key'] == 'newkey':
            if texts['selectoptions'] == '0':
                return JsonResponse({})

            newmanager = staticManager()
            newmanager.keyobj = texts['keyvalue']
            newmanager.type = texts['selectoptions']

            if texts['selectoptions'] == '1':
                newmanager.textobj = texts['text']

            if texts['selectoptions'] == '2':    
                newmanager.textareaobj = texts['textarea']

            if texts['selectoptions'] == '3':
                newmanager.fileobj = handle_uploaded_file(files['file'], 'staticfiles')

            if texts['selectoptions'] == '4':
                newmanager.linkobjh = texts['linkh'] 
                newmanager.linkobjb = texts['linkb'] 

            newmanager.save()

        return JsonResponse({})