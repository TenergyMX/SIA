from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect, HttpResponse
from django.db.models import F, Q, Value, Max, Sum, CharField, BooleanField
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from modules.models import *
from users.models import *
from modules.utils import * 
from datetime import datetime, timedelta
import json, os
import requests
import random
from decimal import Decimal
from modules.utils import *
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.utils.dateparse import parse_date


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

#planes 
def plans_views(request):
    if not request.user.is_superuser:
        return render(request, "error/access_denied.html")
                      
    context = user_data(request)
    module_id = 3
    subModule_id = 3
    last_module_id = request.session.get("last_module_id", 3)
    print("esto contiene el last module id:", last_module_id)
    access = get_module_user_permissions(context, subModule_id)
    sidebar = get_sidebar(context, [1, last_module_id])
    print("esto contiene el sidebar:", sidebar)
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]


    if context["access"]["read"]:
        template = "users/plans.html"
    else:
        template = "error/access_denied.html"
    return render(request, template, context)

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
    print("esto contiene el context de permisos de usuarios:", context)
    response = {"success": False}
    dt = request.GET
    module_id = 1
    subModule_id = 2
    isList = dt.get("isList", False)
    user_role_id = context["role"]["id"]
    name_role_id = context["role"]["name"]
    print("Este es el rol del usuario: ", user_role_id)
    print("Este es el nombre del rol del usuario: ", name_role_id)

    lista = User_Access.objects.values(
        "id",
        "user_id", "user__username", "user__first_name", "user__last_name", "user__email", "user__is_active",
        "role__id", "role__name",
        "company_id", "company__name",
        "area_id", "area__code", "area__name",
    ).order_by("user__first_name")
    # Verificar el rol del usuario actual
    if user_role_id == 1:  
        pass  # No se filtra
    # Si el rol es administrador (rol 2)
    elif user_role_id == 2:  # 
        lista = lista.filter(company_id=context["company"]["id"])

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

    print("Estos son los datos del formulario:", dt)
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
            # Guardar el usuario después de actualizar los datos
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



#-------------PLANES 
#funcíon para la tabla de planes 
def get_table_plans(request):
    response = {"status": "error", "message": "Sin procesar"}
    context = user_data(request)
    subModule_id = 0
    access = get_module_user_permissions(context, subModule_id)["data"]["access"]
    area = context["area"]["name"]
    tipo_user = context["role"]["name"]
    editar = access["update"]
    eliminar = access["delete"]
    agregar = access["create"]
    
    try:
        # Obtener los datos de los planes 
        datos = list(Plans.objects.select_related(
            'company', 'module'
        ).values(
            "id", 
            "company__id", 
            "company__name",  
            "module__id", 
            "module__name",  
            "type_plan", 
            "start_date_plan",
            "end_date_plan",
            "total", 
            "status_payment_plan",
            "time_quantity_plan",  
            "time_unit_plan" 
        ))

        # Mapa de traducción para unidades de tiempo
        time_unit_translation = {
            'day': ('día', 'días'),
            'month': ('mes', 'meses'),
            'year': ('año', 'años')
        }

        plan_type_translation = {
            'basic': 'Básico',
            'advanced': 'Avanzado',
            'premium': 'Premium',
            
        }

        # Procesar cada plan
        for item in datos:
            item["type_plan"] = plan_type_translation.get(item["type_plan"], item["type_plan"])
            item["status_payment_plan"] = "Activo" if item["status_payment_plan"] else "Inactivo"
            item["btn_action"] = ""
            item["btn_action"] += (
                "<button type='button' name='update' class='btn btn-icon btn-sm btn-primary-light edit-btn' onclick='edit_plan(this)' aria-label='info'>"
                "<i class='fa-solid fa-pen'></i>"
                "</button>\n"
            )
            item["btn_action"] += (
                "<button type='button' name='delete' class='btn btn-icon btn-sm btn-danger-light delete-btn' onclick='delete_plan(this)' aria-label='delete'>"
                "<i class='fa-solid fa-trash'></i>"
                "</button>"
            )     
            
            # Formatear el periodo
            quantity = item.get("time_quantity_plan", 0)
            unit = item.get("time_unit_plan", "")
            if unit in time_unit_translation:
                unit_display = time_unit_translation[unit][0] if quantity == 1 else time_unit_translation[unit][1]
                item["periodo"] = f"{quantity} {unit_display}"

            # Calcular la fecha de pago
            #payment_date = calculate_payment_date(item.get("start_date_plan"), quantity, unit)
            #item["payment_date"] = payment_date.strftime('%Y-%m-%d') if payment_date else "N/A"

        # Respuesta exitosa con los datos procesados
        response["data"] = datos
        response["status"] = "success"
        response["message"] = "Datos cargados exitosamente"
    
    except Exception as e:
        response["status"] = "error"
        response["message"] = str(e)

    # Para depuración
    print("esto contiene mi response")
    print(response)

    return JsonResponse(response)

