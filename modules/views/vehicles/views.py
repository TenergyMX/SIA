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
# import qrcode
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import F, Value
from django.db.models.functions import Concat
from django.db.models import Q

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.timezone import localtime
from django.core.exceptions import MultipleObjectsReturned

from django.db.models import OuterRef, Subquery
from decimal import Decimal, InvalidOperation


dotenv_path = join(dirname(dirname(dirname(__file__))), 'awsCred.env')
load_dotenv(dotenv_path)
import qrcode 
import threading
from PIL import Image
import re
from django.db.models import DateField
from django.db.models import Q, F, Value, OuterRef, Subquery, CharField, DateField, IntegerField


# TODO --------------- [ VARIABLES ] ---------- 

AUDITORIA_VEHICULAR_POR_MES = 2
AWS_BUCKET_NAME=str(os.environ.get('AWS_BUCKET_NAME'))
bucket_name=AWS_BUCKET_NAME

ALLOWED_FILE_EXTENSIONS = ['.jpg', '.jpeg', '.png']


def getVehiclesList(request):
    context = {}
    fd = request.POST.get
    print(fd)
    context["success"] = True
    vehicle = Vehicle.objects.filter(id = fd("id"))
    if vehicle:
        temp = vehicle.first()
        context["option"] = f'<option value="{temp.id}">{temp.name}</option>'
    return JsonResponse(context, safe=False)

# TODO --------------- [ VIEWS ] --------------- 
@login_required
def vehicles(request):
    context = user_data(request)
    module_id = 2
    subModule_id = 4
    request.session["last_module_id"] = module_id

    sidebar = get_sidebar(context, [1, module_id])
    access = get_module_user_permissions(context, subModule_id)
    # Limpiar espacios en los títulos de los submódulos
    for module in sidebar["data"]:
        for submodule in module.get("submodules", []):
            submodule["title"] = submodule["title"].strip()  # Limpiar espacios al inicio y final
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]
    # print("estos son los modulos permitidos", context["sidebar"])
    template = "vehicles/vechicles.html" if context["access"]["read"] and check_user_access_to_module(request, module_id, subModule_id) else "error/access_denied.html"
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

    access = get_module_user_permissions(context, subModule_id)
    permisos = get_user_access(context)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["permiso"] = permisos["data"]
    context["sidebar"] = sidebar["data"]

    template = "vehicles/vechicle_details.html" if context["access"]["read"] and check_user_access_to_module(request, module_id, subModule_id) else "error/access_denied.html"
    return render(request, template, context)

# @login_required
# def module_vehicle_tenencia(request):
#     context = user_data(request)
#     module_id = 2
#     subModule_id = 5
    
#     access = get_module_user_permissions(context, subModule_id)
#     sidebar = get_sidebar(context, [1, module_id])
    
#     context["access"] = access["data"]["access"]
#     context["sidebar"] = sidebar["data"]
    
#     template = "vehicles/vehicles_tenencia.html" if context["access"]["read"] and check_user_access_to_module(request, module_id, subModule_id) else "error/access_denied.html"
    
#     return render(request, template, context)

@login_required
def module_vehicle_refrendo(request):
    context = user_data(request)
    module_id = 2
    subModule_id = 6

    access = get_module_user_permissions(context, subModule_id)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]
    
    template = "vehicles/vehicles_refrendo.html" if context["access"]["read"] and check_user_access_to_module(request, module_id, subModule_id) else "error/access_denied.html"
    
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
    
    template = "vehicles/vehicles_verificacion.html" if context["access"]["read"] and check_user_access_to_module(request, module_id, subModule_id) else "error/access_denied.html"
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

    template = "vehicles/responsiva.html" if context["access"]["read"] and check_user_access_to_module(request, module_id, submodule_id) else "error/access_denied.html"
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

    template = "vehicles/vehicle_insurance.html" if context["access"]["read"] and check_user_access_to_module(request, module_id, submodule_id) else "error/access_denied.html"
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

    template = "vehicles/audit.html" if context["access"]["read"] and check_user_access_to_module(request, module_id, submodule_id) else "error/access_denied.html"
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

    template = "vehicles/maintenance.html" if context["access"]["read"] and check_user_access_to_module(request, module_id, submodule_id) else "error/access_denied.html"
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

    template = "vehicles/calendar.html" if context["access"]["read"] and check_user_access_to_module(request, module_id, submodule_id) else "error/access_denied.html"
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

    template = "vehicles/fuel.html"  if context["access"]["read"] and check_user_access_to_module(request, module_id, submodule_id) else "error/access_denied.html"
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

    template = "vehicles/vehicles_driver.html" if context["access"]["read"] and check_user_access_to_module(request, module_id, submodule_id) else "error/access_denied.html"
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

    template = "vehicles/driver_details.html" if context["access"]["read"] and check_user_access_to_module(request, module_id, subModule_id) else "error/access_denied.html" 
    return render(request, template, context)


# TODO --------------- [ HELPER ] ----------


# TODO --------------- [ REQUEST ] ----------


def get_vehicle_maintenance_kilometer(request):
    dt = request.GET.get
    response = {"success":True}
    obj = Vehicle_Maintenance_Kilometer.objects.filter(vehiculo_id=dt("id")).order_by("-kilometer").values("id", "kilometer")
    for item in obj:
        id = str(item["id"])
        item["kilometer"] = str(item["kilometer"])+" km"
        item["acciones"] = f"<div class='row justify-content-center'>"
        item["acciones"] += f"<button type='submit' name='update' data-vehiculo-id='{id}' class='btn btn-primary w-auto mx-2 btn-sm'><i class='fa-solid fa-pencil'></i></button>"
        item["acciones"] += f"<button type='submit' name='delete' data-vehiculo-id='{id}' class='btn btn-danger w-auto mx-2 btn-sm'><i class='fa-solid fa-trash-can'></i></button></div>"
    response["data"] = list(obj)
    # print("esto contiene los mantenimientos", response["data"]) 
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
            owner_id = dt.get("owner_id"),
            fuel_type_vehicle = dt.get("fuel_type_vehicle"),
            # apply_tenencia = dt.get("apply_tenencia") == "on",  
            car_tires = dt.get("car_tires"),
   
        )
        obj.save()
        id = obj.id

        if 'cover-image' in request.FILES and request.FILES['cover-image']:
            load_file = request.FILES.get('cover-image')            
            s3Path = f'docs/{company_id}/vehicle/{id}/'
            file_name, extension = os.path.splitext(load_file.name)                
            new_name = f"cover-image{extension}"
            s3Name = s3Path + new_name
            
            upload_to_s3(load_file, bucket_name, s3Name)
    
            obj.image_path = s3Name
            obj.save()
            
            image_url = generate_presigned_url(bucket_name, s3Name)

        response.update({
            "success": True,
            "status": "success",
            "message": "Vehículo agregado exitosamente.",
            "id": obj.id,
            "image_url": image_url
        })
    
    except Exception as e:
        response["error"] = {"message": str(e)}
        return JsonResponse(response)
    

    # Crear auditoria
    try:
        vehiculos = Vehicle.objects.filter(company_id=1).order_by('id')
        num_vehiculos = vehiculos.count()
        num_auditorias = Vehicle_Audit.objects.filter(
            vehicle__company_id=1,
            vehicle__is_active=True
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
        "vehicle_type", "year", "image_path", "car_tires"
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
        # Obtener el vehículo
    try:
        vehiculo = Vehicle.objects.get(id=vehicle_id)
    except Vehicle.DoesNotExist:
        if detailed:
            return {"alert": False, "missing_tables": ["vehículo no encontrado"]}
        return False

    # apply_tenencia = vehiculo.apply_tenencia

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

            #  Evita verificar tenencia si no aplica
            # if table_name == "tenencia" and not apply_tenencia:
            #     continue


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
            "fuel_type_vehicle",
            "policy_number",
            "car_tires"
        )
        data = data.filter(company_id=context["company"]["id"])

        if context["role"]["id"] == 4:
            data = data.filter(
                Q(responsible_id=context["user"]["id"]) |
                Q(owner_id=context["user"]["id"])
            )
        # Filtro por tipo_carga (activos, inactivos, todos)
        tipo_carga = dt.get("tipo_carga", "todos")
        if tipo_carga == "activos":
            data = data.filter(is_active=True)
        elif tipo_carga == "inactivos":
            data = data.filter(is_active=False)
            
        is_active = dt.get("is_active", None)
        if is_active in ["true", "True", "1"]:
            data = data.filter(is_active=True)
        
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
                    <a href="/vehicles/info/{item['id']}/" class="btn btn-primary btn-sm mb-1" title="Ver información">
                        <i class="fa-solid fa-eye"></i>
                    </a>\n
                    """

                    
                    if item["is_active"]:
                        if access["update"]:
                            item["btn_action"] += """<button class=\"btn btn-primary btn-sm mb-1\" data-vehicle-info=\"update-item\" title="Editar información">
                                <i class="fa-solid fa-pen"></i>
                            </button>\n"""
                        
                        if access["delete"]:
                            item["btn_action"] += """<button class=\"btn btn-danger btn-sm mb-1\" data-vehicle-info=\"delete-item\" title="Eliminar vehículo">
                                <i class="fa-solid fa-trash"></i>
                            </button>\n"""
                        item["btn_action"] += """<button class=\"btn btn-danger btn-sm mb-1\" data-vehicle-info=\"deactivate-item\" title="Desactivar vehículo">
                            <i class="fa-solid fa-power-off"></i>
                        </button>"""

                except Exception as e:
                    print(f"Error processing vehicle with ID {item['id']}: {e}")
        
        # Filtro por estado
        is_active = dt.get("is_active", None)
        if is_active in ["true", "True", "1"]:
            data = data.filter(is_active=True)
        elif is_active in ["false", "False", "0"]:
            data = data.filter(is_active=False)

        # Calcular contadores globales (sin aplicar filtros)
        base_queryset = Vehicle.objects.filter(company_id=context["company"]["id"])
        if context["role"]["id"] == 4:
            base_queryset = base_queryset.filter(
                Q(responsible_id=context["user"]["id"]) |
                Q(owner_id=context["user"]["id"])
            )

        response["counters"] = {
            "total": base_queryset.count(),
            "activos": base_queryset.filter(is_active=True).count(),
            "inactivos": base_queryset.filter(is_active=False).count()
        }

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
        obj.fuel_type_vehicle = dt.get("fuel_type_vehicle", obj.fuel_type_vehicle)
        obj.car_tires = dt.get("car_tires", obj.car_tires)
        # obj.apply_tenencia = "apply_tenencia" in dt


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
        if obj.image_path:
            delete_s3_object(AWS_BUCKET_NAME, str(obj.image_path))
        obj.delete()
    response["success"] = True
    return JsonResponse(response)


# def add_vehicle_tenencia(request):
#     response = {"success": False, "data": []}
#     dt = request.POST

#     vehicle_id = dt.get("vehiculo_id")
    
#     try:
#         obj_vehicle = Vehicle.objects.get(id = vehicle_id)
#         company_id = obj_vehicle.company.id
#     except Vehicle.DoesNotExist:
#         response["error"] = {"message": f"No se encontró ningún vehículo con el ID {vehicle_id}"}
#         return JsonResponse(response)

#     try:
#         obj = Vehicle_Tenencia(
#             vehiculo_id = vehicle_id,
#             fecha_pago = dt.get("fecha_pago"),
#             monto = dt.get("monto")
#         )
#         obj.save()
#         id = obj.id

#         # Guardar el archivo en caso de existir
#         if 'comprobante_pago' in request.FILES and request.FILES['comprobante_pago']:
#             load_file = request.FILES.get('comprobante_pago')
#             folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/tenencia/"
#             #fs = FileSystemStorage(location=settings.MEDIA_ROOT)
#             file_name, extension = os.path.splitext(load_file.name)
            
#             new_name = f"comprobante_pago_{id}.{extension}"
#             #fs.save(folder_path + new_name, load_file)
            
#             obj.comprobante_pago = folder_path + new_name
#             s3Name = folder_path + new_name

#             upload_to_s3(load_file, bucket_name, s3Name)

#             obj.save()

#         response["success"] = True
#     except Exception as e:
#         response["error"] = {"message": str(e)}
#     return JsonResponse(response)

# def get_vehicle_tenencia(request):
#     context = user_data(request)
#     response = {"success": False, "data": []}
#     dt = request.GET
#     vehicle_id = dt.get("vehicle_id", None)
#     subModule_id = 5

#     lista = Vehicle_Tenencia.objects.filter(vehiculo_id = vehicle_id).values("id", "vehiculo_id", "vehiculo__name", "monto", "fecha_pago", "comprobante_pago")

#     access = get_module_user_permissions(context, subModule_id)
#     access = access["data"]["access"]
#     for item in lista:
#         item["btn_action"] = ""
#         if item["comprobante_pago"] :
#             tempDoc = generate_presigned_url(bucket_name, item["comprobante_pago"])
#             item["btn_action"] = f"""<a href="{tempDoc}" class="btn btn-sm btn-info" target="_blank">
#                 <i class="fa-solid fa-file"></i> Comprobante 
#             </a>\n"""
#         if access["update"]:
#             item["btn_action"] += """<button class=\"btn btn-primary btn-sm\" data-vehicle-tenencia=\"update-item\">
#                 <i class="fa-solid fa-pen"></i>
#             </button>\n"""
#         if access["delete"]:
#             item["btn_action"] += """<button class=\"btn btn-danger btn-sm\" data-vehicle-tenencia=\"delete-item\">
#                 <i class="fa-solid fa-trash"></i>
#             </button>"""
#     response["data"] = list(lista)

#     response["success"] = True
#     return JsonResponse(response)

# def get_vehicles_tenencia(request):
#     context = user_data(request)
#     response = {"success": False, "data": [], "counters": {}}
#     dt = request.GET
#     tipo_carga = dt.get("tipo_carga", "todos")
#     vehicle_id = dt.get("vehicle_id")
#     subModule_id = 5


#     hoy = timezone.now().date()
#     un_mes_despues = hoy + timedelta(days=30)

#     # --- Vehículos según permisos ---
#     vehiculos = Vehicle.objects.filter(company_id=context["company"]["id"])
#     if context["role"]["id"] not in [1, 2, 3]:
#         vehiculos = vehiculos.filter(responsible_id=context["user"]["id"])
#     if vehicle_id:
#         vehiculos = vehiculos.filter(id=vehicle_id)

#     total_vehiculos_count = vehiculos.count()

#    # --- Última tenencia por vehículo ---
#     all_tenencias = Vehicle_Tenencia.objects.filter(vehiculo__in=vehiculos)
#     latest_qs = Vehicle_Tenencia.objects.filter(
#         vehiculo_id=OuterRef('vehiculo_id')
#     ).order_by('-fecha_pago')
#     latest_only = all_tenencias.filter(id=Subquery(latest_qs.values('id')[:1]))

   
#     # Aplicar filtro tipo_carga
#     if tipo_carga == "pagadas":
#         lista_queryset = latest_only.filter(
#             Q(comprobante_pago__isnull=False) & ~Q(comprobante_pago="") & Q(fecha_pago__lte=hoy)
#         )
#     elif tipo_carga == "vencidas":
#         lista_queryset = latest_only.filter(
#             Q(fecha_pago__lt=hoy) & (Q(comprobante_pago__isnull=True) | Q(comprobante_pago=""))
#         )
#     elif tipo_carga == "proximas":
#         lista_queryset = latest_only.filter(
#             fecha_pago__gte=hoy, fecha_pago__lte=un_mes_despues
#         )
#     else:
#         lista_queryset = latest_only
#     # Traer datos
#     lista = lista_queryset.values(
#         "id", "vehiculo_id", "vehiculo__name", "vehiculo__company_id",
#         "monto", "fecha_pago", "comprobante_pago"
#     )
#     # Permisos del módulo
#     access = get_module_user_permissions(context, subModule_id)["data"]["access"]

#     # Contadores
#     contadores = {
#         "total": 0,
#         "pagadas": 0,
#         "proximas": 0,
#         "vencidas": 0,
#     }

#     result = []
#     for item in lista:
#         estado = None
#         fecha_pago = item["fecha_pago"]
#         comprobante = item["comprobante_pago"]

#         if comprobante and fecha_pago and fecha_pago <= hoy:
#             estado = "pagada"
#             contadores["pagadas"] += 1
#         elif not comprobante and fecha_pago and fecha_pago < hoy:
#             estado = "vencida"
#             contadores["vencidas"] += 1
#         elif fecha_pago and hoy <= fecha_pago <= un_mes_despues:
#             estado = "proxima"
#             contadores["proximas"] += 1
            
#         item["estado"] = estado
#         contadores["total"] += 1

    
#         item["btn_action"] = ""
#         if item["comprobante_pago"] :
#             tempDoc = generate_presigned_url(bucket_name, item["comprobante_pago"])
#             item["btn_action"] = f"""<a href="{tempDoc}" class="btn btn-sm btn-info" target="_blank">
#                 <i class="fa-solid fa-file"></i> Comprobante 
#             </a>\n"""
#         if access["update"]:
#             item["btn_action"] += """<button class=\"btn btn-primary btn-sm mb-1\" data-vehicle-tenencia=\"update-item\">
#                 <i class="fa-solid fa-pen"></i>
#             </button>\n"""
#         if access["delete"]:
#             item["btn_action"] += """<button class=\"btn btn-danger btn-sm mb-1\" data-vehicle-tenencia=\"delete-item\">
#                 <i class="fa-solid fa-trash"></i>
#             </button>"""
        
#         result.append(item)
#     response["counters"] = {
#         **contadores,
#         "total_vehiculos": total_vehiculos_count,
#     }

#     response["data"] = result
#     response["success"] = True
#     return JsonResponse(response)

# def update_vehicle_tenencia(request):
#     response = {"success": False, "data": []}
#     dt = request.POST
    
#     id = dt.get("id", None)
#     vehicle_id = dt.get("vehicle_id"),

#     if id is None:
#         response["error"] = {"message": "No se proporcionó un ID válido para actualizar."}
#         return JsonResponse(response)
    
#     try:
#         obj = Vehicle_Tenencia.objects.get(id=id)
#     except Vehicle_Tenencia.DoesNotExist:
#         response["error"] = {"message": f"No existe ningún resgitro con el ID '{id}'"}
#         return JsonResponse(response)

#     try:
#         obj.monto = dt.get("monto")
#         obj.fecha_pago = dt.get("fecha_pago")
#         obj.save()
#         vehicle_id = obj.vehiculo_id
        
#         # Guardar el archivo en caso de existir
#         if 'comprobante_pago' in request.FILES and request.FILES['comprobante_pago']:
#             load_file = request.FILES.get('comprobante_pago')
#             company_id = request.session.get('company').get('id')
#             folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/tenencia/{id}/"
#             #fs = FileSystemStorage(location=settings.MEDIA_ROOT)
#             file_name, extension = os.path.splitext(load_file.name)                
            
#             new_name = f"comprobante_pago{extension}"
#             #fs.save(folder_path + new_name, load_file)
#             s3Name = folder_path + new_name

#             obj.comprobante_pago = folder_path + new_name
#             upload_to_s3(load_file, bucket_name, s3Name)
#             obj.save()
        
#         response["success"] = True
#     except Exception as e:
#         response["error"] = {"message": str(e)}
#     return JsonResponse(response)

# def delete_vehicle_tenencia(request):
#     response = {"success": False, "data": []}
#     dt = request.POST
#     id = dt.get("id", None)

#     if id == None:
#         response["error"] = {"message": "Proporcione un id valido"}
#         return JsonResponse(response)

#     try:
#         obj = Vehicle_Tenencia.objects.get(id = id)
#     except Vehicle_Tenencia.DoesNotExist:
#         response["error"] = {"message": "El objeto no existe"}
#         return JsonResponse(response)
#     else:
#         if obj.comprobante_pago:
#             delete_s3_object(AWS_BUCKET_NAME, str(obj.comprobante_pago))
#         obj.delete()
#     response["success"] = True
#     return JsonResponse(response)

