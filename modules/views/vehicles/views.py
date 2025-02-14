from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect, HttpResponse
from django.db.models import F, Q, Value, Max, Sum, CharField, BooleanField
from django.db.models.functions import TruncMonth
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from modules.models import *
from pathlib import Path
from os.path import join, dirname
from users.models import *
from modules.utils import * 
from datetime import date, datetime, timedelta
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv
from django.core.exceptions import ValidationError
import json, os
import requests
import random
import glob
import calendar
import boto3
import boto3.session
import io
import mimetypes
from botocore.client import Config
from botocore.exceptions import ClientError
import zipfile
from zipfile import ZipFile
from io import BytesIO
from decimal import Decimal
from modules.utils import * # Esto es un helpers
#nuevas importaciones
import zipfile
import subprocess
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404


from django.core.files.base import ContentFile
import qrcode
from django.core.files.uploadedfile import InMemoryUploadedFile

dotenv_path = join(dirname(dirname(dirname(__file__))), 'awsCred.env')
load_dotenv(dotenv_path)

# TODO --------------- [ VARIABLES ] ---------- 

AUDITORIA_VEHICULAR_POR_MES = 2
AWS_BUCKET_NAME=str(os.environ.get('AWS_BUCKET_NAME'))
bucket_name=AWS_BUCKET_NAME

ALLOWED_FILE_EXTENSIONS = ['.jpg', '.jpeg', '.png']


# TODO --------------- [ VIEWS ] --------------- 
@login_required
def vehicles(request):
    context = user_data(request)
    module_id = 2
    subModule_id = 4
    request.session["last_module_id"] = module_id

    access = get_module_user_permissions(context, subModule_id)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]

    if context["access"]["read"]:
        template = "vehicles/vechicles.html"
    else:
        template = "error/access_denied.html"
    return render(request, template, context)

@login_required
def vehicles_details(request, vehicle_id = None):
    context = user_data(request)
    context["vehicle"] = {"id": vehicle_id}
    module_id = 2
    subModule_id = 4
    request.session["last_module_id"] = module_id

    access = get_module_user_permissions(context, subModule_id)
    permisos = get_user_access(context)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["permiso"] = permisos["data"]
    context["sidebar"] = sidebar["data"]

    if context["access"]["read"]:
        template = "vehicles/vechicle_details.html"
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
        template = "vehicles/vehicles_tenencia.html"
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
        template = "vehicles/vehicles_refrendo.html"
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
        template = "vehicles/vehicles_verificacion.html"
    else:
        template = "error/access_denied.html"

    return render(request, template, context)

@login_required
def module_vehicle_responsiva(request, qr="", vehicle_id = 0):
    context = user_data(request)
    module_id = 2
    submodule_id = 8

    access = get_module_user_permissions(context, submodule_id)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]

    if context["access"]["read"]:
        template = "vehicles/responsiva.html"
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
        template = "vehicles/vehicle_insurance.html"
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
        template = "vehicles/audit.html"
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
        template = "vehicles/maintenance.html"
    else:
        template = "error/access_denied.html"
    return render(request, template, context)

@login_required
def vehicles_calendar_views(request):
    context = user_data(request)
    module_id = 2
    submodule_id = 21

    access = get_module_user_permissions(context, submodule_id)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]

    if context["access"]["read"]:
        template = "vehicles/calendar.html"
    else:
        template = "error/access_denied.html"
    return render(request, template, context)

@login_required
def vehicles_fuel_views(request):
    context = user_data(request)
    module_id = 2
    submodule_id = 22

    access = get_module_user_permissions(context, submodule_id)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]

    if context["access"]["read"]:
        template = "vehicles/fuel.html"
    else:
        template = "error/access_denied.html"
    return render(request, template, context)

# TODO --------------- [ HELPER ] ----------


# TODO --------------- [ REQUEST ] ----------

def add_vehicle_info(request):
    context = user_data(request)
    response = {"success": False}
    dt = request.POST

    company_id = context["company"]["id"]

    if not company_id:
        response["success"] = False
        response["status"] = "warning"
        response["message"] = {"message": "Tu usuario con cuenta con empresa asignada"}
        return JsonResponse(response)

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
            load_file = request.FILES.get('cover-image')
            #folder_path = f"docs/{company_id}/vehicle/{id}/"
            
            s3Path = f'docs/{company_id}/vehicle/{id}/'
            #fs = FileSystemStorage(location=settings.MEDIA_ROOT)

            file_name, extension = os.path.splitext(load_file.name)                
            new_name = f"cover-image{extension}"

            # Eliminar archivos de portada anteriores usando glob
            #old_files = glob.glob(os.path.join(settings.MEDIA_ROOT, folder_path, "cover-image.*"))
            #for old_file_path in old_files:
            #    if os.path.exists(old_file_path):
            #        os.remove(old_file_path)
            #imageTemp = fs.save(folder_path + new_name, load_file)
            #localPath = folder_path + new_name
            s3Name = s3Path + new_name
            
            upload_to_s3(load_file, bucket_name, s3Name)
    
            obj.image_path = s3Name
            obj.save()
        response["success"] = True
        response["status"] = "success"
        response["message"] = "Vehículo agregado exitosamente."
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
    tempImgPath = generate_presigned_url(bucket_name, data["image_path"])
    data["image_path"] = tempImgPath
    
    response["data"] = data
    response["success"] = True
    response["imgPath"] = tempImgPath
    response["alert"] = alertas(vehicle_id, detailed=True)
    return JsonResponse(response)


