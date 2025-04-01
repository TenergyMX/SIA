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
from django.db.models import F, Value
from django.db.models.functions import Concat
from django.db.models import Q

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.timezone import localtime
from django.core.exceptions import MultipleObjectsReturned


dotenv_path = join(dirname(dirname(dirname(__file__))), 'awsCred.env')
load_dotenv(dotenv_path)

import threading
from PIL import Image

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

    if not check_user_access_to_module(request, module_id, subModule_id):
        return render(request, "error/access_denied.html")
    
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
    if vehicle_id is not None:
        context["vehicle_name"] = Vehicle.objects.get(id = vehicle_id).name
    module_id = 2
    subModule_id = 4
    request.session["last_module_id"] = module_id

    if not check_user_access_to_module(request, module_id, subModule_id):
        return render(request, "error/access_denied.html")
    
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

    if not check_user_access_to_module(request, module_id, subModule_id):
        return render(request, "error/access_denied.html")

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

    if not check_user_access_to_module(request, module_id, subModule_id):
        return render(request, "error/access_denied.html")

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

    if not check_user_access_to_module(request, module_id, subModule_id):
        return render(request, "error/access_denied.html")
    
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

    if not check_user_access_to_module(request, module_id, submodule_id):
        return render(request, "error/access_denied.html")
    
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

    if not check_user_access_to_module(request, module_id, submodule_id):
        return render(request, "error/access_denied.html")

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

    if not check_user_access_to_module(request, module_id, submodule_id):
        return render(request, "error/access_denied.html")

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

    if not check_user_access_to_module(request, module_id, submodule_id):
        return render(request, "error/access_denied.html")

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

    if not check_user_access_to_module(request, module_id, submodule_id):
        return render(request, "error/access_denied.html")

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

    if not check_user_access_to_module(request, module_id, submodule_id):
        return render(request, "error/access_denied.html")
    
    access = get_module_user_permissions(context, submodule_id)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]

    if context["access"]["read"]:
        template = "vehicles/fuel.html"
    else:
        template = "error/access_denied.html"
    return render(request, template, context)


@login_required
def driver_vehicles(request):
    context = user_data(request)
    module_id = 2
    submodule_id = 36

    access = get_module_user_permissions(context, submodule_id)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]

    if context["access"]["read"]:
        template = "vehicles/vehicles_driver.html"
    else:
        template = "error/access_denied.html"
    return render(request, template, context)


@login_required
def drivers_details(request, driver_id = None):
    context = user_data(request)
    context["driver"] = {"id": driver_id}
    module_id = 2
    subModule_id = 36
    request.session["last_module_id"] = module_id

    access = get_module_user_permissions(context, subModule_id)
    permisos = get_user_access(context)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["permiso"] = permisos["data"]
    context["sidebar"] = sidebar["data"]

    if context["access"]["read"]:
        template = "vehicles/driver_details.html"
    else:
        template = "error/access_denied.html"

    return render(request, template, context)


# TODO --------------- [ HELPER ] ----------


# TODO --------------- [ REQUEST ] ----------


def get_vehicle_maintenance_kilometer(request):
    dt = request.GET.get
    response = {"success":True}
    print(dt("id"))
    obj = Vehicle_Maintenance_Kilometer.objects.filter(vehiculo_id=dt("id")).order_by("-kilometer").values("id", "kilometer")
    print(obj)
    print("hola")
    for item in obj:
        id = str(item["id"])
        item["kilometer"] = str(item["kilometer"])+" km"
        item["acciones"] = f"<div class='row justify-content-center'>"
        item["acciones"] += f"<button type='submit' name='update' data-vehiculo-id='{id}' class='btn btn-primary w-auto mx-2 btn-sm'><i class='fa-solid fa-pencil'></i></button>"
        item["acciones"] += f"<button type='submit' name='delete' data-vehiculo-id='{id}' class='btn btn-danger w-auto mx-2 btn-sm'><i class='fa-solid fa-trash-can'></i></button></div>"
    response["data"] = list(obj)
    return JsonResponse(response)

def update_vehicle_kilometer(request):
    #VERIFIED SESSION USER 
    context = user_data(request)
    response = {"success":False}
    dt = request.POST.get

    company_id = context["company"]["id"]

    if not company_id:
        response["success"] = False
        response["status"] = "waring"
        response["message"] = {"message" : "Tu usuario no cuenta con empresa asignada"}
        return JsonResponse(response)
    #PREPARE THE UPDATE
    try:
        obj = Vehicle_Maintenance_Kilometer.objects.get(id = dt("id"))
        flag = Vehicle_Maintenance_Kilometer.objects.filter(vehiculo = obj.vehiculo, kilometer = dt("kilometer")).count() == 0

        if flag:
            Vehicle_Maintenance_Kilometer.objects.filter(id = dt("id")).update(kilometer = dt("kilometer"))
            response["success"] = True
            response["status"] = "success"
            response["message"] = "Kilometraje Cambiado"
        else:
            response["success"] = False
            response["error"] = {"message" : "Kilometraje establecido anteriormente"}
        
    except Exception as e:
        response["success"] = False
        response["error"] = {"message": str(e)}
    return JsonResponse(response)

def delete_vehicle_kilometer(request):
    #VERIFIED SESSION USER 
    context = user_data(request)
    response = {"success":False}
    dt = request.POST.get

    company_id = context["company"]["id"]

    if not company_id:
        response["success"] = False
        response["status"] = "waring"
        response["message"] = {"message" : "Tu usuario no cuenta con empresa asignada"}
        return JsonResponse(response)
    
    #PREPARE THE DELETE
    try:
        obj = Vehicle_Maintenance_Kilometer.objects.get(id = dt("id"))
        obj.delete()
        response["success"] = True
        response["status"] = "success"
        response["message"] = "Kilometraje eliminado" 
    except Exception as e:
        response["success"] = False
        response["error"] = {"message": str(e)}
    return JsonResponse(response)

def add_vehicle_kilometer(request):
    #VERIFIED SESSION USER 
    context = user_data(request)
    response = {"success":False}
    dt = request.POST.get

    company_id = context["company"]["id"]

    if not company_id:
        response["success"] = False
        response["status"] = "waring"
        response["message"] = {"message" : "Tu usuario no cuenta con empresa asignada"}
        return JsonResponse(response)
    
    #PREPARE THE CREATE
    try:
        #GET VEHICLE
        vehicle = Vehicle.objects.get(id = dt("id"))

        #SET THE CONDICIONAL
        flag = Vehicle_Maintenance_Kilometer.objects.filter(vehiculo = vehicle) 

        obj = Vehicle_Maintenance_Kilometer(
            vehiculo = vehicle,
            kilometer = dt("kilometer")
        )
        #IF NOT REGISTER, CREATE THE FIRTS WITHOUT COMPLAINS
        if flag.count() == 0:  
            obj.save()
            id = obj.id
            response["success"] = True
            response["status"] = "success"
            response["message"] = "Kilometraje establecido para mantenimiento"
            response["id"] = id
            
        #CHECK IF THE REGISTER IS GTH THE LAST
        elif flag.filter(kilometer = dt("kilometer")).count() == 0:
            last_obj = Vehicle_Maintenance_Kilometer.objects.filter(vehiculo = vehicle).order_by("-kilometer").first()
            if last_obj.kilometer < float(dt("kilometer")):
                obj.save()
                id = obj.id
                response["success"] = True
                response["status"] = "success"
                response["message"] = "Kilometraje establecido para mantenimiento"
                response["id"] = id
            else:
                response["success"] = False
                response["error"] = {"message" : "Kilometraje debe ser ingresado de manera incremental"}
        else:
            response["success"] = False
            response["error"] = {"message" : "Kilometraje establecido anteriormente"}

    except Exception as e:
        response["success"] = False
        response["error"] = {"message": str(e)}
        return JsonResponse(response)
    
    return JsonResponse(response)