def add_vehicle_refrendo(request):
    response = {"success": False, "data": []}
    dt = request.POST

    vehicle_id = dt.get("vehiculo_id")
    # print(f"Vehicle ID recibido para refrendo: {vehicle_id}")

    try:
        obj_vehicle = Vehicle.objects.get(id = vehicle_id)
        company_id = obj_vehicle.company.id
    except Vehicle.DoesNotExist:
        response["error"] = {"message": f"No se encontró ningún vehículo con el ID {vehicle_id}"}
        return JsonResponse(response)

    try:
        # Validar que la fecha esté dentro de enero - marzo
        fecha_pago_str = dt.get("fecha_pago")
        fecha_pago = datetime.strptime(fecha_pago_str, "%Y-%m-%d").date()

        inicio_periodo = date(fecha_pago.year, 1, 1)
        fin_periodo = date(fecha_pago.year, 3, 31)

        if not (inicio_periodo <= fecha_pago <= fin_periodo):
            response["success"] = False
            response["status"] = "warning"
            response["error"] = {
                "message": f"El pago de refrendo solo puede registrarse entre enero y marzo. Fecha recibida: {fecha_pago}"
            }
            return JsonResponse(response)
        
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
    vehicle_id = dt.get("vehicle_id")

    print("vehicle_id recibido para mostrar solo sus refrendos:", vehicle_id)

    # Validar que vehicle_id sea un número válido
    if not vehicle_id or not vehicle_id.isdigit():
        response["error"] = {"message": "ID de vehículo inválido o no proporcionado."}
        return JsonResponse(response, status=400)

    vehicle_id = int(vehicle_id)

    lista = Vehicle_Refrendo.objects.filter(vehiculo_id = vehicle_id).values(
        "id",
        "vehiculo_id", "vehiculo__name",
        "monto", "fecha_pago", "comprobante_pago"
    )

    for item in lista:
        item["btn_action"] = ""
        if item["comprobante_pago"] :
            tempDoc = generate_presigned_url(bucket_name, item["comprobante_pago"])
            item["btn_action"] = f"""<a href="{tempDoc}" class="btn btn-sm btn-info" target="_blank">
                <i class="fa-solid fa-file"></i> Comprobante 
            </a>\n"""
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
    response = {"success": False, "data": [], "counters": {}}
    dt = request.GET
    vehicle_id = dt.get("vehicle_id", None)
    tipo_carga = dt.get("tipo_carga", "todos")
    subModule_id = 6

    # -------------------------------
    # Fechas de referencia
    # -------------------------------
    hoy = timezone.now().date()
    year = hoy.year
    month = hoy.month

    inicio_trimestre = date(year, 1, 1)
    fin_trimestre = date(year, 3, 31)
    inicio_trimestre_next = date(year + 1, 1, 1)
    fin_trimestre_next = date(year + 1, 3, 31)

    # Ventana de alerta para próximos (dic año anterior – mar año actual)
    inicio_alerta_proximo = date(year - 1, 12, 1)
    fin_alerta_proximo = fin_trimestre

    # -------------------------------
    # Vehículos según permisos
    # -------------------------------
    total_vehiculos = Vehicle.objects.filter(company_id=context["company"]["id"])
    if context["role"]["id"] not in [1, 2, 3]:
        total_vehiculos = total_vehiculos.filter(responsible_id=context["user"]["id"])
    if vehicle_id:
        total_vehiculos = total_vehiculos.filter(id=vehicle_id)
    total_vehiculos_count = total_vehiculos.count()

    # -------------------------------
    # Últimos refrendos por vehículo
    # -------------------------------
    all_refrendos = Vehicle_Refrendo.objects.filter(vehiculo__in=total_vehiculos)
    latest_refrendo = Vehicle_Refrendo.objects.filter(
        vehiculo_id=OuterRef('vehiculo_id')
    ).order_by('-fecha_pago')
    latest_only = all_refrendos.filter(id=Subquery(latest_refrendo.values('id')[:1]))

    CAMPOS = ["id", "vehiculo_id", "vehiculo__name", "monto", "fecha_pago", "comprobante_pago"]

    # -------------------------------
    # Filtrar según tipo_carga
    # -------------------------------
    if tipo_carga == "pagadas":
        lista_queryset = latest_only.filter(
            fecha_pago__range=(inicio_trimestre, fin_trimestre)
        )
        lista_queryset |= latest_only.filter(
            fecha_pago__gt=fin_trimestre 
        )
    elif tipo_carga == "vencidas":
        lista_queryset = latest_only.filter(
            Q(fecha_pago__lt=date(year, 1, 1)) | Q(fecha_pago__isnull=True)
        )
        if month > 3:
            lista_queryset = lista_queryset | latest_only.filter(fecha_pago__year=year - 1)
    elif tipo_carga == "proximas":
        refrendos_anio_anterior_ids = latest_only.filter(fecha_pago__year=year - 1).values_list("vehiculo_id", flat=True)
        refrendos_actual_ids = latest_only.filter(fecha_pago__range=(inicio_trimestre, fin_trimestre)).values_list("vehiculo_id", flat=True)
        if month in [12, 1, 2, 3]:
            lista_queryset = latest_only.filter(vehiculo_id__in=refrendos_anio_anterior_ids).exclude(vehiculo_id__in=refrendos_actual_ids)
        else:
            lista_queryset = latest_only.none()
    elif tipo_carga == "sin_refrendo":
        lista = (
            total_vehiculos.exclude(id__in=Vehicle_Refrendo.objects.values_list("vehiculo_id", flat=True))
            .annotate(
                vehiculo_id=F("id"),
                vehiculo__name=F("name"),
                monto=Value("", output_field=CharField()),
                fecha_pago=Value(None, output_field=DateField()),
                comprobante_pago=Value("", output_field=CharField()),
            )
            .values(*CAMPOS)
        )
    else:
        lista_queryset = latest_only

    if tipo_carga != "sin_refrendo":
        lista = lista_queryset.values(*CAMPOS)

    # -------------------------------
    # Permisos de usuario
    # -------------------------------
    access = get_module_user_permissions(context, subModule_id)["data"]["access"]

    # -------------------------------
    # Inicializar contadores
    # -------------------------------
    contador_pagadas = 0
    contador_proximas = 0
    contador_vencidas = 0
    contador_sin_refrendo = total_vehiculos.exclude(
        id__in=Vehicle_Refrendo.objects.values_list("vehiculo_id", flat=True)
    ).count()

    # -------------------------------
    # Preparar datos para la tabla y contar estados
    # -------------------------------
    result = []
    for item in lista:
        fecha = item["fecha_pago"]
        pago_year = fecha.year if fecha else None
        estado = None

        if fecha and fecha.year >= year:
            estado = "pagada"
            contador_pagadas += 1
        elif month in [12, 1, 2, 3] and pago_year == year - 1 and \
             item["vehiculo_id"] not in latest_only.filter(fecha_pago__range=(inicio_trimestre, fin_trimestre)).values_list("vehiculo_id", flat=True):
            estado = "proxima"
            contador_proximas += 1
        elif (pago_year is None or pago_year < year - 1) or (pago_year == year - 1 and month > 3):
            estado = "vencida"
            contador_vencidas += 1

        if tipo_carga == "sin_refrendo":
            estado = "sin_refrendo"

        item["estado"] = estado

        # Botones de acción
        item["btn_action"] = ""
        if estado not in ["sin_refrendo", None]:
            if item["comprobante_pago"]:
                tempDoc = generate_presigned_url(bucket_name, item["comprobante_pago"])
                item["btn_action"] = f"""<a href="{tempDoc}" class="btn btn-sm btn-info" target="_blank">
                    <i class="fa-solid fa-file"></i> Comprobante 
                </a>\n"""
            if access["update"]:
                item["btn_action"] += """<button class="btn btn-primary btn-sm" data-vehicle-refrendo="update-item">
                    <i class="fa-solid fa-pen"></i>
                </button>\n"""
            if access["delete"]:
                item["btn_action"] += """<button class="btn btn-danger btn-sm" data-vehicle-refrendo="delete-item">
                    <i class="fa-solid fa-trash"></i>
                </button>"""

        result.append(item)

    # -------------------------------
    # Asignar contadores a la respuesta
    # -------------------------------
    response["counters"] = {
        "total": len(lista),
        "pagadas": contador_pagadas,
        "vencidas": contador_vencidas,
        "proximas": contador_proximas,
        "sin_refrendo": contador_sin_refrendo,
        "total_vehiculos": total_vehiculos_count,
        "total_vehiculos_sin_refrendo": contador_sin_refrendo,
    }

    response["data"] = result
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
        fecha_pago = dt.get("fecha_pago")
        if fecha_pago:
            fecha_dt = datetime.strptime(fecha_pago, "%Y-%m-%d")
            if fecha_dt.month not in [1, 2, 3]:
                response["error"] = {"message": "Solo se pueden registrar pagos de refrendo de enero a marzo."}
                return JsonResponse(response)

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
        if obj.comprobante_pago:
            delete_s3_object(AWS_BUCKET_NAME, str(obj.comprobante_pago))
        obj.delete()
    response["success"] = True
    return JsonResponse(response)

def add_vehicle_verificacion(request):
    response = {"success": False}
    dt = request.POST
    vehicle_id = dt.get("vehiculo_id")

    # 1) Obtener vehículo y compañía
    try:
        veh = Vehicle.objects.get(id=vehicle_id)
        company_id = veh.company.id
    except Vehicle.DoesNotExist:
        return JsonResponse({
            "success": False,
            "error": {"message": f"Vehículo {vehicle_id} no encontrado"}
        })

    # 2) Crear registro PAGADO
    try:
        pago = Vehicle_Verificacion.objects.create(
            vehiculo=veh,
            monto=dt.get("monto"),
            engomado=dt.get("engomado"),
            periodo=dt.get("periodo"),
            fecha_pago=dt.get("fecha_pago"),
            lugar=dt.get("lugar"),
            status='PAGADO'
        )

        # 3) Subir comprobante (si existe) a S3
        if 'comprobante_pago' in request.FILES:
            f = request.FILES['comprobante_pago']
            _, ext = os.path.splitext(f.name)
            key = f"docs/{company_id}/vehicle/{vehicle_id}/verificacion/comprobante_{pago.id}{ext}"
            upload_to_s3(f, bucket_name, key)
            pago.comprobante_pago = key
            pago.save()

        # 4) Generar próximo pago con status='PROXIMO'
        fecha_ref = pago.fecha_pago or timezone.now().date()
        fecha_next, periodo_next = obtener_siguiente_pago(veh, fecha_ref)

        Vehicle_Verificacion.objects.create(
            vehiculo=veh,
            monto=pago.monto,
            engomado=pago.engomado,
            periodo=periodo_next,
            fecha_pago=fecha_next,
            lugar=pago.lugar,
            status='PROXIMO'
        )

        response["success"] = True
        response["id"] = pago.id

    except Exception as e:
        response["error"] = {"message": str(e)}

    return JsonResponse(response)

_CALENDARIO = None
def get_calendario_verificacion():
    """
    Carga una sola vez el JSON y lo deja cacheado en _CALENDARIO.
    Imprime cuándo comienza y termina el proceso de lectura del JSON.
    """
    global _CALENDARIO
    if _CALENDARIO is None:
        # print("==> Iniciando lectura del JSON calendario_de_verificacion.json...")
        path = os.path.join(
            settings.BASE_DIR,
            "modules", "static", "assets", "json",
            "calendario_de_verificacion.json"
        )
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
            _CALENDARIO = data.get("data", {})
        # print("==> Lectura del JSON completada con éxito.")
    return _CALENDARIO


def obtener_siguiente_pago(vehiculo, fecha_referencia):
    # print(f"\n==> Obteniendo siguiente pago para vehículo con placa: {vehiculo.plate}")
    calendario = get_calendario_verificacion()
    placa = vehiculo.plate.strip().upper()

    digitos = re.findall(r'\d', placa)
    if not digitos:
        raise ValueError(f"No se encontró dígito numérico en la placa '{vehiculo.plate}'")
    ultimo_digito = digitos[-1]
    # print(f" - Último dígito de placa: {ultimo_digito}")

    entry = calendario.get(ultimo_digito)
    if not entry:
        raise ValueError(f"No existe calendario para placa terminada en '{ultimo_digito}'")

    # print(f" - Engomado: {entry.get('engomado_ES', 'No definido')}")
    # print(f" - Meses S1: {[m.get('month_name_ES', '') for m in entry.get('s1', [])]}")
    # print(f" - Meses S2: {[m.get('month_name_ES', '') for m in entry.get('s2', [])]}")

    sem1 = [m["month_code"] for m in entry["s1"]]
    sem2 = [m["month_code"] for m in entry["s2"]]
    
    # Parsear fecha de referencia (acepta string o date)
    fecha_ref = datetime.strptime(fecha_referencia, "%Y-%m-%d").date() if isinstance(fecha_referencia, str) else fecha_referencia
    mes_ref = fecha_ref.month
    anio_ref = fecha_ref.year

    if mes_ref in sem1:
        target_months = sem2
        periodo = "2do semestre"  # Cambiado a texto descriptivo
        anio_target = anio_ref
    elif mes_ref in sem2:
        target_months = sem1
        periodo = "1er semestre"  # Cambiado a texto descriptivo
        anio_target = anio_ref + 1
    else:
        # Si el mes actual no está en ningún semestre, elegir el próximo sem1 o sem2 más cercano
        if mes_ref < min(sem1):
            target_months = sem1
            periodo = "1er semestre"
            anio_target = anio_ref
        else:
            target_months = sem1
            periodo = "1er semestre"
            anio_target = anio_ref + 1

    mes_target = min(target_months)
    fecha_pago = date(anio_target, mes_target, 1)

    # print(f"==> Próxima verificación será en: {fecha_pago} para el {periodo} del {anio_target}\n")
    return fecha_pago, periodo


def add_vehicle_verificacion_BACK(request):
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
        "monto", "fecha_pago", "comprobante_pago", "status"
    )
    access = get_module_user_permissions(context, subModule_id)
    access = access["data"]["access"]

    for item in lista:
        item["btn_action"] = ""
        if item["comprobante_pago"] :
            tempDoc = generate_presigned_url(bucket_name, item["comprobante_pago"])
            item["btn_action"] = f"""<a href="{tempDoc}" class="btn btn-sm btn-info" target="_blank">
                <i class="fa-solid fa-file"></i> Comprobante 
            </a>\n"""
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
    response = {"success": False, "data": [], "counters": {}}
    dt = request.GET
    vehicle_id = dt.get("vehiculo_id", None)
    tipo_carga = dt.get("tipo_carga", "todos")
    subModule_id = 7

    # Fechas de referencia
    hoy = timezone.now().date()
    year = hoy.year

    # --- VEHÍCULOS DISPONIBLES SEGÚN PERMISOS ---
    total_vehiculos = Vehicle.objects.filter(company_id=context["company"]["id"])
    if context["role"]["id"] not in [1, 2, 3]:
        total_vehiculos = total_vehiculos.filter(responsible_id=context["user"]["id"])
    if vehicle_id:
        total_vehiculos = total_vehiculos.filter(id=vehicle_id)
    total_vehiculos_count = total_vehiculos.count()

    # Vehículos con verificación en cualquier año
    vehicles_with_verificacion = Vehicle_Verificacion.objects.filter(
        vehiculo__in=total_vehiculos
    ).values_list("vehiculo_id", flat=True)

    # Vehículos sin verificación
    sin_verificacion_count = total_vehiculos.exclude(id__in=vehicles_with_verificacion).count()

    # Última verificación por vehículo
    latest_verificacion = Vehicle_Verificacion.objects.filter(
        vehiculo_id=OuterRef('vehiculo_id')
    ).order_by('-fecha_pago')
    all_verificaciones = Vehicle_Verificacion.objects.filter(vehiculo__in=total_vehiculos)
    latest_only = all_verificaciones.filter(id=Subquery(latest_verificacion.values('id')[:1]))

    CAMPOS = [
        "id", "engomado", "periodo", "lugar", "status",
        "vehiculo_id", "vehiculo__name",
        "monto", "fecha_pago", "comprobante_pago"
    ]

    # Aplicar filtro según tipo_carga
    if tipo_carga == "pagadas":
        lista_queryset = latest_only.filter(status='PAGADO')

    elif tipo_carga == "vencidas":
        lista_queryset = latest_only.filter(
            Q(status='PENDIENTE') |
            Q(status='Vencido') |  
            Q(status='VENCIDO') | 
            Q(status='PROXIMO', fecha_pago__lt=hoy)
        )


    elif tipo_carga == "proximas":
        lista_queryset = latest_only.filter(
            status='PROXIMO',
            fecha_pago__gte=hoy
        )
    elif tipo_carga == "sin_verificacion":
        lista = (
            total_vehiculos.exclude(id__in=vehicles_with_verificacion)
            .annotate(
                vehiculo_id=F("id"),
                vehiculo__name=F("name"),
                verificacion_id=Value(None, output_field=IntegerField()),
                engomado=Value("", output_field=CharField()),
                periodo=Value("", output_field=CharField()),
                lugar=Value("", output_field=CharField()),
                status=Value("", output_field=CharField()),
                monto=Value("", output_field=CharField()),
                fecha_pago=Value(None, output_field=DateField()),
                comprobante_pago=Value("", output_field=CharField()),
            )
            .values(*CAMPOS)
        )
    else:  # todos
        lista_queryset = latest_only

    # Convertir a lista de dicts
    if tipo_carga != "sin_verificacion":
        lista = lista_queryset.values(*CAMPOS)

    # Obtener permisos del módulo
    access = get_module_user_permissions(context, subModule_id)["data"]["access"]

    # Contadores
    contadores = {
        "total": 0,
        "pagadas": 0,
        "proximas": 0,
        "vencidas": 0,
        "sin_verificacion": sin_verificacion_count,
    }

    # Preparar datos de respuesta
    result = []
    for item in lista:
        if "verificacion_id" in item:
            item["id"] = item.pop("verificacion_id")

        estado = None
        fecha = item["fecha_pago"]

        if tipo_carga == "sin_verificacion":
            estado = "sin_verificacion"
        elif item["status"] == 'PAGADO':
            estado = "pagada"
            contadores["pagadas"] += 1
        elif item["status"] == 'PROXIMO':
            if fecha and fecha >= hoy:
                estado = "proxima"
                contadores["proximas"] += 1
        elif item["status"] in ['VENCIDO', 'Vencido']:
            estado = "vencida"
            contadores["vencidas"] += 1

            
        elif item["status"] == 'PENDIENTE':
            estado = "vencida"
            contadores["vencidas"] += 1

        item["estado"] = estado
        contadores["total"] += 1

        # Botones de acción
        item["btn_action"] = ""
        if item["estado"] not in ["sin_verificacion", None]:
            if item["comprobante_pago"]:
                tempDoc = generate_presigned_url(bucket_name, item["comprobante_pago"])
                item["btn_action"] = f"""<a href="{tempDoc}" class="btn btn-sm btn-info" target="_blank">
                    <i class="fa-solid fa-file"></i> Comprobante
                </a>\n"""
            if access["update"]:
                item["btn_action"] += """<button class="btn btn-primary btn-sm" data-vehicle-verificacion="update-item">
                    <i class="fa-solid fa-pen"></i>
                </button>\n"""
            if access["delete"]:
                item["btn_action"] += """<button class="btn btn-danger btn-sm" data-vehicle-verificacion="delete-item">
                    <i class="fa-solid fa-trash"></i>
                </button>"""

        result.append(item)

    # Asignar contadores a la respuesta
    response["counters"] = {
        **contadores,
        "total_vehiculos": total_vehiculos_count,
        "total_vehiculos_sin_verificacion": sin_verificacion_count,
    }
    response["data"] = result
    response["success"] = True
    return JsonResponse(response, safe=False)


