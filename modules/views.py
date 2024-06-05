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
from modules.utils import * # Esto es un helpers

# TODO --------------- [ VARIABLES ] ---------- 

AUDITORIA_VEHICULAR_POR_MES = 2


# TODO --------------- [ VIEWS ] ---------- 
def module_home(request):
    context = {}
    return render(request, "home.html" , context)

@login_required
def module_companys(request):
    context = user_data(request)

    sidebar = get_sidebar(context, [1])
    context["sidebar"] = sidebar["data"]

    template = "companys.html"
    return render(request, template, context)
    

@login_required
def module_users(request):
    context = user_data(request)
    module_id = 1
    subModule_id = 2

    access = get_module_user_permissions(context, subModule_id)
    sidebar = get_sidebar(context, module_id)
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]

    if context["access"]["read"]:
        template = "module_users.html"
    else:
        template = "error/access_denied.html"
    return render(request, template, context)

@login_required
def module_providers(request):
    context = user_data(request)
    module_id = 3
    subModule_id = 3

    access = get_module_user_permissions(context, subModule_id)
    sidebar = get_sidebar(context, [1, module_id])

    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]


    if context["access"]["read"]:
        template = "proviers.html"
    else:
        template = "error/access_denied.html"
    return render(request, template, context)


@login_required
def module_vehicle(request):
    context = user_data(request)
    module_id = 2
    subModule_id = 4

    access = get_module_user_permissions(context, subModule_id)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]

    if context["access"]["read"]:
        template = "module_vechicles_info.html"
    else:
        template = "error/access_denied.html"
    return render(request, template, context)

@login_required
def module_vehicle_info_id(request, vehicle_id = None):
    context = user_data(request)
    context["vehicle"] = {"id": vehicle_id}
    module_id = 2
    subModule_id = 4

    access = get_module_user_permissions(context, subModule_id)
    permisos = get_user_access(context)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["permiso"] = permisos["data"]
    context["sidebar"] = sidebar["data"]

    if context["access"]["read"]:
        template = "module_vechicle_info.html"
    else:
        template = "error/access_denied.html"

    return render(request, template, context)

@login_required
def module_vehicle_tenencia(request):
    context = user_data(request)
    module_id = 2
    subModule_id = 5

    access = get_module_user_permissions(context, subModule_id)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]
    
    if context["access"]["read"]:
        template = "module_vehicles_tenencia.html"
    else:
        template = "error/access_denied.html"
    return render(request, template, context)

@login_required
def module_vehicle_refrendo(request):
    context = user_data(request)
    module_id = 2
    subModule_id = 6

    access = get_module_user_permissions(context, subModule_id)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]
    
    if context["access"]["read"]:
        template = "module_vehicles_refrendo.html"
    else:
        template = "error/access_denied.html"
    
    return render(request, template, context)

@login_required
def module_vehicle_verificacion(request):
    context = user_data(request)
    module_id = 2
    subModule_id = 7

    access = get_module_user_permissions(context, subModule_id)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]
    
    if context["access"]["read"]:
        template = "module_vehicles_verificacion.html"
    else:
        template = "error/access_denied.html"

    return render(request, template, context)

@login_required
def module_vehicle_responsiva(request):
    context = user_data(request)
    module_id = 2
    submodule_id = 8

    access = get_module_user_permissions(context, submodule_id)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]

    if context["access"]["read"]:
        template = "module_vehicles_responsiva.html"
    else:
        template = "error/access_denied.html"
    return render(request, template, context)

@login_required
def module_vehicle_insurance(request):
    context = user_data(request)
    module_id = 2
    submodule_id = 9

    access = get_module_user_permissions(context, submodule_id)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]

    if context["access"]["read"]:
        template = "module_vehicle_insurance.html"
    else:
        template = "error/access_denied.html"
    return render(request, template, context)

@login_required
def module_vehicle_audit(request):
    context = user_data(request)
    module_id = 2
    submodule_id = 10

    access = get_module_user_permissions(context, submodule_id)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]

    if context["access"]["read"]:
        template = "module_vehicle_audit.html"
    else:
        template = "error/access_denied.html"
    return render(request, template, context)

@login_required
def module_vehicle_maintenance(request):
    context = user_data(request)
    module_id = 2
    submodule_id = 11

    access = get_module_user_permissions(context, submodule_id)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]

    if context["access"]["read"]:
        template = "module_vehicles_maintenance.html"
    else:
        template = "error/access_denied.html"
    return render(request, template, context)

# TODO --------------- [ HELPER ] ----------

# TODO --------------- [ REQUEST ] ----------
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

    # Validar que la empresa está asignada
    if not company_id:
        response["error"] = {"message": "Tu usuario no cuenta con una empresa asignada"}
        return JsonResponse(response)

    # Validar que todos los campos requeridos están presentes
    if not all([username, password, email, first_name, last_name]):
        response["error"] = {"message": "Todos los campos son obligatorios."}
        return JsonResponse(response)
    
    # Verificar si el nombre de usuario ya existe
    if User.objects.filter(username=username).exists():
        response["error"] = {"message": f"{username} ya existe."}
        return JsonResponse(response)
    
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
            User_Access.objects.create(user_id=user.id, role_id=role_id, company_id=company_id)
        
        response["success"] = True
        response["message"] = "Usuario creado"
    except ValidationError as ve:
        response["error"] = {"message": f"Error de validación: {str(ve)}"}
    except Exception as e:
        response["error"] = {"message": f"Error inesperado: {str(e)}"}

    return JsonResponse(response)

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
        "id", "role__id", "role__name",
        "company_id", "company__name",
        "user_id", "user__username", "user__first_name", "user__last_name", "user__email", "user__is_active"
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
                item["btn_option"] += """
                    <button type="button" name="key" class="btn btn-primary btn-sm" data-user="show-user-permissions" aria-label="keys">
                        <i class="fa-solid fa-key"></i>
                    </button>
                    <button type="button" name="update" class="btn btn-primary btn-sm" data-user="update-item" aria-label="update">
                        <i class="fa-solid fa-pen"></i>
                    </button>
                """
            if access["delete"]:
                item["btn_option"] += """
                    <button type="button" name="delete" class="btn btn-danger btn-sm" data-user="dalete-item" aria-label="delete">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                """
        pass
    
    response["data"] = list(lista)
    response["success"] = True

    return JsonResponse(response)

