from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect, HttpResponse
from django.db.models import F, Q, Value, Max, Sum, CharField, BooleanField
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from modules.models import *
from users.models import *
from datetime import datetime, timedelta
import json, os
import requests
import random
from decimal import Decimal
from modules.utils import *

# TODO --------------- [ VIEWS ] --------------- 
@login_required
def companys_views(request):
    context = user_data(request)
    module_id = 1
    subModule_id = 2
    last_module_id = request.session.get("last_module_id", 2)

    access = get_module_user_permissions(context, subModule_id)
    sidebar = get_sidebar(context, [1, last_module_id])
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]

    if context["access"]["read"]:
        template = "users/companys.html"
    else:
        template = "error/access_denied.html"
    return render(request, template, context)

@login_required
def users_views(request):
    context = user_data(request)
    module_id = 1
    subModule_id = 2
    last_module_id = request.session.get("last_module_id", 2)

    access = get_module_user_permissions(context, subModule_id)
    sidebar = get_sidebar(context, [1, last_module_id])
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]

    if context["access"]["read"]:
        template = "users/users.html"
    else:
        template = "error/access_denied.html"
    return render(request, template, context)

@login_required
def providers_views(request):
    context = user_data(request)
    module_id = 3
    subModule_id = 3
    last_module_id = request.session.get("last_module_id", 2)

    access = get_module_user_permissions(context, subModule_id)
    sidebar = get_sidebar(context, [1, last_module_id])

    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]


    if context["access"]["read"]:
        template = "users/proviers.html"
    else:
        template = "error/access_denied.html"
    return render(request, template, context)

def areas_views(request):
    context = user_data(request)
    module_id = 3
    subModule_id = 3
    last_module_id = request.session.get("last_module_id", 2)

    access = get_module_user_permissions(context, subModule_id)
    sidebar = get_sidebar(context, [1, last_module_id])

    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]


    if context["access"]["read"]:
        template = "users/areas.html"
    else:
        template = "error/access_denied.html"
    return render(request, template, context)

# usuario
def users_profile_view(request):
    context = user_data(request)

    subModule_id = 0
    last_module_id = request.session.get("last_module_id", 2)

    # access = get_module_user_permissions(context, subModule_id)
    sidebar = get_sidebar(context, [1, last_module_id])
    
    # context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]

    return render(request, 'users/profile.html', context)

# TODO --------------- [ REQUEST ] ---------------


def add_user_with_access(request):
    response = {"success": False}
    context = user_data(request)
    dt = request.POST

    # Obtener los datos del formulario del request
    username = dt.get('username', '').title().strip()
    password = dt.get('password', '').strip()
    email = dt.get('email', '').strip()
    first_name = dt.get('name', '').strip()
    last_name = dt.get('last_name', '').strip()
    company_id = context.get("company", {}).get("id")
    role_id = dt.get('role', 4)
    area_id = dt.get('area_id')

    # Validar que la empresa está asignada
    if not company_id:
        response["message"] = "Tu usuario no cuenta con una empresa asignada"
        return JsonResponse(response, status=400)

    # Validar que todos los campos requeridos están presentes
    if not all([username, password, email, first_name, last_name]):
        response["message"] = "Todos los campos son obligatorios."
        return JsonResponse(response, status=400)
    
    # Verificar si el nombre de usuario ya existe
    if User.objects.filter(username=username).exists():
        response["message"] = f"El usuario '{username}' ya existe."
        return JsonResponse(response, status=409)
    
    try:
        with transaction.atomic():
            # Crear el usuario (la contraseña se encripta automáticamente)
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            
            # Crear el registro de acceso
            User_Access.objects.create(
                user_id = user.id,
                role_id = role_id,
                company_id = company_id,
                area_id = area_id
            )
        response["status"] = "success"
        response["message"] = "Usuario creado exitosamente"
        return JsonResponse(response, status=201)
    except ValidationError as ve:
        response["message"] = f"Error de validación: {str(ve)}"
        return JsonResponse(response, status=400)
    except Exception as e:
        response["message"] = f"Error inesperado: {str(e)}"
        return JsonResponse(response, status=500)
    return JsonResponse(response, status=200)

# Obtener un usuaro con acceso
def get_user_with_access(request):
    response = {"success": False}
    return JsonResponse(response)