def update_vehicle_verificacion(request):
    response = {"success": False}
    dt = request.POST
    
    id = dt.get("id", None)
    if not id:
        response["error"] = {"message": "No se proporcionó un ID válido para actualizar."}
        return JsonResponse(response)
    
    try:
        obj = Vehicle_Verificacion.objects.get(id=id)
    except Vehicle_Verificacion.DoesNotExist:
        response["error"] = {"message": f"No existe ningún registro con el ID '{id}'"}
        return JsonResponse(response)

    # print(f"==> Registro encontrado: {obj.id}, Estado actual: {obj.status}")

    try:
        # VERIFICACIÓN CORREGIDA: Excluir el registro actual de la búsqueda
        proximo_registro = Vehicle_Verificacion.objects.filter(
            vehiculo=obj.vehiculo,
            status='PROXIMO'
        ).exclude(id=obj.id).first()  # <- Esta es la línea clave
        
        if proximo_registro:
            print(f"==> Ya existe un registro próximo con ID: {proximo_registro.id}")
        else:
            print("==> No se encontró un registro 'PROXIMO', se creará uno nuevo.")

        # Actualizar datos básicos
        obj.monto = dt.get("monto", obj.monto)
        obj.fecha_pago = dt.get("fecha_pago", obj.fecha_pago)
        obj.lugar = dt.get("lugar", obj.lugar)
        
        # print(f"==> Datos actualizados: Monto: {obj.monto}, Fecha de pago: {obj.fecha_pago}, Lugar: {obj.lugar}")
        
        # Manejo del comprobante
        nuevo_comprobante = request.FILES.get('comprobante_pago')
        if nuevo_comprobante:
            # print(f"==> Se está subiendo un nuevo comprobante: {nuevo_comprobante.name}")
            
            if obj.comprobante_pago:
                try:
                    # print(f"==> Eliminando comprobante anterior: {obj.comprobante_pago}")
                    delete_s3_object(bucket_name, obj.comprobante_pago)
                except Exception as e:
                    print(f"Error al eliminar comprobante anterior: {str(e)}")
            
            company_id = request.session.get('company', {}).get('id')
            if not company_id:
                raise ValueError("No se pudo obtener el company_id de la sesión")
                
            _, extension = os.path.splitext(nuevo_comprobante.name)
            new_name = f"comprobante_pago_{id}{extension}"
            s3_path = f"docs/{company_id}/vehicle/{obj.vehiculo_id}/verificacion/{new_name}"
            
            # print(f"==> Subiendo comprobante a S3: {s3_path}")
            upload_to_s3(nuevo_comprobante, bucket_name, s3_path)
            obj.comprobante_pago = s3_path

        # Cambiar estado a PAGADO
        # print(f"==> Estado actual: {obj.status}, Nuevo comprobante: {nuevo_comprobante}, Monto: {dt.get('monto')}")
        if not obj.status == 'PAGADO' and (nuevo_comprobante or dt.get('monto')):
            # print("==> Cambiando estado a PAGADO.")
            obj.status = 'PAGADO'
            
            # Solo crear nuevo registro si no existe uno próximo (excluyendo el actual)
            if not proximo_registro:
                # print("==> Creando nuevo registro PROXIMO.")
                fecha_next, periodo_next = obtener_siguiente_pago(obj.vehiculo, obj.fecha_pago or timezone.now().date())
                Vehicle_Verificacion.objects.create(
                    vehiculo=obj.vehiculo,
                    engomado=obj.engomado,
                    periodo=periodo_next,
                    fecha_pago=fecha_next,
                    status='PROXIMO'
                )
                # print(f"==> Nuevo registro PROXIMO creado para fecha: {fecha_next}")

        obj.save()
        # print(f"==> Registro actualizado con éxito: {obj.id}, Estado final: {obj.status}")

        response["success"] = True
        response["data"] = {
            "id": obj.id,
            "status": obj.status,
            "has_comprobante": bool(obj.comprobante_pago),
            "nuevo_proximo_creado": not proximo_registro and obj.status == 'PAGADO'
        }

    except Exception as e:
        # print(f"==> ERROR: {str(e)}")
        response["error"] = {"message": str(e)}
        if 'obj' in locals() and obj.pk:
            # print(f"==> Revirtiendo cambios para el registro ID: {obj.id}")
            obj.save()

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
        # print(lista)
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
    response = {"success": False, "data": [], "counters": {}}
    dt = request.GET
    vehicle_id = dt.get("vehicle_id")
    tipo_carga = dt.get("tipo_carga", "todos")
    subModule_id = 9

    hoy = timezone.now().date()

    # Vehículos disponibles
    vehiculos = Vehicle.objects.filter(company_id=context["company"]["id"])
    if context["role"]["id"] not in [1, 2, 3]:
        vehiculos = vehiculos.filter(responsible_id=context["user"]["id"])
    if vehicle_id:
        vehiculos = vehiculos.filter(id=vehicle_id)
    total_vehiculos_count = vehiculos.count()

    # Último seguro por vehículo
    base_qs = Vehicle_Insurance.objects.filter(vehicle__in=vehiculos)
    latest_qs = Vehicle_Insurance.objects.filter(
        vehicle_id=OuterRef("vehicle_id")
    ).order_by("-end_date")
    latest_only = base_qs.filter(id=Subquery(latest_qs.values("id")[:1]))

    # Contadores
    contadores = {
        "total": 0,
        "pagadas": 0,
        "proximas": 0,
        "vencidas": 0,
        "sin_seguro": 0,
    }

    # Vehículos con seguro en cualquier año
    vehicles_with_insurance = Vehicle_Insurance.objects.filter(
        vehicle__in=vehiculos
    ).values_list("vehicle_id", flat=True)
    contadores["sin_seguro"] = vehiculos.exclude(
        id__in=vehicles_with_insurance
    ).count()

    # Filtro según tipo_carga
    if tipo_carga == "pagadas":
        lista_queryset = latest_only.filter(status="PAGADO")
    elif tipo_carga == "vencidas":
        lista_queryset = latest_only.filter(status="VENCIDO")
    elif tipo_carga == "proximas":
        lista_queryset = latest_only.filter(status="PROXIMO")
    elif tipo_carga == "sin_seguro":
        lista = (
            vehiculos.exclude(id__in=vehicles_with_insurance)
            .annotate(
                alias_vehicle_id=F("id"),
                alias_vehicle_name=F("name"),
                alias_responsible_id=F("responsible_id"),
                alias_responsible_first_name=F("responsible__first_name"),
                alias_responsible_last_name=F("responsible__last_name"),
                alias_policy_number=Value("", output_field=CharField()),
                alias_insurance_company=Value("", output_field=CharField()),
                alias_cost=Value("", output_field=CharField()),
                alias_validity=Value("", output_field=CharField()),
                alias_doc=Value("", output_field=CharField()),
                alias_start_date=Value(None, output_field=DateField()),
                alias_end_date=Value(None, output_field=DateField()),
                alias_status=Value("", output_field=CharField()),
            )
            .values(
                "alias_vehicle_id", "alias_vehicle_name",
                "alias_responsible_id", "alias_responsible_first_name", "alias_responsible_last_name",
                "alias_policy_number", "alias_insurance_company", "alias_cost", "alias_validity", "alias_doc",
                "alias_start_date", "alias_end_date", "alias_status"
            )
        )
        contadores["sin_seguro"] = lista.count()
    else:
        lista_queryset = latest_only

    # Si no es sin_seguro, aplicamos values normalmente
    if tipo_carga != "sin_seguro":
        lista = lista_queryset.values(
            "id", "vehicle_id", "vehicle__name",
            "responsible_id", "responsible__first_name", "responsible__last_name",
            "policy_number", "insurance_company", "cost", "validity", "doc",
            "start_date", "end_date", "status"
        ).order_by("-end_date")

    access = get_module_user_permissions(context, subModule_id)["data"]["access"]

    # Preparar respuesta
    result = []
    for item in lista:
        estado = None
        if tipo_carga == "sin_seguro":
            # Mapear alias
            item["vehicle_id"] = item.pop("alias_vehicle_id")
            item["vehicle__name"] = item.pop("alias_vehicle_name")
            item["responsible_id"] = item.pop("alias_responsible_id")
            item["responsible__first_name"] = item.pop("alias_responsible_first_name")
            item["responsible__last_name"] = item.pop("alias_responsible_last_name")
            item["policy_number"] = item.pop("alias_policy_number")
            item["insurance_company"] = item.pop("alias_insurance_company")
            item["cost"] = item.pop("alias_cost")
            item["validity"] = item.pop("alias_validity")
            item["doc"] = item.pop("alias_doc")
            item["start_date"] = item.pop("alias_start_date")
            item["end_date"] = item.pop("alias_end_date")
            item["status"] = item.pop("alias_status")
            item["id"] = item["vehicle_id"]
            estado = "sin_seguro"
        else:
            status = item.get("status")
            if status == "PAGADO":
                estado = "pagada"
                contadores["pagadas"] += 1
            elif status == "PROXIMO":
                estado = "proxima"
                contadores["proximas"] += 1
            elif status == "VENCIDO":
                estado = "vencida"
                contadores["vencidas"] += 1

        item["estado"] = estado
        contadores["total"] += 1

        # Botones
        item["btn_action"] = ""
        if item["estado"] != "sin_seguro" and item.get("doc"):
            tempDoc = generate_presigned_url(bucket_name, item["doc"])
            item["btn_action"] = f"""<a href="{tempDoc}" class="btn btn-sm btn-info" download>
                <i class="fa-solid fa-file"></i> Ver seguro
            </a>\n"""
            if access["update"]:
                item["btn_action"] += """<button class="btn btn-primary btn-sm" data-vehicle-insurance="update-item">
                    <i class="fa-solid fa-pen"></i>
                </button>\n"""
            if access["delete"]:
                item["btn_action"] += """<button class="btn btn-danger btn-sm" data-vehicle-insurance="delete-item">
                    <i class="fa-solid fa-trash"></i>
                </button>\n"""

        result.append(item)

    response["counters"] = {**contadores, "total_vehiculos": total_vehiculos_count}
    response["data"] = result
    response["success"] = True
    return JsonResponse(response)