def add_vehicle_info(request):
    context = user_data(request)
    response = {"success": False}
    dt = request.POST

    company_id = context["company"]["id"]

    if not company_id:
        response["success"] = False
        response["status"] = "warning"
        response["message"] = {"message": "Tu usuario no cuenta con empresa asignada"}
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
    tempImgPath = None
    if data["image_path"]:
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
    - Si es False, devuelve solo un booleano (True si hay alerta, False si no).
    
    Devuelve:
    - Si detailed=True: {"alert": bool, "missing_tables": list}
    - Si detailed=False: bool
    """
    tables = [
        ("tenencia", Vehicle_Tenencia, "vehiculo_id"),
        ("refrendo", Vehicle_Refrendo, "vehiculo_id"),
        ("verificacion", Vehicle_Verificacion, "vehiculo_id"),
        ("insurance", Vehicle_Insurance, "vehicle_id"),
        ("audit", Vehicle_Audit, "vehicle_id"),
        ("maintenance", Vehicle_Maintenance, "vehicle_id"),
        ("qr", Vehicle, "id")
    ]
    
    missing_tables = []
    
    for table_name, table, field_name in tables:
        try:
            filter_kwargs = {field_name: vehicle_id}
            if not table.objects.filter(**filter_kwargs).exists():
                if table_name != "maintenance":
                    missing_tables.append(table_name)
        except Exception as e:
            print(f"Error checking table {table_name}: {e}")

        if table_name == "insurance":
            try:
                ultimo_seguro = table.objects.filter(**filter_kwargs).order_by('-end_date').first()  
                
                if ultimo_seguro:
                    fecha_vencimiento = ultimo_seguro.end_date 
                    fecha_actual = datetime.now().date()
                    diferencia_dias = (fecha_vencimiento - fecha_actual).days
                
                    if 0 <= diferencia_dias <= 30:
                        missing_tables.append(table_name)
            except Exception as e:
                print(f"Error checking insurance table: {e}")

        if table_name == "tenencia":
            try:
                ultima_tenencia = table.objects.filter(**filter_kwargs).order_by('-fecha_pago').first()  
                
                if ultima_tenencia:
                    fecha_pago = ultima_tenencia.fecha_pago 
                    fecha_actual = datetime.now().date()
                    diferencia_dias = (fecha_pago - fecha_actual).days
                
                    if 0 <= diferencia_dias <= 30:
                        missing_tables.append(table_name)
            except Exception as e:
                print(f"Error checking tenencia table: {e}")

        if table_name == "refrendo":
            try:
                ultimo_refrendo = table.objects.filter(**filter_kwargs).order_by('-fecha_pago').first()  
                
                if ultimo_refrendo:
                    fecha_pago = ultimo_refrendo.fecha_pago 
                    fecha_actual = datetime.now().date()
                    diferencia_dias = (fecha_pago - fecha_actual).days
                
                    if 0 <= diferencia_dias <= 30:
                        missing_tables.append(table_name)
            except Exception as e:
                print(f"Error checking refrendo table: {e}")

        if table_name == "verificacion":
            try:
                ultima_verificacion = table.objects.filter(**filter_kwargs).order_by('-fecha_pago').first()  
                
                if ultima_verificacion:
                    fecha_pago = ultima_verificacion.fecha_pago 
                    fecha_actual = datetime.now().date()
                    diferencia_dias = (fecha_pago - fecha_actual).days
                
                    if 0 <= diferencia_dias <= 30:
                        missing_tables.append(table_name)
            except Exception as e:
                print(f"Error checking verificacion table: {e}")

        if table_name == "audit":
            try:
                ultima_auditoria = table.objects.filter(**filter_kwargs).order_by('-audit_date').first()
                
                if ultima_auditoria:
                    fecha_auditoria = ultima_auditoria.audit_date.date()
                    fecha_actual = datetime.now().date()
                    diferencia_dias = (fecha_actual - fecha_auditoria).days
                    
                    if diferencia_dias > 30:
                        missing_tables.append(table_name)
            except Exception as e:
                print(f"Error checking audit table: {e}")

        if table_name == "maintenance":
            try:
                ultimo_mantenimiento = table.objects.filter(**filter_kwargs).order_by('-date').first()  
                
                if ultimo_mantenimiento:
                    if ultimo_mantenimiento.status in ["NUEVO", "ALERTA"]:
                        missing_tables.append(table_name)
            except Exception as e:
                print(f"Error checking maintenance table: {e}")

        if table_name == "qr":
            try:
                qrs = table.objects.filter(**filter_kwargs).first()
                if qrs:
                    qr_informacion = qrs.qr_info
                    qr_accesso = qrs.qr_access  
                    
                    if not qr_informacion or not qr_accesso:
                        missing_tables.append(table_name)
            except Exception as e:
                print(f"Error checking qr table: {e}")
    
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
    try:
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
        data = data.filter(company_id=context["company"]["id"])

        if context["role"]["id"] == 4:
            data = data.filter(
                Q(responsible_id=context["user"]["id"]) |
                Q(owner_id=context["user"]["id"])
            )
        
        if isList:
            data = data.values("id", "name", "plate")
        else:
            access = get_module_user_permissions(context, subModule_id)
            access = access["data"]["access"]
            for item in data:
                try:
                    vehicle_id = item["id"]
                    item["alert"] = alertas(vehicle_id)

                    #consulta para mantenimiento en proceso 
                    maintenance_in_process = Vehicle_Maintenance.objects.filter(vehicle_id=vehicle_id, status="Proceso").exists()
                    item["maintenance_in_process"] = maintenance_in_process
                    
                    if item["image_path"]:
                        tempImgPath = generate_presigned_url(bucket_name, item["image_path"])
                        item["image_path"] = tempImgPath
                    else:
                        item["image_path"] = None
                    
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
                except Exception as e:
                    print(f"Error processing vehicle with ID {item['id']}: {e}")
        
        response["recordsTotal"] = data.count()
        response["data"] = list(data)
        response["success"] = True
    except Exception as e:
        print(f"Error fetching vehicles info: {e}")
    
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
    print(f"Vehicle ID recibido para refrendo: {vehicle_id}")

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
def add_vehicle_responsiva_back(request):
    response = {"success": False}
    context = user_data(request)
    dt = request.POST
    vehicle_id = dt.get("vehicle_id")

    #CONDITIONAL KILOMETER REGISTER GREATER THEN THE KILOMETER VEHICLE
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


    try:#TODO CONTINUE
        with transaction.atomic():

            flag = check_vehicle_kilometer(request, obj_vehicle, dt.get("initial_mileage"), dt.get("start_date"))
            if isinstance(flag, JsonResponse):
                data_flag = json.loads(flag.content.decode('utf-8')).get
                if data_flag("status") == "error":
                    return flag
                elif data_flag("status") == "warning":
                    response["warning"] = {"message" : data_flag("message")}

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
        
        if "warning" in response:
            return JsonResponse(response)
        response["id"] = obj.id
        response["success"] = True
    except Exception as e:
        response["success"] = False
        response["error"] = {"message": str(e)}
    return JsonResponse(response)
    
def get_vehicle_responsiva(request):
    context = user_data(request)
    response = {"success": False, "data": []}
    dt = request.GET
    vehicle_id = dt.get("vehicle_id", None)
    subModule_id = 8

    lista = Vehicle_Responsive.objects.filter(vehicle_id=vehicle_id).values(
        "id", "vehicle__id", "vehicle__name", "responsible__id", "responsible__first_name", "responsible__last_name",
        "image_path_entry_1", "image_path_entry_2", "image_path_exit_1", "image_path_exit_2",
        "initial_mileage", "final_mileage",
        "initial_fuel", "final_fuel",
        "start_date", "end_date",
        "signature", "destination", "trip_purpose"
    ).order_by("-id")

    modified_data_list = []

    for data in lista:
        modified_data = data.copy()

        # **Convertir la fecha a la zona local y formatearla en "DD/MM/YYYY HH:MM"**
        if modified_data.get("start_date"):
            modified_data["start_date"] = localtime(modified_data["start_date"]).strftime("%d/%m/%Y %H:%M")

        if modified_data.get("end_date"):
            modified_data["end_date"] = localtime(modified_data["end_date"]).strftime("%d/%m/%Y %H:%M")

        # Genera URLs solo si los valores existen
        if data.get('image_path_exit_1'):
            modified_data['image_path_exit_1'] = generate_presigned_url(AWS_BUCKET_NAME, str(data['image_path_exit_1']))
        
        if data.get('image_path_exit_2'):
            modified_data['image_path_exit_2'] = generate_presigned_url(AWS_BUCKET_NAME, str(data['image_path_exit_2']))
        # Genera URLs solo si los valores existen
        if data.get('image_path_entry_1'):
            modified_data['image_path_entry_1'] = generate_presigned_url(AWS_BUCKET_NAME, str(data['image_path_entry_1']))

        if data.get('image_path_entry_2'):
            modified_data['image_path_entry_2'] = generate_presigned_url(AWS_BUCKET_NAME, str(data['image_path_entry_2']))

        if data.get('signature'):
            modified_data['signature'] = generate_presigned_url(AWS_BUCKET_NAME, str(data['signature']))

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

    response["data"] = modified_data_list
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
    ).order_by("-id")
    # Filtrado según el rol del usuario

    if context["role"]["id"] in [1, 2]:
        lista = lista.filter(vehicle__company_id=context["company"]["id"])
        print(lista)
    else:
        lista = lista.filter(vehicle__responsible_id=context["user"]["id"])

    # Obtener permisos de acceso
    access = get_module_user_permissions(context, subModule_id)["data"]["access"]
    modified_data_list = []

    for data in lista:
        modified_data = data.copy()
# **Convertir la fecha a la zona local y formatearla en "DD/MM/YYYY HH:MM"**
        if modified_data.get("start_date"):
            modified_data["start_date"] = localtime(modified_data["start_date"]).strftime("%d/%m/%Y %H:%M")

        if modified_data.get("end_date"):
            modified_data["end_date"] = localtime(modified_data["end_date"]).strftime("%d/%m/%Y %H:%M")


        # Procesar imágenes y firmas
        for img_field in ["image_path_exit_1", "image_path_exit_2", "image_path_entry_1", "image_path_entry_2"]:
            if modified_data.get(img_field):
                modified_data[img_field] = generate_presigned_url(AWS_BUCKET_NAME, str(modified_data[img_field]))

        # Procesar firma
        if modified_data.get("signature"):
            modified_data["signature"] = generate_presigned_url(AWS_BUCKET_NAME, str(modified_data["signature"]))

        modified_data_list.append(modified_data)


    # Agregar botones de acción
    for item in modified_data_list:
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

    response["data"] = modified_data_list
    response["success"] = True
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

def upd_audit_checks(request):
    response = {"success": False, "data": []}
    dt = request.POST

    # Obtén la fecha y conviértela en un objeto datetime
    fecha = dt.get("audit_date")
    if not fecha:
        response["error"] = {"message": "No se proporcionó una fecha de auditoría válida"}
        return JsonResponse(response)

    fecha_objeto = datetime.strptime(fecha, '%Y-%m-%d')
    month = fecha_objeto.month
    year = fecha_objeto.year

    # Verifica que se haya proporcionado un 'vehicle_id'
    vehicle_id = dt.get("vehicle_id")
    if not vehicle_id:
        response["error"] = {"message": "No se proporcionó un ID de vehículo válido"}
        return JsonResponse(response)

    # Obtén el ID de la auditoría desde los datos recibidos
    auditoria_id = dt.get("id")
    if not auditoria_id:
        response["error"] = {"message": "No se proporcionó un ID de auditoría válido"}
        return JsonResponse(response)

    # Busca la auditoría usando el 'id' de la auditoría recibido
    try:
        auditoria = Vehicle_Audit.objects.get(id=auditoria_id)
    except Vehicle_Audit.DoesNotExist:
        response["error"] = {"message": f"No se encontró una auditoría con el id {auditoria_id}"}
        return JsonResponse(response)
    except Vehicle_Audit.MultipleObjectsReturned:
        response["error"] = {"message": "Se encontraron múltiples auditorías con ese id, lo que no debería ocurrir."}
        return JsonResponse(response)

    # Verifica que 'checks[]' no esté vacío y corrige el formato si es necesario
    checks = dt.getlist('checks[]')  # Obtiene todos los valores de 'checks[]' como una lista

    if not checks:
        response["error"] = {"message": "No se recibieron checks en la solicitud."}
        return JsonResponse(response)

    # Crear una lista para los checks con la estructura correcta
    checks_data = []
    for check_id in checks:
        try:
            # Busca el check por ID
            check = Vehicle_Audit.objects.get(id=check_id)
            checks_data.append({
                'id': check.id,
                'status': check.status,
                'notas': check.notas
            })
        except Vehicle_Audit.DoesNotExist:
            # Si el check no existe, crea uno con valores predeterminados
            checks_data.append({
                'id': check_id,
                'status': 'muy malo',
                'notas': ''
            })
    

    # Actualiza el campo 'checks' de la auditoría con los nuevos checks
    auditoria.checks = json.dumps(checks_data)
    auditoria.general_notes = dt.get("general_notes")
    auditoria.audit_date = fecha
    try:
        # Guarda la auditoría con los nuevos checks
        auditoria.save()
        response["success"] = True
        response["id"] = auditoria.id
    except Exception as e:
        response["success"] = False
        response["error"] = {"message": str(e)}

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
        "audit_date", "general_notes",
        "checks", "is_visible", "is_checked"  # Asegúrate de incluir estos campos

    )

    if context["role"]["id"] in [1,2,3]:
        lista = lista.filter(vehicle__company_id = context["company"]["id"])
    else:
        lista = lista.filter(vehicle__responsible_id = context["user"]["id"])
    if not context["role"]["id"] in [1,2]:
        lista = lista.exclude(is_visible=False)


    access = get_module_user_permissions(context, subModule_id)
    access = access["data"]["access"]
   # Botones de acción
    
    for item in lista:
        item["btn_action"] = """<button class=\"btn btn-primary btn-sm\" data-vehicle-audit=\"show-info-details\">
            <i class="fa-sharp fa-solid fa-eye"></i>
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

