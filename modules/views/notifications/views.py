from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from modules.models import *
from users.models import *
from modules.utils import *

@login_required
def notifications_views(request):
    if not request.user.is_superuser:
        return render(request, "error/access_denied.html")
    
    context = {}
    context = user_data(request)
    template = "notifications/main_notification.html"
    #module_id = 3
    #subModule_id = 3
    #last_module_id = request.session.get("last_module_id", 3)
    
    #print("esto contiene el last module id:", last_module_id)
    #access = get_module_user_permissions(context, subModule_id)
    #sidebar = get_sidebar(context, [1, last_module_id])
    
    #print("esto contiene el sidebar:", sidebar)
    #context["access"] = access["data"]["access"]
    #context["sidebar"] = sidebar["data"]


    #if context["access"]["read"]:
    #    template = "notifications/main_notification.html"
    #else:
    #    template = "error/access_denied.html"
    
    return render(request, template, context)