# Función auxiliar para generar nuevos registros (NUEVA FUNCIONALIDAD)
def generar_proximos_pagos(queryset, fecha_referencia):
    for seguro in queryset.filter(end_date__gt=fecha_referencia):
        # Verificar si ya existe un registro para el próximo período
        existe = Vehicle_Insurance.objects.filter(
            vehicle_id=seguro['vehicle_id'],
            policy_number=seguro['policy_number'],
            start_date__gt=seguro['end_date']
        ).exists()
        
        if not existe:
            nuevo_seguro = Vehicle_Insurance(
                vehicle_id=seguro['vehicle_id'],
                start_date=seguro['end_date'] + timedelta(days=1),

                status='PROXIMO'
            )
            nuevo_seguro.save()


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
        "policy_number", "insurance_company", "cost", "validity", "doc", "start_date", "end_date","status"
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
        if item["doc"] :
            tempDoc = generate_presigned_url(bucket_name, item["doc"])
            item["btn_action"] = f"""<a href="{tempDoc}" class="btn btn-sm btn-info" download>
                <i class="fa-solid fa-file"></i> Ver seguro
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
    dt = request.POST
    id = dt.get("id")

    if not id:
        response["error"] = {"message": "No se proporcionó un ID de seguro de vehículo"}
        return JsonResponse(response)

    try:
        obj = Vehicle_Insurance.objects.get(id=id)
        obj.vehicle_id = dt.get("vehicle_id", obj.vehicle_id)
        obj.responsible_id = dt.get("responsible_id", obj.responsible_id)
        obj.policy_number = dt.get("policy_number", obj.policy_number)
        obj.insurance_company = dt.get("insurance_company", obj.insurance_company)
        obj.cost = dt.get("cost", obj.cost)
        obj.validity = dt.get("validity", obj.validity)
        obj.start_date = dt.get("start_date", obj.start_date)
        obj.end_date = dt.get("end_date", obj.end_date)

        # Si hay un nuevo archivo adjunto
        if 'doc' in request.FILES:
            load_file = request.FILES['doc']
            company_id = request.session.get('company').get('id')
            folder_path = f'docs/{company_id}/vehicle/{obj.vehicle_id}/seguro/'
            file_name, extension = os.path.splitext(load_file.name)
            new_name = f"doc_{obj.id}{extension}"
            s3Name = folder_path + new_name

            upload_to_s3(load_file, bucket_name, s3Name)
            obj.doc = s3Name

        obj.save()

        # Actualizar info también en el vehículo
        vehicle = obj.vehicle
        vehicle.policy_number = obj.policy_number
        vehicle.validity = obj.end_date
        vehicle.insurance_company = obj.insurance_company
        vehicle.save()

        response["success"] = True
        response["id"] = obj.id

    except Vehicle_Insurance.DoesNotExist:
        response["error"] = {"message": f"No se encontró el registro con ID {id}"}
    except Exception as e:
        response["error"] = {"message": str(e)}

    return JsonResponse(response)


def delete_vehicle_insurance(request):
    response = {"success": False, "data": []}
    dt = request.POST
    id = dt.get("id", None)

    if not id:
        response["error"] = {"message": "Proporcione un id valido"}
        return JsonResponse(response)

    try:
        obj = Vehicle_Insurance.objects.get(id = id)
    except Vehicle_Insurance.DoesNotExist:
        response["error"] = {"message": "El objeto no existe"}
        return JsonResponse(response)
     # Validar existencia del documento antes de borrar en S3
    if obj.doc:
        try:
            delete_s3_object(AWS_BUCKET_NAME, str(obj.doc))
        except Exception as e:
            response["error"] = {"message": f"Error al eliminar de S3: {str(e)}"}
            return JsonResponse(response)

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

    # Obtener la lista de auditorías
    lista = Vehicle_Audit.objects.filter(vehicle_id = vehicle_id).values(
        "id", "vehicle_id", "vehicle__name", 
        "audit_date", "general_notes",
        "checks", "is_visible", "is_checked", "commitment_date", "calification"
    )

    if context["role"]["id"] in [1, 2, 3]:
        lista = lista.filter(vehicle__company_id=context["company"]["id"])
    else:
        lista = lista.filter(vehicle__responsible_id=context["user"]["id"])

    if not context["role"]["id"] in [1, 2]:
        lista = lista.exclude(is_visible=False)

    access = get_module_user_permissions(context, subModule_id)
    access = access["data"]["access"]


    #Función para obtener texto de calificación
    def get_textual_calification(score):
        if score is None:
            return "Sin calificación"
        score = Decimal(str(score))
        calification_map = {
            "malo": (Decimal("0.0"), Decimal("3.0")),
            "regular": (Decimal("3.01"), Decimal("6.89")),
            "bueno": (Decimal("6.9"), Decimal("8.79")),
            "excelente": (Decimal("8.8"), Decimal("10.0"))
        }
        for label, (low, high) in calification_map.items():
            if low <= score <= high:
                return label.capitalize()
        return "Calificación fuera de rango"

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
                        "notes": check_notes,
                        "imagen": generate_presigned_url(AWS_BUCKET_NAME, check.get("imagen", "")) if check.get("imagen") else None,
                        "correction": generate_presigned_url(AWS_BUCKET_NAME, str(
                            VehicleAuditCorrection.objects.filter(audit_id=item["id"], check_name=check_name).values_list('image', flat=True).first() or ""
                        )) if VehicleAuditCorrection.objects.filter(audit_id=item["id"], check_name=check_name).exists() else None
                    })

                # Reemplazar el JSON con la nueva estructura
                item["checks"] = checks_with_names

                
                # Calcular calification_text
                try:
                    score = float(item.get("calification"))
                except (TypeError, ValueError):
                    score = None
                item["calification_text"] = get_textual_calification(score)

            except json.JSONDecodeError as e:
                print(f"Error parsing JSON for checks: {e}")
                item["checks"] = []  # En caso de error, asignar lista vacía
        else:
            item["checks"] = []  # Si no hay checks, asignar lista vacía
            item["calification_text"] = "Sin calificación" 
            
        # Definir si la auditoría está chequeada y visible
        is_checked = item["is_checked"]  # Verifica si está chequeada
        is_visible = item["is_visible"]     # Verifica si es visible

        item["is_checked"] = is_checked
        item["is_visible"] = is_visible

        # Botones de acción
        item["btn_action"] = """<button class=\"btn btn-primary btn-sm\" data-vehicle-audit=\"show-info-details\">
            <i class="fa-sharp fa-solid fa-eye"></i>
        </button>\n"""

        if item.get("imagen_url"):
            item["btn_action"] += f"""<a href="{item['imagen_url']}" target="_blank" class="btn btn-sm btn-info">
                <i class="fa fa-image"></i> Ver Imagen
            </a>\n"""


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
    response = {"success": False, "data": [], "counters": {}}
    dt = request.GET
    vehicle_id = dt.get("vehicle_id", None)
    tipo_carga = dt.get("tipo_carga", "todas")
    period = dt.get("period", None)  # 'mensual' o 'semanal'
    estado = dt.get("estado_calificacion", "").lower()
    print("🧪 Estado recibido:", estado)

    selected_date = dt.get("selected_date", None)  # '2025-08' o '2025-W32'
    subModule_id = 10

    hoy = timezone.now().date()
    un_mes_despues = hoy + timedelta(days=30)

    # Vehículos disponibles según permisos
    total_vehiculos = Vehicle.objects.filter(company_id=context["company"]["id"])
    if context["role"]["id"] not in [1, 2, 3]:
        total_vehiculos = total_vehiculos.filter(responsible_id=context["user"]["id"])
    if vehicle_id:
        total_vehiculos = total_vehiculos.filter(id=vehicle_id)
    total_vehiculos_count = total_vehiculos.count()

    # Base auditorías vinculadas a vehículos
    base_audit_qs = Vehicle_Audit.objects.filter(vehicle__in=total_vehiculos)

    # Excluir no visibles para roles no administrativos
    if context["role"]["id"] not in [1, 2, 3]:
        base_audit_qs = base_audit_qs.exclude(is_visible=False)

    # Subquery para obtener la auditoría más reciente por vehículo
    latest_audit = Vehicle_Audit.objects.filter(
        vehicle_id=OuterRef('vehicle_id')
    ).order_by('-audit_date')

    latest_only = base_audit_qs.filter(id=Subquery(latest_audit.values('id')[:1]))

    # Aplicar filtros según el periodo y fecha seleccionada
    filtered_audit_qs = latest_only  # Por defecto: auditorías del mes actual
    if selected_date and period:
        try:
            if period == "mensual":
                year, month = map(int, selected_date.split("-"))
                filtered_audit_qs = latest_only.filter(
                    audit_date__year=year,
                    audit_date__month=month
                )
            elif period == "semanal":
                year, week = map(int, selected_date.split("-W"))
                filtered_audit_qs = latest_only.filter(
                    audit_date__week=week,
                    audit_date__year=year
                )
        except ValueError:
            pass  # Si el formato es inválido, no aplicar ningún filtro

    # Filtrar según tipo_carga
    if tipo_carga == "evaluadas":
        lista_queryset = filtered_audit_qs.filter(is_checked=True)
    elif tipo_carga == "vencidas":
        lista_queryset = filtered_audit_qs.filter(audit_date__lt=hoy, is_checked=False)
    elif tipo_carga == "proximas":
        lista_queryset = filtered_audit_qs.filter(
            audit_date__gte=hoy, audit_date__lte=un_mes_despues, is_checked=False
        )
    else:  # todas
        lista_queryset = filtered_audit_qs

    # Filtrar por calificación textual
    if estado in ["todas", "malo", "regular", "bueno", "excelente"]:
        rango_estado = {
            "malo": (Decimal("0.0"), Decimal("3.0")),
            "regular": (Decimal("3.01"), Decimal("6.89")),
            "bueno": (Decimal("6.9"), Decimal("8.79")),
            "excelente": (Decimal("8.8"), Decimal("10.0")),
            "todas": (Decimal("0.0"), Decimal("10.0"))
        }
        
        min_val, max_val = rango_estado[estado]
        lista_queryset = lista_queryset.filter(calification__gte=min_val, calification__lte=max_val)

    # Contadores
    response["counters"] = {
        "total": lista_queryset.count(),
        "total_vehiculos": total_vehiculos_count,
        "evaluadas": filtered_audit_qs.filter(is_checked=True).count(),
        "vencidas": filtered_audit_qs.filter(audit_date__lt=hoy, is_checked=False).count(),
        "proximas": filtered_audit_qs.filter(
            audit_date__gte=hoy, audit_date__lte=un_mes_despues, is_checked=False
        ).count(),
    }

    # Seleccionar campos para el listado
    lista = lista_queryset.values(
        "id", "vehicle_id", "vehicle__name",
        "audit_date", "general_notes",
        "checks", "is_visible", "is_checked", "commitment_date", "calification"
    )

    if context["role"]["id"] in [1, 2, 3]:
        lista = lista.filter(vehicle__company_id=context["company"]["id"])
    else:
        lista = lista.filter(vehicle__responsible_id=context["user"]["id"])
    if not context["role"]["id"] in [1, 2, 3]:
        lista = lista.exclude(is_visible=False)

    access = get_module_user_permissions(context, subModule_id)
    access = access["data"]["access"]

    calification_map = {
        "Muy malo": 0,
        "Malo": 2,
        "Regular": 4.5,
        "Bueno": 7,
        "Excelente": 9.5
    }

    def get_textual_calification(score):
        if score is None:
            return "Sin calificación"

        score = Decimal(str(score))

        calification_map = {
            "malo": (Decimal("0.0"), Decimal("3.0")),
            "regular": (Decimal("3.01"), Decimal("6.89")),
            "bueno": (Decimal("6.9"), Decimal("8.79")),
            "excelente": (Decimal("8.8"), Decimal("10.0"))
        }

        for label, (low, high) in calification_map.items():
            if low <= score <= high:
                return label.capitalize()
        return "Calificación fuera de rango"

    #print(f" Filtro aplicado → {estado} | Rango: {min_val} - {max_val}")
    print(f" Queryset count: {lista_queryset.count()}")

    for item in lista:
        print(item.get("calification"), "→", item.get("calification_text"))

        if item["checks"]:
            try:
                checks_string = item["checks"].replace("'", "\"")
                checks_data = json.loads(checks_string)
                checks_with_names = []

                for check in checks_data:
                    check_id = check.get("id")
                    check_status = check.get("status")
                    check_notes = check.get("notas")

                    check_name = Checks.objects.filter(id=check_id).values_list("name", flat=True).first()
                    imagen_check = generate_presigned_url(AWS_BUCKET_NAME, str(check.get("imagen", ""))) if check.get("imagen") else None

                    
                    checks_with_names.append({
                        "id": check_id,
                        "name": check_name if check_name else "Sin nombre",
                        "status": check_status,
                        "notes": check_notes,
                        "imagen": imagen_check,
                        "correction": generate_presigned_url(AWS_BUCKET_NAME, str(
                            VehicleAuditCorrection.objects.filter(audit_id=item["id"], check_name=check_name).values_list('image', flat=True).first() or ""
                        )) if VehicleAuditCorrection.objects.filter(audit_id=item["id"], check_name=check_name).exists() else None
                    })

                item["checks"] = checks_with_names
                try:
                    score = float(item.get("calification"))
                except (TypeError, ValueError):
                    score = None
                item["calification_text"] = get_textual_calification(score)



            except json.JSONDecodeError as e:
                print(f"Error parsing JSON for checks: {e}")
                item["checks"] = []
        else:
            item["checks"] = []

        is_checked = item["is_checked"]
        is_visible = item["is_visible"]

        item["is_checked"] = is_checked
        item["is_visible"] = is_visible

        item["btn_action"] = """<button class=\"btn btn-primary btn-sm\" data-vehicle-audit=\"show-info-details\">
            <i class="fa-sharp fa-solid fa-eye"></i>
        </button>\n"""

        if not is_checked and is_visible:
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
    response["filtro_estado"] = estado
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
    is_new_register = dt.get("is_new_register")== "1"
    subModule_id = 11

    if not vehicle_id:
        response["status"] = "warning"
        response["message"] = "No se proporcionó un ID de vehículo válido"
        return JsonResponse(response)
    
    try:
        obj_vehicle = Vehicle.objects.get(id=vehicle_id)
        if is_new_register:

            try:
                mileage = Decimal(dt.get("mileage")) if dt.get("mileage") else None
            except (InvalidOperation, TypeError):
                mileage = None
            # Verificamos que el kilometraje sea coerente
            if mileage is not None and obj_vehicle.mileage is not None:
                if Decimal(obj_vehicle.mileage) > mileage:
                    response["status"] = "warning"
                    response["message"] = (
                        f"El kilometraje actual del vehículo ({obj_vehicle.mileage} km) "
                        f"es mayor que el ingresado ({mileage} km)."
                    )
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
                status="NUEVO",
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
    

    # Crear el queryset base
    base_maintenance_qs = Vehicle_Maintenance.objects.all()

    # Aplicar filtros según rol
    if context["role"]["id"] in [1, 2]:
        base_maintenance_qs = base_maintenance_qs.filter(vehicle__company_id=context["company"]["id"])
    else:
        base_maintenance_qs = base_maintenance_qs.filter(vehicle__responsible_id=context["user"]["id"])

    # Subquery: seleccionar el mantenimiento más reciente por vehículo
    latest_maintenance = Vehicle_Maintenance.objects.filter(
        vehicle_id=OuterRef('vehicle_id')
    ).order_by('-date')

    # Filtrar el queryset base 
    base_maintenance_qs = base_maintenance_qs.filter(id=Subquery(latest_maintenance.values('id')[:1]))

    # Extraer solo los campos que se van a devolver
    lista = base_maintenance_qs.values(
        "id", "vehicle_id", "vehicle__name",
        "provider_id", "provider__name",
        "date", "type", "cost", 
        "mileage", "time", "general_notes", "actions", "comprobante", "status"
    )

    # print(context["role"])
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
    vehicle_id = dt.get("fuel_vehicle_id", None)
    company_id = context["company"]["id"]
    responsible_id = request.user.id 
    
    # print("POST data:", dt)
    # print("vehicle_id recibido:", vehicle_id)
    # print("company_id:", company_id)
    # print("responsible_id (usuario actual):", responsible_id)

    try:
        obj = Vehicle.objects.get(id = vehicle_id)
    except Vehicle.DoesNotExist:
        response["status"] = "error"
        response["message"] = "El objeto no existe"
        return JsonResponse(response)
    

    if not responsible_id or responsible_id == None:
        response["status"] = "warning"
        response["message"] = "El vehículo no tiene un responsable asignado"

    try:
        with transaction.atomic():
            obj = Vehicle_fuel(
                vehicle_id = vehicle_id,
                responsible_id=responsible_id,
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

                file_name, extension = os.path.splitext(load_file.name)                
                new_name = f"payment_receipt_{id}{extension}"

            
                upload_to_s3(load_file, AWS_BUCKET_NAME, folder_path + new_name)
                obj.payment_receipt = folder_path + new_name
                obj.save()

            response["id"] = obj.id
        response["status"] = "success"
        response["message"] = "Exito"
    except Exception as e:
        response["status"] = "error"
        response["message"] = str(e)
    response["success"] = response["status"] == "success"
    return JsonResponse(response)

def get_vehicles_fuels(request):
    context = user_data(request)
    response = {"status": "error", "message": "sin procesar", "data": []}
    dt = request.GET
    subModule_id = 22
    company_id = context["company"]["id"]
    role_id = context["role"]["id"]
    user_id = context["user"]["id"]

    try:
        # Obtener los registros filtrados por empresa
        datos = Vehicle_fuel.objects.filter(vehicle__company_id=company_id)

        if role_id == 4:
            datos = datos.filter(responsible_id=user_id)

        datos = datos.values(
            "id",
            "vehicle_id", "vehicle__name",
            "responsible_id", "responsible__first_name", "responsible__last_name",
            "payment_receipt",
            "fuel", "fuel_type",
            "cost", "notes", "date"
        )

        access = get_module_user_permissions(context, subModule_id)
        access = access["data"]["access"]

        for item in datos:
            if item["payment_receipt"]:
                item["payment_receipt"] = generate_presigned_url(bucket_name, item["payment_receipt"])

            item["btn_action"] = ""
            if access["update"]:
                item["btn_action"] += (
                    "<button class=\"btn btn-icon btn-sm btn-primary-light\" data-sia-vehicle-fuel=\"update-item\">"
                    "<i class=\"fa-solid fa-pen\"></i></button>\n"
                )
            if access["delete"]:
                item["btn_action"] += (
                    "<button class=\"btn btn-icon btn-sm btn-danger-light\" data-sia-vehicle-fuel=\"delete-item\">"
                    "<i class=\"fa-solid fa-trash\"></i></button>\n"
                )

        response["data"] = list(datos)
        response["status"] = "success"
        response["message"] = "Datos cargados exitosamente"

    except Exception as e:
        print(f"Error en get_vehicles_fuels: {e}")
        response["message"] = str(e)

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
    vehicle_id = dt.get("fuel_vehicle_id", None)
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

    # Verificar si el QR ya ha sido generado
    if qr_type == "consulta":
        qr_url_info = generate_presigned_url(AWS_BUCKET_NAME, str(vehicle.qr_info)) if vehicle.qr_info else None
        qr_url_access = generate_presigned_url(AWS_BUCKET_NAME, str(vehicle.qr_access)) if vehicle.qr_access else None
        qr_url_fuel = generate_presigned_url(AWS_BUCKET_NAME, str(vehicle.qr_fuel)) if vehicle.qr_fuel else None

        return JsonResponse({
            'status': 'generados',
            'qr_url_info': qr_url_info,
            'qr_url_access': qr_url_access,
            'qr_url_fuel': qr_url_fuel
        })

    # Contenido
    domain = request.build_absolute_uri('/')[:-1]
    #domain = "http://192.168.100.106"

    if qr_type == 'info':
        qr_content = f"{domain}/vehicles/info/{vehicle_id}/"
    elif qr_type == 'access':
        qr_content = f"{domain}/vehicles/responsiva/qr/{vehicle_id}"
    elif qr_type == 'fuel':
        qr_content = f"{domain}/vehicles/fuel-form/?vehicle_id={vehicle_id}"


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
    
    # Definir la ruta del archivo en S3
    s3Path = f'docs/{company_id}/vehicle/{vehicle_id}/qr/'
    if qr_type == 'info':
        s3Name = f"qr_info{vehicle_id}.png"
        vehicle.qr_info = s3Path+s3Name
    elif qr_type == 'access':
        s3Name = f"qr_access_{vehicle_id}.png"
        vehicle.qr_access = s3Path+s3Name 
    elif qr_type == 'fuel':
        s3Name = f"qr_fuel_{vehicle_id}.png"
        vehicle.qr_fuel = s3Path + s3Name
    
    # Crear un InMemoryUploadedFile con content_type
    img = InMemoryUploadedFile(
        buffer, None, s3Name, 'image/png', buffer.getbuffer().nbytes, None
    )
    # Subir el archivo a S3 y obtener la URL
    upload_to_s3(img, AWS_BUCKET_NAME, s3Path + s3Name)
        
    vehicle.save()  
    qr_url = generate_presigned_url(AWS_BUCKET_NAME, str(s3Path + s3Name))
    return JsonResponse({'status': 'success', 'qr_url': qr_url, 'qr_type': qr_type})

#funcion para eliminar el qr
def delete_qr(request, qr_type, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)

    # print("qr_type:", qr_type)
    # print("vehicle.qr_fuel:", vehicle.qr_fuel)
    
    url = ""
    if qr_type == 'info' and vehicle.qr_info:
        url = str(vehicle.qr_info)
        vehicle.qr_info.delete()
    elif qr_type == 'access' and vehicle.qr_access:
        url = str(vehicle.qr_access)
        vehicle.qr_access.delete()
    elif qr_type == 'fuel' and vehicle.qr_fuel:
        url = str(vehicle.qr_fuel)
        vehicle.qr_fuel.delete()    
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
    domain = request.build_absolute_uri('/')[:-1]  # Obtiene el dominio dinámicamente
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
            <img src="{domain}/staticfiles/assets/images/brand-logos/CS_LOGO.png" alt="Logo">
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
    area__name__in = ['Almacén', 'RRHH'], role__name = "Encargado").first()
    for item in qsUser:
        to_send.append(item.user.email)
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

    # Check if there is an active maintenance alert for the vehicle
    flag_new = Vehicle_Maintenance.objects.filter(vehicle=obj_vehicle, type="preventivo").order_by("-id").first()
    
    if flag_new and flag_new.status == "ALERTA":
        response["status"] = "warning"
        response["message"] = "Aún no se ha agendado la revisión del mantenimiento para este vehículo."
        return JsonResponse(response)
    # Check if the next maintenance kilometer is near
    next_maintenance_km = next_maintenance.first().kilometer
    flag = next_maintenance_km - Decimal(kilometer)
    # print("esta es la resta del mantenimiento")
    if not flag_new and flag <= 300:
        response["status"] = "warning"
        create_maintenance_record(obj_vehicle, kilometer, date_set, next_maintenance_km)
        response["message"] = f"El kilometraje está cerca de alcanzar los {next_maintenance_km} km, se recomienda agendar una revisión."

    if flag_new:
        diferencia = abs(int(next_maintenance_km)-int(flag_new.mileage))
    else:
        diferencia = abs(int(next_maintenance_km)-int(0))
    if flag_new and flag <= 300 and flag_new.status != "ALERTA" and diferencia >= 300:
        response["status"] = "warning"
        # Create a new maintenance record if necessary
        create_maintenance_record(obj_vehicle, kilometer, date_set, next_maintenance_km)
        response["message"] = f"El kilometraje está cerca de alcanzar los {next_maintenance_km} km, se recomienda agendar una revisión."

        sendEmail_UpdateKilometer(request, "Programar Mantenimiento", [settings.EMAIL_HOST_USER], obj_vehicle)
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
        elif tipo_qr == "fuel":
            url_vehicle = vehicle.qr_fuel.url[1:]
        url_s3 = generate_presigned_url(AWS_BUCKET_NAME, str(url_vehicle))
        return JsonResponse({'url_vehicle':url_s3})
    else:
        return JsonResponse({'error': 'Vehicle not found'}, status=404)

def validar_vehicle_en_sa(request):
    dt = request.POST
    id_vehicle = dt.get("id_vehicle", None)
    
    responsiva = Vehicle_Responsive.objects.filter(vehicle_id=id_vehicle).order_by("-id").first() 
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M") 
    vehicle_name = "" 
   
    if id_vehicle:
        try:
            vehicle = Vehicle.objects.get(id=id_vehicle)
            vehicle_name = vehicle.name 
        except Vehicle.DoesNotExist:
            vehicle_name = ""


    if responsiva:  
        if responsiva.end_date: 
            km_final = responsiva.final_mileage
            gasolina_final = responsiva.final_fuel
            return JsonResponse({
                "success": "Todo bien",
                "status": "SALIDA",
                "vehicle_name": vehicle_name, 
                "km_final":km_final,
                "gasolina_final" : gasolina_final,
                "fecha_actual": fecha_actual 
            })
        else:
            registro = responsiva.id
            responsable = responsiva.responsible.id

            responsables = User.objects.all().order_by("first_name").values("id", "first_name")  

            return JsonResponse({
                "success": "Todo bien",
                "status": "ENTRADA",
                "vehicle_name": vehicle_name,
                "id_register": registro,
                "id_responsable": responsable,
                "fecha_actual": fecha_actual, # Agrega la fecha y hora actual
                "responsables": list(responsables)
            })            
    else:
        return JsonResponse({
            "success": "Todo bien",
            "status": "SALIDA",
            "vehicle_name": vehicle_name,
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
                driver_name=Concat(F('name_driver__first_name'), Value(' '), F('name_driver__last_name'))  
            ).values("id", "company", "driver_name", "image_path"))  
        else:
            access = get_module_user_permissions(context, subModule_id)  
            access = access["data"]["access"]
            area = context["area"]["name"]
            company_id = context["company"]["id"]
            editar = access["update"]
            eliminar = access["delete"]
            tipo_user = context["role"]["id"]
            user_id = context["user"]["id"]

            queryset = Vehicle_Driver.objects.select_related('name_driver').annotate(
                driver_name=Concat(F('name_driver__first_name'), Value(' '), F('name_driver__last_name'))
            ).filter(company_id=company_id)

            if tipo_user == 4:
                queryset = queryset.filter(name_driver_id=user_id)

            datos = list(queryset.values("id", "company", "driver_name", "number_phone", "address", "image_path"))


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
        ).distinct().values('id', 'first_name', 'last_name')  
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
        "name": f"{driver.name_driver.first_name} {driver.name_driver.last_name}" if driver.name_driver else "No asignado",
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
                
                driver_name = f"{driver.name_driver.first_name} {driver.name_driver.last_name}" if driver.name_driver else "No asignado",
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
                driver_name = f"{driver.name_driver.first_name} {driver.name_driver.last_name}" if driver.name_driver else "No asignado"

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
        checks = request.POST.getlist("checks[]")  

        # Validate required data
        if not vehicle_id or not audit_date:
            return JsonResponse({"success": False, "error": "Datos incompletos"})

        # Creating the vehicle audit object
        audit = Vehicle_Audit.objects.create(
            vehicle_id=vehicle_id,
            audit_date=audit_date,
            general_notes=general_notes,
            user_created=request.user if request.user.is_authenticated else None

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

        # ---- Enviar correo al responsable del vehículo ----
        if not audit.email_responsible:

            domain = request.build_absolute_uri('/')[:-1]

            link_vehiculo = f"{domain}/vehicles/info/{audit.vehicle.id}/"
            context_email = {
                "company": audit.vehicle.company.name,
                "subject": "Nueva auditoría registrada",
                "modulo": 2,
                "submodulo": "Auditoría",
                "item": audit.vehicle.id,
                "title": f"Se registró una auditoría para {audit.vehicle.name}",
                "body": (
                    f"Se ha registrado una auditoría para el vehículo <strong>{audit.vehicle.name}</strong> "
                    f"con fecha <strong>{audit.audit_date}</strong>.<br>"
                    f"Puedes ver los detalles de la auditoría aquí: <a href='{link_vehiculo}'>Ver auditoría</a>."
                )
            }
            send_notification(context_email)
            audit.email_responsible = True
            audit.save(update_fields=["email_responsible"])

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
            vehicle_id = request.POST.get('vehicle_id', None)

            # Obtener el ID de la auditoría
            audit_id = request.POST.get('audit_id') 

            # Lista para almacenar los resultados de la auditoría
            audit_results = []

            # Diccionario de calificaciones por estado
            calification_map = {
                "Muy malo": 0,
                "Malo": 2,
                "Regular": 4.5,
                "Bueno": 7,
                "Excelente": 9.5
            }

            calification_values = []

            for check in audit_data:
                check_name = check["id"] 
                
                status = check["status"].strip()
                notas = check["notas"]
                sanitized_name = re.sub(r"\s+", "_", check_name)
                file_key = f'imagen_{sanitized_name}'
                imagen = request.FILES.get(file_key, None)


                
                # Buscar el check en la base de datos por nombre y empresa
                check_instance = Checks.objects.filter(name=check_name, company_id=company_id).first()
                S3name = ""

                if check_instance:
                    # Actualizar el estado y las notas del check
                    check_instance.status = status
                    check_instance.notas = notas
                    check_instance.save()

                    # Si hay una imagen, se procesa
                    if imagen:
                        # Crear un nombre único para la imagen
                        folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/audit/{audit_id}/"
                        file_name, extension = os.path.splitext(imagen.name)
                        new_name = f"{check_name}{extension}"  # Nombre único basado en el check
                        S3name = folder_path + new_name

                        try:
                            # Subir la imagen a S3
                            upload_to_s3(imagen, bucket_name, S3name)
                        except Exception as e:
                            print(f"Error al subir la imagen: {str(e)}")
                            S3name = ""  # Si la carga falla, no se guarda la imagen

                    # Formar la estructura corregida con el ID del check
                    audit_results.append({
                        "id": str(check_instance.id),  # Convertir a string si es necesario
                        "name": check_instance.name,
                        "status": status,
                        "notas": notas,
                        "imagen": S3name or "",
                    })
                    # Calificación por estado si aplica
                    if status in calification_map:
                        calification_values.append(calification_map[status])
                    else:
                        print("estado no reconocido:", status)


            # Calcular promedio si hay datos
            calificacion_final = None
            if calification_values:
                calificacion_final = sum(calification_values) / len(calification_values)

            # Buscar la auditoría de vehículo utilizando el ID de la auditoría
            vehicle_audit = Vehicle_Audit.objects.filter(id=audit_id).first()

            if vehicle_audit:
                # Actualizar el campo 'checks' con los resultados de la auditoría
                vehicle_audit.checks = json.dumps(audit_results)
                vehicle_audit.is_checked = True  # Marcar como verificado
                vehicle_audit.calification = round(calificacion_final, 2) if calificacion_final is not None else None
                print("la calificacion de esta auditoria es:", vehicle_audit.calification)
                vehicle_audit.save()

                # Generar resumen de la auditoría para correo
                audit_summary_html = """
                <table style='border-collapse: collapse; width: 100%;'>
                    <thead>
                        <tr>
                            <th style='border: 1px solid #ddd; padding: 8px;'>Check</th>
                            <th style='border: 1px solid #ddd; padding: 8px;'>Estado</th>
                            <th style='border: 1px solid #ddd; padding: 8px;'>Notas</th>
                        </tr>
                    </thead>
                    <tbody>
                """
                for check in audit_results:
                    check_name = check.get("name") 
                    estado = check["status"]
                    notas = check["notas"] or "Sin comentarios"
                    audit_summary_html += f"""
                        <tr>
                            <td style='border: 1px solid #ddd; padding: 8px;'>{check_name}</td>

                            <td style='border: 1px solid #ddd; padding: 8px;'>{estado}</td>
                            <td style='border: 1px solid #ddd; padding: 8px;'>{notas}</td>
                        </tr>
                    """
                audit_summary_html += "</tbody></table>"

                # Determinar calificación final textual
                if calification_values:
                    promedio = sum(calification_values) / len(calification_values)
                    # Buscar estado más cercano según la escala
                    closest_status = min(calification_map.items(), key=lambda x: abs(x[1]-promedio))[0]
                else:
                    closest_status = "Sin calificación"

                calificacion_final_html = f"<p><strong>Calificación final:</strong> {closest_status}</p>"

                # Concatenar resumen con calificación final
                full_audit_html = audit_summary_html + "<br>" + calificacion_final_html

                
                # --- Enviar correos ---
                # Al responsable
                responsable = vehicle_audit.vehicle.responsible
                if responsable and responsable.email and not vehicle_audit.email_evaluated_responsible:
                    vehicle_audit.email_evaluated_responsible = True  
                    vehicle_audit.save(update_fields=["email_evaluated_responsible"])  

                    domain = request.build_absolute_uri('/')[:-1]
                    link_vehiculo = f"{domain}/vehicles/info/{vehicle_audit.vehicle.id}/"

                    context_email = {
                        "to": [responsable.email],
                        "company": vehicle_audit.vehicle.company.name,
                        "subject": "Auditoría evaluada",
                        "modulo": 2,
                        "submodulo": "Auditoría",
                        "item": vehicle_audit.vehicle.id,
                        "title": f"Auditoría evaluada para {vehicle_audit.vehicle.name}",
                        "body": (
                            f"Hola {responsable.get_full_name() or responsable.username},<br><br>"
                            f"La auditoría realizada al vehículo <strong>{vehicle_audit.vehicle.name}</strong> "
                            f"el día <strong>{vehicle_audit.audit_date}</strong> ha sido evaluada. "
                            f"A continuación se muestra el detalle por check:<br><br>"
                            f"{full_audit_html}<br>"
                            f"Puedes ver los detalles completos aquí: <a href='{link_vehiculo}'>Ver auditoría</a>."
                        )
                    }
                    send_notification(context_email)

                # Al usuario que creó la auditoría
                creator = vehicle_audit.user_created
                if creator and creator.email and not vehicle_audit.email_evaluated_creator:
                    vehicle_audit.email_evaluated_creator = True
                    vehicle_audit.save(update_fields=["email_evaluated_creator"])

                    link_vehiculo = f"{domain}/vehicles/info/{vehicle_audit.vehicle.id}/"

                    context_email = {
                        "to": [creator.email], 
                        "company": vehicle_audit.vehicle.company.name,
                        "subject": "Tu auditoría fue evaluada",
                        "modulo": 2,
                        "submodulo": "Auditoría",
                        "item": vehicle_audit.vehicle.id,
                        "title": f"Tu auditoría fue evaluada - {vehicle_audit.vehicle.name}",
                        "body": f"""
                            Hola {creator.get_full_name() or creator.username},<br><br>
                            La auditoría que registraste para el vehículo 
                            <strong>{vehicle_audit.vehicle.name}</strong> 
                            el día <strong>{vehicle_audit.audit_date}</strong> ha sido evaluada. 
                            Detalle por check:<br><br>
                            {full_audit_html}<br>
                            Puedes ver los detalles completos de la auditoría aquí: <a href='{link_vehiculo}'>Ver auditoría</a>.<br><br>
                        """
                    }
                    send_notification(context_email)

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
        

        gasolina = Decimal(dt.get("initial_fuel"))
        if gasolina < 25:
            fecha_actual = date.today()
            context_email = {
                "company": obj_vehicle.company.name,
                "subject": "Nivel de gasolina bajo",
                "modulo": 2,
                "submodulo": "Gasolina",
                "item": obj_vehicle.id,
                "title": f"Se identifico el nivel de gasolina bajo para el vehículo {obj_vehicle.name}",
                "body": (
                    f"Se ha identificado bajo nivel de gasolina para el vehículo <strong>{obj_vehicle.name}</strong> "
                    f"con fecha <strong>{fecha_actual}</strong>.<br>"
                )
            }
            send_notification(context_email)
            
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

            responsable_id_2 = dt.get("responsible_id")
            vehicle_id_2 = dt.get("vehicle_id")

            # print("**************************************************************************************")
            # print(dt.get("responsible_id"))
            # print(responsable_id_2)
            # print("**************************************************************************************")
            # print(dt.get("vehicle_id"))
            # print(vehicle_id_2)
            # print(vehicle_id)
            
            if not dt.get("vehicle_id") or not dt.get("responsible_id"):
                response["status"] = "error"
                response["message"] = "Falta el ID del vehículo o del responsable."
                return JsonResponse(response)


            obj = Vehicle_Responsive(
                vehicle_id=dt.get("vehicle_id"),
                responsible_id=dt.get("responsible_id"),
                initial_mileage=dt.get("initial_mileage"),
                initial_fuel=dt.get("initial_fuel"),
                destination=dt.get("destination"),
                trip_purpose=dt.get("trip_purpose"),
                start_date=dt.get("start_date")
            )
            
            #conditional last register
            item = Vehicle_Responsive.objects.filter(vehicle__id=dt.get("vehicle_id")).order_by("-created_at").first()
            if item:
                if (int(dt.get("initial_mileage")) - int(item.final_mileage)) > 5:
                    #TODO SE CUMPLIO LA CONDICIONAL")
                    obj.initial_mileage = item.final_mileage
                    obj.initial_fuel = item.final_fuel
                    obj.start_date = item.end_date
                    obj.final_mileage = dt.get("initial_mileage")
                    obj.final_fuel = dt.get("initial_fuel")
                    obj.end_date = dt.get("start_date")
                    
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

        if mileage is not None and obj_vehicle.mileage is not None and obj_vehicle.mileage > mileage:
            response["status"] = "warning"
            response["type"] = "kilometraje"
            response["message"] = "El kilometraje ddebe ser mayor. Kilometrakje del vehículo: " + str(obj_vehicle.mileage) + " Kilometraje proporcionado: " + str(mileage)
            return JsonResponse(response)
        
        gasolina = Decimal(dt.get("final_fuel"))
        if gasolina < 25:
            fecha_actual = date.today()
            context_email = {
                "company": obj_vehicle.company.name,
                "subject": "Nivel de gasolina bajo",
                "modulo": 2,
                "submodulo": "Gasolina",
                "item": obj_vehicle.id,
                "title": f"Se identifico el nivel de gasolina bajo para el vehículo {obj_vehicle.name}",
                "body": (
                    f"Se ha identificado bajo nivel de gasolina para el vehículo <strong>{obj_vehicle.name}</strong> "
                    f"con fecha <strong>{fecha_actual}</strong>.<br>"
                )
            }
            send_notification(context_email)
    except Vehicle.DoesNotExist:
        response["status"] = "warning"
        response["message"] = f"No se encontró ningún vehículo con el ID {vehicle_id}"
        return JsonResponse(response)

    # Iniciar transacción
    try:
        with transaction.atomic():
            # print("*********************************error en iphone*********************************")
            # print(dt.get("id"))
            # print(vehicle_id)
        
            id_value = dt.get("id")

            # Validar que id no esté vacío y sea un número
            if not id_value or not id_value.isdigit():
                response["success"] = False
                response["error"] = {"message": "ID inválido o no proporcionado"}
                return JsonResponse(response)

            obj = Vehicle_Responsive.objects.get(id=int(id_value))

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
            #Conditional, Check if the initial-final mileage diff +- 5
            if abs(int(obj.initial_mileage) - int(dt.get("final_mileage"))) <= 5:
                Vehicle_Responsive(
                    vehicle = obj.vehicle,
                    responsible = obj.responsible,
                    initial_mileage = obj.final_mileage,
                    initial_fuel = obj.final_fuel,
                    destination = obj.destination,
                    trip_purpose = obj.trip_purpose,
                    start_date = obj.start_date
                ).save()

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




# Funcion para obtener los nombres de los vehiculos que ya han sido cargados
def get_user_vehicles(request):
    try:
        context = user_data(request)
        company_id = context["company"]["id"]
        user = request.user

        # print("Usuario autenticado:", user)
        # print("ID de la empresa:", company_id)

        if not company_id:
            print("No se encontró empresa asociada al usuario")
            return JsonResponse({'success': False, 'message': 'No se encontró la empresa asociada al usuario'}, status=400)

        # Obtener todos los vehículos de la empresa
        vehicles_fuel = Vehicle.objects.filter(company_id=company_id, is_active=True).values('id', 'name')

        data = list(vehicles_fuel)
        # print("Vehículos encontrados:", data)

        # Obtener el vehículo asignado al usuario como responsable
        assigned_vehicle = Vehicle.objects.filter(responsible=user, company_id=company_id).first()
        if assigned_vehicle:
            # print("Vehículo asignado al usuario:", assigned_vehicle.name, "(ID:", assigned_vehicle.id, ")")
            user_vehicle_id = assigned_vehicle.id
        else:
            # print("No hay vehículo asignado al usuario.")
            user_vehicle_id = None

        return JsonResponse({'data': data, 'user_vehicle_id': user_vehicle_id})

    except Exception as e:
        print("Error en get_user_vehicles:", str(e))
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


def get_user_vehicles_for_edit(request):
    try:
        context = user_data(request)
        company_id = context["company"]["id"]
        vehicle_id = request.GET.get("vehicle_id")
        vehicles = Vehicle.objects.filter(company_id=company_id, is_active=True)

        if vehicle_id:
            vehicles = vehicles | Vehicle.objects.filter(id=vehicle_id)

        data = vehicles.distinct().values("id", "name").order_by("name")

        return JsonResponse({"data": list(data)})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)



def check_qr_fuel(request, vehicle_id):
    # print("entramos a la funcion check_qr_fuel")
    try:
        vehicle = get_object_or_404(Vehicle, id=vehicle_id)
        # print("Vehículo encontrado:", vehicle.name)
        # print("ID del vehículo:", vehicle.id)
        if vehicle.qr_fuel:
            qr_url_fuel = generate_presigned_url(AWS_BUCKET_NAME, str(vehicle.qr_fuel))
            return JsonResponse({'status': 'success', 'qr_url_fuel': qr_url_fuel})
        else:
            return JsonResponse({'status': 'error', 'message': 'QR no generado'})
    except Vehicle.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'vehiculo no encontrado'}, status=404)

@login_required
def qr_vehicle_fuel_form(request):
    context = user_data(request)
    
    vehicle_id = request.GET.get("vehicle_id", None)

    if not vehicle_id:
        return JsonResponse({"success": False, "message": "Vehicle ID is required"}, status=400)

    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    context["vehicle"] = vehicle
    context["today"] = date.today().isoformat()
    context["fuel_type"] = vehicle.fuel_type_vehicle  

    return render(request, "vehicles/fuel_form_qr.html", context)


# @login_required
# def vehicles_placas(request, vehicle_id = None):
#     context = user_data(request)
#     context["vehicle"] = {"id": vehicle_id}
#     if vehicle_id is not None:
#         context["vehicle_name"] = Vehicle.objects.get(id = vehicle_id).name
#     module_id = 2
#     subModule_id = 37
#     request.session["last_module_id"] = module_id

#     if not check_user_access_to_module(request, module_id, subModule_id):
#         return render(request, "error/access_denied.html")
    
#     access = get_module_user_permissions(context, subModule_id)
#     permisos = get_user_access(context)
#     sidebar = get_sidebar(context, [1, module_id])
    
#     context["access"] = access["data"]["access"]
#     context["permiso"] = permisos["data"]
#     context["sidebar"] = sidebar["data"]

#     if context["access"]["read"]:
#         template = "vehicles/vehicle_placas.html"
#     else:
#         template = "error/access_denied.html"

#     return render(request, template, context)


# Vista para obtener los  registros de vehiculos
@login_required
def get_vehicles(request):
    try:
        context = user_data(request)
        company_id = context["company"]["id"]  

        if not company_id:
            return JsonResponse({'success': False, 'message': 'No se encontró la empresa asociada al usuario'}, status=400)
    # Obtener los registros
        vehiculos = Vehicle.objects.filter(
            company_id=company_id
        ).values('id', 'name') 
        data = list(vehiculos)
        # print("esta es la lista de vehiculos de la empresa:", vehiculos)
        return JsonResponse({'data': data}, safe=False)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

#tabla de placas
def table_placa_vehicle(request):
    response = {"success": False}
    context = user_data(request)
    subModule_id = 37
    access = get_module_user_permissions(context, subModule_id)["data"]["access"]

    vehicle_id = request.GET.get('vehicle_id')
    if not vehicle_id:
        print("No se proporcionó vehicle_id")
        return JsonResponse({"data": []})

    datos = Placas.objects.select_related("vehiculo").filter(
        vehiculo_id=vehicle_id
    ).values(
        "id",
        "plate", 
        "type_plate", 
        "vehiculo__name",  
        "fecha_emision",
        "fecha_vencimiento",
        "entidad_emisora",
        "comments",
        "document_placa",
        "status"
    )

    data_list = []
    for item in datos:
        row = {
            "id": item["id"],
            "plate": item["plate"],
            "type_plate": item["type_plate"],
            "vehiculo": item.get("vehiculo__name", ""),
            "fecha_emision": item["fecha_emision"],
            "fecha_vencimiento": item["fecha_vencimiento"],
            "entidad_emisora": item["entidad_emisora"],
            "comments": item["comments"],
            "btn_view": "",
            "btn_action": "",
            "status": item["status"]
        }

        # Botón Ver Documento
        if item["document_placa"]:
            tempDoc = generate_presigned_url(bucket_name, item["document_placa"])
            row["btn_view"] = f"""<a href="{tempDoc}" class="btn btn-sm btn-info" target="_blank">
                <i class="fa-solid fa-file"></i> Placa 
            </a>\n"""

        # Botón Editar
        if access.get("update"):
            row["btn_action"] += f"""<button class="btn btn-primary btn-sm" data-vehicle-placa="update-placa" 
                data-id="{item['id']}">
                <i class="fa-solid fa-pen"></i>
            </button>\n"""

        # Botón Eliminar
        if access.get("delete"):
            row["btn_action"] += """<button class="btn btn-danger btn-sm" data-vehicle-placa="delete-placa">
                <i class="fa-solid fa-trash"></i>
            </button>"""

        data_list.append(row)

    response.update({"data": data_list, "status": "success", "success": True})
    return JsonResponse(response)

# #tabla de placas
# def table_placa_vehicles(request):
#     response = {"success": False}
#     context = user_data(request)
#     subModule_id = 37
#     company_id = context["company"]["id"]

#     access = get_module_user_permissions(context, subModule_id)["data"]["access"]

#     # Obtener solo las placas cuyos vehículos pertenezcan a la empresa
#     datos = Placas.objects.select_related("vehiculo").filter(
#         vehiculo__company_id=company_id  
#     ).values(
#         "id",
#         "plate", 
#         "type_plate", 
#         "vehiculo__name",  
#         "fecha_emision",
#         "fecha_vencimiento",
#         "entidad_emisora",
#         "comments",
#         "document_placa",
#         "status"
#     )

#     data_list = []
#     for item in datos:
#         row = {
#             "id": item["id"],
#             "plate": item["plate"],
#             "type_plate": item["type_plate"],
#             "vehiculo": item.get("vehiculo__name", ""),
#             "fecha_emision": item["fecha_emision"],
#             "fecha_vencimiento": item["fecha_vencimiento"],
#             "entidad_emisora": item["entidad_emisora"],
#             "comments": item["comments"],
#             "btn_view": "",
#             "btn_action": "",
#             "status": item["status"]
#         }

#         if item["document_placa"]:
#             tempDoc = generate_presigned_url(bucket_name, item["document_placa"])
#             row["btn_view"] = f"""<a href="{tempDoc}" class="btn btn-sm btn-info" target="_blank">
#                 <i class="fa-solid fa-file"></i> Placa 
#             </a>\n"""
#         if access["update"]:
#             row["btn_action"] += f"""<button class="btn btn-primary btn-sm" data-vehicle-placa="update-placa" 
#                 data-id="{item['id']}">
#                 <i class="fa-solid fa-pen"></i>
#             </button>\n"""