def get_vehicle_audit(request):
    context = user_data(request)
    response = {"success": False, "data": []}
    dt = request.GET
    vehicle_id = dt.get("vehicle_id", None)
    subModule_id = 10

    # Obtener la lista de auditorías
    lista = Vehicle_Audit.objects.filter(vehicle_id = vehicle_id).values(
        "id", "vehicle_id", "vehicle__name", 
        "audit_date", "general_notes",
        "checks", "is_visible", "is_checked"  # Asegúrate de incluir estos campos
    )

    if context["role"]["id"] in [1, 2, 3]:
        lista = lista.filter(vehicle__company_id=context["company"]["id"])
    else:
        lista = lista.filter(vehicle__responsible_id=context["user"]["id"])

    if not context["role"]["id"] in [1, 2]:
        lista = lista.exclude(is_visible=False)

    access = get_module_user_permissions(context, subModule_id)
    access = access["data"]["access"]

    for item in lista:
        if item["checks"]:
            try:
                # Reemplazar las comillas simples por dobles
                checks_string = item["checks"].replace("'", "\"")
                
                # Intentar parsear el JSON corregido
                checks_data = json.loads(checks_string)
                checks_with_names = []

                # Recorrer los checks del JSON
                for check in checks_data:
                    check_id = check.get("id")
                    check_status = check.get("status")
                    check_notes = check.get("notas")

                    # Obtener el nombre del check
                    check_name = Checks.objects.filter(id=check_id).values_list("name", flat=True).first()

                    # Construir el nuevo objeto con toda la información
                    checks_with_names.append({
                        "id": check_id,
                        "name": check_name if check_name else "Sin nombre",
                        "status": check_status,
                        "notes": check_notes
                    })

                # Reemplazar el JSON con la nueva estructura
                item["checks"] = checks_with_names
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON for checks: {e}")
                item["checks"] = []  # En caso de error, asignar lista vacía
        else:
            item["checks"] = []  # Si no hay checks, asignar lista vacía

        # Definir si la auditoría está chequeada y visible
        is_checked = item["is_checked"]  # Verifica si está chequeada
        is_visible = item["is_visible"]     # Verifica si es visible

        item["is_checked"] = is_checked
        item["is_visible"] = is_visible

        # Botones de acción
        item["btn_action"] = """<button class=\"btn btn-primary btn-sm\" data-vehicle-audit=\"show-info-details\">
            <i class="fa-sharp fa-solid fa-eye"></i>
        </button>\n"""

        # Si no está chequeada y visible, permitir la edición
        if not is_checked and is_visible:
            if access["update"]:
                item["btn_action"] += """<button class=\"btn btn-primary btn-sm\" data-vehicle-audit=\"update-item\">
                    <i class="fa-solid fa-pen"></i>
                </button>\n"""
            
        # Si tiene permisos de eliminación
        if access["delete"]:
            item["btn_action"] += """<button class=\"btn btn-danger btn-sm\" data-vehicle-audit=\"delete-item\">
                <i class="fa-solid fa-trash"></i>
            </button>\n"""
        

    # Enviar la respuesta
    response["data"] = list(lista)
    response["success"] = True
    return JsonResponse(response)

def get_vehicles_audit(request):
    context = user_data(request)
    response = {"success": False, "data": []}
    dt = request.GET
    vehicle_id = dt.get("vehicle_id", None)
    subModule_id = 10

    # Obtener la lista de auditorías
    lista = Vehicle_Audit.objects.values(
        "id", "vehicle_id", "vehicle__name", 
        "audit_date", "general_notes",
        "checks", "is_visible", "is_checked"  # Asegúrate de incluir estos campos
    )

    if context["role"]["id"] in [1, 2, 3]:
        lista = lista.filter(vehicle__company_id=context["company"]["id"])
    else:
        lista = lista.filter(vehicle__responsible_id = context["user"]["id"])
    if not context["role"]["id"] in [1,2,3]:
        lista = lista.exclude(is_visible=False)

    access = get_module_user_permissions(context, subModule_id)
    access = access["data"]["access"]

    for item in lista:
        if item["checks"]:
            try:
                # Reemplazar las comillas simples por dobles
                checks_string = item["checks"].replace("'", "\"")
                
                # Intentar parsear el JSON corregido
                checks_data = json.loads(checks_string)
                checks_with_names = []

                # Recorrer los checks del JSON
                for check in checks_data:
                    check_id = check.get("id")
                    check_status = check.get("status")
                    check_notes = check.get("notas")

                    # Obtener el nombre del check
                    check_name = Checks.objects.filter(id=check_id).values_list("name", flat=True).first()

                    # Construir el nuevo objeto con toda la información
                    checks_with_names.append({
                        "id": check_id,
                        "name": check_name if check_name else "Sin nombre",
                        "status": check_status,
                        "notes": check_notes
                    })

                # Reemplazar el JSON con la nueva estructura
                item["checks"] = checks_with_names
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON for checks: {e}")
                item["checks"] = []  # En caso de error, asignar lista vacía
        else:
            item["checks"] = []  # Si no hay checks, asignar lista vacía

        # Definir si la auditoría está chequeada y visible
        is_checked = item["is_checked"]  # Verifica si está chequeada
        is_visible = item["is_visible"]     # Verifica si es visible

        item["is_checked"] = is_checked
        item["is_visible"] = is_visible

        # Botones de acción
        item["btn_action"] = """<button class=\"btn btn-primary btn-sm\" data-vehicle-audit=\"show-info-details\">
            <i class="fa-sharp fa-solid fa-eye"></i>
        </button>\n"""

        # Si no está chequeada y visible, permitir la edición
        if not is_checked and is_visible:
            if access["update"]:
                item["btn_action"] += """<button class=\"btn btn-primary btn-sm\" data-vehicle-audit=\"update-item\">
                    <i class="fa-solid fa-pen"></i>
                </button>\n"""
            
        # Si tiene permisos de eliminación
        if access["delete"]:
            item["btn_action"] += """<button class=\"btn btn-danger btn-sm\" data-vehicle-audit=\"delete-item\">
                <i class="fa-solid fa-trash"></i>
            </button>\n"""
        

    # Enviar la respuesta
    response["data"] = list(lista)
    response["success"] = True
    return JsonResponse(response)

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

    # Validar si la auditoría existe
    try:
        obj = Vehicle_Audit.objects.get(id=vehicle_audit_id)
    except Vehicle_Audit.DoesNotExist:
        return JsonResponse({
            "success": False,
            "error": {"message": f"No existe ningún registro con el ID '{vehicle_audit_id}'"}
        })

    # Actualizar la auditoría existente
    try:
        checks_data = []

        # Iterar sobre todos los elementos de request.POST y seleccionar aquellos que comienzan con "check_" o "notas_"
        for key, value in request.POST.items():
            if key.startswith('check_'):
                # Obtener el número del check (después de "check_")
                check_id = key.split('_')[1]  # Esto extrae el número del check, por ejemplo, '9' de 'check_9'
                notes_key = f'notas_{check_id}'  # Construir la clave correspondiente de notas (por ejemplo, 'notas_9')

                # Verificar si también existe una nota correspondiente
                notes_value = request.POST.get(notes_key)

                # Si tanto el estado (check) como las notas existen, agregamos a la lista de checks_data
                if notes_value:
                    checks_data.append({
                        'id': check_id,
                        'status': value,  # El valor del check
                        'notes': notes_value  # El valor de las notas
                    })
        obj.checks = json.dumps(checks_data)


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

        # Filtrar auditorías sin checks o con checks vacíos
        obj_auditoria_no_check = [
            audit for audit in obj_auditoria
            if not audit.checks or any(
                "status" in check and isinstance(check.get("status"), str) and check.get("status").strip() == ""
                for check in json.loads(audit.checks or "[]")
            )
        ]

        if len(obj_auditoria_no_check) == 0:
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
        "mileage","time", "general_notes", "actions", "comprobante", "status"
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
            item["btn_action"] += """<button class=\"btn btn-danger btn-sm\" data-sia-vehicle-maintenance=\"delete-item\">
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
        "mileage","time", "general_notes", "actions", "comprobante", "status"
    )

    print(context["role"])
    if context["role"]["id"] in [1,2]:
        lista = lista.filter(vehicle__company_id = context["company"]["id"])
    else:
        lista = lista.filter(vehicle__responsible_id = context["user"]["id"])
    
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
        obj.status = "PROGRAMADO"
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
        response["success"] = "success"
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
        if obj.comprobante:
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
    tenencia = Vehicle_Tenencia.objects.filter(vehiculo__company_id = company_id).values("vehiculo__name", "fecha_pago")
    refrendo = Vehicle_Refrendo.objects.filter(vehiculo__company_id = company_id).values("vehiculo__name", "fecha_pago")
    verificacion = Vehicle_Verificacion.objects.filter(vehiculo__company_id = company_id).values("vehiculo__name", "fecha_pago")



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
    company_id = context["company"]["id"]
    
    datos = Vehicle_fuel.objects.filter(vehicle__company_id = company_id).values(
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
                            "descripcion":  nueva_descripcion.upper()
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
        qr_content = f"https://sia-tenergy.com/vehicles/info/{vehicle_id}/"
    elif qr_type == 'access':
        qr_content = f"https://sia-tenergy.com/vehicles/responsiva/qr/{vehicle_id}"
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

# TODO ----- [ INTERNAL FUNCTIONS ] -----
#@subject = CharField
#@to = ArrayList
#Vehicle = QuerySet
def sendEmail_UpdateKilometer(request, subject, to_send, vehicle):
    from_send = settings.EMAIL_HOST_USER
    if vehicle.responsible.username:
        responsable = vehicle.responsible.username
    else:
        responsable = "Sin responsable"
    text_content = f'Mensage Generado por plataforma: Mensage Generado por plataforma'
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ background-color: #FFFAFA; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; font-family: Arial, sans-serif; }}
            .container {{ background-color: #A5C334; padding: 36px; border-radius: 18px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); text-align: center; width: 80%; max-width: 600px; }}
            img {{ max-width: 150px; margin-bottom: 20px; }}
            h2 {{ color: #333333; }}
            p {{ color: #555555; line-height: 1.5; }}
            strong {{ color: #000000; }}
        </style>
    </head>
    <body>
        <div class="container">
            <img src="https://sia-tenergy.com/staticfiles/assets/images/brand-logos/logo.png" alt="Logo">
            <h2>{vehicle.name}</h2>
            <p>Responsable del vehiculo: {responsable}</p>
            <p>El vehículo está próximo a alcanzar el kilometraje para su revisión, por lo que es necesario programar el mantenimiento correspondiente</p>
        </div>
    </body>
    </html>
    """
    #AGREGANDO LOS CORREOS DEL ENCARGADO DEL VEHICULO Y DEL RESPONSABLE DE ALMACEN
    to_send.append(vehicle.responsible.email)
    qsUser = User_Access.objects.filter(company__id = request.session["company"]["id"], area__company__id = request.session["company"]["id"],
    area__name = 'Almacén', role__name = "Encargado").first()
    # if qsUser:
    #    to_send.append(qsUser.user.email)
    email = EmailMultiAlternatives(subject, text_content, from_send, to_send)
    email.attach_alternative(html_content, "text/html")
    email.send()
    return True