def alertas(vehicle_id, detailed=False):
    """
    Verifica si el vehículo tiene registros en las tablas relacionadas.
    
    Parámetros:
    - vehicle_id: ID del vehículo a verificar.
    - detailed: Si es True, devuelve un diccionario con 'alert' y 'missing_tables'.
               Si es False, devuelve solo un booleano (True si hay alerta, False si no).
    
    Devuelve:
    - Si detailed=True: {"alert": bool, "missing_tables": list}
    - Si detailed=False: bool
    """
    tables = [
        ("tenencia", Vehicle_Tenencia, "vehiculo_id"),  # Usa vehiculo_id
        ("refrendo", Vehicle_Refrendo, "vehiculo_id"),  # Usa vehiculo_id
        ("verificacion", Vehicle_Verificacion, "vehiculo_id"),  # Usa vehiculo_id
        ("insurance", Vehicle_Insurance, "vehicle_id"),  # Usa vehicle_id
        ("audit", Vehicle_Audit, "vehicle_id"),  # Usa vehicle_id
        ("maintenance", Vehicle_Maintenance, "vehicle_id"),  # Usa vehicle_id
        ("responsiva", Vehicle_Responsive, "vehicle_id"),
        ("qr", Vehicle, "id")
    ]
    
    missing_tables = []
    
    for table_name, table, field_name in tables:
        filter_kwargs = {field_name: vehicle_id}  # Crear el filtro dinámicamente
        if not table.objects.filter(**filter_kwargs).exists():
            missing_tables.append(table_name)
    
        if table_name == "insurance":
            ultimo_seguro = table.objects.filter(**filter_kwargs).order_by('-end_date').first()  
            
            if ultimo_seguro:
                fecha_vencimiento = ultimo_seguro.end_date 
                fecha_actual = datetime.now().date()
                
                diferencia_dias = (fecha_vencimiento - fecha_actual).days
                
                if 0 <= diferencia_dias <= 30:
                    missing_tables.append(table_name)

        if table_name == "tenencia":
            ultima_tenencia = table.objects.filter(**filter_kwargs).order_by('-fecha_pago').first()  
            
            if ultima_tenencia:
                fecha_pago = ultima_tenencia.fecha_pago 
                fecha_actual = datetime.now().date()
                
                diferencia_dias = (fecha_pago - fecha_actual).days
                
                if 0 <= diferencia_dias <= 30:
                    missing_tables.append(table_name)

        if table_name == "refrendo":
            ultimo_refrendo = table.objects.filter(**filter_kwargs).order_by('-fecha_pago').first()  
            
            if ultimo_refrendo:
                fecha_pago = ultimo_refrendo.fecha_pago 
                fecha_actual = datetime.now().date()
                
                diferencia_dias = (fecha_pago - fecha_actual).days
                
                if 0 <= diferencia_dias <= 30:
                    missing_tables.append(table_name)

        if table_name == "verificacion":
            ultima_verificacion = table.objects.filter(**filter_kwargs).order_by('-fecha_pago').first()  
            
            if ultima_verificacion:
                fecha_pago = ultima_verificacion.fecha_pago 
                fecha_actual = datetime.now().date()
                
                diferencia_dias = (fecha_pago - fecha_actual).days
                
                if 0 <= diferencia_dias <= 30:
                    missing_tables.append(table_name)

        # if table_name == "responsiva":
        #     ultima_responsiva = table.objects.filter(**filter_kwargs).order_by('-end_date').first() 
            
        #     if ultima_responsiva:
        #         fecha_final = ultima_responsiva.end_date 
        #         fecha_actual = datetime.now().date()
                
        #         diferencia_dias = (fecha_final - fecha_actual).days
                
        #         if 0 <= diferencia_dias <= 30:
        #             missing_tables.append(table_name)`

        if table_name == "audit":
            ultima_auditoria = table.objects.filter(**filter_kwargs).order_by('-audit_date').first()  
            
            if ultima_auditoria:
                fecha_auditoria = ultima_auditoria.audit_date 
                fecha_actual = datetime.now().date()
                
                diferencia_dias = (fecha_auditoria - fecha_actual).days
                
                if 0 <= diferencia_dias <= 30:
                    missing_tables.append(table_name)

        if table_name == "maintenance":
            ultimo_mantenimiento = table.objects.filter(**filter_kwargs).order_by('-date').first()  
            
            if ultimo_mantenimiento:
                fecha_mantenimiento = ultimo_mantenimiento.date 
                fecha_actual = datetime.now().date()
                
                diferencia_dias = (fecha_mantenimiento - fecha_actual).days
                
                if 0 <= diferencia_dias <= 30:
                    missing_tables.append(table_name)

        if table_name == "qr":
            qrs = table.objects.filter(**filter_kwargs).first()

            if qrs:
                qr_informacion = qrs.qr_info
                qr_accesso = qrs.qr_access  
                
                if not qr_informacion or not qr_accesso:
                    missing_tables.append(table_name)
            

    if detailed:
        return {
            "alert": bool(missing_tables),  
            "missing_tables": missing_tables  
        }
    else:
        return bool(missing_tables) 


    


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
            vehicle_id = item["id"]
            item["alert"] = alertas(vehicle_id)
            
            tempImgPath = generate_presigned_url(bucket_name, item["image_path"])
            item["image_path"] = tempImgPath
            item["btn_action"] = f"""
            <a href="/vehicles/info/{item['id']}/" class="btn btn-primary btn-sm mb-1">
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
    company_id = request.session.get('company').get('id')
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
        obj.model = dt.get("model")
        obj.plate = dt.get("plate", obj.plate)
        obj.serial_number = dt.get("serial_number", obj.serial_number)
        obj.year = dt.get("year")
        obj.brand = dt.get("brand", obj.brand)
        obj.responsible_id = dt.get("responsible_id")
        obj.owner_id = dt.get("owner_id")
        obj.save()

        if 'cover-image' in request.FILES and request.FILES['cover-image'] and True:
            load_file = request.FILES.get('cover-image')
            folder_path = f"docs/{company_id}/vehicle/{id}/"
            
            #fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            file_name, extension = os.path.splitext(load_file.name)                
            new_name = f"cover-image{extension}"

            # Eliminar archivos de portada anteriores usando glob
            #old_files = glob.glob(os.path.join(settings.MEDIA_ROOT, folder_path, "cover-image.*"))
            #for old_file_path in old_files:
            #    if os.path.exists(old_file_path):
            #        os.remove(old_file_path)
            #fs.save(folder_path + new_name, load_file)
            s3Name = folder_path + new_name
            upload_to_s3(load_file, bucket_name, s3Name)
            obj.image_path = folder_path + new_name
            obj.save()
        response["status"] = "success"
        response["success"] = True
        response["message"] = "registro actualizado correctamente"
    except Exception as e:
        response["status"] = "error"
        response["message"] = str(e)
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
        delete_s3_object(AWS_BUCKET_NAME, str(obj.image_path))
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
            load_file = request.FILES.get('comprobante_pago')
            folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/tenencia/"
            #fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            file_name, extension = os.path.splitext(load_file.name)
            
            new_name = f"comprobante_pago_{id}.{extension}"
            #fs.save(folder_path + new_name, load_file)
            
            obj.comprobante_pago = folder_path + new_name
            s3Name = folder_path + new_name

            upload_to_s3(load_file, bucket_name, s3Name)

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
            load_file = request.FILES.get('comprobante_pago')
            company_id = request.session.get('company').get('id')
            folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/tenencia/{id}/"
            #fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            file_name, extension = os.path.splitext(load_file.name)                
            
            new_name = f"comprobante_pago{extension}"
            #fs.save(folder_path + new_name, load_file)
            s3Name = folder_path + new_name

            obj.comprobante_pago = folder_path + new_name
            upload_to_s3(load_file, bucket_name, s3Name)
            obj.save()
        
        response["success"] = True
    except Exception as e:
        response["error"] = {"message": str(e)}
    return JsonResponse(response)

def delete_vehicle_tenencia(request):
    response = {"success": False, "data": []}
    dt = request.POST
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
        delete_s3_object(AWS_BUCKET_NAME, str(obj.comprobante_pago))
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
            load_file = request.FILES.get('comprobante_pago')
            folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/refrendo/"
            #fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            file_name, extension = os.path.splitext(load_file.name)
            
            new_name = f"comprobante_pago_{id}{extension}"
            #fs.save(folder_path + new_name, load_file)
            
            s3Name = folder_path + new_name
            obj.comprobante_pago = folder_path + new_name
            upload_to_s3(load_file, bucket_name, s3Name)
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
            load_file = request.FILES.get('comprobante_pago')
            company_id = request.session.get('company').get('id')
            folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/refrendo/{id}/"
            #fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            file_name, extension = os.path.splitext(load_file.name)                
            
            new_name = f"comprobante_pago{extension}"
            s3Name = folder_path + new_name
            #fs.save(folder_path + new_name, load_file)
            
            obj.comprobante_pago = folder_path + new_name
            upload_to_s3(load_file, bucket_name, s3Name)
            obj.save()
        
        response["success"] = True
    except Exception as e:
        response["error"] = {"message": str(e)}
    return JsonResponse(response)

def delete_vehicle_refrendo(request):
    response = {"success": False, "data": []}
    dt = request.POST
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
        delete_s3_object(AWS_BUCKET_NAME, str(obj.comprobante_pago))
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
            load_file = request.FILES.get('comprobante_pago')
            folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/verificacion/"
            #fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            file_name, extension = os.path.splitext(load_file.name)
            
            new_name = f"comprobante_pago_{id}{extension}"
            #fs.save(folder_path + new_name, load_file)
            
            obj.comprobante_pago = folder_path + new_name
            s3Name = folder_path + new_name
            upload_to_s3(load_file, bucket_name, s3Name)
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
    vehicle_id = dt.get("vehicle_id", None)
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
        item["btn_action"] += """<button class=\"btn btn-primary btn-sm\" data-vehicle-verificacion=\"update-item\">
                <i class="fa-solid fa-pen"></i>
            </button>\n"""
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
            load_file = request.FILES.get('comprobante_pago')
            company_id = request.session.get('company').get('id')
            folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/verificacion/"
            #fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            file_name, extension = os.path.splitext(load_file.name)                
            
            new_name = f"comprobante_pago_{id}{extension}"
            s3Name = folder_path + new_name
            #fs.save(folder_path + new_name, load_file)
            
            obj.comprobante_pago = folder_path + new_name
            upload_to_s3(load_file, bucket_name, s3Name)
            obj.save()
        
        response["success"] = True
    except Exception as e:
        response["error"] = {"message": str(e)}
    return JsonResponse(response)



# cargar funcion completa
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
            response["status"] = "warning"
            response["message"] = "El kilometraje del vehículo es mayor que el valor proporcionado."
            return JsonResponse(response)
    except Vehicle.DoesNotExist:
        response["status"] = "warning"
        response["message"] = f"No se encontró ningún vehículo con el ID {vehicle_id}"
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
                load_file = request.FILES.get('signature')
                folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/responsiva/"
                #fs = FileSystemStorage(location=settings.MEDIA_ROOT)
                file_name, extension = os.path.splitext(load_file.name)

                # Eliminar el archivo anterior con el mismo nombre
#                for item in ["png", "jpg", "jpeg", "gif", "tiff", "bmp", "raw"]:
#                    old_file_path = os.path.join(settings.MEDIA_ROOT, folder_path, f"signature.{item}")
#                    if os.path.exists(old_file_path): os.remove(old_file_path)
#             
                new_name = f"signature{extension}"
                s3Name = folder_path + new_name
                #fs.save(folder_path + new_name, load_file)

                obj.signature = folder_path + new_name
                upload_to_s3(load_file, bucket_name, s3Name)
                obj.save()
        if 'image_path_exit_1' in request.FILES and request.FILES['image_path_exit_1']:
            load_file = request.FILES.get('image_path_exit_1')
            folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/responsiva/"
            #fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            file_name, extension = os.path.splitext(load_file.name)

            # Eliminar el archivo anterior con el mismo nombre
            #for item in ["png", "jpg", "jpeg", "gif", "tiff", "bmp", "raw"]:
            #    old_file_path = os.path.join(settings.MEDIA_ROOT, folder_path, f"salida_1.{item}")
            #    if os.path.exists(old_file_path): os.remove(old_file_path)
            
            new_name = f"salida_1{extension}"
            #fs.save(folder_path + new_name, load_file)

            obj.image_path_exit_1 = folder_path + new_name
            upload_to_s3(load_file, AWS_BUCKET_NAME, folder_path + new_name)
            obj.save()
        if 'image_path_exit_2' in request.FILES and request.FILES['image_path_exit_2']:
            load_file = request.FILES.get('image_path_exit_2')
            folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/responsiva/"
            #fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            file_name, extension = os.path.splitext(load_file.name)

            # Eliminar el archivo anterior con el mismo nombre
            #for item in ["png", "jpg", "jpeg", "gif", "tiff", "bmp", "raw"]:
            #    old_file_path = os.path.join(settings.MEDIA_ROOT, folder_path, f"salida_2.{item}")
            #    if os.path.exists(old_file_path): os.remove(old_file_path)
            
            new_name = f"salida_2{extension}"
            #fs.save(folder_path + new_name, load_file)

            obj.image_path_exit_2 = folder_path + new_name
            upload_to_s3(load_file, AWS_BUCKET_NAME, folder_path + new_name)
            obj.save()
        
        response["id"] = obj.id
        response["success"] = True
    except Exception as e:
        response["success"] = False
        response["error"] = {"message": str(e)}
    response["success"] = True
    return JsonResponse(response)
    
# caargar funcion completa
def get_vehicle_responsiva(request):
    context = user_data(request)
    response = {"success": False, "data": []}
    dt = request.GET
    vehicle_id = dt.get("vehicle_id", None)
    subModule_id = 8

    lista = Vehicle_Responsive.objects.filter(vehicle_id = vehicle_id).values(
        "id", "vehicle_id", "vehicle__name", "responsible_id", "responsible__first_name", "responsible__last_name",
        "image_path_entry_1", "image_path_entry_2", "image_path_exit_1", "image_path_exit_2",
        "initial_mileage", "final_mileage",
        "initial_fuel", "final_fuel",
        "start_date", "end_date",
        "signature", "destination", "trip_purpose"
    )

    modified_data_list = []

    for data in lista:
        modified_data = data.copy()

        file_path1 = data.get('image_path_exit_1')
        if file_path1:
            imagePath1 = generate_presigned_url(AWS_BUCKET_NAME, str(file_path1))
            modified_image_path_exit_1 = imagePath1
            
            modified_data['image_path_exit_1'] = modified_image_path_exit_1
            modified_data_list.append(modified_data)

        file_path2 = data.get('image_path_exit_2')
        if file_path2:
            imagePath2 = generate_presigned_url(AWS_BUCKET_NAME, str(file_path2))
            modified_image_path_exit_2 = imagePath2
            
            modified_data['image_path_exit_2'] = modified_image_path_exit_2
            modified_data_list.append(modified_data)

        signature = data.get('signature')
        if signature:
            sign = generate_presigned_url(AWS_BUCKET_NAME, str(signature))
            modified_sign = sign
            
            modified_data['signature'] = modified_sign
            modified_data_list.append(modified_data)


    access = get_module_user_permissions(context, subModule_id)
    access = access["data"]["access"]
    for item in modified_data_list:
        item["btn_action"] = """<button class=\"btn btn-primary btn-sm\" data-vehicle-responsiva=\"show-info-details\" title=\"Mostrar info\">
            <i class="fa-solid fa-eye"></i>
        </button>\n"""
        if access["delete"]:
            item["btn_action"] += """<button class=\"btn btn-danger btn-sm\" data-vehicle-responsiva=\"delete-item\">
                <i class="fa-solid fa-trash"></i>
            </button>"""
    response["data"] = list(modified_data_list)
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

    modified_data_list = []

    for data in lista:
        modified_data = data.copy()

        file_path1 = data.get('image_path_exit_1')
        if file_path1:
            imagePath1 = generate_presigned_url(AWS_BUCKET_NAME, str(file_path1))
            modified_image_path_exit_1 = imagePath1
        
            modified_data['image_path_exit_1'] = modified_image_path_exit_1
            modified_data_list.append(modified_data)
        
        file_path2 = data.get('image_path_exit_2')
        if file_path2:
            imagePath2 = generate_presigned_url(AWS_BUCKET_NAME, str(file_path2))
            modified_image_path_exit_2 = imagePath2
            
            modified_data['image_path_exit_2'] = modified_image_path_exit_2
            modified_data_list.append(modified_data)

        signature = data.get('signature')
        if signature:
            sign = generate_presigned_url(AWS_BUCKET_NAME, str(signature))
            modified_sign = sign
            
            modified_data['signature'] = modified_sign
            modified_data_list.append(modified_data)

        file_path3 = data.get('image_path_entry_1')
        # imagePath3 = generate_presigned_url(AWS_BUCKET_NAME, str(file_path3))
        # modified_image_path_exit_3 = imagePath3
        
        # modified_data['image_path_entry_1'] = modified_image_path_exit_3
        # modified_data_list.append(modified_data)

        # file_path4 = data.get('image_path_entry_2')
        # imagePath4 = generate_presigned_url(AWS_BUCKET_NAME, str(file_path4))
        # modified_image_path_exit_4 = imagePath4
        
        # modified_data['image_path_entry_2'] = modified_image_path_exit_4
        # modified_data_list.append(modified_data)

    if context["role"]["id"] == 1:
        """"""
    elif context["role"]["id"] in [1,2]:
        lista = lista.filter(vehicle__company_id = context["company"]["id"])
    else:
        lista = lista.filter(vehicle__responsible_id = context["user"]["id"])

    access = get_module_user_permissions(context, subModule_id)
    access = access["data"]["access"]

    for item in modified_data_list:
        #item["btn_action"] = ""
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
    response["data"] = list(modified_data_list)
    response["success"] = True
    return JsonResponse(response)

def update_vehicle_responsiva(request):
    response = {"success": False}
    context = user_data(request)
    dt = request.POST
    id = dt.get("id", None)
    registro = dt.get("registro", "entrada")

    if id is None or id == "":
        response["status"] = "warning"
        response["error"] = "No se proporcionó un ID válido para actualizar."
        return JsonResponse(response)
    
    try:
        obj = Vehicle_Responsive.objects.get(id=id)
    except Vehicle_Responsive.DoesNotExist:
        response["status"] = "warning"
        response["message"] = f"No existe ningún resgitro con el ID '{id}'"
        return JsonResponse(response)

    company_id = obj.vehicle.company.id
    vehicle_id = obj.vehicle.id

    try:
        obj_vehicle = Vehicle.objects.get(id = vehicle_id)

        if dt.get("final_mileage", None):
            initial_mileage = Decimal(obj.initial_mileage)
            final_mileage = Decimal(dt["final_mileage"])
            
            if initial_mileage > final_mileage:
                response["status"] = "warning"
                response["message"] = "El kilometraje inicial es mayor al kilometraje final"
                return JsonResponse(response)
            if obj_vehicle.mileage > final_mileage:
                response["status"] = "warning"
                response["message"] = "El kilometraje del vehículo es mayor que el valor proporcionado."
                return JsonResponse(response)

    except Vehicle.DoesNotExist:
        response["status"] = "error"
        response["message"] = f"No se encontró ningún vehículo con el ID {vehicle_id}"
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

        load_file_1 = request.FILES.get('image_path_entry_1')
        if load_file_1:

            load_file = request.FILES.get('image_path_entry_1')
            folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/responsiva/"
            #folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/responsiva/{registro}/"
            #fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            file_name, extension = os.path.splitext(load_file.name)

            # Eliminar el archivo anterior con el mismo nombre
            #for item in ["png", "jpg", "jpeg", "gif", "tiff", "bmp", "raw"]:
            #    old_file_path = os.path.join(settings.MEDIA_ROOT, folder_path, f"salida_1.{item}")
            #    if os.path.exists(old_file_path): os.remove(old_file_path)
            
            new_name = f"entrada_1{extension}"
            #fs.save(folder_path + new_name, load_file)

            obj.image_path_entry_1 = folder_path + new_name
            upload_to_s3(load_file, AWS_BUCKET_NAME, folder_path + new_name)
            obj.save()
        load_file_2 = request.FILES.get('image_path_entry_2')
        if load_file_2:

            load_file = request.FILES.get('image_path_entry_2')
            folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/responsiva/"
            #folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/responsiva/{registro}/"
            #fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            file_name, extension = os.path.splitext(load_file.name)

            # Eliminar el archivo anterior con el mismo nombre
            #for item in ["png", "jpg", "jpeg", "gif", "tiff", "bmp", "raw"]:
            #    old_file_path = os.path.join(settings.MEDIA_ROOT, folder_path, f"salida_1.{item}")
            #    if os.path.exists(old_file_path): os.remove(old_file_path)
            
            new_name = f"entrada_2{extension}"
            #fs.save(folder_path + new_name, load_file)

            obj.image_path_entry_2 = folder_path + new_name
            upload_to_s3(load_file, AWS_BUCKET_NAME, folder_path + new_name)
            obj.save()
        response["status"] = "success"
        response["success"] = True
    except Exception as e:
        response["status"] = "success"
        response["message"] = str(e)
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
        #delete_s3_object(AWS_BUCKET_NAME, str(obj.comprobante_pago))
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
                load_file = request.FILES.get('doc')
                company_id = request.session.get('company').get('id')
                folder_path = f'docs/{company_id}/vehicle/{vehicle_id}/seguro/'
                #fs = FileSystemStor0age(location=settings.MEDIA_ROOT)
                file_name, extension = os.path.splitext(load_file.name)
                new_name = f"doc_{obj.id}{extension}"
                #zip_buffer = io.BytesIO()
                # Eliminar el archivo anterior, si existe
                # Esto no aplica en AWS S3 Buckets
                #for item in ["pdf", "doc", "docx", "xls", "xlsx"]:
                #    old_file_path = os.path.join(settings.MEDIA_ROOT, folder_path, f"doc_{obj.id}.{item}")
                #    if os.path.exists(old_file_path):
                #        os.remove(old_file_path)

                # Crear el archivo ZIP
                #zip_file_path = os.path.join(settings.MEDIA_ROOT, folder_path, f"doc_{obj.id}.zip")
                #os.makedirs(os.path.dirname(zip_file_path), exist_ok=True)
                #with zipfile.ZipFile(zip_file_path, 'w') as zipf:
                    # Add the uploaded file to the zip file
                #    zipf.writestr(file_name + extension, load_file.read())

                #NEW SAVE ZIP IN AWS S3
                #with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                    # Add the uploaded file to the ZIP archive
                    # The first argument is the name the file will have inside the ZIP
                    # The second argument is the file-like object to add
                    #zip_file.writestr(load_file.name, load_file.read())
                 # After writing, move the buffer's pointer back to the start
                #zip_buffer.seek(0)

                #SAVE FILE WITH THE ORIGINAL EXTENSION


                s3Name = folder_path + new_name

                # Guardar la ruta del archivo ZIP en el objeto
                obj.doc = s3Name
                #zip_buffer.name = new_name
                
                upload_to_s3(load_file, bucket_name, s3Name)

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

def get_vehicles_insurance(request):
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
            tempDoc = generate_presigned_url(bucket_name, item["doc"])
            item["btn_action"] = f"""<a href="{tempDoc}" class="btn btn-sm btn-info" download>
                <i class="fa-solid fa-file"></i> Descargar
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