#         if access["delete"]:
#             row["btn_action"] += """<button class="btn btn-danger btn-sm" data-vehicle-placa="delete-placa">
#                 <i class="fa-solid fa-trash"></i>
#             </button>"""

#         data_list.append(row)

#     response.update({"data": data_list, "status": "success", "success": True})
#     return JsonResponse(response)

@login_required
def get_vehicles_placa(request):
    try:
        context = user_data(request)
        company_id = context["company"]["id"]  

        if not company_id:
            return JsonResponse({'success': False, 'message': 'No se encontró la empresa asociada al usuario'}, status=400)
    # Obtener los registros
        vehiculos = Vehicle.objects.filter(
            company_id=company_id
        ).values('id', 'name') 
        data = list(vehiculos)
        # print("esta es la lista de vehiculos de la empresa para tarjetas:", vehiculos)
        return JsonResponse({'data': data}, safe=False)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)



#función para agregar PLACA
def add_placa(request):
    context = user_data(request)
    dt = request.POST
    company_id = context["company"]["id"]

    if request.method == 'POST':
        try:
            plate = request.POST.get('placa_vehicle', '').strip()
            type_plate = request.POST.get('plate_type', '').strip()
            vehiculo_id = request.POST.get('fuel_vehicle_id')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            entidad_emisora = request.POST.get('entity_plate', '').strip()
            comments = request.POST.get('comments', '').strip()
            document_placa = request.FILES.get('document_placa') 

            if not plate or not start_date or not end_date:
                return JsonResponse({'success': False, 'message': 'Los campos Placa, Fecha de emisión y Fecha de vencimiento son obligatorios.'})

            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()

            if end_date_obj <= start_date_obj:
                return JsonResponse({'success': False, 'message': 'La fecha de vencimiento debe ser posterior a la fecha de emisión.'})

            vehiculo = None
            if vehiculo_id:
                vehiculo = Vehicle.objects.get(id=int(vehiculo_id))

                placa_existente = Placas.objects.filter(
                    plate__iexact=plate,
                    vehiculo=vehiculo
                ).exists()

                if placa_existente:
                    return JsonResponse({'success': False, 'message': 'Ya existe una placa registrada con ese número para este vehículo.'})

            nueva_placa = Placas.objects.create(
                plate=plate,
                type_plate=type_plate,
                vehiculo=vehiculo,
                fecha_emision=start_date_obj,
                fecha_vencimiento=end_date_obj,
                entidad_emisora=entidad_emisora,
                comments=comments,
                status="nuevo" 
            )

            if document_placa:
                s3Path = f'docs/{company_id}/vehicle/placas/{nueva_placa.id}/'
                file_name, extension = os.path.splitext(document_placa.name)
                new_name = f"placa_{nueva_placa.id}{extension}"
                S3name = s3Path + new_name

                upload_to_s3(document_placa, bucket_name, S3name)

                nueva_placa.document_placa = S3name
                nueva_placa.save()


            return JsonResponse({'success': True, 'message': 'Placa registrada correctamente.'})

        except Vehicle.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'El vehículo seleccionado no existe.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error inesperado: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Método de solicitud no válido.'})