#@obj_vehicle = QuerySet Vehicle
#@kilometer = Decimal
#@date_set = DateTime

def create_maintenance_record(obj_vehicle, kilometer, date_set, next_maintenance_km):
    # Create the maintenance record
    status = "ALERTA"
    km = next_maintenance_km
    new_date = datetime.strptime(date_set, "%Y-%m-%dT%H:%M").date() + timedelta(days=14)
    
    obj_maintenance = Vehicle_Maintenance(
        vehicle=obj_vehicle,
        type="preventivo",
        status=status,
        date=new_date,
        mileage=kilometer,
        general_notes=f"Vehículo cerca de los {km} km, necesario programar revisión"
    )
    obj_maintenance.save()

def check_vehicle_kilometer(request, obj_vehicle=None, kilometer=None, date_set=None):
    response = {"status": "success"}
    print("llegamos a checar el kilometraje")
    print(obj_vehicle)
    print(kilometer)
    print(date_set)

    # Check if maintenance kilometer records exist
    obj_maintenance_kilometer = Vehicle_Maintenance_Kilometer.objects.filter(vehiculo=obj_vehicle)
    if obj_maintenance_kilometer.count() == 0:
        response["status"] = "error"
        response["error"] = {"message": "Kilometraje para mantenimiento no asignado, por favor registre el kilometraje de manera manual"}
        return JsonResponse(response)

    # Find the next maintenance kilometer
    next_maintenance = obj_maintenance_kilometer.filter(kilometer__gte=kilometer).order_by("kilometer")
    if next_maintenance.count() == 0:
        response["status"] = "error"
        response["error"] = {"message": "El próximo kilometraje para mantenimiento no ha sido registrado. Por favor, ingrese el kilometraje manualmente."}
        return JsonResponse(response)
    print("esta es la resta del mantenimiento")
    # Check if there is an active maintenance alert for the vehicle
    flag_new = Vehicle_Maintenance.objects.filter(vehicle=obj_vehicle, type="preventivo").order_by("-id").first()
    
    if flag_new and flag_new.status == "ALERTA":
        response["status"] = "warning"
        response["message"] = "Aún no se ha agendado la revisión del mantenimiento para este vehículo."
        return JsonResponse(response)
    # Check if the next maintenance kilometer is near
    next_maintenance_km = next_maintenance.first().kilometer
    flag = next_maintenance_km - Decimal(kilometer)
    print("esta es la resta del mantenimiento")
    if not flag_new and flag <= 200:
        response["status"] = "warning"
        create_maintenance_record(obj_vehicle, kilometer, date_set, next_maintenance_km)
        response["message"] = f"El kilometraje está cerca de alcanzar los {next_maintenance_km} km, se recomienda agendar una revisión."

    if flag_new:
        diferencia = abs(int(next_maintenance_km)-int(flag_new.mileage))
    else:
        diferencia = abs(int(next_maintenance_km)-int(0))
    if flag_new and flag <= 200 and flag_new.status != "ALERTA" and diferencia >= 200:
        response["status"] = "warning"
        # Create a new maintenance record if necessary
        create_maintenance_record(obj_vehicle, kilometer, date_set, next_maintenance_km)
        response["message"] = f"El kilometraje está cerca de alcanzar los {next_maintenance_km} km, se recomienda agendar una revisión."

        sendEmail_UpdateKilometer(request, "Programar Mantenimiento", [settings.EMAIL_HOST_USER], obj_vehicle)
    print("llegamos al final de checar el kilometraje")
    return JsonResponse(response)


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

            responsables = User.objects.all().order_by("first_name").values("id", "first_name")  

            return JsonResponse({
                "success": "Todo bien",
                "status": "ENTRADA",
                "id_register": registro,
                "id_responsable": responsable,
                "fecha_actual": fecha_actual, # Agrega la fecha y hora actual
                "responsables": list(responsables)
            })            
    else:
        return JsonResponse({
            "success": "Todo bien",
            "status": "SALIDA",
            "fecha_actual": fecha_actual  # Agrega la fecha y hora actual
        })

# Función para la tabla conductores
def get_table_vehicles_driver(request):
    response = {"status": "error", "message": "Sin procesar"}
    try:
        context = user_data(request)
        isList = request.GET.get("isList", False)
        subModule_id = 36

        if isList:
            datos = list(Vehicle_Driver.objects.select_related('name_driver').annotate(
                driver_name=Concat(F('name_driver__username'), Value(' '), F('name_driver__last_name'))  
            ).values("id", "company", "driver_name", "image_path"))  
        else:
            access = get_module_user_permissions(context, subModule_id)  
            access = access["data"]["access"]
            area = context["area"]["name"]
            company_id = context["company"]["id"]
            editar = access["update"]
            eliminar = access["delete"]
            tipo_user = context["role"]["name"]

            datos = list(Vehicle_Driver.objects.select_related('name_driver').annotate(
                driver_name=Concat(F('name_driver__username'), Value(' '), F('name_driver__last_name'))  
            ).filter(company_id=company_id).values("id", "company", "driver_name", "number_phone", "address", "image_path"))

            for item in datos:

                item["btn_action"] = ""
                item["btn_action"] = f"""
                <a href="/drivers/info/{item['id']}/" class="btn btn-primary btn-sm mb-1">
                    <i class="fa-solid fa-eye"></i>
                </a>\n
                """
                item["btn_action"] += (
                    "<button type='button' name='update' class='btn btn-icon btn-sm btn-primary-light edit-btn' onclick='edit_drivers(this)' aria-label='info'>"
                    "<i class='fa-solid fa-pen'></i>"
                    "</button>\n"
                )
                item["btn_action"] += (
                    "<button type='button' name='delete' class='btn btn-icon btn-sm btn-danger-light delete-btn' onclick='delete_driver(this)' aria-label='delete'>"
                    "<i class='fa-solid fa-trash'></i>"
                    "</button>"
                )
                item["alert"] = alerta_conductor(item["id"])

        response["data"] = datos
        response["status"] = "success"
        response["message"] = "Datos cargados exitosamente"
    except Exception as e:
        response["message"] = str(e)

    return JsonResponse(response)