# Obtener a todos los usuarios con acceso
def get_users_with_access(request):
    context = user_data(request)
    response = {"success": False}
    dt = request.GET
    module_id = 1
    subModule_id = 2
    isList = dt.get("isList", False)

    lista = User_Access.objects.values(
        "id",
        "user_id", "user__username", "user__first_name", "user__last_name", "user__email", "user__is_active",
        "role__id", "role__name",
        "company_id", "company__name",
        "area_id", "area__code", "area__name",
    )
    
    if isList:
        lista = lista.filter(
            company_id = context["company"]["id"]
        ).values(
            "id",
            "user_id",
            "user__username",
            "user__first_name",
            "user__last_name"
        )
    else:
        access = get_module_user_permissions(context, subModule_id)
        access = access["data"]["access"]

        for item in lista:
            item["btn_option"] = ""
            if access["update"] and item["user_id"] != context["user"]["id"]:
                if not item["role__id"] in [1,2]:
                    item["btn_option"] += "<button type=\"button\" name=\"key\" class=\"btn btn-icon btn-sm btn-primary-light\" data-user=\"show-user-permissions\" aria-label=\"keys\">" \
                        "<i class=\"fa-solid fa-key\"></i>" \
                    "</button>\n"
                item["btn_option"] += "<button type=\"button\" name=\"update\" class=\"btn btn-icon btn-sm btn-primary-light\" data-user=\"update-item\" aria-label=\"update\">" \
                        "<i class=\"fa-solid fa-pen\"></i>" \
                    "</button>\n"
            if access["delete"] and item["user_id"] != context["user"]["id"]:
                item["btn_option"] += "" \
                "<button type=\"button\" name=\"delete\" class=\"btn btn-icon btn-sm btn-danger-light\" data-user=\"dalete-item\" aria-label=\"delete\">" \
                    "<i class=\"fa-solid fa-trash\"></i>" \
                "</button>\n"
        pass
    
    response["data"] = list(lista)
    response["success"] = True

    return JsonResponse(response)

# Actualizar usuario con acceso
def update_user_with_access(request):
    response = { "status": "success" }
    context = user_data(request)
    dt = request.POST

    # Obtener los datos del formulario del request
    username = dt.get('username', '').title().strip()
    password = dt.get('password', '').strip()
    email = dt.get('email', '').strip()
    first_name = dt.get('name', '').strip()
    last_name = dt.get('last_name', '').strip()
    company_id = context.get("company", {}).get("id")
    role_id = dt.get('role', 4)
    user_id = dt.get('user_id')
    area_id = dt.get("area_id")

    # Validar que todos los campos necesarios están presentes
    if not user_id:
        response["error"] = {"message": "El ID del usuario es obligatorio."}
        return JsonResponse(response)

    if not company_id:
        response["error"] = {"message": "Tu usuario no cuenta con una empresa asignada"}
        return JsonResponse(response)
    
    try:
        with transaction.atomic():
            # Obtener el usuario a actualizar
            user = User.objects.get(id=user_id)

            # Actualizar los datos del usuario
            if username:
                if User.objects.filter(username=username).exclude(id=user_id).exists():
                    response["status"] = "warning"
                    response["message"] = f"El usuario '{username}' ya existe."
                    return JsonResponse(response, status=409)
            user.username = username.title()
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            if password:
                user.set_password(password)
            user.save()

            # Actualizar los datos de acceso
            access_record, created = User_Access.objects.get_or_create(user=user)
            access_record.role_id = role_id
            access_record.company_id = company_id
            access_record.area_id = area_id
            access_record.save()

        response["status"] = "success"
        response["message"] = "Usuario actualizado exitosamente"
        return JsonResponse(response, status=200) # 200 OK
    except User.DoesNotExist:
        response["error"] = {"message": "El usuario no existe."}
        return JsonResponse(response, status=404)  # 404 Not Found
    except ValidationError as ve:
        response["error"] = {"message": f"Error de validación: {str(ve)}"}
        return JsonResponse(response, status=400)  # 400 Bad Request
    except Exception as e:
        response["error"] = {"message": f"Error inesperado: {str(e)}"}
        return JsonResponse(response, status=500)
    return JsonResponse(response)

