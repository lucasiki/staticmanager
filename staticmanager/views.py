from django.http import JsonResponse
from django.shortcuts import render, HttpResponseRedirect
from django.urls import reverse
from django.views import View
from django.conf import settings
import os
from .models import staticManager, Staticcategory 
from django.core.paginator import Paginator
from datetime import datetime
from django.db.models import Q
import pandas as pd
from accounts.validations import user_auth, user_admin

# Create your views here.

def deletefile(f):
    try:
        path = settings.MEDIA_ROOT
        fullpath = f"{path}/{str(f)}"    
        os.remove(fullpath) 
    except Exception as Err:
        print(Err)
        return 0
    return 1

def handle_uploaded_file(f, staticpath):
    formateddate = datetime.strftime(datetime.today(), "%Y%m%d%h%M%S")
    path = f"{settings.MEDIA_ROOT}/{staticpath}"
    fullpath = f"{path}/{formateddate}-{str(f)}"

    if not os.path.exists(path):
        os.makedirs(path)


    with open(fullpath, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return (f"{staticpath}/{formateddate}-{str(f)}")

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

def processWords(df):
    listA = []
    for x in range(len(df)):
        listA.append(df.iloc[x,:])

    for object in listA:
        try:
            newmanager = staticManager()
            newmanager.keyobj = object.key
            newmanager.type = object.type
            newmanager.dimension = object.dimension

            category = Staticcategory.objects.filter(name = object.category)
            if len(category) == 0:
                Category = Staticcategory(name = object.category).save()
                category = Staticcategory.objects.filter(name = object.category)
                Category = category[0]
            else:
                Category = category[0]
            newmanager.category = Category

            if object.type == 1:
                newmanager.textobj = object.content

            if object.type == 2:    
                newmanager.textareaobj = object.content

            if object.type == 3:
                newmanager.fileobj = object.content

            if object.type == 4:
                objects = object.content.split(':')
                newmanager.linkobjh = objects[0]
                newmanager.linkobjb = objects[1]

            newmanager.save()
        except Exception as Err:
            print(Err)
            pass

#initialize#
try:
    if (len(staticManager.objects.all()) == 0):
        try:
            df = pd.read_excel('staticmanager/static/defaultwords.xlsx')
            processWords(df)
        except:
            pass
except:
    pass
#initialize#

class toggleManager(View):
    @user_admin
    def get(self, request):
        try:
            if request.session['staticmanager'] == True:
                request.session['staticmanager'] = False
                return HttpResponseRedirect(reverse('index-view'))
        except:
            pass
        request.session['staticmanager'] = True
        return HttpResponseRedirect(reverse('index-view'))


class categoryView(View):
    @user_admin
    def post(self, request):
        ret = request.POST

        if ret['key'] == 'update':
            obj = staticManager.objects.filter(id = ret['id'])[0]
            if ret['name'] != '':
                category = Staticcategory.objects.filter(name = ret['name'])
                if len(category) == 0:
                    Category = Staticcategory(name = ret['name']).save()
                    category = Staticcategory.objects.filter(name = ret['name'])
                    Category = category[0]
                else:
                    Category = category[0]
                obj.category = Category
                obj.save()
            categorys = []

        if ret['key'] == 'delete':
            Staticcategory.objects.filter(name = ret['name']).delete()
            categorys = []

        if ret['key'] == 'category':
            categorys = list(Staticcategory.objects.filter(name__icontains = ret['name']).order_by('name').values())
        
        return JsonResponse({'values': categorys})


class staticManagerView(View):
    @user_admin
    def get(self,request):
        Slug = request.GET.get('search')
        objects = staticManager.objects.all().order_by('id')
        categories = Staticcategory.objects.all().order_by('-id')
        if Slug != None:
            objects = objects.filter(
            Q(keyobj__contains=Slug) 
            | Q(textobj__contains=Slug) 
            | Q(textareaobj__contains=Slug) 
            | Q(fileobj__contains=Slug) 
            | Q(linkobjh__contains=Slug) 
            | Q(linkobjb__contains=Slug) 
            )

        Cat = request.GET.get('category')
        if Cat != None:
            Cat = categories.filter(name = Cat)[0]
            objects = objects.filter(category = Cat)

        typeSearch = request.GET.get('Type')
        if typeSearch != None:
            objects = objects.filter(type = int(typeSearch))
            

        newobj = processObjects(objects)


        paginator = Paginator(objects, 20)
        page_number = request.GET.get('page')
        objects = paginator.get_page(page_number)

        keys = ['keyobj', 'type', 'textobj', 'textareaobj', 'fileobj']


        context={
            "objects":objects,
            "keys" : keys,
            "newobj": newobj,
            "session": request.session,
            "categories": categories
            }
        return render(request, 'staticmanager/index.html', context)
    @user_admin
    def post(self,request, Slug=''):
       
        texts = request.POST
        files = request.FILES

        if texts['key'] == 'newDimension':
            obj = staticManager.objects.filter(id = texts['value'])
            obj = obj[0]
            obj.dimension = texts['newDimension']
            obj.save()
            return JsonResponse({})

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

            if texts['categoryInput'] != '':
                category = Staticcategory.objects.filter(name = texts['categoryInput'])
                if len(category) == 0:
                    Category = Staticcategory(name = texts['categoryInput']).save()
                    category = Staticcategory.objects.filter(name = texts['categoryInput'])
                    Category = category[0]
                else:
                    Category = category[0]
                newmanager.category = Category

            if texts['selectoptions'] == '1':
                newmanager.textobj = texts['text']

            if texts['selectoptions'] == '2':    
                newmanager.textareaobj = texts['textarea']

            if texts['selectoptions'] == '3':
                newmanager.fileobj = handle_uploaded_file(files['file'], 'staticfiles')
                newmanager.dimension = texts['dimensions']

            if texts['selectoptions'] == '4':
                newmanager.linkobjh = texts['linkh'] 
                newmanager.linkobjb = texts['linkb'] 

            if texts['selectoptions'] == '5':
                excel = handle_uploaded_file(files['fileexcel'], 'staticfiles')
                df = pd.read_excel('srcResearch' + settings.MEDIA_URL + excel)
                processWords(df)
                return JsonResponse({})
            newmanager.save()

        return JsonResponse({})