def alerta_conductor(id_conductor):
    try:
        # Obtiene la licencia del conductor usando su ID
        licence = Licences_Driver.objects.filter(name_driver_id=id_conductor).order_by("-id").first()
        # Si no hay licencia registrada para el conductor, retorna True
        if not licence:
            return True

        # Si existe licencia, verifica la fecha de expiración
        today = timezone.now().date()
        one_month_left = today + timedelta(days=30)

        # Verifica si la fecha de expiración es dentro de un mes
        if licence.expiration_date and licence.expiration_date <= one_month_left:
            return True

        # Si no se cumplen las condiciones, retorna False
        return False
    except Exception as e:
        # En caso de algún error, devuelve False
        return False


# Funcion para obtener los nombres de los usuarios que ya han sido cargados para agregar un equipo 
@login_required
@csrf_exempt
def get_users(request):
    try:
        context = user_data(request)
        company_id = context["company"]["id"]
        if not company_id:
            return JsonResponse({'success': False, 'message': 'No se encontró la empresa asociada al usuario'}, status=400)
        
        users = User.objects.filter(
            id__in=User_Access.objects.filter(company_id=company_id).values('user_id')
        ).distinct().values('id', 'username', 'last_name')  
        data = list(users)
        return JsonResponse({'data': data}, safe=False)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

#Función para agregar un  conductor
def add_driver(request):
    context = user_data(request)
    subModule_id = 36
    response = {"success": False}
    dt = request.POST
    access = get_module_user_permissions(context, subModule_id)  
    company_id = context["company"]["id"]

    if request.method == 'POST':
        name_driver = request.POST.get('driver_vehicle').strip()
        number_phone = request.POST.get('number_phone')
        address = request.POST.get('address')  
        img = request.FILES.get('driver_image') 

        if not name_driver or not number_phone or not address:
            return JsonResponse({'success': False, 'message': 'Todos los campos son obligatorios.'})
        if Vehicle_Driver.objects.filter(name_driver=name_driver).exists() :
            return JsonResponse({'success': False, 'message': 'Este nombre ya se encuentra en la base de datos, ingresa otro diferente.'})


        try:
            with transaction.atomic():
                
                # Crear el conductor sin la imagen inicialmente
                driver = Vehicle_Driver.objects.create(
                    company_id=company_id,
                    name_driver_id=name_driver,
                    number_phone=number_phone,
                    address=address,
                )

                # Si hay imagen, procesarla
                if img:
                    # Generar la ruta de la imagen
                    s3Path = f'docs/{company_id}/vehicle/conductor/{name_driver}/'
                    # Obtener el nombre y extensión
                    file_name, extension = os.path.splitext(img.name)
                    # Nuevo nombre de la imagen
                    new_name = f"conductor_{name_driver}{extension}"
                    # Unir la ruta y el nombre
                    S3name = s3Path + new_name
                    # Subir archivo a S3 (asegúrate de tener configurada la función upload_to_s3)
                    upload_to_s3(img, bucket_name, S3name)

                    # Guardar la ruta en el modelo
                    driver.image_path = S3name
                    driver.save()

            return JsonResponse({'success': True, 'message': 'Conductor agregado correctamente!'})
        
        except ValidationError as e:
            return JsonResponse({'success': False, 'message': str(e)})
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Error inesperado: ' + str(e)})

    return JsonResponse({'success': False, 'message': 'Método de solicitud no válido'})


#función para mostrar la información antes de editar
def get_drivers(request):
    driver_id = request.GET.get('id')
    if driver_id:
        try:
            driver = Vehicle_Driver.objects.get(id=driver_id)
            driver_image_url = driver.image_path.url if driver.image_path else None
            tempImgPath = ""
            if driver_image_url != None:
                tempImgPath = generate_presigned_url(bucket_name, driver_image_url[1:])
            
            return JsonResponse({
                "success": True,
                "data": {
                    "id": driver.id,
                    "driver_id": driver.name_driver.id,
                    "driver_username": driver.name_driver.username, 
                    "number_phone": driver.number_phone,
                    "address": driver.address,
                    "driver_image": tempImgPath
                }
            })
        except Vehicle_Driver.DoesNotExist:
            return JsonResponse({"success": False, "message": "Conductor no encontrado."}, status=404)
    return JsonResponse({"success": False, "message": "ID no proporcionado."}, status=400)


#Función para editar la información 
@login_required
@csrf_exempt
def edit_driver(request):
    context = user_data(request)
    subModule_id = 36
    response = {"success": False}
    dt = request.POST
    access = get_module_user_permissions(context, subModule_id)  
    company_id = context["company"]["id"]

    if request.method == 'POST':
        _id = request.POST.get('id')
        name_driver = request.POST.get('driver_vehicle')
        number_phone = request.POST.get('number_phone')
        address = request.POST.get('address')
        img = request.FILES.get('driver_image')
   

        if not name_driver or not number_phone or not address:
            return JsonResponse({'success': False, 'message': 'Todos los campos son obligatorios.'})
        try:
            driver = Vehicle_Driver.objects.get(id=_id)
            
            driver.name_driver_id = name_driver  
            driver.number_phone = number_phone
            driver.address = address
            #actualizar la imagen si es necesario
            if img:
                # Generar la ruta de la imagen
                    s3Path = f'docs/{company_id}/vehicle/conductor/{name_driver}/'
                    # Obtener el nombre y extensión
                    file_name, extension = os.path.splitext(img.name)
                    # Nuevo nombre de la imagen
                    new_name = f"conductor_{name_driver}{extension}"
                    # Unir la ruta y el nombre
                    S3name = s3Path + new_name
                    if driver.image_path:
                        delete_s3_object(AWS_BUCKET_NAME, str(driver.image_path.url[1:]))
                    # Subir archivo a S3 (asegúrate de tener configurada la función upload_to_s3)
                    upload_to_s3(img, bucket_name, S3name)

                    # Guardar la ruta en el modelo
                    driver.image_path = S3name
                    driver.save()

            return JsonResponse({'success': True, 'message': 'Equipo editado correctamente!'})

        except Equipment_Tools.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Equipo no encontrado'}, status=404)

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error interno del servidor: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'message': 'Método de solicitud inválido'})