# Función para calcular la fecha de pago
def calculate_payment_date(start_date, quantity, unit):

    try:
        if not start_date:
            start_date = timezone.now()
            print("esto contiene mi fecha:", start_date)

        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')

        if unit == 'day':
            payment_date = start_date + timedelta(days=quantity)
            return payment_date  
        elif unit == 'month':
            return start_date + relativedelta(months=quantity)
        elif unit == 'year':
            return start_date + relativedelta(years=quantity)

        return None
    except Exception as e:
        print(f"Error al calcular la fecha de pago: {str(e)}")
        return None  

# Funcion para obtener los nombres de las empresas
@login_required
def get_company_plan(request):
    try:
        empresas = Company.objects.values('id', 'name')  
        data = list(empresas)
        return JsonResponse({'data': data}, safe=False)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

# Funcion para obtener los módulos
@login_required
def get_modules_plan(request):
    try:
        # Obtén todos los módulos disponibles
        modules = Module.objects.values('id', 'name')
        data = list(modules)
        return JsonResponse({'data': data}, safe=False)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

# Función para agregar un plan
def add_plan(request):
    print("Datos recibidos:")
    print(request.POST)
    if request.method == 'POST':
        # Obtener datos del formulario
        company_id = request.POST.get('company_plan')
        module_company = request.POST.get('modules_company')
        type_plan = request.POST.get('type_plan')
        start_date_plan = request.POST.get('start_date_plan')
        time_quantity_plan = request.POST.get('time_quantity_plan')
        time_unit_plan = request.POST.get('time_unit_plan')
        status_payment_plan = True

        # Validar campos requeridos
        if not all([company_id, module_company, type_plan, start_date_plan, time_quantity_plan, time_unit_plan]):
            return JsonResponse({"success": False, "message": "Todos los campos son obligatorios."})

        try:
            # Obtener la empresa
            company = Company.objects.get(id=company_id)

            # Comprobar si la empresa ya tiene el módulo asignado
            for module_id in module_company:
                module = Module.objects.get(id=module_id)
                # Verificar si este módulo ya está asignado a la empresa
                if Plans.objects.filter(company=company, module=module).exists():
                    return JsonResponse({"success": False, "message": f"El módulo {module.name} ya está asignado a esta empresa."})

            # Asignar el costo del plan basado en el tipo de plan
            if type_plan == 'basic':
                total_cost = 399
            elif type_plan == 'advanced':
                total_cost = 999
            elif type_plan == 'premium':
                total_cost = 1299
            else:
                return JsonResponse({"success": False, "message": "Tipo de plan no válido."})

            # Calcular la fecha de finalización usando la función 'calculate_payment_date'
            start_date = parse_date(start_date_plan)
            if not start_date:
                return JsonResponse({"success": False, "message": "Fecha de inicio no válida."})

            # Llamar a la función para calcular la fecha de pago (finalización)
            end_date = calculate_payment_date(start_date, int(time_quantity_plan), time_unit_plan)
            if not end_date:
                return JsonResponse({"success": False, "message": "Error al calcular la fecha de finalización."})

            # Crear el plan
            plan = Plans(
                company=company,
                module=module,
                type_plan=type_plan,
                start_date_plan=start_date,
                end_date_plan=end_date,
                time_unit_plan=time_unit_plan,
                time_quantity_plan=time_quantity_plan,
                total=total_cost,
                status_payment_plan=status_payment_plan,
                #status_payment_plan=True,
            )
            plan.save()

            return JsonResponse({"success": True, "message": "Plan agregado con éxito."})
        except Company.DoesNotExist:
            return JsonResponse({"success": False, "message": "Empresa no encontrada."})
        except Module.DoesNotExist:
            return JsonResponse({"success": False, "message": "Módulos no encontrados."})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Método no permitido."})