# Actualizar usuario con acceso
def update_user_with_access(request):
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
    user_id = dt.get('user_id')

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
                    response["error"] = {"message": f"El nombre de usuario '{username}' ya existe."}
                    return JsonResponse(response)
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
            access_record.save()

        response["success"] = True
    except User.DoesNotExist:
        response["error"] = {"message": "El usuario no existe."}
    except ValidationError as ve:
        response["error"] = {"message": f"Error de validación: {str(ve)}"}
    except Exception as e:
        response["error"] = {"message": f"Error inesperado: {str(e)}"}

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
    company_id = request.session.get('company').get('id')
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
        obj = Provider(
            name = dt.get("name"),
            company_id = company_id,
            phone_number = dt.get("phone_number"),
            address = dt.get("address")
        )
        obj.save()
        response["id"] = obj.id
        response["success"] = True
    except Exception as e:
        response["success"] = False
        response["error"] = {"message": str(e)}

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
                item["btn_action"] += """<button class=\"btn btn-primary btn-sm mb-1\" data-provider=\"update-item\">
                    <i class="fa-solid fa-pen"></i>
                </button>\n"""
            if access["delete"]:
                item["btn_action"] += """<button class=\"btn btn-danger btn-sm mb-1\" data-provider=\"delete-item\">
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
        response["error"] = {"message": "No se proporcionó un ID válido"}
        return JsonResponse(response)

    try:
        obj = Provider.objects.get(id=id)
    except Provider.DoesNotExist:
        response["error"] = {"message": f"No existe ningún registro con el ID '{id}'"}
        return JsonResponse(response)
    
    try:
        obj.name = dt.get("name")
        obj.company_id = company_id
        obj.phone_number = dt.get("phone_number")
        obj.address = dt.get("address")
        obj.is_active = is_active
        obj.save()

        response["success"] = True
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



def add_vehicle_info(request):
    context = user_data(request)
    response = {"success": False}
    dt = request.POST

    company_id = context["company"]["id"]

    try:
        obj = Vehicle(
            is_active = dt.get("is_active", True),
            company_id = company_id,
            name = dt.get("name"),
            state = dt.get("state", "QUERETARO"),
            plate = dt.get("plate"),
            model = dt.get("model"),
            year = dt.get("year", 2024),
            serial_number = dt.get("serial_number"),
            brand = dt.get("brand"),
            color = dt.get("color"),
            vehicle_type = dt.get("vehicle_type", "Personal"),
            validity = dt.get("validity"),
            mileage = dt.get("mileage"),
            responsible_id = dt.get("responsible_id"),
            owner_id = dt.get("owner_id")
        )
        obj.save()
        id = obj.id

        if 'cover-image' in request.FILES and request.FILES['cover-image']:
            load_file = request.FILES['cover-image']
            company_id = request.session.get('company').get('id')
            folder_path = f"docs/{company_id}/vehicle/{id}/"
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)

            file_name, extension = os.path.splitext(load_file.name)                
            new_name = f"cover-image{extension}"

            # Eliminar el archivo anterior en caso de existir
            for item in ["png", "jpg", "jpeg","gif"]:
                old_file_path = os.path.join(settings.MEDIA_ROOT, folder_path, f"cover-image.{item}")
                if os.path.exists(old_file_path): os.remove(old_file_path)

            fs.save(folder_path + new_name, load_file)

            obj.image_path = folder_path + new_name
            obj.save()

        response["success"] = True
        response["id"] = obj.id
    except Exception as e:
        response["success"] = False
        response["error"] = {"message": str(e)}
        return JsonResponse(response)
    

    # Crear auditoria
    try:
        vehiculos = Vehicle.objects.filter(company_id=1).order_by('id')

        num_vehiculos = vehiculos.count()
        num_auditorias = Vehicle_Audit.objects.filter(
            vehicle__company_id = 1,
            active = True
        ).count()
        num = 3 # cantidad de auditorias a crear

        if num_vehiculos >= 3 and num_auditorias == 0:
            """ Crear auditoria """
            fecha_actual = datetime.now()

            # Calcular la fecha del mes siguiente
            fecha_siguiente = fecha_actual.replace(day=28) + timedelta(days=4)
            fecha_siguiente = fecha_siguiente.replace(day=28)

            # Generar una fecha aleatoria dentro del rango del día 10 al 28 del mes siguiente
            fecha_aleatoria = fecha_siguiente.replace(day=random.randint(10, 28))

            for vehiculo in vehiculos[:num]:
                obj = Vehicle_Audit(
                    vehicle_id = vehiculo.id,
                    audit_date = fecha_aleatoria
                )
                obj.save()
            pass
        pass
    except Exception as e:
        response["error"] = {"message": str(e)}

    return JsonResponse(response)

def get_vehicle_info(request):
    response = {"success": False, "data": []}
    dt = request.GET
    subModule_id = 4

    vehicle_id = dt.get("vehicle_id", None)

    if vehicle_id is None:
        response["error"] = {"message": "No se proporcionó un ID de vehículo válido"}
        return JsonResponse(response)
    
    data = Vehicle.objects.filter(id = vehicle_id)

    if not data.exists():
        response["error"] = {"message": "No se proporcionó un ID de vehículo válido"}
        return JsonResponse(response)
    
    data = data.values(
        "id", "is_active", "brand", "color",
        "company_id", "company__name",
        "insurance_company", "mileage", "model", "name", "plate",
        "responsible_id", "responsible__first_name", "responsible__last_name",
        "serial_number", "state", "validity",
        "vehicle_type", "year", "image_path"
    )[0]
    data["image_path"] = "/" + data["image_path"]

    response["data"] = data
    response["success"] = True
    return JsonResponse(response)

def get_vehicles_info(request):
    response = {"success": False, "data": []}
    context = user_data(request)
    dt = request.GET
    isList = dt.get("isList", False)
    subModule_id = 4

    data = Vehicle.objects.order_by('name').values(
        "id", "is_active", "image_path", "name", "state",
        "company_id", "company__name", "plate", "model",
        "year", "serial_number", "brand", "color", "vehicle_type", "validity", "mileage",
        "insurance_company", "responsible_id",
        "responsible_id", "responsible__first_name", "responsible__last_name",
        "owner_id", "owner__first_name",
        "transmission_type",
        "policy_number"
    )

    data = data.filter(company_id = context["company"]["id"])

    if (context["role"]["id"] == 4):
        data = data.filter(
            Q(responsible_id = context["user"]["id"]) |
            Q(owner_id = context["user"]["id"])
        )

    if isList:
        data = data.values("id", "name", "plate")
    else:
        access = get_module_user_permissions(context, subModule_id)
        access = access["data"]["access"]
        for item in data:
            item["image_path"] = "/" + item["image_path"]
            item["btn_action"] = f"""
            <a href="/module/vehicle/info/{item['id']}/" class="btn btn-primary btn-sm mb-1">
                <i class="fa-solid fa-eye"></i>
            </a>\n
            """
            if access["update"]:
                item["btn_action"] += """<button class=\"btn btn-primary btn-sm mb-1\" data-vehicle-info=\"update-item\">
                    <i class="fa-solid fa-pen"></i>
                </button>\n"""
            if access["delete"]:
                item["btn_action"] += """<button class=\"btn btn-danger btn-sm mb-1\" data-vehicle-info=\"delete-item\">
                    <i class="fa-solid fa-trash"></i>
                </button>"""
    response["recordsTotal"] = data.count()
    response["data"] = list(data)
    response["success"] = True
    return JsonResponse(response)

def update_vehicle_info(request):
    response = {"success": False}
    dt = request.POST

    id = dt.get("id", None)

    if not id:
        response["error"] = {"message": "No se proporcionó un ID de vehículo válido"}
        return JsonResponse(response)

    try:
        obj = Vehicle.objects.get(id=id)
    except Vehicle.DoesNotExist:
        response["error"] = {"message": f"No existe ningún vehículo con el ID '{id}'"}
        return JsonResponse(response)
    
    try:
        obj.is_active = dt.get("is_active", obj.is_active)
        obj.name = dt.get("name", obj.name)
        obj.state = dt.get("state")
        obj.color = dt.get("color", obj.color)
        obj.mileage = dt.get("mileage", obj.mileage)
        obj.model = dt.get("model", obj.model)
        obj.serial_number = dt.get("serial_number", obj.serial_number)
        obj.year = dt.get("year", obj.year)
        obj.brand = dt.get("brand", obj.brand)
        obj.responsible_id = dt.get("responsible_id")
        obj.owner_id = dt.get("owner_id")
        obj.save()

        if 'cover-image' in request.FILES and request.FILES['cover-image']:
            load_file = request.FILES['cover-image']
            company_id = request.session.get('company').get('id')
            folder_path = f"docs/{company_id}/vehicle/{id}/"
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)

            file_name, extension = os.path.splitext(load_file.name)                
            new_name = f"cover-image{extension}"

            # Eliminar el archivo anterior en caso de existir
            for item in ["png", "jpg", "jpeg","gif"]:
                old_file_path = os.path.join(settings.MEDIA_ROOT, folder_path, f"cover-image.{item}")
                if os.path.exists(old_file_path): os.remove(old_file_path)

            fs.save(folder_path + new_name, load_file)

            obj.image_path = folder_path + new_name
            obj.save()
        response["success"] = True
    except Exception as e:
        response["error"] = {"message": str(e)}

    return JsonResponse(response)

def delete_vehicle_info(request):
    response = {"success": False, "data": []}
    dt = request.POST
    id = dt.get("id", None)

    if id == None:
        response["error"] = {"message": "Proporcione un id valido", "id": id}
        return JsonResponse(response)

    try:
        obj = Vehicle.objects.get(id = id)
    except Vehicle.DoesNotExist:
        response["error"] = {"message": "El objeto no existe"}
        return JsonResponse(response)
    else:
        obj.delete()
    response["success"] = True
    return JsonResponse(response)


def add_vehicle_tenencia(request):
    response = {"success": False, "data": []}
    dt = request.POST

    vehicle_id = dt.get("vehiculo_id")
    
    try:
        obj_vehicle = Vehicle.objects.get(id = vehicle_id)
        company_id = obj_vehicle.company.id
    except Vehicle.DoesNotExist:
        response["error"] = {"message": f"No se encontró ningún vehículo con el ID {vehicle_id}"}
        return JsonResponse(response)

    try:
        obj = Vehicle_Tenencia(
            vehiculo_id = vehicle_id,
            fecha_pago = dt.get("fecha_pago"),
            monto = dt.get("monto")
        )
        obj.save()
        id = obj.id

        # Guardar el archivo en caso de existir
        if 'comprobante_pago' in request.FILES and request.FILES['comprobante_pago']:
            load_file = request.FILES['comprobante_pago']
            folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/tenencia/"
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            file_name, extension = os.path.splitext(load_file.name)
            
            new_name = f"comprobante_pago_{id}.{extension}"
            fs.save(folder_path + new_name, load_file)
            
            obj.comprobante_pago = folder_path + new_name
            obj.save()

        response["success"] = True
    except Exception as e:
        response["error"] = {"message": str(e)}
    return JsonResponse(response)

def get_vehicle_tenencia(request):
    context = user_data(request)
    response = {"success": False, "data": []}
    dt = request.GET
    vehicle_id = dt.get("vehicle_id", None)
    subModule_id = 5

    lista = Vehicle_Tenencia.objects.filter(vehiculo_id = vehicle_id).values("id", "vehiculo_id", "vehiculo__name", "monto", "fecha_pago", "comprobante_pago")

    access = get_module_user_permissions(context, subModule_id)
    access = access["data"]["access"]
    for item in lista:
        item["btn_action"] = ""
        if access["update"]:
            item["btn_action"] += """<button class=\"btn btn-primary btn-sm\" data-vehicle-tenencia=\"update-item\">
                <i class="fa-solid fa-pen"></i>
            </button>\n"""
        if access["delete"]:
            item["btn_action"] += """<button class=\"btn btn-danger btn-sm\" data-vehicle-tenencia=\"delete-item\">
                <i class="fa-solid fa-trash"></i>
            </button>"""
    response["data"] = list(lista)

    response["success"] = True
    return JsonResponse(response)

def get_vehicles_tenencia(request):
    context = user_data(request)
    response = {"success": False, "data": []}
    dt = request.GET
    subModule_id = 5

    lista = Vehicle_Tenencia.objects.values(
        "id",
        "vehiculo_id", "vehiculo__name", "vehiculo__company_id",
        "monto", "fecha_pago", "comprobante_pago"
    )

    if context["role"]["id"] in [1,2,3]:
        lista = lista.filter(vehiculo__company_id = context["company"]["id"])
    else:
        lista = lista.filter(vehiculo__responsible_id = context["user"]["id"])

    access = get_module_user_permissions(context, subModule_id)
    access = access["data"]["access"]
    for item in lista:
        item["btn_action"] = ""
        if access["update"]:
            item["btn_action"] += """<button class=\"btn btn-primary btn-sm mb-1\" data-vehicle-tenencia=\"update-item\">
                <i class="fa-solid fa-pen"></i>
            </button>\n"""
        if access["delete"]:
            item["btn_action"] += """<button class=\"btn btn-danger btn-sm mb-1\" data-vehicle-tenencia=\"delete-item\">
                <i class="fa-solid fa-trash"></i>
            </button>"""
    response["data"] = list(lista)
    response["success"] = True
    return JsonResponse(response)

def update_vehicle_tenencia(request):
    response = {"success": False, "data": []}
    dt = request.POST
    
    id = dt.get("id", None)
    vehicle_id = dt.get("vehicle_id"),

    if id is None:
        response["error"] = {"message": "No se proporcionó un ID válido para actualizar."}
        return JsonResponse(response)
    
    try:
        obj = Vehicle_Tenencia.objects.get(id=id)
    except Vehicle_Tenencia.DoesNotExist:
        response["error"] = {"message": f"No existe ningún resgitro con el ID '{id}'"}
        return JsonResponse(response)

    try:
        obj.monto = dt.get("monto")
        obj.fecha_pago = dt.get("fecha_pago")
        obj.save()
        vehicle_id = obj.vehiculo_id
        
        # Guardar el archivo en caso de existir
        if 'comprobante_pago' in request.FILES and request.FILES['comprobante_pago']:
            load_file = request.FILES['comprobante_pago']
            company_id = request.session.get('company').get('id')
            folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/tenencia/{id}/"
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            file_name, extension = os.path.splitext(load_file.name)                
            
            new_name = f"comprobante_pago{extension}"
            fs.save(folder_path + new_name, load_file)
            
            obj.comprobante_pago = folder_path + new_name
            obj.save()
        
        response["success"] = True
    except Exception as e:
        response["error"] = {"message": str(e)}
    return JsonResponse(response)

def delete_vehicle_tenencia(request):
    response = {"success": False, "data": []}
    dt = request.GET
    id = dt.get("id", None)

    if id == None:
        response["error"] = {"message": "Proporcione un id valido"}
        return JsonResponse(response)

    try:
        obj = Vehicle_Tenencia.objects.get(id = id)
    except Vehicle_Tenencia.DoesNotExist:
        response["error"] = {"message": "El objeto no existe"}
        return JsonResponse(response)
    else:
        obj.delete()
    response["success"] = True
    return JsonResponse(response)



def add_vehicle_refrendo(request):
    response = {"success": False, "data": []}
    dt = request.POST

    vehicle_id = dt.get("vehiculo_id")
    
    try:
        obj_vehicle = Vehicle.objects.get(id = vehicle_id)
        company_id = obj_vehicle.company.id
    except Vehicle.DoesNotExist:
        response["error"] = {"message": f"No se encontró ningún vehículo con el ID {vehicle_id}"}
        return JsonResponse(response)

    try:
        obj = Vehicle_Refrendo(
            vehiculo_id = vehicle_id,
            fecha_pago = dt.get("fecha_pago"),
            monto = dt.get("monto")
        )
        obj.save()
        id = obj.id

        # Guardar el archivo en caso de existir
        if 'comprobante_pago' in request.FILES and request.FILES['comprobante_pago']:
            load_file = request.FILES['comprobante_pago']
            folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/refrendo/"
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            file_name, extension = os.path.splitext(load_file.name)
            
            new_name = f"comprobante_pago_{id}{extension}"
            fs.save(folder_path + new_name, load_file)
            
            obj.comprobante_pago = folder_path + new_name
            obj.save()

        response["success"] = True
        response["id"] = obj.id
    except Exception as e:
        response["success"] = False
        response["error"] = {"message": str(e)}
    return JsonResponse(response)

def get_vehicle_refrendo(request):
    response = {"success": False, "data": []}
    dt = request.GET
    vehicle_id = dt.get("vehicle_id", None)

    lista = Vehicle_Refrendo.objects.filter(vehiculo_id = vehicle_id).values(
        "id",
        "vehiculo_id", "vehiculo__name",
        "monto", "fecha_pago", "comprobante_pago"
    )

    for item in lista:
        item["btn_action"] = ""
        item["btn_action"] += """<button class=\"btn btn-primary btn-sm\" data-vehicle-refrendo=\"update-item\">
            <i class="fa-solid fa-pen"></i>
        </button>\n"""
        item["btn_action"] += """<button class=\"btn btn-danger btn-sm\" data-vehicle-refrendo=\"delete-item\">
            <i class="fa-solid fa-trash"></i>
        </button>"""
    response["data"] = list(lista)

    response["success"] = True
    return JsonResponse(response)

def get_vehicles_refrendo(request):
    context = user_data(request)
    response = {"success": False, "data": []}
    dt = request.GET
    vehicle_id = dt.get("vehicle_id", None)
    subModule_id = 6

    lista = Vehicle_Refrendo.objects.values("id", "vehiculo_id", "vehiculo__name", "monto", "fecha_pago", "comprobante_pago")

    if context["role"]["id"] in [1,2,3]:
        lista = lista.filter(vehiculo__company_id = context["company"]["id"])
    else:
        lista = lista.filter(vehiculo__responsible_id = context["user"]["id"])

    access = get_module_user_permissions(context, subModule_id)
    access = access["data"]["access"]
    for item in lista:
        item["btn_action"] = ""
        if access["update"]:
            item["btn_action"] += """<button class=\"btn btn-primary btn-sm\" data-vehicle-refrendo=\"update-item\">
                <i class="fa-solid fa-pen"></i>
            </button>\n"""
        if access["delete"]:
            item["btn_action"] += """<button class=\"btn btn-danger btn-sm\" data-vehicle-refrendo=\"delete-item\">
                <i class="fa-solid fa-trash"></i>
            </button>"""
    response["data"] = list(lista)

    response["success"] = True
    return JsonResponse(response)

def update_vehicle_refrendo(request):
    response = {"success": False, "data": []}
    dt = request.POST
    
    id = dt.get("id", None)
    vehicle_id = dt.get("vehicle_id"),

    if id is None:
        response["error"] = {"message": "No se proporcionó un ID válido para actualizar."}
        return JsonResponse(response)
    
    try:
        obj = Vehicle_Refrendo.objects.get(id=id)
    except Vehicle_Refrendo.DoesNotExist:
        response["error"] = {"message": f"No existe ningún resgitro con el ID '{id}'"}
        return JsonResponse(response)

    try:
        obj.monto = dt.get("monto")
        obj.fecha_pago = dt.get("fecha_pago")
        obj.save()
        vehicle_id = obj.vehiculo_id
        
        # Guardar el archivo en caso de existir
        if 'comprobante_pago' in request.FILES and request.FILES['comprobante_pago']:
            load_file = request.FILES['comprobante_pago']
            company_id = request.session.get('company').get('id')
            folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/refrendo/{id}/"
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            file_name, extension = os.path.splitext(load_file.name)                
            
            new_name = f"comprobante_pago{extension}"
            fs.save(folder_path + new_name, load_file)
            
            obj.comprobante_pago = folder_path + new_name
            obj.save()
        
        response["success"] = True
    except Exception as e:
        response["error"] = {"message": str(e)}
    return JsonResponse(response)

def delete_vehicle_refrendo(request):
    response = {"success": False, "data": []}
    dt = request.GET
    id = dt.get("id", None)

    if id == None:
        response["error"] = {"message": "Proporcione un id valido"}
        return JsonResponse(response)

    try:
        obj = Vehicle_Refrendo.objects.get(id = id)
    except Vehicle_Refrendo.DoesNotExist:
        response["error"] = {"message": "El objeto no existe"}
        return JsonResponse(response)
    else:
        obj.delete()
    response["success"] = True
    return JsonResponse(response)



def add_vehicle_verificacion(request):
    response = {"success": False, "data": []}
    dt = request.POST
    vehicle_id = dt.get("vehiculo_id")
    
    try:
        obj_vehicle = Vehicle.objects.get(id = vehicle_id)
        company_id = obj_vehicle.company.id
    except Vehicle.DoesNotExist:
        response["error"] = {"message": f"No se encontró ningún vehículo con el ID {vehicle_id}"}
        return JsonResponse(response)

    try:
        obj = Vehicle_Verificacion(
            vehiculo_id = vehicle_id,
            monto = dt.get("monto"),
            engomado = dt.get("engomado"),
            periodo = dt.get("periodo"),
            fecha_pago = dt.get("fecha_pago"),
            lugar = dt.get("lugar")
        )
        obj.save()
        id = obj.id

        # Guardar el archivo en caso de existir
        if 'comprobante_pago' in request.FILES and request.FILES['comprobante_pago']:
            load_file = request.FILES['comprobante_pago']
            folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/verificacion/"
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            file_name, extension = os.path.splitext(load_file.name)
            
            new_name = f"comprobante_pago_{id}{extension}"
            fs.save(folder_path + new_name, load_file)
            
            obj.comprobante_pago = folder_path + new_name
            obj.save()

        response["success"] = True
        response["id"] = obj.id
    except Exception as e:
        response["error"] = {"message": str(e)}
    return JsonResponse(response)

def get_vehicle_verificacion(request):
    context = user_data(request)
    response = {"success": False, "data": []}
    dt = request.GET
    vehicle_id = dt.get("vehiculo_id", None)
    subModule_id = 7

    lista = Vehicle_Verificacion.objects.filter(
        vehiculo_id = vehicle_id
    ).values(
        "id", "engomado", "periodo", "lugar",
        "vehiculo_id", "vehiculo__name",
        "monto", "fecha_pago", "comprobante_pago"
    )

    access = get_module_user_permissions(context, subModule_id)
    access = access["data"]["access"]

    for item in lista:
        item["btn_action"] = ""
        if access["update"]:
            item["btn_action"] += """<button class=\"btn btn-primary btn-sm\" data-vehicle-verificacion=\"update-item\">
                <i class="fa-solid fa-pen"></i>
            </button>\n"""
        if access["delete"]:
            item["btn_action"] += """<button class=\"btn btn-danger btn-sm\" data-vehicle-verificacion=\"delete-item\">
                <i class="fa-solid fa-trash"></i>
            </button>"""
    response["data"] = list(lista)
    response["success"] = True
    return JsonResponse(response)

def get_vehicles_verificacion(request):
    context = user_data(request)
    response = {"success": False, "data": []}
    dt = request.GET
    vehicle_id = dt.get("vehiculo_id", None)
    subModule_id = 7

    lista = Vehicle_Verificacion.objects.values(
        "id","engomado", "periodo", "lugar",
        "vehiculo_id", "vehiculo__name",
        "monto", "fecha_pago", "comprobante_pago"
    )

    if context["role"]["id"] in [1,2,3]:
        lista = lista.filter(
            vehiculo__company_id = context["company"]["id"]
        )
    else:
        lista = lista.filter(vehiculo__responsible_id = context["user"]["id"])

    access = get_module_user_permissions(context, subModule_id)
    access = access["data"]["access"]

    for item in lista:
        item["btn_action"] = ""
        if access["update"]:
            item["btn_action"] += """<button class=\"btn btn-primary btn-sm\" data-vehicle-verificacion=\"update-item\">
                <i class="fa-solid fa-pen"></i>
            </button>\n"""
        if access["delete"]:
            item["btn_action"] += """<button class=\"btn btn-danger btn-sm\" data-vehicle-verificacion=\"delete-item\">
                <i class="fa-solid fa-trash"></i>
            </button>"""
    response["data"] = list(lista)
    response["success"] = True
    return JsonResponse(response)

def update_vehicle_verificacion(request):
    response = {"success": False, "data": []}
    dt = request.POST
    
    id = dt.get("id", None)
    vehicle_id = dt.get("vehicle_id"),

    if id is None:
        response["error"] = {"message": "No se proporcionó un ID válido para actualizar."}
        return JsonResponse(response)
    
    try:
        obj = Vehicle_Verificacion.objects.get(id=id)
    except Vehicle_Verificacion.DoesNotExist:
        response["error"] = {"message": f"No existe ningún resgitro con el ID '{id}'"}
        return JsonResponse(response)

    try:
        obj.monto = dt.get("monto")
        obj.fecha_pago = dt.get("fecha_pago")
        obj.save()
        vehicle_id = obj.vehiculo_id
        
        # Guardar el archivo en caso de existir
        if 'comprobante_pago' in request.FILES and request.FILES['comprobante_pago']:
            load_file = request.FILES['comprobante_pago']
            company_id = request.session.get('company').get('id')
            folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/verificacion/"
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            file_name, extension = os.path.splitext(load_file.name)                
            
            new_name = f"comprobante_pago_{id}{extension}"
            fs.save(folder_path + new_name, load_file)
            
            obj.comprobante_pago = folder_path + new_name
            obj.save()
        
        response["success"] = True
    except Exception as e:
        response["error"] = {"message": str(e)}
    return JsonResponse(response)



def add_vehicle_responsiva(request):
    response = {"success": False}
    context = user_data(request)
    dt = request.POST

    vehicle_id = dt.get("vehicle_id")
    
    try:
        obj_vehicle = Vehicle.objects.get(id = vehicle_id)
        company_id = obj_vehicle.company.id

        # Verificamos que el kilometraje sea coerente
        mileage = Decimal(dt.get("initial_mileage")) if dt.get("initial_mileage") else None
        if mileage is not None and obj_vehicle.mileage is not None and obj_vehicle.mileage > mileage:
            response["warning"] = {"message": "El kilometraje del vehículo es mayor que el valor proporcionado."}
            return JsonResponse(response)
    except Vehicle.DoesNotExist:
        response["error"] = {"message": f"No se encontró ningún vehículo con el ID {vehicle_id}"}
        return JsonResponse(response)


    try:
        with transaction.atomic():
            obj = Vehicle_Responsive(
                vehicle_id = dt.get("vehicle_id"),
                responsible_id = dt.get("responsible_id"),
                initial_mileage = dt.get("initial_mileage"),
                initial_fuel = dt.get("initial_fuel"),
                destination = dt.get("destination"),
                trip_purpose = dt.get("trip_purpose"),
                start_date = dt.get("start_date")
            )
            obj.save()

            obj_vehicle.mileage = dt.get("initial_mileage")
            obj_vehicle.save()

            if 'signature' in request.FILES and request.FILES['signature']:
                load_file = request.FILES['signature']
                folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/responsiva/"
                fs = FileSystemStorage(location=settings.MEDIA_ROOT)
                file_name, extension = os.path.splitext(load_file.name)

                # Eliminar el archivo anterior con el mismo nombre
                for item in ["png", "jpg", "jpeg", "gif", "tiff", "bmp", "raw"]:
                    old_file_path = os.path.join(settings.MEDIA_ROOT, folder_path, f"signature.{item}")
                    if os.path.exists(old_file_path): os.remove(old_file_path)
                
                new_name = f"signature{extension}"
                fs.save(folder_path + new_name, load_file)

                obj.signature = folder_path + new_name
                obj.save()
        if 'image_path_exit_1' in request.FILES and request.FILES['image_path_exit_1']:
            load_file = request.FILES['image_path_exit_1']
            folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/responsiva/"
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            file_name, extension = os.path.splitext(load_file.name)

            # Eliminar el archivo anterior con el mismo nombre
            for item in ["png", "jpg", "jpeg", "gif", "tiff", "bmp", "raw"]:
                old_file_path = os.path.join(settings.MEDIA_ROOT, folder_path, f"salida_1.{item}")
                if os.path.exists(old_file_path): os.remove(old_file_path)
            
            new_name = f"salida_1{extension}"
            fs.save(folder_path + new_name, load_file)

            obj.image_path_exit_1 = folder_path + new_name
            obj.save()
        if 'image_path_exit_2' in request.FILES and request.FILES['image_path_exit_2']:
            load_file = request.FILES['image_path_exit_2']
            folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/responsiva/"
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            file_name, extension = os.path.splitext(load_file.name)

            # Eliminar el archivo anterior con el mismo nombre
            for item in ["png", "jpg", "jpeg", "gif", "tiff", "bmp", "raw"]:
                old_file_path = os.path.join(settings.MEDIA_ROOT, folder_path, f"salida_2.{item}")
                if os.path.exists(old_file_path): os.remove(old_file_path)
            
            new_name = f"salida_2{extension}"
            fs.save(folder_path + new_name, load_file)

            obj.image_path_exit_2 = folder_path + new_name
            obj.save()
        
        response["id"] = obj.id
        response["success"] = True
    except Exception as e:
        response["success"] = False
        response["error"] = {"message": str(e)}
    response["success"] = True
    return JsonResponse(response)

def get_vehicle_responsiva(request):
    context = user_data(request)
    response = {"success": False, "data": []}
    dt = request.GET
    vehicle_id = dt.get("vehicle_id", None)
    subModule_id = 8

    lista = Vehicle_Responsive.objects.filter(vehicle_id = vehicle_id).values(
        "id", "responsible_id", "responsible__first_name", "responsible__last_name",
        "image_path_entry_1", "image_path_entry_2", "image_path_exit_1", "image_path_exit_2",
        "initial_mileage", "final_mileage",
        "initial_fuel", "final_fuel",
        "start_date", "end_date",
        "signature", "destination", "trip_purpose"
    )

    access = get_module_user_permissions(context, subModule_id)
    access = access["data"]["access"]
    for item in lista:
        item["btn_action"] = """<button class=\"btn btn-primary btn-sm\" data-vehicle-responsiva=\"show-info-details\" title=\"Mostrar info\">
            <i class="fa-solid fa-eye"></i>
        </button>\n"""
        if access["delete"]:
            item["btn_action"] += """<button class=\"btn btn-danger btn-sm\" data-vehicle-responsiva=\"delete-item\">
                <i class="fa-solid fa-trash"></i>
            </button>"""
    response["data"] = list(lista)
    response["success"] = True
    return JsonResponse(response)

def get_vehicles_responsiva(request):
    context = user_data(request)
    response = {"success": False, "data": []}
    dt = request.GET
    vehicle_id = dt.get("vehicle_id", None)
    subModule_id = 8

    lista = Vehicle_Responsive.objects.values(
        "id", "vehicle_id", "vehicle__name",
        "responsible_id", "responsible__first_name", "responsible__last_name",
        "image_path_entry_1", "image_path_entry_2", "image_path_exit_1", "image_path_exit_2",
        "initial_mileage", "final_mileage",
        "initial_fuel", "final_fuel",
        "start_date", "end_date",
        "signature", "destination", "trip_purpose"
    )

    if context["role"]["id"] == 1:
        """"""
    elif context["role"]["id"] in [1,2]:
        lista = lista.filter(vehicle__company_id = context["company"]["id"])
    else:
        lista = lista.filter(vehicle__responsible_id = context["user"]["id"])

    access = get_module_user_permissions(context, subModule_id)
    access = access["data"]["access"]

    for item in lista:
        check = item["final_mileage"] and item["end_date"]
        item["btn_action"] = """<button class=\"btn btn-primary btn-sm\" data-vehicle-responsiva=\"show-info-details\" title=\"Mostrar info\">
            <i class="fa-solid fa-eye"></i>
        </button>\n"""
        if not check:
            item["btn_action"] += """<button class=\"btn btn-primary btn-sm\" data-vehicle-responsiva=\"check\" title="Check">
            <i class="fa-regular fa-list-check"></i>
        </button>\n"""
        if access["delete"]:
            item["btn_action"] += """<button class=\"btn btn-danger btn-sm\" data-vehicle-responsiva=\"delete-item\">
                <i class="fa-solid fa-trash"></i>
            </button>"""
    response["data"] = list(lista)
    response["success"] = True
    return JsonResponse(response)

def update_vehicle_responsiva(request):
    response = {"success": False}
    context = user_data(request)
    dt = request.POST
    id = dt.get("id", None)
    registro = dt.get("registro", "entrada")

    if id is None or id == "":
        response["error"] = {"message": "No se proporcionó un ID válido para actualizar.", "id": id}
        return JsonResponse(response)
    
    try:
        obj = Vehicle_Responsive.objects.get(id=id)
    except Vehicle_Responsive.DoesNotExist:
        response["error"] = {"message": f"No existe ningún resgitro con el ID '{id}'"}
        return JsonResponse(response)

    company_id = obj.vehicle.company.id
    vehicle_id = obj.vehicle.id

    try:
        obj_vehicle = Vehicle.objects.get(id = vehicle_id)

        if dt.get("final_mileage", None):
            initial_mileage = Decimal(obj.initial_mileage)
            final_mileage = Decimal(dt["final_mileage"])
            
            if initial_mileage > final_mileage:
                response["warning"] = {"message": "El kilometraje inicial es mayor al kilometraje final"}
                return JsonResponse(response)
            if obj_vehicle.mileage > final_mileage:
                response["warning"] = {"message": "El kilometraje del vehículo es mayor que el valor proporcionado."}
                return JsonResponse(response)

    except Vehicle.DoesNotExist:
        response["error"] = {"message": f"No se encontró ningún vehículo con el ID {vehicle_id}"}
        return JsonResponse(response)

    try:
        with transaction.atomic():
            obj.final_fuel = dt.get("final_fuel")
            obj.final_mileage = dt.get("final_mileage")
            obj.end_date = dt.get("end_date")
            obj.save()

            if registro == "salida":
                obj_vehicle.mileage = dt.get("initial_mileage")
            elif registro == "entrada":
                obj_vehicle.mileage = dt.get("final_mileage")
            obj_vehicle.save()

        if 'image_path_exit_1' in request.FILES and request.FILES['image_path_exit_1']:
            load_file = request.FILES['image_path_exit_1']
            folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/responsiva/{registro}/"
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            file_name, extension = os.path.splitext(load_file.name)

            # Eliminar el archivo anterior con el mismo nombre
            for item in ["png", "jpg", "jpeg", "gif", "tiff", "bmp", "raw"]:
                old_file_path = os.path.join(settings.MEDIA_ROOT, folder_path, f"salida_1.{item}")
                if os.path.exists(old_file_path): os.remove(old_file_path)
            
            new_name = f"salida_1{extension}"
            fs.save(folder_path + new_name, load_file)

            obj.image_path_exit_1 = folder_path + new_name
            obj.save()
        response["success"] = True
    except Exception as e:
        response["success"] = False
        response["error"] = {"message": str(e)}
    return JsonResponse(response)

def delete_vehicle_responsiva(request):
    response = {"success": False, "data": []}
    dt = request.POST
    id = dt.get("id", None)

    if id == None:
        response["error"] = {"message": "Proporcione un id valido"}
        return JsonResponse(response)

    try:
        obj = Vehicle_Responsive.objects.get(id = id)
    except Vehicle_Responsive.DoesNotExist:
        response["error"] = {"message": "El objeto no existe"}
        return JsonResponse(response)
    else:
        obj.delete()
    response["success"] = True
    return JsonResponse(response)



def add_vehicle_insurance(request):
    response = {"success": False, "data": []}
    dt = request.POST

    vehicle_id = dt.get("vehicle_id")

    if not vehicle_id:
        response["error"] = {"message": "No se proporcionó un ID de vehículo válido"}
        return JsonResponse(response)
    
    try:
        obj_vehicle = Vehicle.objects.get(id=vehicle_id)
    except Vehicle.DoesNotExist:
        response["error"] = {"message": f"No se encontró ningún vehículo con el ID {vehicle_id}"}
        return JsonResponse(response)

    try:
        with transaction.atomic():
            obj = Vehicle_Insurance(
                vehicle_id = vehicle_id,
                responsible_id = dt.get("responsible_id"),
                policy_number = dt.get("policy_number"),
                insurance_company = dt.get("insurance_company"),
                cost = dt.get("cost"),
                validity = dt.get("validity"),
                start_date = dt.get("start_date"),
                end_date = dt.get("end_date")
            )
            obj.save()

            # Guardar el número de póliza en el vehículo
            obj_vehicle.policy_number = dt.get("policy_number")
            obj_vehicle.validity = dt.get("end_date")
            obj.insurance_company = dt.get("insurance_company")
            obj_vehicle.save()

            # Guardar el archivo adjunto, si existe
            if 'doc' in request.FILES and request.FILES['doc']:
                load_file = request.FILES['doc']
                company_id = request.session.get('company').get('id')
                folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/seguro/"
                fs = FileSystemStorage(location=settings.MEDIA_ROOT)
                file_name, extension = os.path.splitext(load_file.name)

                # Eliminar el archivo anterior, si existe
                for item in ["pdf", "doc", "docx", "xls", "xlsx"]:
                    old_file_path = os.path.join(settings.MEDIA_ROOT, folder_path, f"doc_{obj.id}.{item}")
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                
                new_name = f"doc_{obj.id}{extension}"
                fs.save(folder_path + new_name, load_file)

                obj.doc = folder_path + new_name
                obj.save()

            # Configurar la respuesta exitosa
            response["id"] = obj.id
            response["success"] = True

    except Vehicle.DoesNotExist:
        response["success"] = False
        response["error"] = {"message": f"No se encontró ningún vehículo con el ID {vehicle_id}"}

    except Exception as e:
        response["success"] = False
        response["error"] = {"message": str(e)}

    return JsonResponse(response)

def get_vehicle_insurance(request):
    context = user_data(request)
    response = {"success": False, "data": []}
    dt = request.GET
    vehicle_id = dt.get("vehicle_id", None)
    subModule_id = 9


    lista = Vehicle_Insurance.objects \
    .filter(vehicle__company_id = context["company"]["id"]) \
    .values(
        "id", 
        "vehicle_id", "vehicle__name",
        "responsible_id", "responsible__first_name", "responsible__last_name",
        "policy_number", "insurance_company", "cost", "validity", "doc", "start_date", "end_date"
    )

    if context["role"]["id"] not in [1,2,3]:
        lista = lista.filter(
            vehicle__responsible_id=context["user"]["id"]
        ) | lista.filter(
            responsible_id=context["user"]["id"]
        )
    
    access = get_module_user_permissions(context, subModule_id)
    access = access["data"]["access"]

    for item in lista:
        item["btn_action"] = ""
        if item["doc"] != None:
            item["btn_action"] = f"""<a href="/{item['doc']}" class="btn btn-sm btn-info" download>
                <i class="fa-solid fa-file"></i>
            </a>\n"""
        if access["update"]:
            item["btn_action"] += """<button class=\"btn btn-primary btn-sm\" data-vehicle-insurance=\"update-item\">
                <i class="fa-solid fa-pen"></i>
            </button>\n"""
        if access["delete"]:
            item["btn_action"] += """<button class=\"btn btn-danger btn-sm\" data-vehicle-insurance=\"delete-item\">
                <i class="fa-solid fa-trash"></i>
            </button>\n"""
    response["data"] = list(lista)
    response["success"] = True
    return JsonResponse(response)

def update_vehicle_insurance(request):
    response = {"success": False, "data": []}
    dt = request.GET
    vehicle_id = dt.get("vehicle_id", None)
    return JsonResponse(response)

def delete_vehicle_insurance(request):
    response = {"success": False, "data": []}
    dt = request.POST
    id = dt.get("id", None)

    if id == None:
        response["error"] = {"message": "Proporcione un id valido"}
        return JsonResponse(response)

    try:
        obj = Vehicle_Insurance.objects.get(id = id)
    except Vehicle_Insurance.DoesNotExist:
        response["error"] = {"message": "El objeto no existe"}
        return JsonResponse(response)
    else:
        obj.delete()
    response["success"] = True
    return JsonResponse(response)



def add_vehicle_audit(request):
    response = {"success": False, "data": []}
    dt = request.POST

    vehicle_id = dt.get("vehicle_id")
    fecha = dt.get("audit_date")
    fecha_objeto = datetime.strptime(fecha, '%Y-%m-%d')
    month = fecha_objeto.month
    year = fecha_objeto.year

    if not vehicle_id:
        response["error"] = {"message": "No se proporcionó un ID de vehículo válido"}
        return JsonResponse(response)
        
    auditoria = Vehicle_Audit.objects.filter(
        audit_date__month = month,
        audit_date__year= year,
        vehicle_id = vehicle_id
    )

    if auditoria.exists():
        response["warning"] = {"message": "El vehiculo ya tiene una auditoria para el mes seleccionado"}
        return JsonResponse(response)
    
    try:
        obj = Vehicle_Audit(
            vehicle_id = dt.get("vehicle_id"),
            audit_date = dt.get("audit_date"),
            check_interior = dt.get("check_interior"),
            notes_interior = dt.get("notes_interior"),
            check_exterior = dt.get("check_exterior"),
            notes_exterior = dt.get("notes_exterior"),
            check_tires = dt.get("check_tires"),
            notes_tires = dt.get("notes_tires"),
            check_antifreeze_level = dt.get("check_antifreeze_level"),
            check_fuel_level = dt.get("check_tires"),
            general_notes = dt.get("general_notes")
        )
        obj.save()
        id = obj.id
        response["id"] = id
        response["success"] = True
    except Exception as e:
        response["success"] = False
        response["error"] = {"message": str(e)}
    response["success"] = True
    return JsonResponse(response)

def get_vehicle_audit(request):
    context = user_data(request)
    response = {"success": False, "data": []}
    dt = request.GET
    vehicle_id = dt.get("vehicle_id", None)
    subModule_id = 10

    lista = Vehicle_Audit.objects.filter(
        vehicle_id = vehicle_id
    ).values(
        "id", "vehicle_id", "vehicle__name",
        "notes_interior", "check_interior",
        "audit_date", "check_antifreeze_level",
        "check_exterior", "notes_exterior",
        "notes_tires", "check_tires",
        "check_fuel_level",
        "general_notes"
    )

    if context["role"]["id"] in [1,2,3]:
        lista = lista.filter(vehicle__company_id = context["company"]["id"])
    else:
        lista = lista.filter(vehicle__responsible_id = context["user"]["id"])
    if not context["role"]["id"] in [1,2]:
        lista = lista.exclude(visible=False)


    access = get_module_user_permissions(context, subModule_id)
    access = access["data"]["access"]
    for item in lista:
        item["btn_action"] = """<button class=\"btn btn-primary btn-sm\" data-vehicle-audit=\"show-info-details\">
            <i class="fa-sharp fa-solid fa-eye"></i>
        </button>\n"""
        item["btn_action"] += """<button class=\"btn btn-primary btn-sm\" data-vehicle-audit=\"check\" title="Check">
            <i class="fa-regular fa-ballot-check"></i>
        </button>\n"""
        if access["update"]:
            item["btn_action"] += """<button class=\"btn btn-primary btn-sm\" data-vehicle-audit=\"update-item\">
                <i class="fa-solid fa-pen"></i>
            </button>\n"""
        if access["delete"]:
            item["btn_action"] += """<button class=\"btn btn-danger btn-sm\" data-vehicle-audit=\"delete-item\">
                <i class="fa-solid fa-trash"></i>
            </button>\n"""
    response["data"] = list(lista)
    response["success"] = True
    return JsonResponse(response)

def get_vehicles_audit(request):
    context = user_data(request)
    response = {"success": False, "data": []}
    dt = request.GET
    vehicle_id = dt.get("vehicle_id", None)
    subModule_id = 10

    lista = Vehicle_Audit.objects.values(
        "id", "vehicle_id", "vehicle__name",
        "notes_interior", "check_interior",
        "audit_date", "check_antifreeze_level",
        "check_exterior", "notes_exterior",
        "notes_tires", "check_tires",
        "check_fuel_level",
        "general_notes"
    )

    if context["role"]["id"] in [1,2,3]:
        lista = lista.filter(vehicle__company_id = context["company"]["id"])
    else:
        lista = lista.filter(vehicle__responsible_id = context["user"]["id"])
    if not context["role"]["id"] in [1,2]:
        lista = lista.exclude(visible=False)

    access = get_module_user_permissions(context, subModule_id)
    access = access["data"]["access"]
    for item in lista:
        check = item["check_interior"] is not None and item["check_exterior"] is not None and item["check_tires"] is not None
        item["btn_action"] = """<button class=\"btn btn-primary btn-sm\" data-vehicle-audit=\"show-info-details\">
            <i class="fa-sharp fa-solid fa-eye"></i>
        </button>\n"""
        if not check:
            item["btn_action"] += """<button class=\"btn btn-primary btn-sm\" data-vehicle-audit=\"check\" title="Check">
            <i class="fa-regular fa-list-check"></i>
        </button>\n"""
        if access["update"]:
            item["btn_action"] += """<button class=\"btn btn-primary btn-sm\" data-vehicle-audit=\"update-item\">
                <i class="fa-solid fa-pen"></i>
            </button>\n"""
        if access["delete"]:
            item["btn_action"] += """<button class=\"btn btn-danger btn-sm\" data-vehicle-audit=\"delete-item\">
                <i class="fa-solid fa-trash"></i>
            </button>\n"""

    response["data"] = list(lista)
    response["success"] = True
    return JsonResponse(response)

def update_vehicle_audit(request):
    response = {"success": False}
    dt = request.POST

    id = dt.get("id", None)
    vehicle_id = dt.get("vehicle_id")
    company_id = request.session['company']["id"]

    if id is None or id == "":
        response["error"] = {"message": "No se proporcionó un ID válido para actualizar.", "id": id}
        return JsonResponse(response)
    
    try:
        obj = Vehicle_Audit.objects.get(id=id)
    except Vehicle_Audit.DoesNotExist:
        response["error"] = {"message": f"No existe ningún resgitro con el ID '{id}'"}
        return JsonResponse(response)
    
    try:
        obj.check_interior = dt.get("check_interior")
        obj.notes_interior = dt.get("notes_interior")
        obj.check_exterior = dt.get("check_exterior")
        obj.notes_exterior = dt.get("notes_exterior")
        obj.check_tires = dt.get("check_tires")
        obj.notes_tires = dt.get("notes_tires")
        obj.check_antifreeze_level = dt.get("check_antifreeze_level")
        obj.check_fuel_level = dt.get("check_tires")
        obj.general_notes = dt.get("general_notes")

        obj.save()

        # response["id"] = obj.id
        response["success"] = True
    except Exception as e:
        response["success"] = False
        response["error"] = {"message": str(e)}

    # ! Generar Las proximas Auditorias
    try:
        obj_vehiculos = Vehicle.objects.filter(
            company_id = company_id,
            active = True
        )

        obj_auditoria = Vehicle_Audit.objects.filter(vehicle__company_id = company_id)

        obj_auditoria_no_check = obj_auditoria.filter(
            (Q(check_interior=None) | Q(check_interior="")),
            (Q(check_exterior=None) | Q(check_exterior="")),
            (Q(check_tires=None) | Q(check_tires=""))
        )

        if obj_auditoria_no_check.count() == 0:
            """ Generar las nuevas auditorias """
            list_id_vehiculos = list(obj_vehiculos.values_list("id", flat=True))
            random.shuffle(list_id_vehiculos)

            count = len(list_id_vehiculos)
            partes_completas = count // AUDITORIA_VEHICULAR_POR_MES
            residuo = count % AUDITORIA_VEHICULAR_POR_MES
            total_partes = partes_completas + (1 if residuo != 0 else 0)

            # Fecha Final
            fecha_actual = datetime.now()

            # Calcular la fecha de inicio
            fecha_inicio = fecha_actual - timedelta(days=30 * total_partes)
            
            # Obtener los registros  de los últimos N meses
            list_id_vehiculos_auditados = Vehicle_Audit.objects.filter(
                audit_date__gte=fecha_inicio,
                audit_date__lte=fecha_actual
            ).values_list("vehicle_id", flat=True)

            vehiculos_no_auditados = set(list_id_vehiculos) - set(list_id_vehiculos_auditados)
            vehiculos_no_auditados = list(vehiculos_no_auditados)
            vehiculos_no_auditados = vehiculos_no_auditados[:AUDITORIA_VEHICULAR_POR_MES]
            
            if len(vehiculos_no_auditados) < AUDITORIA_VEHICULAR_POR_MES:
                for item in list_id_vehiculos:
                    if item not in vehiculos_no_auditados:
                        vehiculos_no_auditados.append(item)
                    if len(vehiculos_no_auditados) == AUDITORIA_VEHICULAR_POR_MES: break
                    
            # Crear las auditorias en la tabla

            # Calcular la fecha del mes siguiente
            fecha_siguiente = fecha_actual.replace(day=28) + timedelta(days=4)
            fecha_siguiente = fecha_siguiente.replace(day=28)

            # Generar una fecha aleatoria dentro del rango del día 10 al 28 del mes siguiente
            fecha_aleatoria = fecha_siguiente.replace(day=random.randint(10, 28))

            for id in vehiculos_no_auditados:
                obj = Vehicle_Audit(
                    vehicle_id = id,
                    audit_date = fecha_aleatoria
                )
                obj.save()
        pass
    except Exception as e:
        response["success"] = False
        response["error"] = {"message": str(e)}

    return JsonResponse(response)

def delete_vehicle_audit(request):
    response = {"success": False, "data": []}
    dt = request.POST
    id = dt.get("id", None)

    if id == None:
        response["error"] = {"message": "Proporcione un id valido", id: id}
        return JsonResponse(response)

    try:
        obj = Vehicle_Audit.objects.get(id = id)
    except Vehicle_Audit.DoesNotExist:
        response["error"] = {"message": "El objeto no existe"}
        return JsonResponse(response)
    else:
        obj.delete()
    response["success"] = True
    return JsonResponse(response)



def add_vehicle_maintenance(request):
    context = user_data(request)
    response = {"success": False}
    dt = request.POST
    vehicle_id = dt.get("vehicle_id")
    subModule_id = 11

    if not vehicle_id:
        response["error"] = {"message": "No se proporcionó un ID de vehículo válido"}
        return JsonResponse(response)
    
    try:
        obj_vehicle = Vehicle.objects.get(id=vehicle_id)

        # Verificamos que el kilometraje sea coerente
        mileage = Decimal(dt.get("mileage")) if dt.get("mileage") else None
        if mileage is not None and obj_vehicle.mileage is not None and obj_vehicle.mileage > mileage:
            response["warning"] = {"message": "El kilometraje del vehículo es mayor que el valor proporcionado."}
            return JsonResponse(response)
    except Vehicle.DoesNotExist:
        response["error"] = {"message": f"No se encontró ningún vehículo con el ID {vehicle_id}"}
        return JsonResponse(response)

    array = dt.getlist("actions[]")
    actions = {accion: "PENDIENTE" for accion in array}
    actions = str(actions)

    try:
        with transaction.atomic():
            obj = Vehicle_Maintenance(
                vehicle_id = dt.get("vehicle_id"),
                provider_id = dt.get("provider_id"),
                date = dt.get("date"),
                type = dt.get("type"),
                cost = dt.get("cost"),
                mileage = dt.get("mileage"),
                time = dt.get("time"),
                general_notes = dt.get("general_notes"),
                actions = actions
            )
            obj.save()

            obj_vehicle.mileage = dt.get("mileage")
            obj_vehicle.save()

            response["id"] = obj.id
        response["success"] = True
    except Exception as e:
        response["success"] = False
        response["error"] = {"message": str(e)}

    try:
        # Guardar el archivo en caso de existir
        if 'comprobante' in request.FILES and request.FILES['comprobante']:
            load_file = request.FILES['comprobante']
            company_id = request.session.get('company').get('id')
            folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/maintenance/"
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)

            file_name, extension = os.path.splitext(load_file.name)
            new_name = f"comprobante_{id}{extension}"
            
            # Eliminar el archivo anterior en caso de existir
            for item in ["png", "jpg", "jpeg","gif", "pdf", "doc", "docx", "xls", "xlsx"]:
                old_file_path = os.path.join(settings.MEDIA_ROOT, folder_path, f"comprobante_{id}.{item}")
                if os.path.exists(old_file_path): os.remove(old_file_path)
            
            fs.save(folder_path + new_name, load_file)
            
            obj.comprobante = folder_path + new_name
            obj.save()
        pass
    except Exception as e:
        pass
    return JsonResponse(response)

def get_vehicle_maintenance(request):
    context = user_data(request)
    response = {"success": False, "data": []}
    dt = request.GET
    vehicle_id = dt.get("vehicle_id", None)
    subModule_id = 11
    
    lista = Vehicle_Maintenance.objects.filter(
        vehicle_id = vehicle_id).values(
        "id", "vehicle_id", "vehicle__name",
        "provider_id", "provider__name",
        "date", "type", "cost", 
        "mileage","time", "general_notes", "actions", "comprobante"
    )

    if context["role"] in [2,3]:
        data = lista.filter(vehicle__company_id = context["company"]["id"])
    else:
        data = lista.filter(vehicle__responsible_id = context["user"]["id"])

    access = get_module_user_permissions(context, subModule_id)
    access = access["data"]["access"]
    for item in lista:
        check = item["cost"] is not None and item["mileage"] is not None
        item["btn_action"] = """<button class=\"btn btn-primary btn-sm\" data-vehicle-maintenance=\"show-info-details\">
            <i class="fa-sharp fa-solid fa-eye"></i>
        </button>\n"""
        if not check:
            item["btn_action"] += """<button class=\"btn btn-primary btn-sm\" data-vehicle-maintenance=\"check\" title="Check">
            <i class="fa-regular fa-list-check"></i>
        </button>\n"""
        if access["update"]:
            item["btn_action"] += """<button class=\"btn btn-primary btn-sm\" data-vehicle-maintenance=\"update-item\">
                <i class="fa-solid fa-pen"></i>
            </button>\n"""
        if access["delete"]:
            item["btn_action"] += """<button class=\"btn btn-danger btn-sm\" data-vehicle-maintenance=\"delete-item\">
                <i class="fa-solid fa-trash"></i>
            </button>\n"""

    response["data"] = list(lista)
    response["success"] = True
    return JsonResponse(response)

def get_vehicles_maintenance(request):
    context = user_data(request)
    response = {"success": False, "data": []}
    dt = request.GET
    subModule_id = 11
    
    lista = Vehicle_Maintenance.objects.values(
        "id", "vehicle_id", "vehicle__name",
        "provider_id", "provider__name",
        "date", "type", "cost", 
        "mileage","time", "general_notes", "actions", "comprobante"
    )

    if context["role"] in [2,3]:
        data = lista.filter(vehicle__company_id = context["company"]["id"])
    else:
        data = lista.filter(vehicle__responsible_id = context["user"]["id"])
    
    access = get_module_user_permissions(context, subModule_id)
    access = access["data"]["access"]
    
    for item in lista:
        check = item["mileage"] is not None
        item["btn_action"] = """<button class=\"btn btn-primary btn-sm\" data-vehicle-maintenance=\"show-info-details\">
            <i class="fa-sharp fa-solid fa-eye"></i>
        </button>\n"""
        if not check:
            item["btn_action"] += """<button class=\"btn btn-primary btn-sm\" data-vehicle-maintenance=\"check\" title="Check">
            <i class="fa-regular fa-list-check"></i>
        </button>\n"""
        if access["update"]:
            item["btn_action"] += """<button class=\"btn btn-primary btn-sm\" data-vehicle-maintenance=\"update-item\">
                <i class="fa-solid fa-pen"></i>
            </button>\n"""
        if access["delete"]:
            item["btn_action"] += """<button class=\"btn btn-danger btn-sm\" data-vehicle-maintenance=\"delete-item\">
                <i class="fa-solid fa-trash"></i>
            </button>\n"""

    response["data"] = list(lista)
    response["success"] = True
    return JsonResponse(response)

def update_vehicle_maintenance(request):
    response = {"success": False}
    dt = request.POST
    vehicle_id = dt.get("vehicle_id")
    id = dt.get("id", None)

    if not id:
        response["error"] = {"message": "No se proporcionó un ID válido"}
        return JsonResponse(response)
    
    try:
        obj_vehicle = Vehicle.objects.get(id=vehicle_id)

        # Verificamos que el kilometraje sea coerente
        mileage = Decimal(dt.get("mileage")) if dt.get("mileage") else None
        if mileage is not None and obj_vehicle.mileage is not None and obj_vehicle.mileage > mileage:
            response["warning"] = {"message": "El kilometraje del vehículo es mayor que el kilometraje proporcionado."}
            return JsonResponse(response)
    except Vehicle.DoesNotExist:
        response["error"] = {"message": f"No se encontró ningún vehículo con el ID {vehicle_id}"}
        return JsonResponse(response)

    try:
        obj = Vehicle_Maintenance.objects.get(id=id)
    except Vehicle_Maintenance.DoesNotExist:
        response["error"] = {"message": f"No existe ningún registro con el ID '{id}'"}
        return JsonResponse(response)

    if dt.getlist("actions[]"):
        array = dt.getlist("actions[]")
        actions = {accion: "PENDIENTE" for accion in array}
        actions = str(actions)
    elif "actionsformat2" in dt:
        actions = dt["actionsformat2"]
    else:
        actions = ""

    try:
        if dt.get("vehicle_id"):
            obj.vehicle_id = dt.get("vehicle_id")
        if dt.get("provider_id"):
            obj.provider_id = dt.get("provider_id")
        if dt.get("date"):
            obj.date = dt.get("date")
        if dt.get("type"):
            obj.type = dt.get("type")
        if dt.get("cost"):
            obj.cost = dt.get("cost")
        if dt.get("mileage"):
            obj.mileage = dt.get("mileage")
        if dt.get("time"):
            obj.time = dt.get("time")
        if dt.get("general_note"):
            obj.general_notes = dt.get("general_note", None)
        obj.actions = actions
        obj.save()
        
        # Guardar el archivo en caso de existir
        if 'comprobante' in request.FILES and request.FILES['comprobante']:
            load_file = request.FILES['comprobante']
            company_id = request.session.get('company').get('id')
            folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/maintenance/"
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)

            file_name, extension = os.path.splitext(load_file.name)
            new_name = f"comprobante_{id}{extension}"
            
            # Eliminar el archivo anterior en caso de existir
            for item in ["png", "jpg", "jpeg","gif", "pdf", "doc", "docx", "xls", "xlsx"]:
                old_file_path = os.path.join(settings.MEDIA_ROOT, folder_path, f"comprobante_{id}.{item}")
                if os.path.exists(old_file_path): os.remove(old_file_path)
            
            fs.save(folder_path + new_name, load_file)
            
            obj.comprobante = folder_path + new_name
            obj.save()

        response["success"] = True
    except Exception as e:
        response["success"] = False
        response["error"] = {"message": str(e)}
    return JsonResponse(response)

def delete_vehicle_maintenance(request):
    response = {"success": False, "data": []}
    dt = request.POST
    id = dt.get("id", None)

    if id == None:
        response["error"] = {"message": "Proporcione un id valido", id: id}
        return JsonResponse(response)

    try:
        obj = Vehicle_Maintenance.objects.get(id = id)
    except Vehicle_Maintenance.DoesNotExist:
        response["error"] = {"message": "El objeto no existe"}
        return JsonResponse(response)
    else:
        obj.delete()
    response["success"] = True
    return JsonResponse(response)


def get_notifications(request):
    response = {"success": False, "data": []}
    context = user_data(request)
    company_id = context["company"]["id"]
    fecha_actual = datetime.now().date()
    current_year = datetime.today().year
    current_month = datetime.today().month
    roles_usuario = [1,2,3]

    access = get_user_access(context)
    access = access["data"]

    obj_vehicles = Vehicle.objects.filter(company_id=company_id).values().exclude(is_active=False)
    if context["role"]["id"] not in roles_usuario:
        obj_vehicles = obj_vehicles.filter(responsible_id = context["user"]["id"])

    # !   /-----------------------------------------------/
    # !  /  VEHICULOS   / INFO
    # ! /-----------------------------------------------/
    # Nada de nada
    # !   /-----------------------------------------------/
    # !  /  VEHICULOS   / TENENCIA 
    # ! /-----------------------------------------------/
    if 5 in access and access[5]["read"]:
        obj_tenencia = Vehicle_Tenencia.objects.filter(vehiculo__company_id=company_id)

        if context["role"]["id"] not in roles_usuario:
            obj_tenencia = obj_tenencia.filter(vehiculo__responsible_id=context["user"]["id"])

        obj_tenencia = obj_tenencia.values('vehiculo__id', 'vehiculo__name').annotate(ultima_fecha_pago=Max('fecha_pago'))

        vehicles_with_tenencia = set()
        for item in obj_tenencia:
            ultima_fecha_pago = item["ultima_fecha_pago"]
            if ultima_fecha_pago < fecha_actual:
                response["data"].append({
                    "alert": "danger",
                    "icon": "<i class=\"fa-solid fa-car-side fs-18\"></i>",
                    "title": "Vehículo sin tenencia (Vencido)",
                    "text": f"Vehículo: {item['vehiculo__name']}",
                    "link": f"/module/vehicle/info/{item['vehiculo__id']}/"
                })
            elif fecha_actual <= ultima_fecha_pago <= fecha_actual + timedelta(days=5):
                dias_restantes = (ultima_fecha_pago - fecha_actual).days
                response["data"].append({
                    "alert": "info",
                    "icon": "<i class=\"fa-solid fa-info fs-18\"></i>",
                    "title": f"Tenencia a punto de vencer en {dias_restantes} días",
                    "text": f"Vehículo: {item['vehiculo__name']}",
                    "link": f"/module/vehicle/info/{item['vehiculo__id']}/"
                })
            vehicles_with_tenencia.add(item['vehiculo__id'])

        vehicles_without_tenencia = obj_vehicles.exclude(id__in=vehicles_with_tenencia)

        for vehicle in vehicles_without_tenencia:
            response["data"].append({
                "alert": "danger",
                "icon": "<i class=\"fa-solid fa-car-side fs-18\"></i>",
                "title": "Vehículo sin tenencia",
                "text": f"Vehículo: {vehicle['name']}",
                "link": f"/module/vehicle/info/{vehicle['id']}/"
            })
        pass
    # !   /-----------------------------------------------/
    # !  /  VEHICULOS   / REFRENDO 
    # ! /-----------------------------------------------/
    if 6 in access and access[6]["read"]:
        obj_refrendo = Vehicle_Refrendo.objects.filter(vehiculo__company_id=company_id)

        # Filtrar por el rol del usuario
        if context["role"]["id"] not in roles_usuario:
            obj_refrendo = obj_refrendo.filter(vehiculo__responsible_id=context["user"]["id"])

        # Anotar la última fecha de pago por vehículo
        obj_refrendo = obj_refrendo.values('vehiculo__id', 'vehiculo__name') \
            .annotate(ultima_fecha=Max('fecha_pago'))
        
        # Verificar si hay vehículos sin refrendos o vencidos
        vehicles_with_refrendo = set()
        for item in obj_refrendo:
            if item["ultima_fecha"] < fecha_actual:
                response["data"].append({
                    "alert": "warning",
                    "icon": "<i class=\"fa-solid fa-car-side fs-18\"></i>",
                    "title": "Vehículo sin refrendo (Vencido)",
                    "text": f"Vehículo: {item['vehiculo__name']}",
                    "link": f"/module/vehicle/info/{item['vehiculo__id']}/"
                })
            elif item["ultima_fecha"] <= fecha_actual + timedelta(days=5):
                dias_restantes = (item["ultima_fecha"] - fecha_actual).days
                response["data"].append({
                    "alert": "info",
                    "icon": "<i class=\"fa-solid fa-info fs-18\"></i>",
                    "title": f"refrendo a punto de vencer en {abs(dias_restantes)} días",
                    "text": f"Vehículo: {item['vehiculo__name']}",
                    "link": f"/module/vehicle/info/{item['vehiculo__id']}/"
                })
            vehicles_with_refrendo.add(item['vehiculo__id'])
        
        # Obtener los vehículos que no tienen registros de seguro
        vehicles_without_refrendo = obj_vehicles.exclude(id__in=vehicles_with_refrendo) \
            .values_list('name', flat=True)

        # Agregar vehículos sin registros de refrendo
        for name in vehicles_without_refrendo:
            response["data"].append({
                "alert": "danger",
                "icon": "<i class=\"fa-solid fa-car-side fs-18\"></i>",
                "title": "Vehículo sin refrendo",
                "text": f"Vehículo: {name}"
            })
        pass
    # !   /-----------------------------------------------/
    # !  /  VEHICULOS   / VERIFICACION 
    # ! /-----------------------------------------------/
    if 7 in access and access[7]["read"]:
        obj_verificacion = Vehicle_Verificacion.objects.filter(vehiculo__company_id=company_id)

        if context["role"]["id"] not in roles_usuario:
            obj_verificacion = obj_verificacion.filter(vehiculo__responsible_id=context["user"]["id"])
        try:
            url = request.build_absolute_uri(settings.STATIC_URL + 'assets/json/calendario_de_verificacion.json')
            file_json = requests.get(url)
            cv = file_json.json()
            cv = cv["data"]

            def obtener_ultimo_digito(diccionario):
                plate = diccionario.get('plate', '')
                for char in reversed(plate):
                    if char.isdigit():
                        return char
                return False
            
            for item in obj_vehicles:
                # print(item)
                d = obtener_ultimo_digito(item)
                payment_months = [cv[d]["s1"][0]["month_code"], cv[d]["s1"][1]["month_code"]]
                payment_months_ES = [cv[d]["s1"][0]["month_name_ES"], cv[d]["s1"][1]["month_name_ES"]]

                registro = obj_verificacion.filter(
                    Q(fecha_pago__year= current_year) &
                    Q(fecha_pago__month__in = payment_months) &
                    Q(vehiculo_id = item["id"])
                )
                if registro.exists():
                    """" El registro existe, No hacer nada """
                elif current_month  in payment_months:
                    """" Estamos en el mes para el pago del 1er Semestre """
                    response["data"].append({
                        "alert": "warning",
                        "icon": "<i class=\"fa-regular fa-money-bill-wave fs-18\"></i>",
                        "title": f"Realizar el pago de la verificación 1er Sem.",
                        "text": f"Vehículo: {item['name']}",
                        "link": f"/module/vehicle/info/{item['id']}/"
                    })
                elif (current_month + 1)  == cv[d]["s1"][0]["month_code"]:
                    """" Falta un mes para el pago del 1er Semestre """
                    month_name_ES = cv[d]["s1"][0]["month_name_ES"]
                    response["data"].append({
                        "alert": "info",
                        "icon": "<i class=\"fa-regular fa-money-bill-wave fs-18\"></i>",
                        "title": f"Próximo pago de verificación en {month_name_ES}",
                        "text": f"Vehículo: {item['name']}",
                        "link": f"/module/vehicle/info/{item['id']}/"
                    })
                elif current_month  == cv[d]["s2"][0]["month_code"] or current_month  == cv[d]["s2"][1]["month_code"]:
                    """" Estamos en el mes para el pago del 2do Semestre """
                    response["data"].append({
                        "alert": "warning",
                        "icon": "<i class=\"fa-regular fa-money-bill-wave fs-18\"></i>",
                        "title": f"Realizar el pago de la verificación 2do Sem.",
                        "text": f"Vehículo: {item['name']}",
                        "link": f"/module/vehicle/info/{item['id']}/"
                    })
                elif (current_month + 1)  == cv[d]["s2"][0]["month_code"]:
                    """" Falta un mes para el pago del 2er Semestre """
                    month_name_ES = cv[d]["s2"][0]["month_name_ES"]
                    response["data"].append({
                        "alert": "info",
                        "icon": "<i class=\"fa-regular fa-money-bill-wave fs-18\"></i>",
                        "title": f"Próximo pago de verificación en {month_name_ES}",
                        "text": f"Vehículo: {item['name']}",
                        "link": f"/module/vehicle/info/{item['id']}/"
                    })
        except Exception as e:
            print("Error: Vehiculos Verificacion")
    # !   /-----------------------------------------------/
    # !  /  VEHICULOS / SEGUROS
    # ! /-----------------------------------------------/
    if 9 in access and access[9]["read"]:
        obj_seguros = Vehicle_Insurance.objects.filter(vehicle__company_id=company_id)

        # Filtrar por el rol del usuario
        if context["role"]["id"] not in roles_usuario:
            obj_seguros = obj_seguros.filter(vehicle__responsible_id=context["user"]["id"])

        # Anotar la última fecha de seguro por vehículo
        obj_seguros = obj_seguros.values('vehicle__id', 'vehicle__name') \
            .annotate(ultima_fecha=Max('end_date'))

        # Verificar si hay vehículos sin seguros o vencidos
        vehicles_with_seguro = set()
        for item in obj_seguros:
            ultima_fecha = item["ultima_fecha"]
            if ultima_fecha < fecha_actual:
                response["data"].append({
                    "alert": "warning",
                    "icon": "<i class=\"fa-solid fa-car-side fs-18\"></i>",
                    "title": "Vehículo sin seguro (Vencido)",
                    "text": f"Vehículo: {item['vehicle__name']}",
                    "link": f"/module/vehicle/info/{vehicle['id']}/"
                })
            elif ultima_fecha <= fecha_actual + timedelta(days=5):
                dias_restantes = (ultima_fecha - fecha_actual).days
                response["data"].append({
                    "alert": "info",
                    "icon": "<i class=\"fa-solid fa-info fs-18\"></i>",
                    "title": f"Seguro a punto de vencer en {dias_restantes} días",
                    "text": f"Vehículo: {item['vehicle__name']}",
                    "link": f"/module/vehicle/info/{vehicle['id']}/"
                })
            vehicles_with_seguro.add(item['vehicle__id'])

        # Obtener los vehículos que no tienen registros de seguro
        vehicles_without_seguro = obj_vehicles.exclude(id__in=vehicles_with_seguro)

        # Agregar notificación para vehículos sin seguro
        for vehicle in vehicles_without_seguro:
            response["data"].append({
                "alert": "danger",
                "icon": "<i class=\"fa-solid fa-car-side fs-18\"></i>",
                "title": "Vehículo sin seguro",
                "text": f"Vehículo: {vehicle['name']}",
                "link": f"/module/vehicle/info/{vehicle['id']}/"
            })
        pass
    # !   /-----------------------------------------------/
    # !  /  VEHICULOS / AUDITORIA
    # ! /-----------------------------------------------/
    if 10 in access and access[10]["read"]:
        obj_auditorias = Vehicle_Audit.objects.filter( vehicle__company_id = company_id )

        if context["role"]["id"] not in roles_usuario:
            obj_auditorias = obj_auditorias.filter(vehicle__responsible_id=context["user"]["id"])

        obj_auditorias_hoy = obj_auditorias.filter(audit_date=fecha_actual)
        obj_auditorias_hoy.filter(visible=False).update(visible=True)

        for auditoria in obj_auditorias_hoy:
            response["data"].append({
                "alert": "info",
                "icon": "<i class=\"fa-solid fa-clipboard-check fs-18\"></i>",
                "title": "Auditoría programada para hoy",
                "text": f"Vehículo: {auditoria.vehicle.name}",
                "link": f"/module/vehicle/info/{auditoria.vehicle.id}/"
            })
        pass
    # !   /-----------------------------------------------/
    # !  /  VEHICULOS / MANTENIMIENTO
    # ! /-----------------------------------------------/
    if 11 in access and access[11]["read"]:
        obj_mantenimiento = Vehicle_Maintenance.objects.filter(vehicle__company_id=company_id)

        # Filtrar por el rol del usuario
        if context["role"]["id"] not in roles_usuario:
            obj_mantenimiento = obj_mantenimiento.filter(vehicle__responsible_id=context["user"]["id"])
        pass
    # ! -----------------------------------------------
    response["recordsTotal"] = len(response["data"])
    response["success"] = True
    return JsonResponse(response)



# TODO --------------- [ END ] ----------
# ! Este es el fin