#funcion para eliminar conductores
@login_required
@csrf_exempt
def delete_driver(request):                          
    if request.method == 'POST':
        form = request.POST
        _id = form.get('id')

        if not _id:
            return JsonResponse({'success': False, 'message': 'No ID provided'})

        try:
            driver = Vehicle_Driver.objects.get(id=_id)
        except Vehicle_Driver.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Category not found'})

        driver.delete()

        return JsonResponse({'success': True, 'message': 'Conductor eliminado correctamente!'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

#funcion para mostrar los detalles del conductor
def get_driver_details(request, driver_id):
    driver = get_object_or_404(Vehicle_Driver.objects.select_related('company', 'name_driver'), id=driver_id)

    driver_image_url = driver.image_path.url if driver.image_path else None
    tempImgPath = ""
    if driver_image_url != None:
            tempImgPath = generate_presigned_url(bucket_name, driver_image_url[1:])
            
    data = {
        "id": driver.id,
        "name": f"{driver.name_driver.username} {driver.name_driver.last_name}" if driver.name_driver else "No asignado",
        "company__name": driver.company.name if driver.company else "No asignada",
        "number_phone": driver.number_phone if driver.number_phone else "No disponible",
        "address": driver.address if driver.address else "No disponible",
        "image_path": tempImgPath
    }

    return JsonResponse(data)


#función para agregar licencia
def add_licence(request):
    context = user_data(request)
    dt = request.POST
    company_id = context["company"]["id"]

    if request.method == 'POST':        
        name_driver_id = request.POST.get('name_driver_id', '').strip() 
        start_date = request.POST.get('start_date')
        expiration_date = request.POST.get('expiration_date')  
        license_driver = request.FILES.get('license_driver') 

        if not name_driver_id or not start_date or not expiration_date or not license_driver:
            return JsonResponse({'success': False, 'message': 'Todos los campos son obligatorios.'})
        
        try:
            # Convertir las fechas a objetos de tipo datetime
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            expiration_date_obj = datetime.strptime(expiration_date, '%Y-%m-%d')

            # Validar que la fecha de vencimiento sea mayor que la fecha de inicio
            if expiration_date_obj <= start_date_obj:
                return JsonResponse({'success': False, 'message': 'La fecha de vencimiento debe ser mayor que la fecha de inicio.'})
            
            name_driver_id = int(name_driver_id)  
            driver = Vehicle_Driver.objects.get(id=name_driver_id)  
        except (ValueError, Vehicle_Driver.DoesNotExist):
            return JsonResponse({'success': False, 'message': 'El conductor seleccionado no existe.'})

        try:
            with transaction.atomic():
                licence = Licences_Driver.objects.create(
                    name_driver=driver, 
                    start_date=start_date,
                    expiration_date=expiration_date,
                )

                if license_driver:
                    s3Path = f'docs/{company_id}/vehicle/licencia/{name_driver_id}/'
                    file_name, extension = os.path.splitext(license_driver.name)
                    new_name = f"licencia_{name_driver_id}{extension}"
                    S3name = s3Path + new_name

                    upload_to_s3(license_driver, bucket_name, S3name)

                    licence.license_driver = S3name
                    licence.save()


            return JsonResponse({'success': True, 'message': 'Licencia agregada correctamente!'})
        
        except ValidationError as e:
            return JsonResponse({'success': False, 'message': str(e)})
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Error inesperado: ' + str(e)})

    return JsonResponse({'success': False, 'message': 'Método de solicitud no válido'})


#funcion de la tabla licencias
def get_table_licence(request):
    driver_id = request.GET.get('id')
    if driver_id:
        try:
            # Obtener el conductor
            driver = Vehicle_Driver.objects.get(id=driver_id)

            # Obtener las licencias asociadas al conductor
            licences = Licences_Driver.objects.filter(name_driver=driver).order_by("-id")  

            # Serializar las licencias
            licences_data = []
            first_licence = True
            for licence in licences:
                
                driver_name = f"{driver.name_driver.username} {driver.name_driver.last_name}" if driver.name_driver else "No asignado",
                start_date = licence.start_date
                expiration_date = licence.expiration_date
                licence_driver_url = licence.license_driver.url if licence.license_driver else None
                licence_driver = ""
                
                # If it's the first license, check expiration and set alert
                if first_licence:
                    if licence_driver_url is not None:
                        licence_driver = generate_presigned_url(bucket_name, licence_driver_url[1:])
                    
                    # Initialize the alert flag
                    alert_flag = False

                    # If there's no expiration date or no licence file, activate the alert
                    if not expiration_date or not licence_driver:
                        alert_flag = True
                    else:
                        # If less than a month to expiration, set alert to True
                        if expiration_date - datetime.now().date() <= timedelta(days=30):
                            alert_flag = True

                    first_licence = False
                    status_licence = True  # First license should be active
                else:
                    # For subsequent licenses, just mark them as inactive (status_licence = False)
                    status_licence = False
                    alert_flag = False  # No need to check expiration for other licenses

                licences_data.append({
                    "id": licence.id,
                    "driver_name": driver_name,
                    "expiration_date": licence.expiration_date.strftime("%Y-%m-%d") if licence.expiration_date else "",  
                    "start_date": licence.start_date.strftime("%Y-%m-%d") if licence.start_date else "",  
                    "license_driver": licence_driver,
                    "alert": alert_flag,  # Añadimos la bandera de alerta
                    "status_licence": status_licence,  # First license is active, others are inactive
                    "btn_action": f"""
                        <button class="btn btn-sm btn-primary btn-edit" onclick="btn_edit_licence(this)">
                            <i class="fa-solid fa-pen-to-square"></i>
                        </button>                     
                        <button class="btn btn-sm btn-danger" onclick="delete_licence(this)">
                            <i class="fa-solid fa-trash"></i>
                        </button>
                    """,
                })
                

            return JsonResponse({
                "success": True,
                "data": licences_data
            })
        except Vehicle_Driver.DoesNotExist:
            return JsonResponse({"success": False, "message": "Conductor no encontrado."}, status=404)
    return JsonResponse({"success": False, "message": "ID no proporcionado."}, status=400)


# Función para editar la información de la licencia
@login_required
@csrf_exempt
def edit_licence(request):
    context = user_data(request)
    subModule_id = 36
    response = {"success": False}
    access = get_module_user_permissions(context, subModule_id)  
    company_id = context["company"]["id"]

    if request.method == 'POST':
        _id = request.POST.get('id')
        start_date = request.POST.get('start_date')
        expiration_date = request.POST.get('expiration_date')
        license_driver = request.FILES.get('license_driver')

        if not start_date or not expiration_date:
            return JsonResponse({'success': False, 'message': 'Todos los campos son obligatorios.'})
        
        try:
            licence = Licences_Driver.objects.get(id=_id)
            name_driver_id = licence.name_driver.id

            # Actualizar los datos de la licencia
            licence.start_date = start_date
            licence.expiration_date = expiration_date

            # Actualizar el documento si es necesario
            if license_driver:
                s3Path = f'docs/{company_id}/vehicle/licencia/{name_driver_id}/'
                file_name, extension = os.path.splitext(license_driver.name)
                new_name = f"licencia_{name_driver_id}{extension}"
                S3name = s3Path + new_name

                upload_to_s3(license_driver, bucket_name, S3name)
                licence.license_driver = S3name


            # Guardar siempre los cambios
            licence.save()

            return JsonResponse({'success': True, 'message': 'Licencia actualizada correctamente!'})

        except Licences_Driver.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Licencia no encontrada'}, status=404)

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error interno del servidor: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'message': 'Método de solicitud inválido'})

#funcion para eliminar licencias
@login_required
@csrf_exempt
def delete_licence(request):                          
    if request.method == 'POST':
        form = request.POST
        _id = form.get('id')

        if not _id:
            return JsonResponse({'success': False, 'message': 'No ID licence'})

        try:
            licence = Licences_Driver.objects.get(id=_id)
        except Licences_Driver.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Licence not found'})

        licence.delete()

        return JsonResponse({'success': True, 'message': 'Licencia eliminada correctamente!'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})


# Funcion para obtener los nombres de los vehiculos que ya han sido cargados para agregar un equipo 
@login_required
@csrf_exempt
def get_vehicles(request):
    try:
        context = user_data(request)
        company_id = context["company"]["id"]
        if not company_id:
            return JsonResponse({'success': False, 'message': 'No se encontró la empresa asociada al usuario'}, status=400)

        vehicles = Vehicle.objects.filter(company_id=company_id).values('id', 'name')  # Asegúrate de que 'name' es el campo correcto en el modelo
        data = list(vehicles)

        return JsonResponse({'data': data}, safe=False)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

#función para agregar licencia
def add_multa(request):
    context = user_data(request)
    dt = request.POST
    company_id = context["company"]["id"]

    if request.method == 'POST':
        
        name_driver_multa = request.POST.get('name_driver_multa', '').strip() 
        name_driver_multa_id = request.POST.get('name_driver_multa_id')
        vehicle = request.POST.get('vehicle')
        cost = request.POST.get('cost')
        notes = request.POST.get('notes')
        reason = request.POST.get('reason')
        date = request.POST.get('date')

        if not name_driver_multa or not vehicle or not cost or not notes or not reason or not date:
            return JsonResponse({'success': False, 'message': 'Todos los campos son obligatorios.'})
        
        try:
            
            name_driver_multa_id = int(name_driver_multa_id)  
            driver = Vehicle_Driver.objects.get(id=name_driver_multa_id)
            vehicle = Vehicle.objects.get(id=vehicle)

        except (ValueError, driver.DoesNotExist):
            return JsonResponse({'success': False, 'message': 'El conductor seleccionado no existe.'})

        try:
            with transaction.atomic():
                multa = Multas.objects.create(
                    name_driver=driver,
                    vehicle = vehicle,
                    cost = cost,
                    notes = notes,
                    reason = reason,
                    date = date,  
                )

                multa.save()

            return JsonResponse({'success': True, 'message': 'Multa agregada correctamente!'})
        
        except ValidationError as e:
            return JsonResponse({'success': False, 'message': str(e)})
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Error inesperado: ' + str(e)})

    return JsonResponse({'success': False, 'message': 'Método de solicitud no válido'})


#funcion de la tabla licencias
def get_table_multas(request):
    driver_id = request.GET.get('id')
    if driver_id:
        try:
            # Obtener el conductor
            driver = Vehicle_Driver.objects.get(id=driver_id)

            # Obtener las multas asociadas al conductor
            multas = Multas.objects.filter(name_driver=driver)  

            # Serializar las licencias
            multas_data = []
            for multa in multas:

                # Serializar el nombre del conductor
                driver_name = f"{driver.name_driver.username} {driver.name_driver.last_name}" if driver.name_driver else "No asignado"

                # Serializar el vehículo (en lugar de pasar el objeto completo)
                vehicle_info = {
                    "id": multa.vehicle.id,
                    "modelo": multa.vehicle.name,  # Adjust according to your model fields
                }

                # Crear el objeto de multa con la información serializada
                multas_data.append({
                    "id": multa.id,
                    "driver_name": driver_name,
                    "vehicle": vehicle_info,  
                    "cost": multa.cost,
                    "notes": multa.notes,
                    "reason": multa.reason,
                    "date": multa.date,
                    "btn_action": f"""
                        <button class="btn btn-sm btn-primary btn-edit" onclick="btn_edit_multa(this)">
                            <i class="fa-solid fa-pen-to-square"></i>
                        </button>                     
                        <button class="btn btn-sm btn-danger" onclick="delete_multa(this)">
                            <i class="fa-solid fa-trash"></i>
                        </button>
                    """
                })

            return JsonResponse({
                "success": True,
                "data": multas_data
            })
        except Vehicle_Driver.DoesNotExist:
            return JsonResponse({"success": False, "message": "Conductor no encontrado."}, status=404)
    return JsonResponse({"success": False, "message": "ID no proporcionado."}, status=400)



# Función para editar la información de multa
@login_required
@csrf_exempt
def edit_multa(request):
    context = user_data(request)
    subModule_id = 36
    response = {"success": False}
    access = get_module_user_permissions(context, subModule_id)  
    company_id = context["company"]["id"]

    if request.method == 'POST':
        _id = request.POST.get('id')
        name_driver = request.POST.get('name_driver_multa')
        vehicle = request.POST.get('vehicle')
        cost = request.POST.get('cost')
        notes = request.POST.get('notes')
        reason = request.POST.get('reason')
        date = request.POST.get('date')

        if not name_driver or not vehicle or not cost or not notes or not reason or not date:
            return JsonResponse({'success': False, 'message': 'Todos los campos son obligatorios.'})
        
        try:    
            multa = Multas.objects.get(id=_id)

            name_driver_id = multa.name_driver.id
            modelo_vehicle_id = multa.vehicle.id    

            multa.cost = cost
            multa.notes = notes
            multa.reason = reason
            multa.date = date

            # Guardar siempre los cambios
            multa.save()

            return JsonResponse({'success': True, 'message': 'Multa actualizada correctamente!'})

        except Multas.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Multa no encontrada'}, status=404)

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error interno del servidor: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'message': 'Método de solicitud inválido'})