def get_vehicle_insurance(request):
    context = user_data(request)
    response = {"success": False, "data": []}
    dt = request.GET
    vehicle_id = dt.get("vehicle_id", None)
    subModule_id = 9

    lista = Vehicle_Insurance.objects.filter(vehicle_id = vehicle_id).values(
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
            tempDoc = generate_presigned_url(bucket_name, item["doc"])
            item["btn_action"] = f"""<a href="{tempDoc}" class="btn btn-sm btn-info" download>
                <i class="fa-solid fa-file"></i> Descargar
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
        delete_s3_object(AWS_BUCKET_NAME, str(obj.doc))
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

from django.http import JsonResponse
from django.db.models import Q
import random
from datetime import datetime, timedelta

def update_vehicle_audit(request):
    response = {"success": False}
    dt = request.POST

    vehicle_audit_id = dt.get("id")
    vehicle_id = dt.get("vehicle_id")
    company_id = request.session['company']["id"]

    if not vehicle_audit_id:
        return JsonResponse({
            "success": False,
            "error": {"message": "No se proporcionó un ID válido para actualizar."}
        })

    try:
        obj = Vehicle_Audit.objects.get(id=vehicle_audit_id)
    except Vehicle_Audit.DoesNotExist:
        return JsonResponse({
            "success": False,
            "error": {"message": f"No existe ningún registro con el ID '{vehicle_audit_id}'"}
        })

    try:
        obj.check_interior = dt.get("check_interior")
        obj.notes_interior = dt.get("notes_interior")
        obj.check_exterior = dt.get("check_exterior")
        obj.notes_exterior = dt.get("notes_exterior")
        obj.check_tires = dt.get("check_tires")
        obj.notes_tires = dt.get("notes_tires")
        obj.check_antifreeze_level = dt.get("check_antifreeze_level")
        obj.check_fuel_level = dt.get("check_fuel_level")  # Corrige este campo
        obj.general_notes = dt.get("general_notes")

        obj.save()
        response["success"] = True
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": {"message": str(e)}
        })

    # Generar las próximas auditorías
    try:
        obj_vehiculos = Vehicle.objects.filter(company_id=company_id, is_active=True)
        obj_auditoria = Vehicle_Audit.objects.filter(vehicle__company_id=company_id)

        obj_auditoria_no_check = obj_auditoria.filter(
            Q(check_interior__isnull=True) | Q(check_interior=""),
            Q(check_exterior__isnull=True) | Q(check_exterior=""),
            Q(check_tires__isnull=True) | Q(check_tires="")
        )

        if obj_auditoria_no_check.count() == 0:
            list_id_vehiculos = list(obj_vehiculos.values_list("id", flat=True))
            random.shuffle(list_id_vehiculos)

            count = len(list_id_vehiculos)
            partes_completas = count // AUDITORIA_VEHICULAR_POR_MES
            residuo = count % AUDITORIA_VEHICULAR_POR_MES
            total_partes = partes_completas + (1 if residuo != 0 else 0)

            fecha_actual = datetime.now()
            fecha_inicio = fecha_actual - timedelta(days=30 * total_partes)

            list_id_vehiculos_auditados = Vehicle_Audit.objects.filter(
                audit_date__gte=fecha_inicio,
                audit_date__lte=fecha_actual
            ).values_list("vehicle_id", flat=True)

            vehiculos_no_auditados = set(list_id_vehiculos) - set(list_id_vehiculos_auditados)
            vehiculos_no_auditados = list(vehiculos_no_auditados)[:AUDITORIA_VEHICULAR_POR_MES]

            if len(vehiculos_no_auditados) < AUDITORIA_VEHICULAR_POR_MES:
                for item in list_id_vehiculos:
                    if item not in vehiculos_no_auditados:
                        vehiculos_no_auditados.append(item)
                    if len(vehiculos_no_auditados) == AUDITORIA_VEHICULAR_POR_MES:
                        break

            fecha_siguiente = fecha_actual.replace(day=28) + timedelta(days=4)
            fecha_siguiente = fecha_siguiente.replace(day=28)
            fecha_aleatoria = fecha_siguiente.replace(day=random.randint(10, 28))

            for id in vehiculos_no_auditados:
                Vehicle_Audit.objects.create(vehicle_id=id, audit_date=fecha_aleatoria)

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
    is_new_register = dt.get("is_new_register", False)
    subModule_id = 11

    if not vehicle_id:
        response["status"] = "warning"
        response["message"] = "No se proporcionó un ID de vehículo válido"
        return JsonResponse(response)
    
    try:
        obj_vehicle = Vehicle.objects.get(id=vehicle_id)
        if is_new_register == 1:
            # Verificamos que el kilometraje sea coerente
            mileage = Decimal(dt.get("mileage")) if dt.get("mileage") else None
            if mileage is not None and obj_vehicle.mileage is not None and obj_vehicle.mileage > mileage:
                response["status"] = "warning"
                response["message"] = "El kilometraje del vehículo es mayor que el valor proporcionado."
                return JsonResponse(response)
    except Vehicle.DoesNotExist:
        response["status"] = "warning"
        response["message"] = f"No se encontró ningún vehículo con el ID {vehicle_id}"
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
        response["status"] = "success"
        response["message"] = "Exito"
    except Exception as e:
        response["success"] = False
        response["error"] = {"message": str(e)}

    try:
        # Guardar el archivo en caso de existir
        if 'comprobante' in request.FILES and request.FILES['comprobante']:
            load_file = request.FILES.get('comprobante')
            company_id = request.session.get('company').get('id')
            folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/maintenance/"
            #fs = FileSystemStorage(location=settings.MEDIA_ROOT)

            file_name, extension = os.path.splitext(load_file.name)
            new_name = f"comprobante_{id}{extension}"

            s3Name = folder_path + new_name
            
            # Eliminar el archivo anterior en caso de existir
            for item in ["png", "jpg", "jpeg","gif", "pdf", "doc", "docx", "xls", "xlsx"]:
                old_file_path = os.path.join(settings.MEDIA_ROOT, folder_path, f"comprobante_{id}.{item}")
                if os.path.exists(old_file_path): os.remove(old_file_path)
            
            #fs.save(folder_path + new_name, load_file)
            
            obj.comprobante = folder_path + new_name
            upload_to_s3(load_file, bucket_name, s3Name)
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
        item["btn_action"] = """<button class=\"btn btn-primary btn-sm\" data-sia-vehicle-maintenance=\"show-info-details\">
            <i class="fa-sharp fa-solid fa-eye"></i>
        </button>\n"""
        if not check:
            item["btn_action"] += """<button class=\"btn btn-primary btn-sm\" data-sia-vehicle-maintenance=\"check\" title="Check">
            <i class="fa-regular fa-list-check"></i>
        </button>\n"""
        if access["update"]:
            item["btn_action"] += """<button class=\"btn btn-primary btn-sm\" data-sia-vehicle-maintenance=\"update-item\">
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
        item["btn_action"] = """<button class=\"btn btn-icon btn-sm btn-primary-light\" data-sia-vehicle-maintenance=\"show-info-details\">
            <i class="fa-sharp fa-solid fa-eye"></i>
        </button>\n"""
        if not check:
            item["btn_action"] += """<button class=\"btn btn-icon btn-sm btn-primary-light\" data-sia-vehicle-maintenance=\"check\" title="Check">
            <i class="fa-regular fa-list-check"></i>
        </button>\n"""
        if access["update"]:
            item["btn_action"] += """<button class=\"btn btn-icon btn-sm btn-primary-light\" data-sia-vehicle-maintenance=\"update-item\">
                <i class="fa-solid fa-pen"></i>
            </button>\n"""
        if access["delete"]:
            item["btn_action"] += """<button class=\"btn btn-icon btn-sm btn-danger-light\" data-sia-vehicle-maintenance=\"delete-item\">
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

    context = user_data(request)
    tipo_user = context["role"]["name"].lower()

    if not id:
        response["error"] = {"message": "No se proporcionó un ID válido"}
        return JsonResponse(response)
    
    try:
        obj_vehicle = Vehicle.objects.get(id=vehicle_id)

        if tipo_user not in ["administrador", "super usuario"]:
            mileage = Decimal(dt.get("mileage")) if dt.get("mileage") else None
            if mileage is not None and obj_vehicle.mileage is not None and obj_vehicle.mileage > mileage:
                response["status"] = "warning"
                response["message"] = "El kilometraje del vehículo es mayor que el kilometraje proporcionado."
                return JsonResponse(response)
            
    except Vehicle.DoesNotExist:
        response["status"] = "success"
        response["message"] = f"No se encontró ningún vehículo con el ID {vehicle_id}"
        return JsonResponse(response)

    try:
        obj = Vehicle_Maintenance.objects.get(id=id)
    except Vehicle_Maintenance.DoesNotExist:
        response["status"] = "error"
        response["message"] = f"No existe ningún registro con el ID '{id}'"
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
        if dt.get("mileage") and (tipo_user == "administrador" or tipo_user == "super usuario"):
            obj.mileage = dt.get("mileage")
        if dt.get("time"):
            obj.time = dt.get("time")
        if dt.get("general_note"):
            obj.general_notes = dt.get("general_note", None)
        obj.actions = actions
        obj.save()
        
        # Guardar el archivo en caso de existir
        if 'comprobante' in request.FILES and request.FILES['comprobante']:
            load_file = request.FILES.get('comprobante')
            company_id = request.session.get('company').get('id')
            folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/maintenance/"
            #fs = FileSystemStorage(location=settings.MEDIA_ROOT)

            file_name, extension = os.path.splitext(load_file.name)
            new_name = f"comprobante_{id}{extension}"
            s3Name = folder_path + new_name
            
            # Eliminar el archivo anterior en caso de existir
#            for item in ["png", "jpg", "jpeg","gif", "pdf", "doc", "docx", "xls", "xlsx"]:
#                 old_file_path = os.path.join(settings.MEDIA_ROOT, folder_path, f"comprobante_{id}.{item}")
#                 if os.path.exists(old_file_path): os.remove(old_file_path)
            
            #fs.save(folder_path + new_name, load_file)
            
            obj.comprobante = folder_path + new_name
            upload_to_s3(load_file, bucket_name, s3Name)
            obj.save()

        response["status"] = "success"
        response["message"] = "Exito"
    except Exception as e:
        response["status"] = "error"
        response["message"] = str(e)
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
        delete_s3_object(AWS_BUCKET_NAME, str(obj.comprobante))
        obj.delete()
    response["success"] = True
    return JsonResponse(response)



def get_vehicles_calendar(request):
    context = user_data(request)
    response = {"status": "error", "message": "sin procesar", "data": []}
    dt = request.GET
    month = dt.get("month")
    year = dt.get("year")
    response["data"] = []
    company_id = context["company"]["id"]

    # Obtener la fecha actual
    fecha_actual = datetime.now().date()

    mante = Vehicle_Maintenance.objects.filter(vehicle__company_id = company_id).values("date", "vehicle__name")
    audit = Vehicle_Audit.objects.filter(vehicle__company_id = company_id).values("audit_date", "vehicle__name")
    tenencia = Vehicle_Tenencia.objects.filter().values("vehiculo__name", "fecha_pago")
    refrendo = Vehicle_Refrendo.objects.filter().values("vehiculo__name", "fecha_pago")
    verificacion = Vehicle_Verificacion.objects.filter().values("vehiculo__name", "fecha_pago")



    if year and year != None:
        mante = mante.filter(date__year = year)
        audit = audit.filter(audit_date__year = year)
        verificacion = verificacion.filter(fecha_pago__year = year)

    if month and month != None:
        mante = mante.filter(date__month = month)
        audit = audit.filter(audit_date__month = month)
        verificacion = verificacion.filter(fecha_pago__month = month)

    # Función auxiliar para obtener el color en función de la fecha de finalización
    def get_color(end_date):
        if end_date < fecha_actual:
            return "#A5C334"  # Verde
        else:
            return "#FFA500"
    
    # Función auxiliar para agregar eventos al response
    def add_event(event_list, title_prefix, date_field, name_field):
        for item in event_list:
            end_date = item[date_field]
            color = get_color(end_date)
            response["data"].append({
                "title": f"{title_prefix}: {item[name_field]}",
                "start": end_date,
                "end": end_date,
                "color": color,
                "description": ""
            })

    # Agregar eventos de mantenimiento, auditoría y verificación
    add_event(mante, "Mant", "date", "vehicle__name")
    add_event(audit, "Auditoria", "audit_date", "vehicle__name")
    add_event(tenencia, "Pago de Tenencia", "fecha_pago", "vehiculo__name")
    add_event(refrendo, "Pago de Refrendo", "fecha_pago", "vehiculo__name")
    add_event(verificacion, "Pago de Verificación", "fecha_pago", "vehiculo__name")


    response["status"] = "success"
    response["message"] = "eventos cargados exitosamente"
    return JsonResponse(response)



def add_vehicle_fuel(request):
    context = user_data(request)
    response = {"status": "error", "message": "sin procesar","data": []}
    dt = request.POST
    vehicle_id = dt.get("vehicle_id", None)
    responsible_id = dt.get("responsible_id", None)
    company_id = context["company"]["id"]
    
    try:
        obj = Vehicle.objects.get(id = vehicle_id)
    except Vehicle.DoesNotExist:
        response["status"] = "error"
        response["message"] = "El objeto no existe"
        return JsonResponse(response)
    
    responsible_id = obj.responsible_id

    if not responsible_id or responsible_id == None:
        response["status"] = "warning"
        response["message"] = "El vehículo no tiene un responsable asignado"

    try:
        with transaction.atomic():
            obj = Vehicle_fuel(
                vehicle_id = vehicle_id,
                responsible_id = responsible_id,
                fuel = dt.get("fuel"),
                fuel_type = dt.get("fuel_type"),
                cost = dt.get("cost"),
                notes = dt.get("notes"),
                date = dt.get("date"),
            )
            obj.save()
            id = obj.id

            if 'payment_receipt' in request.FILES and request.FILES['payment_receipt']:
                load_file = request.FILES.get('payment_receipt')
                folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/fuel/"
                #fs = FileSystemStorage(location=settings.MEDIA_ROOT)

                file_name, extension = os.path.splitext(load_file.name)                
                new_name = f"payment_receipt_{id}{extension}"

                # Eliminar archivos anteriores usando glob
                #old_files = glob.glob(os.path.join(settings.MEDIA_ROOT, folder_path, f"payment_receipt{id}.*"))
                #for old_file_path in old_files:
                #    if os.path.exists(old_file_path):
                #        os.remove(old_file_path)
                #fs.save(folder_path + new_name, load_file)
                upload_to_s3(load_file, AWS_BUCKET_NAME, folder_path + new_name)
                obj.payment_receipt = folder_path + new_name
                obj.save()

            response["id"] = obj.id
        response["status"] = "success"
        response["message"] = "Exito"
    except Exception as e:
        response["status"] = "error"
        response["message"] = str(e)
    return JsonResponse(response)

def get_vehicles_fuels(request):
    context = user_data(request)
    response = {"status": "error", "message": "sin procesar","data": []}
    dt = request.GET
    vehicle_id = dt.get("vehicle_id", None)
    subModule_id = 22

    datos = Vehicle_fuel.objects.values(
        "id",
        "vehicle_id", "vehicle__name",
        "responsible_id", "responsible__first_name", "responsible__last_name",
        "payment_receipt",
        "fuel", "fuel_type",
        "cost", "notes","date"
    )

    access = get_module_user_permissions(context, subModule_id)
    access = access["data"]["access"]
    
    for item in datos:
        item["btn_action"] = ""
        if access["update"]:
            item["btn_action"] += "<button class=\"btn btn-icon btn-sm btn-primary-light\" data-sia-vehicle-fuel=\"update-item\">" \
                "<i class=\"fa-solid fa-pen\"></i>" \
            "</button>\n"
        if access["delete"]:
            item["btn_action"] += "<button class=\"btn btn-icon btn-sm btn-danger-light\" data-sia-vehicle-fuel=\"delete-item\">" \
                "<i class=\"fa-solid fa-trash\"></i>" \
            "</button>\n"
    response["data"] = list(datos)
    response["status"] = "success"
    response["message"] = "Datos cargados exitosamente"
    return JsonResponse(response)

def get_vehicles_fuels_charts(request):
    context = user_data(request)
    dt = request.GET
    vehicle_id = dt.get("vehicle_id", None)
    tipo = dt.get("type", "Litros")
    year = dt.get("year")
    
    response = {
        "status": "error",
        "message": "sin procesar",
        "data": {
            "chart": {
                "series": {"data": []},
                "xaxis": {"categories": []},
                "yaxis": {"title": {"text": "nada"}}
            }
        }
    }

    datos = Vehicle_fuel.objects.all()
    if year:
        datos = datos.filter(date__year=year)
    if vehicle_id:
        datos = datos.filter(vehicle_id=vehicle_id)

    MONTHS_ES = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }

    if tipo in ["Litros", "Pesos"]:
        field = 'fuel' if tipo == "Litros" else 'cost'
        datos_por_mes = datos.annotate(
            mes=TruncMonth('date')
        ).values('mes').annotate(
            total=Sum(field)
        ).order_by('mes')

        for dato in datos_por_mes:
            month_name = MONTHS_ES[dato['mes'].month]
            response["data"]["chart"]["xaxis"]["categories"].append(month_name)
            response["data"]["chart"]["series"]["data"].append(float(dato['total']))

        response["data"]["chart"]["yaxis"]["title"]["text"] = "Litros" if tipo == "Litros" else "Costos"
        response["data"]["chart"]["name"] = "Litros" if tipo == "Litros" else "Importe"
        response["status"] = "success"
        response["message"] = "Datos cargados exitosamente"
    else:
        response["message"] = "Tipo no válido"

    return JsonResponse(response)

def update_vehicle_fuel(request):
    context = user_data(request)
    response = {"status": "error", "message": "sin procesar","data": []}
    dt = request.POST
    id = dt.get("id", None)
    vehicle_id = dt.get("vehicle_id", None)
    responsible_id = dt.get("responsible_id", None)
    company_id = context["company"]["id"]
    
    try:
        with transaction.atomic():
            obj = Vehicle_fuel.objects.get(id = id)
            obj.fuel = dt.get("fuel")
            obj.fuel_type = dt.get("fuel_type")
            obj.cost = dt.get("cost")
            obj.notes = dt.get("notes")
            obj.date = dt.get("date")
            obj.save()
            id = obj.id

            if 'payment_receipt' in request.FILES and request.FILES['payment_receipt']:
                load_file = request.FILES.get('payment_receipt')
                folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/fuel/"
                #fs = FileSystemStorage(location=settings.MEDIA_ROOT)

                file_name, extension = os.path.splitext(load_file.name)                
                new_name = f"payment_receipt_{id}{extension}"

                # Eliminar archivos anteriores usando glob
                old_files = glob.glob(os.path.join(settings.MEDIA_ROOT, folder_path, f"payment_receipt{id}.*"))
                for old_file_path in old_files:
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                #fs.save(folder_path + new_name, load_file)
                upload_to_s3(load_file, AWS_BUCKET_NAME, folder_path + new_name)
                obj.payment_receipt = folder_path + new_name
                obj.save()

            response["id"] = obj.id
        response["status"] = "success"
        response["message"] = "Exito"
    except Exception as e:
        response["status"] = "error"
        response["message"] = str(e)
    return JsonResponse(response)

def delete_vehicle_fuel(request):
    response = {"success": False, "data": []}
    dt = request.POST
    id = dt.get("id", None)

    if id == None:
        response["error"] = {"message": "Proporcione un id valido", id: id}
        return JsonResponse(response)

    try:
        obj = Vehicle_fuel.objects.get(id = id)
    except Vehicle_fuel.DoesNotExist:
        response["error"] = {"message": "El objeto no existe"}
        return JsonResponse(response)
    else:
        delete_s3_object(AWS_BUCKET_NAME, str(obj.payment_receipt))
        obj.delete()
    response["success"] = True
    return JsonResponse(response)



@csrf_exempt
def add_option(request):
    if request.method == 'POST':
        try:
            
            # Cargar datos del cuerpo del request
            data = json.loads(request.body)
            
            option_name = data.get('option_maintenance_name', '').strip()
            maintenance_type = data.get('maintenance_type', '').strip()

            if not option_name or not maintenance_type:
                return JsonResponse({'status': 'error', 'message': 'Faltan datos necesarios'}, status=400)

            # Definir la ruta del archivo JSON
            directorio_actual = os.path.dirname(os.path.abspath(__file__))
            directorio_json = os.path.join(directorio_actual, '..', '..', 'static', 'assets', 'json', 'vehicles-maintenance.json')

            # Cargar el JSON desde el archivo
            with open(directorio_json, 'r') as file:
                json_data = json.load(file)

            # Función para agregar un nuevo ítem
            def agregar_item(json_data, tipo_mantenimiento, nueva_descripcion):
                for mantenimiento in json_data['data']:
                    if mantenimiento['tipo'].lower() == tipo_mantenimiento.lower():
                        max_id = max([item['id'] for item in mantenimiento['items']])
                        nuevo_id = max_id + 1
                        nuevo_item = {
                            "id": nuevo_id,
                            "descripcion": nueva_descripcion
                        }
                        mantenimiento['items'].append(nuevo_item)
                        return json_data
                return None

            # Llamar a la función para agregar el ítem
            data_actualizada = agregar_item(json_data, maintenance_type, option_name)

            if data_actualizada:
                # Guardar el JSON actualizado
                with open(directorio_json, 'w') as file:
                    json.dump(data_actualizada, file, indent=4)

                # Ejecutar python manage.py collectstatic
                try:
                    subprocess.run(['python', 'manage.py', 'collectstatic', '--noinput'], check=True)
                except subprocess.CalledProcessError as e:
                    return JsonResponse({'status': 'error', 'message': 'Error al ejecutar collectstatic'}, status=500)

                return JsonResponse({'status': 'success', 'message': 'Mantenimiento agregado correctamente'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Tipo de mantenimiento no encontrado'}, status=400)
            
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Error en el formato de JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Error interno: {str(e)}'}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'},status=405)


def obtener_opciones(request):
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    directorio_json = os.path.join(directorio_actual, '..', '..', 'static', 'assets', 'json', 'vehicles-maintenance.json')

    try:
        with open(directorio_json, 'r') as file:
            json_data = json.load(file)

        opciones = []
        for mantenimiento in json_data['data']:
            for item in mantenimiento['items']:
                opciones.append({
                    'id': item['id'],
                    'descripcion': item['descripcion']
                })

        return JsonResponse(opciones, safe=False)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def delete_vehicle_verificacion(request):
    response = {"success": False, "data": []}
    dt = request.POST
    id = dt.get("id", None)

    if id == None:
        response["error"] = {"message": "Proporcione un id valido"}
        return JsonResponse(response)

    try:
        obj = Vehicle_Verificacion.objects.get(id = id)
    except Vehicle_Verificacion.DoesNotExist:
        response["error"] = {"message": "El objeto no existe"}
        return JsonResponse(response)
    else:
        obj.delete()
    response["success"] = True
    return JsonResponse(response)


#función para generar el código qr
def generate_qr(request, qr_type, vehicle_id):
    context = user_data(request)
    company_id = context["company"]["id"]
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)

    # Obtener la URL base dinámicamente
    # protocol = 'https' if request.is_secure() else 'http' 
    # host = request.get_host()  
    # BASE_URL = f"{protocol}://{host}"  

    # Verificar si el QR ya ha sido generado
    if qr_type == "consulta":
        qr_url_info = generate_presigned_url(AWS_BUCKET_NAME, str(vehicle.qr_info)) if vehicle.qr_info else None
        qr_url_access = generate_presigned_url(AWS_BUCKET_NAME, str(vehicle.qr_access)) if vehicle.qr_access else None
        
        return JsonResponse({
            'status': 'generados',
            'qr_url_info': qr_url_info,
            'qr_url_access': qr_url_access
        })
     
    # Contenido
    if qr_type == 'info':
        qr_content = f"Vehicle Info: {vehicle.name}"
    elif qr_type == 'access':
        qr_content = f"http://sia-tenergy.com/vehicles/responsiva/qr/{vehicle_id}"
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid QR type'}, status=400)
    
    # Generar el QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_content)
    qr.make(fit=True)
    
    img = qr.make_image(fill='black', back_color='white')
    
    # Guardar la imagen en un buffer
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    # Convertir el buffer en un ContentFile y darle un nombre
    # content_file = ContentFile(buffer.read())
    # content_file.name = f"qr_{vehicle_id}.png"  # Establecer un nombre para el archivo
    
    # Definir la ruta del archivo en S3
    s3Path = f'docs/{company_id}/vehicle/{vehicle_id}/qr/'
    if qr_type == 'info':
        s3Name = f"qr_info{vehicle_id}.png"
        vehicle.qr_info = s3Path+s3Name
    elif qr_type == 'access':
        s3Name = f"qr_access_{vehicle_id}.png"
        vehicle.qr_access = s3Path+s3Name 
    
    # Crear un InMemoryUploadedFile con content_type
    img = InMemoryUploadedFile(
        buffer, None, s3Name, 'image/png', buffer.getbuffer().nbytes, None
    )
    # Subir el archivo a S3 y obtener la URL
    upload_to_s3(img, AWS_BUCKET_NAME, s3Path + s3Name)
        
    vehicle.save()  # Asegurarse de guardar los cambios en el modelo
    qr_url = generate_presigned_url(AWS_BUCKET_NAME, str(s3Path + s3Name))
    return JsonResponse({'status': 'success', 'qr_url': qr_url})

#funcion para eliminar el qr
def delete_qr(request, qr_type, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    url = ""
    if qr_type == 'info' and vehicle.qr_info:
        url = str(vehicle.qr_info)
        vehicle.qr_info.delete()
    elif qr_type == 'access' and vehicle.qr_access:
        url = str(vehicle.qr_access)
        vehicle.qr_access.delete()
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid QR type or QR does not exist'}, status=400)
    delete_s3_object(AWS_BUCKET_NAME, url)
    return JsonResponse({'status':'success'})

#funcion para descargar el qr
def descargar_qr(request):
    id_vehicle = request.GET.get("id_vehicle")
    tipo_qr = request.GET.get("tipo_qr")

    vehicle = Vehicle.objects.filter(id=id_vehicle).first()
    if vehicle:
        if tipo_qr == "info":
            url_vehicle = vehicle.qr_info.url[1:]
        elif tipo_qr == "access":
            url_vehicle = vehicle.qr_access.url[1:]
        url_s3 = generate_presigned_url(AWS_BUCKET_NAME, str(url_vehicle))
        return JsonResponse({'url_vehicle':url_s3})
    else:
        return JsonResponse({'error': 'Vehicle not found'}, status=404)


def validar_vehicle_en_sa(request):
    dt = request.POST
    id_vehicle = dt.get("id_vehicle", None)
    
    responsiva = Vehicle_Responsive.objects.filter(vehicle_id=id_vehicle).order_by("-start_date").first() 
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")  # Obtiene la fecha y hora actual

    if responsiva:  # Verifica que haya un registro
        if responsiva.end_date:  # Verifica si el campo end_date tiene un valor
            km_final = responsiva.final_mileage
            gasolina_final = responsiva.final_fuel
            return JsonResponse({
                "success": "Todo bien",
                "status": "SALIDA",
                "km_final":km_final,
                "gasolina_final" : gasolina_final,
                "fecha_actual": fecha_actual  # Agrega la fecha y hora actual
            })
        else:
            registro = responsiva.id
            responsable = responsiva.responsible.id
            return JsonResponse({
                "success": "Todo bien",
                "status": "ENTRADA",
                "id_register": registro,
                "id_responsable": responsable,
                "fecha_actual": fecha_actual  # Agrega la fecha y hora actual
            })            
    else:
        return JsonResponse({
            "success": "Todo bien",
            "status": "SALIDA",
            "fecha_actual": fecha_actual  # Agrega la fecha y hora actual
        })

# TODO --------------- [ END ] ----------
# ! Este es el fin