@csrf_exempt  
def update_status_placa(request):
    if request.method == 'POST':
        # Obtener los datos enviados
        placa_id = request.POST.get('id')
        new_status = request.POST.get('status')

        try:
            # Obtener el mantenimiento
            placa = Placas.objects.get(id=placa_id)
            
            # Verificar si la fecha ya pasó y si el estado no es "vencido"
            current_date = timezone.now().date()
            placa_date = placa.fecha_vencimiento
            if placa_date < current_date and placa.status not in ["Vigente", "Vencido"]:
                new_status = "Vencido" 
            
            # Actualizar el estado
            placa.status = new_status
            placa.save()

            # Responder con éxito
            return JsonResponse({'status': 'success', 'message': 'Estado actualizado correctamente.'})

        except Placas.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Placa no encontrado.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido.'})


#funcion para eliminar placa
@login_required
@csrf_exempt
def delete_placa(request):                          
    if request.method == 'POST':
        form = request.POST
        _id = form.get('id')

        if not _id:
            return JsonResponse({'success': False, 'message': 'No ID provided'})

        try:
            placa = Placas.objects.get(id=_id)
        except Placas.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Category not found'})

        placa.delete()

        return JsonResponse({'success': True, 'message': 'Placa eliminada correctamente!'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

#Función para editar la información 
@login_required
@csrf_exempt
def edit_placa(request):
    # print("entramos a la funcion edit_placa")
    context = user_data(request)
    subModule_id = 37
    company_id = context["company"]["id"]

    if request.method == 'GET':
        placa_id = request.GET.get('id')
        # print("placa encontrada:", placa_id)

        try:
            placa = Placas.objects.get(id=placa_id)
            data = {
                "id": placa.id,
                "plate": placa.plate,
                "type_plate": placa.type_plate,
                "vehiculo_id": placa.vehiculo_id,
                "fecha_emision": placa.fecha_emision,
                "fecha_vencimiento": placa.fecha_vencimiento,
                "entidad_emisora": placa.entidad_emisora,
                "comments": placa.comments,
                "document_url": placa.document_placa.url if placa.document_placa else ""

            }
            return JsonResponse({"status": "success", "data": data})
        except Placas.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Placa no encontrada"})
    
    if request.method == 'POST':
        _id = request.POST.get('id')
        plate = request.POST.get('placa_vehicle')
        type_plate = request.POST.get('plate_type')
        vehiculo_id = request.POST.get('fuel_vehicle_id')
        fecha_emision = request.POST.get('start_date')
        fecha_vencimiento = request.POST.get('end_date')
        entidad_emisora = request.POST.get('entity_plate')
        comments = request.POST.get('comments')
        document = request.FILES.get('document_placa')

        if not plate or not fecha_emision or not fecha_vencimiento:
            return JsonResponse({'success': False, 'message': 'Campos obligatorios faltantes.'})
        
        try:
            placa = Placas.objects.get(id=_id)
            placa.plate = plate
            placa.type_plate = type_plate
            placa.vehiculo_id = vehiculo_id
            placa.fecha_emision = fecha_emision
            placa.fecha_vencimiento = fecha_vencimiento
            placa.entidad_emisora = entidad_emisora
            placa.comments = comments

            if document:
                # Reemplazar archivo anterior si existe
                if placa.document_placa:
                    delete_s3_object(AWS_BUCKET_NAME, str(placa.document_placa.url[1:]))
                file_name, extension = os.path.splitext(document.name)
                new_file_name = f"placa_{plate}{extension}"
                s3Path = f'docs/{company_id}/vehicle/placa/{plate}/'
                S3name = s3Path + new_file_name
                upload_to_s3(document, AWS_BUCKET_NAME, S3name)
                placa.document_placa = S3name

            placa.save()
            return JsonResponse({'success': True, 'message': 'Placa actualizada correctamente'})
        
        except Placas.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Placa no encontrada'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error interno: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'message': 'Método de solicitud inválido'})

# FACTURAS--------------- [ START ] ----------
#tabla de facturas por vehiculo
def table_factura_vehicle(request):
    response = {"success": False}
    context = user_data(request)
    subModule_id = 37
    access = get_module_user_permissions(context, subModule_id)["data"]["access"]

    vehicle_id = request.GET.get('vehicle_id')
    # print("entramos a la funcion de mostrar la tabla de las faturas del vehiculo:", vehicle_id)

    if not vehicle_id:
        return JsonResponse({"data": []})

    datos = Facturas_Vehicle.objects.select_related("vehiculo", "name_user").filter(
        vehiculo_id=vehicle_id
    )

    data_list = []
    
    for item in datos:
        # Construir fila
        row = {
            "id": item.id,
            "number": item.number,
            "fecha_vencimiento": item.fecha_vencimiento.strftime('%Y-%m-%d'),
            "vehiculo": item.vehiculo.name if item.vehiculo else "",
            #"name_user": f"{item.name_user.first_name} {item.name_user.last_name}" if item.name_user else "",
            #"comments": item.comments or "",
            "status": item.status or "",
            "btn_view": "",
            "btn_action": "",
        }

        # Botón Ver Documento
        if item.document_factura:
            tempDoc = generate_presigned_url(bucket_name, item.document_factura.name)
            row["btn_view"] = f"""<a href="{tempDoc}" class="btn btn-sm btn-info" target="_blank">
                <i class="fa-solid fa-file"></i> Ver 
            </a>"""

        # Botón Editar
        if access.get("update"):
            row["btn_action"] += f"""<button class="btn btn-primary btn-sm" data-vehicle-factura="update-factura" 
                data-id="{item.id}">
                <i class="fa-solid fa-pen"></i>
            </button>\n"""

        # Botón Eliminar
        if access.get("delete"):
            row["btn_action"] += """<button class="btn btn-danger btn-sm" data-vehicle-factura="delete-factura">
                <i class="fa-solid fa-trash"></i>
            </button>"""

        data_list.append(row)

    response.update({"data": data_list, "status": "success", "success": True})
    return JsonResponse(response)

#función para agregar factura
def add_factura(request):
    context = user_data(request)
    company_id = context["company"]["id"]

    if request.method == 'POST':
        try:
            number = request.POST.get('number', '').strip()
            status = request.POST.get('status', '').strip()
            vehiculo_id = request.POST.get('vehiculo')
            #name_user_id = request.POST.get('name_user')
            fecha_vencimiento = request.POST.get('fecha_vencimiento')
            #commsssents = request.POST.get('comments', '').strip()
            document_factura = request.FILES.get('document_factura')

            # Validaciones básicas
            if not number or not status or not vehiculo_id or not fecha_vencimiento:
                return JsonResponse({'success': False, 'message': 'Los campos Número, Estado, Vehículo y Fecha de emisión son obligatorios.'})

            vehiculo = Vehicle.objects.get(id=int(vehiculo_id)) if vehiculo_id else None

            # Verificar duplicado
            if Facturas_Vehicle.objects.filter(number__iexact=number, vehiculo=vehiculo).exists():
                return JsonResponse({'success': False, 'message': 'Ya existe una factura registrada con ese número para este vehículo.'})

            # Crear instancia
            nueva_factura = Facturas_Vehicle.objects.create(
                vehiculo=vehiculo,
                #name_user=name_user,
                fecha_vencimiento=fecha_vencimiento,
                number=number,
                status=status,
                #comments=comments
            )

            # Subir archivo si existe
            if document_factura:
                s3Path = f'docs/{company_id}/vehicle/facturas/{nueva_factura.id}/'
                file_name, extension = os.path.splitext(document_factura.name)
                new_name = f"factura_{nueva_factura.id}{extension}"
                S3name = s3Path + new_name

                upload_to_s3(document_factura, bucket_name, S3name)

                nueva_factura.document_factura = S3name
                nueva_factura.save()

            return JsonResponse({'success': True, 'message': 'Factura registrada correctamente.'})

        except Vehicle.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'El vehículo seleccionado no existe.'})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'El usuario seleccionado no existe.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error inesperado: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Método de solicitud no válido.'})

# editar factura
#Función para editar la información 
@login_required
@csrf_exempt
def edit_factura(request):
    context = user_data(request)
    company_id = context["company"]["id"]

    if request.method == 'GET':
        factura_id = request.GET.get('id')
        try:
            factura = Facturas_Vehicle.objects.get(id=factura_id)
            data = {
                "id": factura.id,
                "number": factura.number,
                "status": factura.status,
                "vehiculo_id": factura.vehiculo.id if factura.vehiculo else None,
                #"name_user_id": factura.name_user.id if factura.name_user else None,
                "fecha_vencimiento": factura.fecha_vencimiento.strftime('%Y-%m-%d'),
                #"comments": factura.comments,
                "document_url": factura.document_factura.url if factura.document_factura else ""
            }
            return JsonResponse({"status": "success", "data": data})
        except Facturas_Vehicle.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Factura no encontrada"})

    if request.method == 'POST':
        try:
            _id = request.POST.get('id')
            number = request.POST.get('number', '').strip()
            status = request.POST.get('status', '').strip()
            vehiculo_id = request.POST.get('vehiculo')
            #name_user_id = request.POST.get('name_user')
            fecha_vencimiento = request.POST.get('fecha_vencimiento')
            #comments = request.POST.get('comments', '').strip()
            document_factura = request.FILES.get('document_factura')

            if not number or not status or not vehiculo_id or not fecha_vencimiento:
                return JsonResponse({'success': False, 'message': 'Campos obligatorios faltantes.'})

            factura = Facturas_Vehicle.objects.get(id=_id)
            factura.number = number
            factura.status = status
            factura.vehiculo = Vehicle.objects.get(id=int(vehiculo_id)) if vehiculo_id else None
            #factura.name_user = User.objects.get(id=int(name_user_id)) if name_user_id else None
            factura.fecha_vencimiento = fecha_vencimiento
            #factura.comments = comments

            if document_factura:
                if factura.document_factura:
                    delete_s3_object(AWS_BUCKET_NAME, str(factura.document_factura.name))
                file_name, extension = os.path.splitext(document_factura.name)
                new_name = f"factura_{factura.id}{extension}"
                s3_path = f'docs/{company_id}/vehicle/facturas/{factura.id}/{new_name}'
                upload_to_s3(document_factura, AWS_BUCKET_NAME, s3_path)
                factura.document_factura = s3_path

            factura.save()
            return JsonResponse({'success': True, 'message': 'Factura actualizada correctamente.'})
        
        except Facturas_Vehicle.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Factura no encontrada.'})
        except Vehicle.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Vehículo no válido.'})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Usuario no válido.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error interno: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Método de solicitud inválido.'})

#funcion para eliminar factura
@login_required
@csrf_exempt
def delete_factura(request):                          
    if request.method == 'POST':
        form = request.POST
        _id = form.get('id')

        if not _id:
            return JsonResponse({'success': False, 'message': 'No ID provided'})

        try:
            factura = Facturas_Vehicle.objects.get(id=_id)
        except Facturas_Vehicle.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Category not found'})

        factura.delete()

        return JsonResponse({'success': True, 'message': 'Factura eliminada correctamente!'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})


# TARJETAS DE VEHICULOS 
@login_required
def get_vehicles_card(request):
    try:
        context = user_data(request)
        company_id = context["company"]["id"]  

        if not company_id:
            return JsonResponse({'success': False, 'message': 'No se encontró la empresa asociada al usuario'}, status=400)
    # Obtener los registros
        vehiculos = Vehicle.objects.filter(
            company_id=company_id
        ).values('id', 'name') 
        data = list(vehiculos)
        # print("esta es la lista de vehiculos de la empresa para tarjetas:", vehiculos)
        return JsonResponse({'data': data}, safe=False)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)



def add_card(request):
    context = user_data(request)
    company_id = context["company"]["id"]

    if request.method == 'POST':
        try:
            number_card = request.POST.get('number_card', '').strip()
            vehiculo_id = request.POST.get('vehiculo_card')
            type_card = request.POST.get('type_card', '').strip()
            name_user_id = request.POST.get('name_user')
            fecha_vencimiento = request.POST.get('fecha_vencimiento')
            document_card = request.FILES.get('document_card')

            if not number_card or not vehiculo_id or not fecha_vencimiento or not type_card:
                return JsonResponse({
                    'success': False,
                    'message': 'Número de tarjeta, tipo, vehículo y fecha de vencimiento son obligatorios.'
                })

            # Validar fecha
            try:
                fecha_obj = datetime.strptime(fecha_vencimiento, "%Y-%m-%d").date()
            except ValueError:
                return JsonResponse({'success': False, 'message': 'Formato de fecha inválido.'})

            if fecha_obj <= datetime.today().date():
                return JsonResponse({'success': False, 'message': 'La fecha de vencimiento debe ser posterior a hoy.'})

            # Determinar el estado en base a la fecha
            estado = "Vigente" if fecha_obj > datetime.today().date() else "Vencida"

            try:
                vehiculo = Vehicle.objects.get(id=int(vehiculo_id))
            except Vehicle.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'El vehículo seleccionado no existe.'})

            name_user = None
            if name_user_id:
                try:
                    name_user = User.objects.get(id=int(name_user_id))
                except User.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'El usuario seleccionado no existe.'})

            if Card_Vehicle.objects.filter(number_card__iexact=number_card, vehiculo=vehiculo).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Ya existe una tarjeta registrada con ese número para este vehículo.'
                })

            # Crear nueva tarjeta
            nueva_tarjeta = Card_Vehicle.objects.create(
                vehiculo=vehiculo,
                name_user=name_user,
                fecha_vencimiento=fecha_obj,
                number_card=number_card,
                type_card=type_card,
                status=estado
            )

            if document_card:
                s3Path = f'docs/{company_id}/vehicle/tarjetas/{nueva_tarjeta.id}/'
                file_name, extension = os.path.splitext(document_card.name)
                new_name = f"tarjeta_{nueva_tarjeta.id}{extension}"
                S3name = s3Path + new_name

                try:
                    upload_to_s3(document_card, bucket_name, S3name)
                except Exception as e:
                    return JsonResponse({'success': False, 'message': f'Error al subir el archivo: {str(e)}'})

                nueva_tarjeta.document_card = S3name
                nueva_tarjeta.save()

            return JsonResponse({'success': True, 'message': 'Tarjeta registrada correctamente.'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error inesperado: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Método de solicitud no válido.'})



def table_card_vehicle(request):
    response = {"success": False}
    context = user_data(request)
    subModule_id = 37
    access = get_module_user_permissions(context, subModule_id)["data"]["access"]

    vehicle_id = request.GET.get('vehicle_id')
    # print("Entramos a la función de mostrar la tabla de tarjetas del vehículo:", vehicle_id)

    if not vehicle_id:
        return JsonResponse({"data": []})

    datos = Card_Vehicle.objects.select_related("vehiculo", "name_user").filter(
        vehiculo_id=vehicle_id
    )

    data_list = []

    for item in datos:

        status = ""
        if item.fecha_vencimiento:
            hoy = date.today()
            if item.fecha_vencimiento < hoy:
                status = "Vencida"
            elif item.fecha_vencimiento <= hoy + timedelta(days=30):
                status = "Por vencer"
            else:
                status = "Vigente"

        row = {
            "id": item.id,
            "number_card": item.number_card,
            "vehiculo": item.vehiculo.name if item.vehiculo else "",
            "type_card": item.type_card or "",
            "fecha_vencimiento": item.fecha_vencimiento.strftime('%Y-%m-%d') if item.fecha_vencimiento else "",
            "name_user": f"{item.name_user.first_name} {item.name_user.last_name}" if item.name_user else "",
            "status": status, 
            "btn_view": "",
            "btn_action": "",
        }

        # Botón Ver Documento
        if item.document_card:
            tempDoc = generate_presigned_url(bucket_name, item.document_card.name)
            row["btn_view"] = f"""<a href="{tempDoc}" class="btn btn-sm btn-info" target="_blank">
                <i class="fa-solid fa-file"></i> Ver 
            </a>"""

        # Botón Editar
        if access.get("update"):
            row["btn_action"] += f"""<button class="btn btn-primary btn-sm" data-vehicle-card="update-card" 
                data-id="{item.id}">
                <i class="fa-solid fa-pen"></i>
            </button>\n"""

        # Botón Eliminar
        if access.get("delete"):
            row["btn_action"] += f"""<button class="btn btn-danger btn-sm" data-vehicle-card="delete-card" data-id="{item.id}">
                <i class="fa-solid fa-trash"></i>
            </button>"""

        data_list.append(row)

    response.update({"data": data_list, "status": "success", "success": True})
    return JsonResponse(response)


# editar tarjeta
def edit_card(request):
    context = user_data(request)
    company_id = context["company"]["id"]

    if request.method == 'GET':
        card_id = request.GET.get('id')
        try:
            card = Card_Vehicle.objects.get(id=card_id)
            data = {
                "id": card.id,
                "number_card": card.number_card,
                "status": card.status,
                "type_card": card.type_card,
                "vehiculo_id": card.vehiculo.id if card.vehiculo else None,
                "name_user_id": card.name_user.id if card.name_user else None,
                "fecha_vencimiento": card.fecha_vencimiento.strftime('%Y-%m-%d'),
                "document_url": card.document_card.url if card.document_card else ""
            }
            return JsonResponse({"status": "success", "data": data})
        except Card_Vehicle.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Tarjeta no encontrada"})

    if request.method == 'POST':
        try:
            card_id = request.POST.get('id')
            if not card_id:
                return JsonResponse({'success': False, 'message': 'ID de tarjeta no proporcionado.'})

            card = Card_Vehicle.objects.get(id=card_id)

            # Obtener nuevos valores o mantener los actuales
            number_card = request.POST.get('number_card', card.number_card).strip()
            type_card = request.POST.get('type_card', card.type_card)
            vehiculo_id = request.POST.get('vehiculo') or (card.vehiculo.id if card.vehiculo else None)
            name_user_id = request.POST.get('name_user') or (card.name_user.id if card.name_user else None)
            fecha_vencimiento = request.POST.get('fecha_vencimiento') or card.fecha_vencimiento.strftime('%Y-%m-%d')
            document_card = request.FILES.get('document_card')

            # Validación mínima
            if not number_card or not vehiculo_id or not fecha_vencimiento:
                return JsonResponse({'success': False, 'message': 'Faltan campos clave.'})

            # Validar fecha
            try:
                fecha_obj = datetime.strptime(fecha_vencimiento, "%Y-%m-%d").date()
            except ValueError:
                return JsonResponse({'success': False, 'message': 'Formato de fecha inválido.'})

            estado = "Vigente" if fecha_obj > datetime.today().date() else "Vencida"

            # Validar que no se repita el número de tarjeta para el mismo vehículo
            if Card_Vehicle.objects.exclude(id=card.id).filter(
                number_card__iexact=number_card,
                vehiculo_id=vehiculo_id
            ).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Ya existe una tarjeta con ese número para este vehículo.'
                })

            # Actualizar valores
            card.number_card = number_card
            card.type_card = type_card
            card.fecha_vencimiento = fecha_obj
            card.status = estado

            try:
                card.vehiculo = Vehicle.objects.get(id=int(vehiculo_id))
            except Vehicle.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Vehículo no válido.'})

            try:
                card.name_user = User.objects.get(id=int(name_user_id)) if name_user_id else None
            except User.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Usuario no válido.'})

            # Si viene un nuevo archivo, reemplazar el anterior
            if document_card:
                if card.document_card:
                    delete_s3_object(AWS_BUCKET_NAME, str(card.document_card.name))

                file_name, extension = os.path.splitext(document_card.name)
                new_name = f"tarjeta_{card.id}{extension}"
                s3_path = f'docs/{company_id}/vehicle/tarjetas/{card.id}/{new_name}'

                try:
                    upload_to_s3(document_card, AWS_BUCKET_NAME, s3_path)
                    card.document_card = s3_path
                except Exception as e:
                    return JsonResponse({'success': False, 'message': f'Error al subir archivo: {str(e)}'})

            card.save()
            return JsonResponse({'success': True, 'message': 'Tarjeta actualizada correctamente.'})

        except Card_Vehicle.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Tarjeta no encontrada.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error interno: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Método de solicitud inválido.'})