# Obtener todos los permisos del usuario que tiene acceso a SIA
def get_userPermissions(request):
    context = user_data(request)
    response = {"success": True, "data": []}
    dt = request.GET
    user_id = dt.get("user_id")

    if not user_id:
        # Si no se proporciona user_id, devolver una lista vacía
        return JsonResponse(response)

    # Obtener los permisos del usuario
    permisos = SubModule_Permission.objects.filter(user_id=user_id)

    # Crear un diccionario de permisos por módulo
    permisos_por_modulo = {
        permiso["subModule_id"]: permiso 
        for permiso in permisos.values("subModule_id", "create", "read", "update", "delete")
    }

    # Obtener los módulos activos
    modulos = SubModule.objects.filter(is_active=True).select_related("module")

    # Iterar sobre los módulos y asignar los permisos correspondientes
    for modulo in modulos:
        datos = {
            "module_name": modulo.module.name,
            "submodule_id": modulo.id,
            "submodule_name": modulo.name,
            "create": False,
            "read": False,
            "update": False,
            "delete": False
        }

        # Si hay permisos para este módulo, actualizar los datos con los permisos correspondientes
        permiso_modulo = permisos_por_modulo.get(modulo.id)
        if permiso_modulo:
            datos.update(permiso_modulo)

        response["data"].append(datos)
    response["success"] = True
    return JsonResponse(response)

# Denegar o dar acceso a [Create, Read, Update, Delete] de un submodulo de un usuario con acceso a SIA
def update_userPermissions(request):
    response = {"success": False}
    dt = request.POST

    user_id = dt.get("user_id")
    submodule_id = dt.get("submodule_id", None)
    campo_db = dt.get("permission_type")
    checked = True if dt.get("checked") == "true" else False

    permiso = SubModule_Permission.objects.filter(subModule_id = submodule_id, user_id = user_id)
    
    # return JsonResponse(response)
    if permiso.exists():
        """ El Permiso existe y solo se actualiza """
        # update_data = {campo_db: checked}
        # permiso.update(**update_data)
    else:
        """ El Permiso No existe. proceder a guardarlo """
        add_data = {campo_db: checked}
        new_permiso = SubModule_Permission(
            subModule_id = submodule_id,
            user_id = user_id,
            **add_data
        )
        new_permiso.save()
    response["success"] = True
    return JsonResponse(response)


def get_companys(request):
    response = {"success": False}
    dt = request.GET
    isList = dt.get("isList", False)

    lista = Company.objects.values()

    if isList:
        lista = lista.values("id", "name")

    response["data"] = list(lista)
    response["success"] = True
    return JsonResponse(response)


def add_provider(request):
    response = {"success": False}
    context = user_data(request)
    dt = request.POST
    company_id = context["company"]["id"]

    try:
        name = dt.get("name").title().strip()
        # Verificar si ya existe un proveedor con el mismo nombre
        if Provider.objects.filter(name=name, company_id=company_id).exists():
            response["status"] = "warning"
            response["message"] = "Ya existe un proveedor con este nombre."
            return JsonResponse(response)
        obj = Provider(
            name = name,
            company_id = company_id,
            phone_number = dt.get("phone_number"),
            address = dt.get("address"),
            is_active = dt.get("is_active", True)
        )
        obj.save()
        response["id"] = obj.id
        response["status"] = "success"
        response["message"] = "Proveedor registrado exitosamente"
    except ValidationError as e:
        response["status"] = "error"
        response["message"] = str(e)
    except Exception as e:
        response["status"] = "false"
        response["message"] = str(e)
    return JsonResponse(response)

def get_providers(request):
    response = {"success": False}
    context = user_data(request)
    dt = request.GET
    isList = dt.get("isList", False)
    company_id = context["company"]["id"]
    subModule_id = 2

    lista = Provider.objects.filter(company_id = company_id).values()

    if isList:
        lista = lista.values("id", "name").exclude(is_active=False)
    
    if not isList:
        access = get_module_user_permissions(context, subModule_id)
        access = access["data"]["access"]
        for item in lista:
            item["btn_action"] = ""
            if access["update"]:
                item["btn_action"] += """<button class=\"btn btn-icon btn-sm btn-primary-light" data-sia-provider=\"update-item\">
                    <i class="fa-solid fa-pen"></i>
                </button>\n"""
            if access["delete"]:
                item["btn_action"] += """<button class=\"btn btn-icon btn-sm btn-danger-light\" data-sia-provider=\"delete-item\">
                    <i class="fa-solid fa-trash"></i>
                </button>\n"""
        pass

    response["data"] = list(lista)
    response["success"] = True
    return JsonResponse(response)