# Función para editar un plan
@csrf_exempt
def edit_plans(request):
    print("la funcion para editar esta siendo llamada")
    context = user_data(request)
    try:
        if request.method == 'POST':
            # Obtener los datos enviados por el formulario
            _id = request.POST.get('id')  
            company_id = request.POST.get('company_plan') 
            module_company = request.POST.getlist('modules_company') 
            type_plan = request.POST.get('type_plan')
            start_date_plan = request.POST.get('start_date_plan')
            time_quantity_plan = request.POST.get('time_quantity_plan')
            time_unit_plan = request.POST.get('time_unit_plan')
            status_payment_plan = request.POST.get('status')  # Activo o Inactivo

            print(f"Datos del formulario recibidos: {request.POST}")

            # Validar campos requeridos
            if not all([_id, company_id, module_company, type_plan, start_date_plan, time_quantity_plan, time_unit_plan, status_payment_plan ]):
                return JsonResponse({"success": False, "message": "Todos los campos son obligatorios."})

            try:
                # Obtener el plan que se va a editar
                plan = Plans.objects.get(id=_id)

                # Verificar si los módulos ya están asignados a la empresa
                for module_id in module_company:
                    module = Module.objects.get(id=module_id)
                    if Plans.objects.filter(company_id=company_id, module=module).exclude(id=_id).exists():
                        return JsonResponse({"success": False, "message": f"El módulo {module.name} ya está asignado a esta empresa."})

                # Asignar el costo del plan basado en el tipo de plan
                if type_plan == 'basic':
                    total_cost = 399
                elif type_plan == 'advanced':
                    total_cost = 999
                elif type_plan == 'premium':
                    total_cost = 1299
                else:
                    return JsonResponse({"success": False, "message": "Tipo de plan no válido."})

                # Calcular la fecha de finalización usando la función 'calculate_payment_date'
                start_date = parse_date(start_date_plan)
                if not start_date:
                    return JsonResponse({"success": False, "message": "Fecha de inicio no válida."})

                end_date = calculate_payment_date(start_date, int(time_quantity_plan), time_unit_plan)
                if not end_date:
                    return JsonResponse({"success": False, "message": "Error al calcular la fecha de finalización."})

                # Actualizar los campos del plan
                plan.company_id = company_id
                plan.module_id = module_company[0]  
                plan.start_date_plan = start_date
                plan.end_date_plan = end_date
                plan.time_quantity_plan = time_quantity_plan
                plan.time_unit_plan = time_unit_plan
                plan.status_payment_plan = bool(int(status_payment_plan)) 
                plan.total = total_cost
                plan.type_plan = type_plan

                print(f"Datos del plan a guardar: {plan}")
                plan.save()

                return JsonResponse({"success": True, "message": "Plan editado con éxito.", "data": {"id": plan.id,"status_payment_plan": "Activo" if plan.status_payment_plan else "Inactivo", "end_date_plan": plan.end_date_plan
                }})

            except Module.DoesNotExist:
                return JsonResponse({"success": False, "message": "Módulo no encontrado."})
            except Company.DoesNotExist:
                return JsonResponse({"success": False, "message": "Empresa no encontrada."})
            except Exception as e:
                return JsonResponse({"success": False, "message": f"Error interno: {str(e)}"})

    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error interno del servidor: {str(e)}"}, status=500)

    return JsonResponse({"success": False, "message": "Método no permitido."})