#funcion para eliminar licencias
@login_required
@csrf_exempt
def delete_multa(request):                          
    if request.method == 'POST':
        form = request.POST
        _id = form.get('id')

        if not _id:
            return JsonResponse({'success': False, 'message': 'No ID Multa'})

        try:
            multa = Multas.objects.get(id=_id)
        except Multas.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Multa not found'})

        multa.delete()

        return JsonResponse({'success': True, 'message': 'Multa eliminada correctamente!'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

#funcion para agregar check
@login_required
@csrf_exempt
def add_check(request):
    context = user_data(request)
    company_id = context["company"]["id"]

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()

        if not name:
            return JsonResponse({'success': False, 'message': 'Todos los campos son obligatorios.'})

        try:
            with transaction.atomic():
                company = Company.objects.get(id=company_id)

                # Verificar si ya existe un check con el mismo nombre en la misma empresa
                if Checks.objects.filter(company=company, name__iexact=name).exists():
                    return JsonResponse({'success': False, 'message': 'El nombre del check ya existe para esta empresa.'})

                check = Checks.objects.create(
                    company=company,  
                    name=name
                )

            return JsonResponse({'success': True, 'message': 'Check agregado correctamente!'})
        except Company.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Empresa no encontrada.'})
        except ValidationError as e:
            return JsonResponse({'success': False, 'message': str(e)})
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Error inesperado: ' + str(e)})

    return JsonResponse({'success': False, 'message': 'Método de solicitud no válido'})


#obtener los check por empresa
def obtener_checks_empresa(request):
    context = user_data(request)
    # dt = request.POST
    company_id = context["company"]["id"]
    checks = Checks.objects.filter(company_id=company_id).values("id", "name")
    return JsonResponse(list(checks), safe=False)


#obtener los checks de una auditoria de vehiculo
def get_checks_by_audit(request, audit_id):
    response = {"success": False, "data": []}

    try:
        # Obtener la auditoría por ID
        audit = Vehicle_Audit.objects.get(id=audit_id)
        checks = json.loads(audit.checks)  
        
        checks_with_names = []
        for check in checks:
            check_id = check.get("id")
            check_status = check.get("status")
            check_notes = check.get("notes")

            check_name = Checks.objects.filter(id=check_id).values_list("name", flat=True).first()

            checks_with_names.append({
                "id": check_id,
                "name": check_name if check_name else "Sin nombre",
                "status": check_status,
                "notes": check_notes
            })
        
        response["success"] = True
        response["data"] = checks_with_names
    except Vehicle_Audit.DoesNotExist:
        response["error"] = "No se encontró la auditoría"
    except Exception as e:
        response["error"] = str(e)

    return JsonResponse(response)


@csrf_exempt
def add_vehicle_audit(request):
    if request.method == "POST":
        # Extracting data from the request
        vehicle_id = request.POST.get("vehicle_id")
        audit_date = request.POST.get("audit_date")
        general_notes = request.POST.get("general_notes")
        checks = request.POST.getlist("checks[]")  # This will give a list of check ids

        # Validate required data
        if not vehicle_id or not audit_date:
            return JsonResponse({"success": False, "error": "Datos incompletos"})

        # Creating the vehicle audit object
        audit = Vehicle_Audit.objects.create(
            vehicle_id=vehicle_id,
            audit_date=audit_date,
            general_notes=general_notes,
        )

        check_objects = []
        for check_id in checks:
            try:
                check = Checks.objects.get(id=check_id)  # Get the check by ID
                # Creating the check structure with default values for 'status' and 'notas'
                check_data = {
                    "id": check.id,
                    "status": "muy malo",  # Default status
                    "notas": ""  # Default empty notes
                }
                check_objects.append(check_data)
            except Checks.DoesNotExist:
                print(f"Error: Check with ID {check_id} does not exist.")

        # You can now process the check data (such as storing it in the audit's 'checks' field)
        # Assuming that your model's 'checks' is a ManyToMany field
        audit.checks = check_objects  # Store the data in the 'checks_data' field or whatever field is necessary
        audit.is_visible = True
        audit.save()

        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "Método no permitido"})

# Vista para evaluar la auditoría
def evaluate_audit(request):
    if request.method == 'POST':
        try:
            # Obtener los datos enviados desde el frontend
            audit_data = json.loads(request.POST.get('audit_data', '[]'))

            # Obtener el ID de la empresa desde el contexto del usuario
            context = user_data(request)
            company_id = context["company"]["id"]

            # Lista para almacenar los resultados de la auditoría
            audit_results = []

            for check in audit_data:
                check_name = check["id"]  # Aquí viene el nombre del check
                status = check["status"]
                notas = check["notas"]

                # Buscar el check en la base de datos por nombre y empresa
                check_instance = Checks.objects.filter(name=check_name, company_id=company_id).first()
                
                if check_instance:
                    # Actualizar el estado y las notas del check
                    check_instance.status = status
                    check_instance.notas = notas
                    check_instance.save()

                    # Formar la estructura corregida con el ID del check
                    audit_results.append({
                        "id": str(check_instance.id),  # Convertir a string si es necesario
                        "status": status,
                        "notas": notas
                    })
            
            # Buscar la auditoría de vehículo utilizando el ID de la auditoría
            audit_id = request.POST.get('audit_id')
            vehicle_audit = Vehicle_Audit.objects.filter(id=audit_id).first()
            
            if vehicle_audit:
                # Actualizar el campo 'checks' con los resultados de la auditoría
                vehicle_audit.checks = json.dumps(audit_results)
                vehicle_audit.is_checked = True  # Marcar como verificado
                vehicle_audit.save()

                # Responder con éxito y devolver la estructura corregida
                return JsonResponse({'success': True, 'audit_results': audit_results})
            else:
                return JsonResponse({'success': False, 'error': 'Vehicle audit not found'})
        
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})
def add_vehicle_responsiva(request):
    response = {"success": False}
    dt = request.POST
    vehicle_id = dt.get("vehicle_id")
    response["type"] = ""

    # CONDITIONAL KILOMETER REGISTER GREATER THAN THE KILOMETER VEHICLE
    try:
        obj_vehicle = Vehicle.objects.get(id=vehicle_id)
        company_id = obj_vehicle.company.id
        #verificar que no este en mantenimiento el vehiculo
        mantenimiento = Vehicle_Maintenance.objects.filter(vehicle_id=vehicle_id, status="Proceso").first()
        if mantenimiento:
            response["status"] = "warning"
            response["type"] = "mantenimiento"
            response["message"] = "El vehículo se encuentra en mantenimiento, no se puede generar una responsiva."
            return JsonResponse(response)
        # Verificamos que el kilmetraje sea coherente
        mileage = Decimal(dt.get("initial_mileage")) if dt.get("initial_mileage") else None
        if mileage is not None and obj_vehicle.mileage is not None and obj_vehicle.mileage > mileage:
            response["status"] = "warning"
            response["type"] = "kilometraje"
            response["message"] = "El kilometraje ddebe ser mayor. Kilometrakje del vehículo: " + str(obj_vehicle.mileage) + " Kilometraje proporcionado: " + str(mileage)
            return JsonResponse(response)
    except Vehicle.DoesNotExist:
        response["status"] = "warning"
        response["message"] = f"No se encontró ningún vehículo con el ID {vehicle_id}"
        return JsonResponse(response)

    try:
        with transaction.atomic():
            flag = check_vehicle_kilometer(request, obj_vehicle, dt.get("initial_mileage"), dt.get("start_date"))
            if isinstance(flag, JsonResponse):
                data_flag = json.loads(flag.content.decode('utf-8')).get
                if data_flag("status") == "error":
                    return flag
                elif data_flag("status") == "warning":
                    response["warning"] = True
                    response["type"] = "kilometraje"
                    response["status"] = data_flag("status")
                    response["message"] = data_flag("message")

            obj = Vehicle_Responsive(
                vehicle_id=dt.get("vehicle_id"),
                responsible_id=dt.get("responsible_id"),
                initial_mileage=dt.get("initial_mileage"),
                initial_fuel=dt.get("initial_fuel"),
                destination=dt.get("destination"),
                trip_purpose=dt.get("trip_purpose"),
                start_date=dt.get("start_date")
            )
            obj.save()
            obj_vehicle.mileage = dt.get("initial_mileage")
            obj_vehicle.save()

            if 'signature' in request.FILES and request.FILES['signature']:
                load_file = request.FILES.get('signature')
                folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/responsiva/{obj.id}/"
                file_name, extension = os.path.splitext(load_file.name)

                new_name = f"signature{extension}"
                # Crear el hilo para cargar la imagen
                thread = threading.Thread(target=upload_images_in_background, args=(load_file, folder_path, new_name, AWS_BUCKET_NAME))
                thread.start()
                
                obj.signature = folder_path + new_name

            if 'image_path_exit_1' in request.FILES and request.FILES['image_path_exit_1']:
                load_file = request.FILES.get('image_path_exit_1')
                folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/responsiva/{obj.id}/"
                file_name, extension = os.path.splitext(load_file.name)

                new_name = f"salida_1{extension}"
                # Crear el hilo para cargar la imagen
                thread = threading.Thread(target=upload_images_in_background, args=(load_file, folder_path, new_name, AWS_BUCKET_NAME))
                thread.start()
                
                obj.image_path_exit_1 = folder_path + new_name

            if 'image_path_exit_2' in request.FILES and request.FILES['image_path_exit_2']:
                load_file = request.FILES.get('image_path_exit_2')
                folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/responsiva/{obj.id}/"
                file_name, extension = os.path.splitext(load_file.name)

                new_name = f"salida_2{extension}"
                # Crear el hilo para cargar la imagen
                thread = threading.Thread(target=upload_images_in_background, args=(load_file, folder_path, new_name, AWS_BUCKET_NAME))
                thread.start()
                
                obj.image_path_exit_2 = folder_path + new_name
            obj.save()

            if "warning" in response:
                return JsonResponse(response)

            response["id"] = obj.id
            response["success"] = True
    except Exception as e:
        response["success"] = False
        response["error"] = {"message": str(e)}

    return JsonResponse(response)

