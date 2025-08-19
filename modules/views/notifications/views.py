from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from modules.models import *
from users.models import *
from modules.utils import *
from django.core import serializers 
@login_required
def notifications_views(request):
    # Primero verificar si es superusuario
    if request.user.is_superuser:
        acceso_permitido = True
    else:
        # Buscar el rol asignado en User_Access para este usuario
        user_access = User_Access.objects.filter(user=request.user).first()
        if user_access and user_access.role.name.lower() == "administrador":
            acceso_permitido = True
        else:
            acceso_permitido = False
    
    if not acceso_permitido:
        return render(request, "error/access_denied.html")
    context = {}
    context = user_data(request)
    qs_modules = Module.objects.exclude(short_name__iexact = "usuario").values("id", "name")
    for mods in qs_modules:
        mods["path"] = mods["name"].replace(" ","-")
    context["modules"] = list(qs_modules)
    
    qs_areas = Area.objects.filter(company__name__iexact = context["company"]["name"]).values("id", "name", "company__name")
    for area in qs_areas:
        userAccess = User_Access.objects.filter(
            company__name=area["company__name"],
            area__id=area["id"]
        ).values("user__first_name", "user__last_name", "user__email", "id")
        area["correos"] = list(userAccess)
    context["areas"] = qs_areas
    
    # context_email = {
    #     "company" : context["company"]["name"],
    #     "subject" : "Prueba de correos",#Titulo del mensaje
    #     "modulo" : 2,#modulo de sia
    #     "submodulo" : "Responsiva",#tipo
    #     "item" : 26,#id del vehiculo a registrar 
    #     "title" : "Esta es una prueba para el sistema de notificaciones",
    #     "body" : "Este es el contenido que se mostrara",
    # }
    # send_notification(context_email)
    
    #module_id = 3
    subModule_id = 3
    last_module_id = request.session.get("last_module_id", 3)
    access = get_module_user_permissions(context, subModule_id)
    sidebar = get_sidebar(context, [1, last_module_id])
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]
    if context["access"]["read"]:
        template = "notifications/main_notification.html"
    else:
        template = "error/access_denied.html"
    return render(request, template, context)

def notificationRead_modules(request):
    try:
        context = {}
        init = user_data(request)
        option = request.GET.get("option")
        #TODO Loads select2 options, modules
        qs_moduls = SubModule.objects.filter(module__name__iexact = option).values("id", "name", "icon")
        context["modules"] = list(qs_moduls)
        
        #TODO Loads select2 options. items
        model_map = {
            "Equipos y herramientas": Equipment_Tools,
            "Servicios": Services,
            "Infraestructura": Infrastructure,
            "Equipos de computo": ComputerSystem,
            "Vehículo": Vehicle,
        }

        model_class = model_map.get(option)
        if model_class:
            items = model_class.objects.filter(company__name__iexact=init["company"]["name"])
            context["items"] = serializers.serialize("json", items)
        else:
            context["status"] = "error"
            context["message"] = "Sin registros"
            return JsonResponse(context, safe=False)
        
    except Exception as e:
        context["status"] = "error"
        context["message"] = str(e)
    return JsonResponse(context, safe=False)

def create_notification(request):
    try:
        context = {}
        init = user_data(request)
        fd = request.GET.get

        arr_notification = fd("notification").split("|//|")[:-1]
        arr_users = fd("users").split("|//|")[:-1]
        
        for arr in arr_notification:
            body = arr.split("||")
            for email in arr_users:
                qs_notification = Notification_System()  # Instantiate here
                
                qs_notification.mods = body[0]
                qs_notification.company = Company.objects.get(pk = init["company"]["id"])
                items = [int(x) for x in body[2].split(',')]
                if "0" in body[1]:
                    qs_notification.cats = "todos"
                    qs_notification.itemsID = items
                else:
                    for cat in body[1].split(","):
                        qs_notification.cats = SubModule.objects.get(pk=cat).name
                        qs_notification.itemsID = items
                        qs_notification.usuario = email
                        bnd = Notification_System.objects.filter(mods=body[0], cats=SubModule.objects.get(pk=cat).name, usuario=email)
                        if bnd.exists():
                            obj = bnd.first()
                            obj.itemsID = items
                            obj.status = "update"
                            obj.save()
                        else:
                            qs_notification.save()
                    continue
                qs_notification.usuario = email
                bnd = Notification_System.objects.filter(mods=body[0], cats="todos", usuario=email)
                if bnd.exists():
                    obj = bnd.first()
                    obj.itemsID = items
                    obj.status = "update"
                    obj.save()
                else:
                    qs_notification.save()
        context["status"] = "success"
        context["message"] = "Notificaciones Registradas"
    except Exception as e:
        context["status"] = "error"
        context["message"] = str(e)
    
    return JsonResponse(context, safe=False)

def read_notification(request):
    context = {}
    init = user_data(request)
    qs_notifications = list(Notification_System.objects.filter(company__id = init["company"]["id"]).values("id", "usuario", "mods", "cats", "itemsID", "active", "status"))
    
    for notification in qs_notifications:
        pass
    
    context["data"] = qs_notifications
    return JsonResponse(context, safe=False)

def delete_notification(request):
    context = {}
    try:
        fd = request.GET.get
        qs_notifications = Notification_System.objects.get(pk = fd("id"))
        qs_notifications.delete()
        context["status"] = "success"
        context["message"] = "Registro eliminado"
    except Exception as e:
        context["status"] = "error"
        context["message"] = str(e)
    return JsonResponse(context, safe=False)