#funcion para eliminar planes
@login_required
def delete_plans(request):
    if request.method == 'POST':
        form = request.POST
        _id = form.get('id')

        if not _id:
            return JsonResponse({'success': False, 'message': 'No ID provided'})

        try:
            plans = Plans.objects.get(id=_id)
        except Plans.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Plan not found'})

        plans.delete()

        return JsonResponse({'success': True, 'message': 'Plan eliminado correctamente!'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

# Función para la tabla de empresas (Company)
def get_companys(request):
    response = {"success": False, "message": "Sin procesar"}
    try:
        isList = request.GET.get("isList", False)
        
        # Obtener los datos de las compañías
        if isList:
            lista = Company.objects.values("id", "name", "address")
        else:
            lista = Company.objects.values()

            for item in lista:
                item["btn_action"] = (
                    "<button type='button' name='update' class='btn btn-icon btn-sm btn-primary-light edit-btn' onclick='edit_companys(this)' aria-label='edit'>"
                    "<i class='fa-solid fa-pen'></i>"
                    "</button>\n"
                    "<button type='button' name='delete' class='btn btn-icon btn-sm btn-danger-light delete-btn' onclick='delete_company(this)' aria-label='delete'>"
                    "<i class='fa-solid fa-trash'></i>"
                    "</button>"
                )

        # Preparar la respuesta con los datos de las empresas
        response["data"] = list(lista)
        response["success"] = True
        response["message"] = "Datos cargados exitosamente"
    
    except Exception as e:
        response["message"] = str(e)

    # Devolver la respuesta en formato JSON
    return JsonResponse(response)

#funcion para agregar empresas
@login_required
def add_company(request):
    context = user_data(request)

    if request.method == 'POST':
        try:
            name_company = request.POST.get('name').strip()
            addres_company = request.POST.get('address')
            email_user = request.POST.get('email_company').strip()
            # Validaciones
            if not name_company or not addres_company or not email_user:
                return JsonResponse({'success': False, 'message': 'Todos los campos son obligatorios.'})
            # Verificar duplicados (sin importar mayúsculas o minúsculas)
            if Company.objects.filter(
                name__iexact=name_company
            ).exists():
                return JsonResponse({'success': False, 'message': 'El nombre de la empresa ya existe.'})
            
            if User.objects.filter(email__iexact=email_user).exists():
                return JsonResponse({'success': False, 'message': 'El correo electrónico ya está en uso.'})

            # Crear una nueva empresa
            with transaction.atomic():
                company = Company.objects.create(
                    name=name_company,
                    address=addres_company,

                )

                # Crear el usuario administrador
                username = f"admin_{name_company.replace(' ', '_').lower()}"  # Nombre de usuario
                #email = f"{username}@gmail.com"  

                user = User.objects.create_user(
                    username=username,
                    password='123456', 
                    email=email_user,
                    #email='',
                    first_name=f"Admin {name_company}",
                    last_name=''
                )
            
                # Asignar el rol de "Administrador" a este usuario
                role = Role.objects.get(name="Administrador")  
                
                # Verificar o crear el área "Sistemas" para esta empresa
                area_sistemas, created = Area.objects.get_or_create(
                    company_id=company.id,
                    name="Sistemas",
                    defaults={
                        'code': "SI",
                        'description': "Área de Sistemas",
                        'is_active': True
                    }
                )

                # Crear el acceso del usuario
                user_access = User_Access.objects.create(
                    user_id=user.id,
                    role_id=role.id,  
                    company_id=company.id, 
                    area_id=area_sistemas.id
                )

                # Agregar las áreas "Sistemas", "Compras" y "Almacén"
                areas = [
                    {"name": "Compras", "code": "CO"},
                    {"name": "Almacén", "code": "AL"}
                ]
                for area_data in areas:
                    Area.objects.get_or_create(
                        company_id=company.id,
                        name=area_data['name'],
                        defaults={
                            'code': area_data['code'],
                            'description': f"Área de {area_data['name']}",
                            'is_active': True
                        }
                    )

                active_plans = Plans.objects.filter(company=company, status_payment_plan=True)
                if active_plans.exists():
                    for plan in active_plans:
                        module = plan.module
                        User_Access.objects.create(
                            user_id=user.id,
                            company_id=company.id,
                            module_id=module.id,
                            role_id=role.id
                        )

            #permisos de administrador
            #user.is_staff = True  
                user.save()

            return JsonResponse({'success': True, 'message': 'Empresa, administrador y areas agregado correctamente!'})
        except ValidationError as e:
            return JsonResponse({'success': False, 'message': str(e)})
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Error inesperado: ' + str(e)})
    return JsonResponse({'success': False, 'message': 'Método de solicitud no válido'})

# Función para editar las empresas 
def edit_company(request):
    context = user_data(request)
    company_id = context["company"]["id"]
    try:
        if request.method == 'POST':
            _id = request.POST.get('id')
            name_company = request.POST.get('name').strip()
            address_company = request.POST.get('address').strip()

            # Validaciones
            if not all([_id, name_company, address_company]):
                return JsonResponse({'success': False, 'message': 'Todos los campos son obligatorios.'})

            company = Company.objects.get(id=_id)

            # Verificar si el nombre de la empresa cambió
            name_changed = company.name != name_company
            
            # Verificar duplicados (sin importar mayúsculas o minúsculas)
            if Company.objects.filter(name__iexact=name_company).exclude(id=_id).exists():
                return JsonResponse({'success': False, 'message': 'El nombre de la empresa ya existe.'})

            # actualizar los campos de la empresa 
            company.name = name_company
            company.address = address_company
            company.save()

            # Si el nombre de la empresa cambió, actualizar el nombre del usuario administrador
            if name_changed:
                # Obtener el usuario administrador 
                user_access = User_Access.objects.get(company_id=_id, role__name="Administrador")
                admin_user = user_access.user
                
                # Actualizar el nombre del usuario administrador
                admin_user.username = f"admin_{name_company.replace(' ', '_').lower()}"
                admin_user.first_name = f"Admin {name_company}"
                admin_user.email = f"{admin_user.username}@gmail.com"  # Actualizar email si es necesario
                admin_user.save()


            return JsonResponse({'success': True, 'message': 'Empresa editado correctamente!'})

    except Services.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Empresa no encontrado'}, status=404)

    except ValueError as ve:
        return JsonResponse({'success': False, 'message': f'Error de valor: {str(ve)}'}, status=400)

    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error interno del servidor: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'message': 'Método de solicitud inválido'})

#funcion para eliminar las empresas
@login_required
def delete_company(request):
    if request.method == 'POST':
        form = request.POST
        _id = form.get('id')

        if not _id:
            return JsonResponse({'success': False, 'message': 'No ID provided'})

        try:
            category = Company.objects.get(id=_id)
        except Company.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Category not found'})

        category.delete()

        return JsonResponse({'success': True, 'message': 'Empresa eliminada correctamente!'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