def update_vehicle_responsiva(request):
    response = {"success": False}
    dt = request.POST
    vehicle_id = dt.get("vehicle_id")

    # Verificamos que el vehículo exista
    try:
        obj_vehicle = Vehicle.objects.get(id=vehicle_id)
        company_id = obj_vehicle.company.id
        mantenimiento = Vehicle_Maintenance.objects.filter(vehicle_id=vehicle_id, status="Proceso").first()
        if mantenimiento:
            response["status"] = "warning"
            response["message"] = "El vehículo se encuentra en mantenimiento, no se puede generar una responsiva."
            return JsonResponse(response)
                # Verificamos que el kilmetraje sea coherente
        mileage = Decimal(dt.get("final_mileage")) if dt.get("final_mileage") else None
        print(mileage)
        print(obj_vehicle.mileage)
        print("estos son los kilometrajes")
        if mileage is not None and obj_vehicle.mileage is not None and obj_vehicle.mileage > mileage:
            response["status"] = "warning"
            response["type"] = "kilometraje"
            response["message"] = "El kilometraje ddebe ser mayor. Kilometrakje del vehículo: " + str(obj_vehicle.mileage) + " Kilometraje proporcionado: " + str(mileage)
            return JsonResponse(response)
    except Vehicle.DoesNotExist:
        response["status"] = "warning"
        response["message"] = f"No se encontró ningún vehículo con el ID {vehicle_id}"
        return JsonResponse(response)

    # Iniciar transacción
    try:
        with transaction.atomic():
            obj = Vehicle_Responsive.objects.get(id=dt.get("id"))
            obj.final_mileage = dt.get("final_mileage")
            obj.final_fuel = dt.get("final_fuel")
            obj.end_date = dt.get("end_date")

            # Verificar si se recibió una firma para actualizar
            if 'signature' in request.FILES and request.FILES['signature']:
                load_file = request.FILES.get('signature')
                folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/responsiva/{obj.id}/"
                file_name, extension = os.path.splitext(load_file.name)

                new_name = f"signature{extension}"
                # Crear el hilo para cargar la imagen
                thread = threading.Thread(target=upload_images_in_background, args=(load_file, folder_path, new_name, AWS_BUCKET_NAME))
                thread.start()

                obj.signature = folder_path + new_name

            # Verificar si se recibió la primera imagen de salida
            if 'image_path_entry_1' in request.FILES and request.FILES['image_path_entry_1']:
                load_file = request.FILES.get('image_path_entry_1')
                folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/responsiva/{obj.id}/"
                file_name, extension = os.path.splitext(load_file.name)

                new_name = f"entrada_1{extension}"
                # Crear el hilo para cargar la imagen
                thread = threading.Thread(target=upload_images_in_background, args=(load_file, folder_path, new_name, AWS_BUCKET_NAME))
                thread.start()

                obj.image_path_entry_1 = folder_path + new_name

            # Verificar si se recibió la segunda imagen de salida
            if 'image_path_entry_2' in request.FILES and request.FILES['image_path_entry_2']:
                load_file = request.FILES.get('image_path_entry_2')
                folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/responsiva/{obj.id}/"
                file_name, extension = os.path.splitext(load_file.name)

                new_name = f"entrada_2{extension}"
                # Crear el hilo para cargar la imagen
                thread = threading.Thread(target=upload_images_in_background, args=(load_file, folder_path, new_name, AWS_BUCKET_NAME))
                thread.start()

                obj.image_path_entry_2 = folder_path + new_name
            obj.save()

            response["id"] = obj.id
            response["success"] = True

    except Exception as e:
        response["success"] = False
        response["error"] = {"message": str(e)}

    return JsonResponse(response)


def upload_images_in_background(file, folder_path, new_name, bucket_name):
    """
    Función para cargar imágenes de forma asincrónica en un bucket de AWS S3.
    
    :param file: El archivo que se quiere cargar.
    :param folder_path: El directorio en el que se debe almacenar la imagen en S3.
    :param new_name: El nuevo nombre del archivo una vez cargado.
    :param bucket_name: El nombre del bucket de AWS S3 donde se va a almacenar la imagen.
    """
    s3_client = boto3.client('s3')

    # Ruta completa del archivo que se va a subir
    file_path = folder_path + new_name

    try:
        # Re-open file or duplicate the in-memory file object
        file_copy = io.BytesIO(file.read())  # Duplicate file in memory

        # Redimensionar la imagen antes de subirla
        # Subir archivo redimensionado a S3
        s3_client.upload_fileobj(file_copy, bucket_name, file_path)
    except FileNotFoundError:
        print(f"El archivo {new_name} no fue encontrado.")
    except NoCredentialsError:
        print("Las credenciales de AWS no están configuradas correctamente.")
    except Exception as e:
        print(f"Error al subir el archivo {new_name}: {e}")
    finally:
        # Close the copied file to free memory
        file_copy.close()


@csrf_exempt
def verificar_mantenimiento(request):
    response = {"success": False}
    
    if request.method == "POST":
        try:
            selected_options={}
            # Procesar el cuerpo de la solicitud como JSON
            data = json.loads(request.body)
            # Obtener los valores del JSON
            selected_options = list(data.get("selectedOption"))  # Ahora es una lista
            vehicle_id = data.get("vehicle")
            tipo = data.get("tipo")
            id_edit = data.get("id_edit")

            # Verificar que 'selectedOption' sea una lista
            if not isinstance(selected_options, list):
                response["status"] = "warning"
                response["message"] = "El campo 'selectedOption' debe ser una lista."
                return JsonResponse(response)

            # Verificar que el vehículo exista
            try:
                obj_vehicle = Vehicle.objects.get(id=vehicle_id)
                company_id = obj_vehicle.company.id
            except Vehicle.DoesNotExist:
                response["status"] = "warning"
                response["message"] = f"No se encontró ningún vehículo con el ID {vehicle_id}"
                return JsonResponse(response)

            # Obtener el último mantenimiento del vehículo
            try:
                last_maintenance = Vehicle_Maintenance.objects.filter(vehicle=obj_vehicle, type = tipo)
                count = last_maintenance.count()
                last_maintenance_obj = last_maintenance.order_by('-date').first()
                old_maintenance_obj = last_maintenance.first()
                if id_edit:
                    if int(last_maintenance_obj.id) == int(id_edit) and count <= 1:
                        response["status"] = "warning"
                        response["message"] = "No hay registros anteriores."    
                        return JsonResponse(response)
                    elif int(old_maintenance_obj.id) == int(id_edit):   
                        response["status"] = "warning"
                        response["message"] = ""    
                        return JsonResponse(response)
                        # Caso cuando el ID editado coincide con el último, se debe obtener el registro anterior
                    elif int(last_maintenance_obj.id) == int(id_edit):
                        
                        # Verificar si hay un registro anterior
                        if count > 1:
                            # Tomar el siguiente registro (anterior al último)
                            last_maintenance_obj = last_maintenance.order_by("-date")[1]  # El segundo objeto en la consulta
                        else:
                            response["status"] = "warning"
                            response["message"] = "No hay registros anteriores."
                            return JsonResponse(response)
                    else:
                        _id = int(id_edit)-1
                        last_maintenance_obj = last_maintenance.filter(id = _id).first() # .first() para obtener el primer resultado, si existe

                # Verificar si se encontró algún mantenimiento
                if last_maintenance_obj and last_maintenance_obj.actions and count >= 1:
                #     actions = json.loads(last_maintenance_obj.actions)  # Convertir el campo JSON en un diccionario
                #     # Verificar si alguna de las opciones está en las acciones del último mantenimiento
                # Si ninguna opción coincide
                    response["message"] = ""
                    response["status"] = "success"
                    for selected_option in selected_options:
                        if selected_option in last_maintenance_obj.actions:
                            response["status"] = "info"
                            response["message"] += f"{selected_option}*"
                    
                    if response["status"] == "success":
                        response["message"] = "Las opciones no están registradas en el último mantenimiento."

                    return JsonResponse(response)
                    
                else:
                    response["status"] = "info"
                    response["message"] = ""
            except Vehicle_Maintenance.DoesNotExist:
                response["status"] = "warning"
                response["message"] = ""
        
        except json.JSONDecodeError:
            response["status"] = "error"
            response["message"] = "Error al procesar los datos JSON. Asegúrate de que el formato sea correcto."
        except Exception as e:
            response["status"] = "error"
            response["message"] = f"Error interno: {str(e)}"
    
    return JsonResponse(response)

@csrf_exempt  # Eximir la protección CSRF para este endpoint, si estás usando POST
def update_status_man(request):
    if request.method == 'POST':
        # Obtener los datos enviados
        maintenance_id = request.POST.get('id')
        new_status = request.POST.get('status')

        try:
            # Obtener el mantenimiento
            maintenance = Vehicle_Maintenance.objects.get(id=maintenance_id)
            
            # Verificar si la fecha ya pasó y si el estado no es "Proceso" o "Finalizado"
            current_date = timezone.now().date()
            maintenance_date = maintenance.date
            if maintenance_date < current_date and maintenance.status not in ["Proceso", "Finalizado"]:
                new_status = "Retrasado"  # Si la fecha ya pasó, marcar como "Retrasado"
            
            # Actualizar el estado
            maintenance.status = new_status
            maintenance.save()

            # Responder con éxito
            return JsonResponse({'status': 'success', 'message': 'Estado actualizado correctamente.'})

        except Vehicle_Maintenance.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Mantenimiento no encontrado.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido.'})
# TODO --------------- [ END ] ----------
# ! Este es el fin