#funcion para eliminar tarjeta
@login_required
@csrf_exempt
def delete_card(request):                          
    if request.method == 'POST':
        form = request.POST
        _id = form.get('id')

        if not _id:
            return JsonResponse({'success': False, 'message': 'No ID provided'})

        try:
            tarjeta = Card_Vehicle.objects.get(id=_id)
        except Card_Vehicle.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'tarjeta not found'})

        tarjeta.delete()

        return JsonResponse({'success': True, 'message': 'Tarjeta eliminada correctamente!'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

#CONTRATO DE VEHICULOS
@login_required
def get_vehicles_contract(request):
    try:
        context = user_data(request)
        company_id = context["company"]["id"]  

        if not company_id:
            return JsonResponse({'success': False, 'message': 'No se encontró la empresa asociada al usuario'}, status=400)
    # Obtener los registros
        vehiculos = Vehicle.objects.filter(
            company_id=company_id
        ).values('id', 'name') 
        data = list(vehiculos)
        # print("esta es la lista de vehiculos de la empresa para tarjetas:", vehiculos)
        return JsonResponse({'data': data}, safe=False)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

# tabla de contrato
def table_contract_vehicle(request):
    response = {"success": False}
    context = user_data(request)
    subModule_id = 37
    access = get_module_user_permissions(context, subModule_id)["data"]["access"]

    vehicle_id = request.GET.get('vehicle_id')
    # print("Entramos a la función de mostrar la tabla de contrato del vehículo:", vehicle_id)

    if not vehicle_id:
        return JsonResponse({"data": []})

    datos = Contract_Vehicle.objects.select_related("vehiculo").filter(
        vehiculo_id=vehicle_id
    )

    data_list = []

    for item in datos:

        row = {
            "id": item.id,
            "vehiculo": item.vehiculo.name if item.vehiculo else "",
            "type_contract": item.type_contract or "",
            "fecha_contract": item.fecha_contract.strftime('%Y-%m-%d') if item.fecha_contract else "",
            "fecha_finiquito": item.fecha_finiquito.strftime('%Y-%m-%d') if item.fecha_finiquito else "",
            "status_modified": not item.is_canceled and item.status_modified,
            "is_canceled": item.is_canceled,
            "btn_status_action": "" if item.status_modified or item.is_canceled else f"""
                <div class="d-flex justify-content-start gap-2">
                    <button class="btn btn-outline-success btn-sm" title="Aceptar" 
                            data-vehicle-contract="accept" data-id="{item.id}">
                        <i class="fa-solid fa-check"></i>
                    </button>
                    <button class="btn btn-outline-danger btn-sm" title="Cancelar" 
                            data-vehicle-contract="cancel" data-id="{item.id}">
                        <i class="fa-solid fa-xmark"></i>
                    </button>
                </div>
            """,


            "btn_view_contract": "",
            "btn_view_letter": "",
            "btn_action": "",
        }

        # Botón Ver Documento
        if item.document_contract:
            tempDoc = generate_presigned_url(bucket_name, item.document_contract.name)
            row["btn_view_contract"] = f"""<a href="{tempDoc}" class="btn btn-sm btn-info" target="_blank">
                <i class="fa-solid fa-file"></i> Ver 
            </a>"""

        if item.document_letter:
            tempDoc = generate_presigned_url(bucket_name, item.document_letter.name)
            row["btn_view_letter"] = f"""<a href="{tempDoc}" class="btn btn-sm btn-info" target="_blank">
                <i class="fa-solid fa-file"></i> Ver 
            </a>"""

        # Botón Editar
        if access.get("update"):
            row["btn_action"] += f"""<button class="btn btn-primary btn-sm" data-vehicle-contract="update-contract" 
                data-id="{item.id}">
                <i class="fa-solid fa-pen"></i>
            </button>\n"""

        # Botón Eliminar
        if access.get("delete"):
            row["btn_action"] += f"""<button class="btn btn-danger btn-sm" data-vehicle-contract="delete-contract" data-id="{item.id}">
                <i class="fa-solid fa-trash"></i>
            </button>"""

        data_list.append(row)

    response.update({"data": data_list, "status": "success", "success": True})
    return JsonResponse(response)

# agregar contrato
def add_contract(request):
    context = user_data(request)
    company_id = context["company"]["id"]

    if request.method == 'POST':
        try:
            vehiculo_id = request.POST.get('vehiculo_contract')
            type_contract = request.POST.get('type_contract', '').strip()
            fecha_contract = request.POST.get('fecha_contract')
            fecha_finiquito = request.POST.get('fecha_finiquito')
            document_contract = request.FILES.get('document_contract')

            # Validaciones básicas
            if not vehiculo_id or not fecha_contract or not type_contract:
                return JsonResponse({
                    'success': False,
                    'message': 'Tipo de contrato, vehículo y fecha de contrato son obligatorios.'
                })

            vehiculo = Vehicle.objects.get(id=int(vehiculo_id))

            # Convertir fechas
            try:
                fecha_contract_obj = datetime.strptime(fecha_contract, "%Y-%m-%d").date()
                fecha_finiquito_obj = datetime.strptime(fecha_finiquito, "%Y-%m-%d").date()
            except ValueError:
                return JsonResponse({'success': False, 'message': 'Formato de fecha inválido.'})

            if fecha_finiquito_obj <= fecha_contract_obj:
                return JsonResponse({
                    'success': False,
                    'message': 'La fecha de finiquito debe ser posterior a la fecha de contrato.'
                })

            # Validar que no se repita la fecha de contrato para ese vehículo
            if Contract_Vehicle.objects.filter(fecha_contract=fecha_contract_obj, vehiculo=vehiculo).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Ya existe un contrato registrado en esa fecha para este vehículo.'
                })

            # Crear contrato
            nuevo_contrato = Contract_Vehicle.objects.create(
                vehiculo=vehiculo,
                type_contract=type_contract,
                fecha_contract=fecha_contract_obj,
                fecha_finiquito=fecha_finiquito_obj,
            )

            # Subir archivo si existe
            if document_contract:
                s3Path = f'docs/{company_id}/vehicle/contratos/{nuevo_contrato.id}/'
                file_name, extension = os.path.splitext(document_contract.name)
                new_name = f"contrato_{nuevo_contrato.id}{extension}"
                S3name = s3Path + new_name

                upload_to_s3(document_contract, bucket_name, S3name)

                nuevo_contrato.document_contract = S3name
                nuevo_contrato.save()

            return JsonResponse({'success': True, 'message': 'Contrato registrado correctamente.'})

        except Vehicle.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'El vehículo seleccionado no existe.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error inesperado: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Método de solicitud no válido.'})


# editar contrato
def edit_contract(request):
    context = user_data(request)
    company_id = context["company"]["id"]

    if request.method == 'GET':
        contract_id = request.GET.get('id')
        try:
            contract = Contract_Vehicle.objects.get(id=contract_id)
            data = {
                "id": contract.id,
                "type_contract": contract.type_contract,
                "vehiculo_id": contract.vehiculo.id if contract.vehiculo else None,
                "fecha_contract": contract.fecha_contract.strftime('%Y-%m-%d'),
                "fecha_finiquito": contract.fecha_finiquito.strftime('%Y-%m-%d'),
                "document_contract": contract.document_contract.url if contract.document_contract else ""
            }
            return JsonResponse({"status": "success", "data": data})
        except Contract_Vehicle.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Contrato no encontrado"})

    if request.method == 'POST':
        try:
            contract_id = request.POST.get('id')
            if not contract_id:
                return JsonResponse({'success': False, 'message': 'ID de contrato no proporcionado.'})

            contract = Contract_Vehicle.objects.get(id=contract_id)

            # Obtener valores nuevos
            type_contract = request.POST.get('type_contract', contract.type_contract)
            vehiculo_id = request.POST.get('vehiculo_contract') or (contract.vehiculo.id if contract.vehiculo else None)
            fecha_contract = request.POST.get('fecha_contract') or contract.fecha_contract.strftime('%Y-%m-%d')
            fecha_finiquito = request.POST.get('fecha_finiquito') or contract.fecha_finiquito.strftime('%Y-%m-%d')
            document_contract = request.FILES.get('document_contract')

            # Validaciones mínimas
            if not vehiculo_id or not fecha_contract or not type_contract:
                return JsonResponse({'success': False, 'message': 'Faltan campos clave.'})

            # Validar fechas
            try:
                fecha_contract_obj = datetime.strptime(fecha_contract, "%Y-%m-%d").date()
                fecha_finiquito_obj = datetime.strptime(fecha_finiquito, "%Y-%m-%d").date()
            except ValueError:
                return JsonResponse({'success': False, 'message': 'Formato de fecha inválido.'})

            if fecha_finiquito_obj <= fecha_contract_obj:
                return JsonResponse({'success': False, 'message': 'La fecha de finiquito debe ser posterior a la fecha de contrato.'})

            # Validar contrato duplicado
            if Contract_Vehicle.objects.exclude(id=contract.id).filter(
                fecha_contract=fecha_contract_obj,
                vehiculo_id=vehiculo_id
            ).exists():
                return JsonResponse({'success': False, 'message': 'Ya existe un contrato con esa fecha para este vehículo.'})

            # Actualizar datos
            contract.type_contract = type_contract
            contract.fecha_contract = fecha_contract_obj
            contract.fecha_finiquito = fecha_finiquito_obj

            try:
                contract.vehiculo = Vehicle.objects.get(id=int(vehiculo_id))
            except Vehicle.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Vehículo no válido.'})

            # Subir archivo nuevo si existe
            if document_contract:
                if contract.document_contract:
                    delete_s3_object(bucket_name, str(contract.document_contract.name))  # asegúrate de que `delete_s3_object` esté definido

                file_name, extension = os.path.splitext(document_contract.name)
                new_name = f"contrato_{contract.id}{extension}"
                s3_path = f'docs/{company_id}/vehicle/contratos/{contract.id}/{new_name}'

                try:
                    upload_to_s3(document_contract, bucket_name, s3_path)
                    contract.document_contract = s3_path
                except Exception as e:
                    return JsonResponse({'success': False, 'message': f'Error al subir archivo: {str(e)}'})

            contract.save()
            return JsonResponse({'success': True, 'message': 'Contrato actualizado correctamente.'})

        except Contract_Vehicle.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Contrato no encontrado.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error interno: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Método de solicitud inválido.'})

# funcion para eliminar  un contrato
@login_required
@csrf_exempt
def delete_contract(request):                          
    if request.method == 'POST':
        form = request.POST
        _id = form.get('id')

        if not _id:
            return JsonResponse({'success': False, 'message': 'No ID provided'})

        try:
            contract = Contract_Vehicle.objects.get(id=_id)
        except Contract_Vehicle.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'contract not found'})

        contract.delete()

        return JsonResponse({'success': True, 'message': 'Contrato eliminado correctamente!'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@csrf_exempt
def upload_letter_finiquito(request):
    context = user_data(request)
    company_id = context["company"]["id"]

    if request.method == "POST":
        try:
            contrato_id = request.POST.get("id")
            document_letter = request.FILES.get("document_letter")

            if not contrato_id or not document_letter:
                return JsonResponse({"success": False, "message": "Faltan datos obligatorios."})

            contrato = Contract_Vehicle.objects.get(id=contrato_id)

            # Construir ruta y nombre de archivo
            s3Path = f'docs/{company_id}/vehicle/finiquitos/{contrato.id}/'
            file_name, extension = os.path.splitext(document_letter.name)
            new_name = f"finiquito_{contrato.id}{extension}"
            S3name = s3Path + new_name

            # Subir archivo a S3
            upload_to_s3(document_letter, bucket_name, S3name)

            # Guardar cambios en el modelo
            contrato.document_letter = S3name
            contrato.status_modified = True
            contrato.save()

            return JsonResponse({"success": True, "message": "Carta finiquito subida correctamente."})

        except Contract_Vehicle.DoesNotExist:
            return JsonResponse({"success": False, "message": "Contrato no encontrado."})
        except Exception as e:
            return JsonResponse({"success": False, "message": f"Error inesperado: {str(e)}"})

    return JsonResponse({"success": False, "message": "Método no permitido."})

@csrf_exempt
def cancel_contract_vehicle(request):
    if request.method == "POST":
        try:
            contrato_id = request.POST.get("id")
            if not contrato_id:
                return JsonResponse({"success": False, "message": "ID de contrato no proporcionado."})

            contrato = Contract_Vehicle.objects.get(id=contrato_id)

            if contrato.status_modified:
                return JsonResponse({"success": False, "message": "El contrato ya fue cancelado."})

            contrato.is_canceled = True
            contrato.status_modified = False
            contrato.save()

            return JsonResponse({"success": True, "message": "Contrato cancelado correctamente."})

        except Contract_Vehicle.DoesNotExist:
            return JsonResponse({"success": False, "message": "Contrato no encontrado."})
        except Exception as e:
            return JsonResponse({"success": False, "message": f"Error inesperado: {str(e)}"})

    return JsonResponse({"success": False, "message": "Método no permitido."})


# CARTA DE FACTURA
@login_required
def get_vehicles_letter_factura(request):
    try:
        context = user_data(request)
        company_id = context["company"]["id"]  

        if not company_id:
            return JsonResponse({'success': False, 'message': 'No se encontró la empresa asociada al usuario'}, status=400)
    # Obtener los registros
        vehiculos = Vehicle.objects.filter(
            company_id=company_id
        ).values('id', 'name') 
        data = list(vehiculos)
        # print("esta es la lista de vehiculos de la empresa para carta de facturacion:", vehiculos)
        return JsonResponse({'data': data}, safe=False)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

#tabla de cartas de facturas
def table_letter_factura_vehicle(request):
    response = {"success": False}
    context = user_data(request)
    subModule_id = 37
    access = get_module_user_permissions(context, subModule_id)["data"]["access"]

    vehicle_id = request.GET.get('vehicle_id')
    # print("Entramos a la función de mostrar la tabla de carta de factura del vehículo:", vehicle_id)

    if not vehicle_id:
        return JsonResponse({"data": []})

    datos = Letter_Facturas_Vehicle.objects.select_related("vehiculo").filter(
        vehiculo_id=vehicle_id
    )

    data_list = []

    for item in datos:

        row = {
            "id": item.id,
            "vehiculo": item.vehiculo.name if item.vehiculo else "",
            "date": item.date.strftime('%Y-%m-%d') if item.date else "",
            "btn_view": "",
            "btn_action": "",
        }

        # Botón Ver Documento
        if item.document_letter_factura:
            tempDoc = generate_presigned_url(bucket_name, item.document_letter_factura.name)
            row["btn_view"] = f"""<a href="{tempDoc}" class="btn btn-sm btn-info" target="_blank">
                <i class="fa-solid fa-file"></i> Ver 
            </a>"""

        # Botón Editar
        if access.get("update"):
            row["btn_action"] += f"""<button class="btn btn-primary btn-sm" data-vehicle-letter-factura="update-letter-factura" 
                data-id="{item.id}">
                <i class="fa-solid fa-pen"></i>
            </button>\n"""

        # Botón Eliminar
        if access.get("delete"):
            row["btn_action"] += f"""<button class="btn btn-danger btn-sm" data-vehicle-letter-factura="delete-letter-factura" data-id="{item.id}">
                <i class="fa-solid fa-trash"></i>
            </button>"""

        data_list.append(row)

    response.update({"data": data_list, "status": "success", "success": True})
    return JsonResponse(response)

# agregar carta de factura
def add_letter_factura(request):
    context = user_data(request)
    company_id = context["company"]["id"]

    if request.method == 'POST':
        try:
            vehiculo_id = request.POST.get('vehiculo_letter_factura')
            date = request.POST.get('date')
            document_letter_factura = request.FILES.get('document_letter_factura')

            vehiculo = Vehicle.objects.get(id=int(vehiculo_id))
            # Convertir fechas
            try:
                date_obj = datetime.strptime(date, "%Y-%m-%d").date()
            except ValueError:
                return JsonResponse({'success': False, 'message': 'Formato de fecha inválido.'})

            # Crear contrato
            nuevo_carta_factura = Letter_Facturas_Vehicle.objects.create(
                vehiculo=vehiculo,
                date=date,
            )

            # Subir archivo si existe
            if document_letter_factura:
                s3Path = f'docs/{company_id}/vehicle/letter_factura/{nuevo_carta_factura.id}/'
                file_name, extension = os.path.splitext(document_letter_factura.name)
                new_name = f"contrato_{nuevo_carta_factura.id}{extension}"
                S3name = s3Path + new_name

                upload_to_s3(document_letter_factura, bucket_name, S3name)

                nuevo_carta_factura.document_letter_factura = S3name
                nuevo_carta_factura.save()

            return JsonResponse({'success': True, 'message': 'Carta registrada correctamente.'})

        except Vehicle.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'El vehículo seleccionado no existe.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error inesperado: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Método de solicitud no válido.'})

# editar carta de factura
def edit_letter_factura(request):
    context = user_data(request)
    company_id = context["company"]["id"]

    if request.method == 'GET':
        letter_factura_id = request.GET.get('id')
        try:
            letter_factura = Letter_Facturas_Vehicle.objects.get(id=letter_factura_id)
            data = {
                "id": letter_factura.id,
                "vehiculo_id": letter_factura.vehiculo.id if letter_factura.vehiculo else None,
                "date": letter_factura.date.strftime('%Y-%m-%d'),
                "document_letter_factura": letter_factura.document_letter_factura.url if letter_factura.document_letter_factura else ""
            }
            return JsonResponse({"status": "success", "data": data})
        except Letter_Facturas_Vehicle.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Contrato no encontrado"})

    elif request.method == 'POST':
        try:
            letter_factura_id = request.POST.get('id')
            if not letter_factura_id:
                return JsonResponse({'success': False, 'message': 'ID de contrato no proporcionado.'})

            letter_factura = Letter_Facturas_Vehicle.objects.get(id=letter_factura_id)

            vehiculo_id = request.POST.get('vehiculo_letter_factura') or (letter_factura.vehiculo.id if letter_factura.vehiculo else None)
            date_str = request.POST.get('date') or letter_factura.date.strftime('%Y-%m-%d')
            document_letter_factura = request.FILES.get('document_letter_factura')

            if not vehiculo_id or not date_str:
                return JsonResponse({'success': False, 'message': 'Faltan campos clave.'})

            # Convertir fecha
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return JsonResponse({'success': False, 'message': 'Formato de fecha inválido.'})

            # Asignar valores nuevos
            letter_factura.date = date_obj

            try:
                letter_factura.vehiculo = Vehicle.objects.get(id=int(vehiculo_id))
            except Vehicle.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Vehículo no válido.'})

            # Subir archivo si existe
            if document_letter_factura:
                if letter_factura.document_letter_factura:
                    delete_s3_object(bucket_name, str(letter_factura.document_letter_factura.name))

                file_name, extension = os.path.splitext(document_letter_factura.name)
                new_name = f"carta_factura_{letter_factura.id}{extension}"
                s3_path = f'docs/{company_id}/vehicle/letter_factura/{letter_factura.id}/{new_name}'

                try:
                    upload_to_s3(document_letter_factura, bucket_name, s3_path)
                    letter_factura.document_letter_factura = s3_path
                except Exception as e:
                    return JsonResponse({'success': False, 'message': f'Error al subir archivo: {str(e)}'})

            letter_factura.save()
            return JsonResponse({'success': True, 'message': 'Contrato actualizado correctamente.'})

        except Letter_Facturas_Vehicle.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Contrato no encontrado.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error interno: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Método de solicitud inválido.'})

