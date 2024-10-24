from django.http import HttpResponse
from users.models import *
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.template.loader import render_to_string
from decouple import config

def get_module_user_permissions(_datos, _subModule_id):
    response = {"success": True, "data": {"info":{}, "access": {}}}
    response["data"]["access"] = {"create": False, "read": False, "update": False, "delete": False}

    if _datos["role"]["id"] in [1,2]:
        response["data"]["access"] = {key: True for key in response["data"]["access"]}
    else:
        obj = SubModule_Permission.objects.filter(user_id__user_id = _datos["user"]["id"], subModule_id = _subModule_id)
        
        if obj.count() > 0:
            obj = obj.values(
                "id", "subModule__module_id", "subModule_id",
                "create", "read", "update", "delete"
            )[0]
            response["data"]["access"]["create"] = obj["create"]
            response["data"]["access"]["read"] = obj["read"]
            response["data"]["access"]["update"] = obj["update"]
            response["data"]["access"]["delete"] = obj["delete"]
            # response["data"]["info"]["module_id"] = obj["submodule__module_id"]
            pass
    return response

def get_sidebar(data={}, module_ids=None):
    response = {"success": True, "data": {}}
    sidebar_data = []

    if data["role"]["id"] in [1,2]:
        submodules = SubModule.objects.filter(
            is_active=True
        ).order_by('module_id')

        if data["role"]["id"] in [2]:
            submodules = submodules.exclude(superUserExclusive = True)

        if module_ids is not None:
            if isinstance(module_ids, int):
                module_ids = [module_ids]
            submodules = submodules.filter(module_id__in=module_ids)
    else:
        submodules = SubModule_Permission.objects.filter(
            subModule__is_active = True,
            read = True,
            user_id__user_id = data["user"]["id"]
        ).order_by('subModule__module_id')

        if module_ids is not None:
            if isinstance(module_ids, int):
                module_ids = [module_ids]
            submodules = submodules.filter(subModule__module_id__in=module_ids)

    modules = {}
    for submodule in submodules:
        module_name = submodule.subModule.module.name if hasattr(submodule, 'subModule') else submodule.module.name
        if module_name not in modules:
            modules[module_name] = []
        modules[module_name].append({
            "title": submodule.subModule.short_name if hasattr(submodule, 'subModule') else submodule.short_name,
            "icon": submodule.subModule.icon if hasattr(submodule, 'subModule') else submodule.icon,
            "link": submodule.subModule.link if hasattr(submodule, 'subModule') else submodule.link
        })

    sidebar_data = [{"title": module_name, "submodules": submodules_data} for module_name, submodules_data in modules.items()]

    response["data"] = sidebar_data
    return response

def get_user_access(context = {}):
    response = {"success": True}
    data = {}

    if context["role"]["id"] in [1,2]:
        obj = SubModule.objects.values().exclude(is_active=False)
        for item in obj:
            data[item["id"]] = {}
            data[item["id"]]["create"] = True
            data[item["id"]]["read"] = True
            data[item["id"]]["update"] = True
            data[item["id"]]["delete"] = True
    else:
        obj = SubModule_Permission.objects.filter(
            user_id__user_id = context["user"]["id"]
        ).values()
        
        for item in obj:
            data[item["subModule_id"]] = {}
            data[item["subModule_id"]]["create"] = item["create"]
            data[item["subModule_id"]]["read"] = item["read"] 
            data[item["subModule_id"]]["update"] = item["update"] 
            data[item["subModule_id"]]["delete"] = item["delete"]
    response["data"] = data
    return response


def update_session_data(request):
    # Obtener el usuario actual
    user = request.user
    
    # Crear un diccionario con los datos del usuario
    user_data = {
        'id': user.id,
        'username': user.username,
        'name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
    }

    # Obtener el acceso del usuario
    access = User_Access.objects.filter(user=user).first()

    # Crear un diccionario con los datos de sesión
    session_data = {
        'access': {'id': None},
        'role': {'id': 4, 'name': None, 'level': None},
        'company': {'id': None, 'name': None},
        'user': user_data,
        'area': {'id': None, 'name': None}
    }
    # Actualizar el diccionario de datos de sesión si hay acceso
    if access:
        session_data.update({
            'access': {'id': access.id},
            'role': {
                'id': access.role_id,
                'name': access.role.name,
                'level': access.role.level,
            },
            'company': {
                'id': access.company.id,
                'name': access.company.name,   
            },
            'area': {
                'id': access.area.id,
                'name': access.area.name,
            }
        })
    # Actualizar la sesión con los datos recopilados
    request.session.update(session_data)

def user_data(request):
    context = {}
    # Verificar y actualizar los datos de sesión
    print(request.session.get('access'))
    if not request.session.get('company') or not request.session.get('area'):
        update_session_data(request)
        context["success"] = True

    # Obtener los datos de sesión y agregarlos al contexto
    context.update({ key: request.session.get(key, {}) for key in ["access", "role", "user", "company", "area"] })
    return context