def update_provider(request):
    response = {"success": False}
    context = user_data(request)
    dt = request.POST
    id = dt.get("id", None)
    is_active = bool(int(request.POST.get("is_active", "0")))
    company_id = context["company"]["id"]

    if not id:
        response["status"] = "warning"
        response["message"] = "No se proporcionó un ID válido"
        return JsonResponse(response)

    try:
        obj = Provider.objects.get(id=id)
    except Provider.DoesNotExist:
        response["status"] = "warning"
        response["message"] = f"No existe ningún registro con el ID '{id}'"
        return JsonResponse(response)
    
    try:
        obj.name = dt.get("name")
        obj.company_id = company_id
        obj.phone_number = dt.get("phone_number")
        obj.address = dt.get("address")
        obj.is_active = is_active
        obj.save()

        response["status"] = "success"
        response["message"] = "Registro actualizado exitosamente"
    except Exception as e:
        response["success"] = False
        response["error"] = {"message": str(e)}
    return JsonResponse(response)

def delete_provider(request):
    response = {"success": False, "data": []}
    dt = request.POST
    id = dt.get("id", None)

    if id == None:
        response["error"] = {"message": "Proporcione un id valido", "id": id}
        return JsonResponse(response)

    try:
        obj = Provider.objects.get(id = id)
    except Provider.DoesNotExist:
        response["error"] = {"message": "El objeto no existe"}
        return JsonResponse(response)
    else:
        obj.delete()
    response["success"] = True
    return JsonResponse(response)



def add_area(request):
    response = {"success": False}
    context = user_data(request)
    dt = request.POST
    id = dt.get("id", None)
    is_active = bool(int(request.POST.get("is_active", "1")))
    company_id = context["company"]["id"]

    filtro = Area.objects.filter(
        company_id = company_id,
        code = dt.get("code"),
        name = dt.get("name")
    ).exists()

    if filtro:
        response["error"] = {"message": f"Ya existe esta la area {dt.get('name')}"}
        return JsonResponse(response)
    
    try:
        obj = Area(
            company_id = company_id,
            code = dt.get("code"),
            name = dt.get("name"),
            description = dt.get("description"),
            is_active = is_active
        )
        obj.save()

        response["id"] = obj.id
        response["success"] = True
    except Exception as e:
        response["success"] = False
        response["error"] = {"message": str(e)}
    return JsonResponse(response)
    
def get_areas(request):
    response = {"success": False}
    context = user_data(request)
    dt = request.GET
    isList = dt.get("isList", False)
    company_id = context["company"]["id"]
    subModule_id = 2

    lista = Area.objects.filter(company_id = company_id).values()

    if isList:
        lista = lista.values("id", "name").exclude(is_active=False)
    
    if not isList:
        access = get_module_user_permissions(context, subModule_id)
        access = access["data"]["access"]
        for item in lista:
            item["btn_action"] = ""
            if access["update"]:
                item["btn_action"] += "<button class=\"btn btn-icon btn-sm btn-primary-light\" data-area=\"update-item\">" \
                    "<i class=\"fa-solid fa-pen\"></i>"\
                "</button>\n"
            if access["delete"]:
                item["btn_action"] += "<button class=\"btn btn-icon btn-sm btn-danger-light\" data-area=\"delete-item\">" \
                    "<i class=\"fa-solid fa-trash\"></i>" \
                "</button>"
        pass

    response["data"] = list(lista)
    response["success"] = True
    return JsonResponse(response)

def update_area(request):
    response = {"success": False}
    context = user_data(request)
    dt = request.POST
    id = dt.get("id", None)
    is_active = bool(int(request.POST.get("is_active", "0")))
    company_id = context["company"]["id"]

    if not id:
        response["error"] = {"message": "No se proporcionó un ID válido"}
        return JsonResponse(response)

    try:
        obj = Area.objects.get(id=id)
    except Area.DoesNotExist:
        response["error"] = {"message": f"No existe ningún registro con el ID '{id}'"}
        return JsonResponse(response)
    
    try:
        obj.name = dt.get("name")
        obj.company_id = company_id
        obj.code = dt.get("code")
        obj.description = dt.get("description")
        obj.is_active = is_active
        obj.save()

        response["success"] = True
    except Exception as e:
        response["success"] = False
        response["error"] = {"message": str(e)}
    return JsonResponse(response)