# funcion para eliminar  una carta
@login_required
@csrf_exempt
def delete_letter_factura(request):                          
    if request.method == 'POST':
        form = request.POST
        _id = form.get('id')

        if not _id:
            return JsonResponse({'success': False, 'message': 'No ID provided'})

        try:
            letter_factura = Letter_Facturas_Vehicle.objects.get(id=_id)
        except Letter_Facturas_Vehicle.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'letter not found'})

        letter_factura.delete()

        return JsonResponse({'success': True, 'message': 'Carta de factura eliminada correctamente!'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

# HOLOGRAMAS
@login_required
def get_vehicles_hologram(request):
    try:
        context = user_data(request)
        company_id = context["company"]["id"]  

        if not company_id:
            return JsonResponse({'success': False, 'message': 'No se encontró la empresa asociada al usuario'}, status=400)
    # Obtener los registros
        vehiculos = Vehicle.objects.filter(
            company_id=company_id
        ).values('id', 'name') 
        data = list(vehiculos)
        # print("esta es la lista de vehiculos de la empresa para carta de facturacion:", vehiculos)
        return JsonResponse({'data': data}, safe=False)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

#tabla de cartas de facturas
def table_hologram_vehicle(request):
    response = {"success": False}
    context = user_data(request)
    subModule_id = 37
    access = get_module_user_permissions(context, subModule_id)["data"]["access"]

    vehicle_id = request.GET.get('vehicle_id')

    if not vehicle_id:
        return JsonResponse({"data": []})

    datos = Hologram_Vehicle.objects.select_related("vehiculo").filter(
        vehiculo_id=vehicle_id
    )

    data_list = []

    for item in datos:

        row = {
            "id": item.id,
            "vehiculo": item.vehiculo.name if item.vehiculo else "",
            "date_hologram": item.date_hologram.strftime('%Y-%m-%d') if item.date_hologram else "",
            "btn_view": "",
            "btn_action": "",
        }

        # Botón Ver Documento
        if item.document_hologram:
            tempDoc = generate_presigned_url(bucket_name, item.document_hologram.name)
            row["btn_view"] = f"""<a href="{tempDoc}" class="btn btn-sm btn-info" target="_blank">
                <i class="fa-solid fa-file"></i> Ver 
            </a>"""

        # Botón Editar
        if access.get("update"):
            row["btn_action"] += f"""<button class="btn btn-primary btn-sm" data-vehicle-hologram="update-hologram" 
                data-id="{item.id}">
                <i class="fa-solid fa-pen"></i>
            </button>\n"""

        # Botón Eliminar
        if access.get("delete"):
            row["btn_action"] += f"""<button class="btn btn-danger btn-sm" data-vehicle-hologram="delete-hologram" data-id="{item.id}">
                <i class="fa-solid fa-trash"></i>
            </button>"""

        data_list.append(row)

    response.update({"data": data_list, "status": "success", "success": True})
    return JsonResponse(response)

# agregaR holograma
def add_hologram(request):
    context = user_data(request)
    company_id = context["company"]["id"]

    if request.method == 'POST':
        try:
            vehiculo_id = request.POST.get('vehiculo_hologram')
            date_hologram = request.POST.get('date_hologram')
            document_hologram = request.FILES.get('document_hologram')

            if not date_hologram:
                return JsonResponse({'success': False, 'message': 'La fecha es obligatoria.'})
            if not isinstance(date_hologram, str):
                return JsonResponse({'success': False, 'message': 'El valor de la fecha no es una cadena válida.'})

            try:
                date_obj = datetime.strptime(date_hologram, "%Y-%m-%d").date()
            except ValueError:
                return JsonResponse({'success': False, 'message': 'Formato de fecha inválido.'})

            vehiculo = Vehicle.objects.get(id=int(vehiculo_id))

            nuevo_hologram = Hologram_Vehicle.objects.create(
                vehiculo=vehiculo,
                date_hologram=date_obj,
            )

            if document_hologram:
                s3Path = f'docs/{company_id}/vehicle/hologram/{nuevo_hologram.id}/'
                file_name, extension = os.path.splitext(document_hologram.name)
                new_name = f"contrato_{nuevo_hologram.id}{extension}"
                S3name = s3Path + new_name

                upload_to_s3(document_hologram, bucket_name, S3name)

                nuevo_hologram.document_hologram = S3name
                nuevo_hologram.save()

            return JsonResponse({'success': True, 'message': 'Holograma registrado correctamente.'})

        except Vehicle.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'El vehículo seleccionado no existe.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error inesperado: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Método de solicitud no válido.'})

# editar holograma
def edit_hologram(request):
    context = user_data(request)
    company_id = context["company"]["id"]

    if request.method == 'GET':
        hologram_id = request.GET.get('id')
        try:
            hologram = Hologram_Vehicle.objects.get(id=hologram_id)
            data = {
                "id": hologram.id,
                "vehiculo_id": hologram.vehiculo.id if hologram.vehiculo else None,
                "date_hologram": hologram.date_hologram.strftime('%Y-%m-%d'),
                "document_hologram": hologram.document_hologram.url if hologram.document_hologram else ""
            }
            return JsonResponse({"status": "success", "data": data})
        except Hologram_Vehicle.DoesNotExist:
            return JsonResponse({"status": "error", "message": "holograma no encontrado"})

    elif request.method == 'POST':
        try:
            hologram_id = request.POST.get('id')
            if not hologram_id:
                return JsonResponse({'success': False, 'message': 'ID de contrato no proporcionado.'})

            hologram = Hologram_Vehicle.objects.get(id=hologram_id)

            vehiculo_id = request.POST.get('vehiculo_hologram') or (hologram.vehiculo.id if hologram.vehiculo else None)
            date_hologram = request.POST.get('date_hologram') or hologram.date_hologram.strftime('%Y-%m-%d')
            document_hologram = request.FILES.get('document_hologram')

            if not vehiculo_id or not date_hologram:
                return JsonResponse({'success': False, 'message': 'Faltan campos clave.'})

            # Convertir fecha
            try:
                date_obj = datetime.strptime(date_hologram, "%Y-%m-%d").date()
            except ValueError:
                return JsonResponse({'success': False, 'message': 'Formato de fecha inválido.'})

            # Asignar valores nuevos
            hologram.date_hologram = date_obj

            try:
                hologram.vehiculo = Vehicle.objects.get(id=int(vehiculo_id))
            except Vehicle.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Vehículo no válido.'})

            # Subir archivo si existe
            if document_hologram:
                if hologram.document_hologram:
                    delete_s3_object(bucket_name, str(hologram.document_hologram.name))

                file_name, extension = os.path.splitext(document_hologram.name)
                new_name = f"hologram_{hologram.id}{extension}"
                s3_path = f'docs/{company_id}/vehicle/hologram/{hologram.id}/{new_name}'

                try:
                    upload_to_s3(document_hologram, bucket_name, s3_path)
                    hologram.document_hologram = s3_path
                except Exception as e:
                    return JsonResponse({'success': False, 'message': f'Error al subir archivo: {str(e)}'})

            hologram.save()
            return JsonResponse({'success': True, 'message': 'Holograma actualizado correctamente.'})

        except Hologram_Vehicle.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Contrato no encontrado.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error interno: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Método de solicitud inválido.'})

# funcion para eliminar  un hologramma
@login_required
@csrf_exempt
def delete_hologram(request):                          
    if request.method == 'POST':
        form = request.POST
        _id = form.get('id')

        if not _id:
            return JsonResponse({'success': False, 'message': 'No ID provided'})

        try:
            hologram = Hologram_Vehicle.objects.get(id=_id)
        except Hologram_Vehicle.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'hologram not found'})

        hologram.delete()

        return JsonResponse({'success': True, 'message': 'Holograma eliminado correctamente!'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})


#CARNET
@login_required
def get_vehicles_carnet(request):
    try:
        context = user_data(request)
        company_id = context["company"]["id"]  

        if not company_id:
            return JsonResponse({'success': False, 'message': 'No se encontró la empresa asociada al usuario'}, status=400)
    # Obtener los registros
        vehiculos = Vehicle.objects.filter(
            company_id=company_id
        ).values('id', 'name') 
        data = list(vehiculos)
        # print("esta es la lista de vehiculos de la empresa para carta de facturacion:", vehiculos)
        return JsonResponse({'data': data}, safe=False)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

#tabla de carnett
def table_carnet_vehicle(request):
    response = {"success": False}
    context = user_data(request)
    subModule_id = 37
    access = get_module_user_permissions(context, subModule_id)["data"]["access"]

    vehicle_id = request.GET.get('vehicle_id')

    if not vehicle_id:
        return JsonResponse({"data": []})

    datos = Carnet_Vehicle.objects.select_related("vehiculo").filter(
        vehiculo_id=vehicle_id
    )

    data_list = []

    for item in datos:

        row = {
            "id": item.id,
            "vehiculo": item.vehiculo.name if item.vehiculo else "",
            "date_carnet": item.date_carnet.strftime('%Y-%m-%d') if item.date_carnet else "",
            "btn_view": "",
            "btn_action": "",
        }

        # Botón Ver Documento
        if item.document_carnet:
            tempDoc = generate_presigned_url(bucket_name, item.document_carnet.name)
            row["btn_view"] = f"""<a href="{tempDoc}" class="btn btn-sm btn-info" target="_blank">
                <i class="fa-solid fa-file"></i> Ver 
            </a>"""

        # Botón Editar                                                                                                                                                                                                                          
        if access.get("update"):
            row["btn_action"] += f"""<button class="btn btn-primary btn-sm" data-vehicle-carnet="update-carnet" 
                data-id="{item.id}">
                <i class="fa-solid fa-pen"></i>
            </button>\n"""

        # Botón Eliminar
        if access.get("delete"):
            row["btn_action"] += f"""<button class="btn btn-danger btn-sm" data-vehicle-carnet="delete-carnet" data-id="{item.id}">
                <i class="fa-solid fa-trash"></i>
            </button>"""

        data_list.append(row)

    response.update({"data": data_list, "status": "success", "success": True})
    return JsonResponse(response)

# agregar carnet
def add_carnet(request):
    context = user_data(request)
    company_id = context["company"]["id"]

    if request.method == 'POST':
        try:
            vehiculo_id = request.POST.get('vehiculo_carnet')
            date_carnet = request.POST.get('date_carnet')
            document_carnet = request.FILES.get('document_carnet')

            if not date_carnet:
                return JsonResponse({'success': False, 'message': 'La fecha es obligatoria.'})
            if not isinstance(date_carnet, str):
                return JsonResponse({'success': False, 'message': 'El valor de la fecha no es una cadena válida.'})

            try:
                date_obj = datetime.strptime(date_carnet, "%Y-%m-%d").date()
            except ValueError:
                return JsonResponse({'success': False, 'message': 'Formato de fecha inválido.'})

            vehiculo = Vehicle.objects.get(id=int(vehiculo_id))

            nuevo_carnet = Carnet_Vehicle.objects.create(
                vehiculo=vehiculo,
                date_carnet=date_obj,
            )

            if document_carnet:
                s3Path = f'docs/{company_id}/vehicle/carnet/{nuevo_carnet.id}/'
                file_name, extension = os.path.splitext(document_carnet.name)
                new_name = f"contrato_{nuevo_carnet.id}{extension}"
                S3name = s3Path + new_name

                upload_to_s3(document_carnet, bucket_name, S3name)

                nuevo_carnet.document_carnet = S3name
                nuevo_carnet.save()

            return JsonResponse({'success': True, 'message': 'Carnet registrado correctamente.'})

        except Vehicle.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'El vehículo seleccionado no existe.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error inesperado: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Método de solicitud no válido.'})

# editar carnet
def edit_carnet(request):
    context = user_data(request)
    company_id = context["company"]["id"]

    if request.method == 'GET':
        carnet_id = request.GET.get('id')
        try:
            carnet = Carnet_Vehicle.objects.get(id=carnet_id)
            data = {
                "id": carnet.id,
                "vehiculo_id": carnet.vehiculo.id if carnet.vehiculo else None,
                "date_carnet": carnet.date_carnet.strftime('%Y-%m-%d'),
                "document_carnet": carnet.document_carnet.url if carnet.document_carnet else ""
            }
            return JsonResponse({"status": "success", "data": data})
        except Carnet_Vehicle.DoesNotExist:
            return JsonResponse({"status": "error", "message": "carnet no encontrado"})

    elif request.method == 'POST':
        try:
            carnet_id = request.POST.get('id')
            if not carnet_id:
                return JsonResponse({'success': False, 'message': 'ID de carnet no proporcionado.'})

            carnet = Carnet_Vehicle.objects.get(id=carnet_id)

            vehiculo_id = request.POST.get('vehiculo_carnet') or (carnet.vehiculo.id if carnet.vehiculo else None)
            date_carnet = request.POST.get('date_carnet') or carnet.date_hologram.strftime('%Y-%m-%d')
            document_carnet = request.FILES.get('document_carnet')

            if not vehiculo_id or not date_carnet:
                return JsonResponse({'success': False, 'message': 'Faltan campos clave.'})

            # Convertir fecha
            try:
                date_obj = datetime.strptime(date_carnet, "%Y-%m-%d").date()
            except ValueError:
                return JsonResponse({'success': False, 'message': 'Formato de fecha inválido.'})

            # Asignar valores nuevos
            carnet.date_carnet = date_obj

            try:
                carnet.vehiculo = Vehicle.objects.get(id=int(vehiculo_id))
            except Vehicle.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Vehículo no válido.'})

            # Subir archivo si existe
            if document_carnet:
                if carnet.document_carnet:
                    delete_s3_object(bucket_name, str(carnet.document_carnet.name))

                file_name, extension = os.path.splitext(document_carnet.name)
                new_name = f"carnet_{carnet.id}{extension}"
                s3_path = f'docs/{company_id}/vehicle/carnet/{carnet.id}/{new_name}'

                try:
                    upload_to_s3(document_carnet, bucket_name, s3_path)
                    carnet.document_carnet = s3_path
                except Exception as e:
                    return JsonResponse({'success': False, 'message': f'Error al subir archivo: {str(e)}'})

            carnet.save()
            return JsonResponse({'success': True, 'message': 'Carnet actualizado correctamente.'})

        except Carnet_Vehicle.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Carnet no encontrado.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error interno: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Método de solicitud inválido.'})

# funcion para eliminar un carnet
@login_required
@csrf_exempt
def delete_carnet(request):                          
    if request.method == 'POST':
        form = request.POST
        _id = form.get('id')

        if not _id:
            return JsonResponse({'success': False, 'message': 'No ID provided'})

        try:
            carnet = Carnet_Vehicle.objects.get(id=_id)
        except Carnet_Vehicle.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'hologram not found'})

        carnet.delete()

        return JsonResponse({'success': True, 'message': 'Carnet eliminado correctamente!'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})



@csrf_exempt
def deactivate_vehicle(request):
    if request.method == "POST":
        vehicle_id = request.POST.get("id")
        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)
            vehicle.is_active = False
            vehicle.save()
            return JsonResponse({
                "status": "success",
                "message": f"Vehículo '{vehicle.name}' desactivado correctamente."
            })
        except Vehicle.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Vehículo no encontrado."
            })
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": f"Error al desactivar el vehículo: {e}"
            })
    else:
        return JsonResponse({
            "status": "error",
            "message": "Método no permitido. Solo se acepta POST."
        })


# Vista para guardar fecha compromiso
@login_required
def save_commitment_date(request):
    if request.method == "POST":
        try:
            audit_id = request.POST.get("audit_id")
            commitment_date = request.POST.get("commitment_date")

            if not audit_id or not commitment_date:
                return JsonResponse({"success": False, "error": "Faltan datos"})

            vehicle_audit = Vehicle_Audit.objects.filter(id=audit_id).first()
            if not vehicle_audit:
                return JsonResponse({"success": False, "error": "Auditoría no encontrada"})

            # Guardar la fecha compromiso
            vehicle_audit.commitment_date = commitment_date
            vehicle_audit.save(update_fields=["commitment_date"])

            # --- Enviar correo al auditor/encargado ---
            domain = request.build_absolute_uri("/")[:-1]
            link_vehiculo = f"{domain}/vehicles/info/{vehicle_audit.vehicle.id}/"

            creator = vehicle_audit.user_created
            if creator and creator.email:
                context_email = {
                    "to": [creator.email],
                    "company": vehicle_audit.vehicle.company.name,
                    "subject": "Fecha compromiso asignada",
                    "modulo": 2,
                    "submodulo": "Auditoría",
                    "item": vehicle_audit.vehicle.id,
                    "title": f"Fecha compromiso asignada en auditoría de {vehicle_audit.vehicle.name}",
                    "body": f"""
                        Hola {creator.get_full_name() or creator.username},<br><br>
                        Se ha asignado una <strong>fecha compromiso</strong> para atender los hallazgos encontrados 
                        en la auditoría realizada al vehículo <strong>{vehicle_audit.vehicle.name}</strong> 
                        el día <strong>{vehicle_audit.audit_date}</strong>.<br><br>

                        📅 Fecha compromiso: <strong>{vehicle_audit.commitment_date}</strong><br><br>

                        Te invitamos a dar seguimiento a las acciones correctivas necesarias. <br><br>
                        Puedes revisar la auditoría y los detalles completos en el siguiente enlace:<br>
                        👉 <a href="{link_vehiculo}">Ver auditoría</a>.<br><br>
                    """
                }
                send_notification(context_email)
                print("se envio al correo:", creator.email)

            return JsonResponse({"success": True, "message": "Fecha compromiso guardada y correo enviado"})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Método no permitido"})

@csrf_exempt
def save_correction_evidence(request):
    if request.method == "POST":
        audit_id = request.POST.get("audit_id")
        files = request.FILES

        try:
            audit = Vehicle_Audit.objects.get(id=audit_id)
            company_id = audit.vehicle.company.id if audit.vehicle and audit.vehicle.company else "general"
            vehicle_id = audit.vehicle.id if audit.vehicle else "0"

            uploaded_paths = {}  # Guardamos paths S3 por check

            for field_name, file in files.items():
                if field_name.startswith("correction_"):
                    check_name = field_name.replace("correction_", "")

                    # Nombre único en S3
                    folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/audit/{audit_id}/corrections/"
                    file_name, extension = os.path.splitext(file.name)
                    new_name = f"{check_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}{extension}"
                    s3_path = folder_path + new_name

                    # Subir a S3
                    try:
                        upload_to_s3(file, bucket_name, s3_path)
                    except Exception as e:
                        return JsonResponse({"success": False, "error": f"Error al subir {check_name}: {str(e)}"})

                    # Guardar en DB
                    VehicleAuditCorrection.objects.create(
                        audit=audit,
                        check_name=check_name,
                        image=s3_path
                    )

                    uploaded_paths[check_name] = s3_path

            #Devolver todas las imágenes existentes también
            all_corrections = VehicleAuditCorrection.objects.filter(audit=audit)
            all_paths = {
                c.check_name: generate_presigned_url(bucket_name, c.image) for c in all_corrections
            }

            print("esto contiene la url de las imagenes", all_paths)

            # --- Enviar correo al auditor/encargado ---
            domain = request.build_absolute_uri("/")[:-1]
            link_vehiculo = f"{domain}/vehicles/info/{audit.vehicle.id}/"

            creator = audit.user_created
            if creator and creator.email:
                context_email = {
                    "to": [creator.email],
                    "company": audit.vehicle.company.name,
                    "subject": "Evidencias de corrección cargadas",
                    "modulo": 2,
                    "submodulo": "Auditoría",
                    "item": audit.vehicle.id,
                    "title": f"Evidencias de corrección subidas en auditoría de {audit.vehicle.name}",
                    "body": f"""
                        Hola {creator.get_full_name() or creator.username},<br><br>
                        Se han subido <strong>evidencias de corrección</strong> para atender los hallazgos encontrados 
                        en la auditoría realizada al vehículo <strong>{audit.vehicle.name}</strong> 
                        el día <strong>{audit.audit_date}</strong>.<br><br>

                        📂 Ahora puedes revisar las imágenes de las correcciones realizadas.<br><br>

                        👉 <a href="{link_vehiculo}">Ver auditoría</a>.<br><br>
                    """
                }
                send_notification(context_email)
                print("Correo de evidencias enviado para auditoría:", audit.id)
                print("los correo a los que fue enviado son:", creator.email)
                
            return JsonResponse({
                "success": True,
                "message": "Evidencias de corrección guardadas en S3",
                "paths": all_paths
            })

        except Vehicle_Audit.DoesNotExist:
            return JsonResponse({"success": False, "error": "Auditoría no encontrada"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Método no permitido"})


# TODO --------------- [ END ] ----------
# ! Este es el fin


