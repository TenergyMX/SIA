from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect, HttpResponse
from django.db.models import F, Q, Value, Max, Sum, CharField, BooleanField
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from django.template.loader import get_template
from modules.models import *
from pathlib import Path
from os.path import join, dirname
from modules.models import *
from users.models import *
from datetime import datetime, timedelta
import json, os
import requests
import random
import calendar
import glob
from xhtml2pdf import pisa
# py personalizado
from modules.utils import *
# from helpers.enviar_correo import *
import boto3
import boto3.session
import io
import mimetypes
from botocore.client import Config
from botocore.exceptions import ClientError
import zipfile
from zipfile import ZipFile
from io import BytesIO
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv

# import qrcode
from django.shortcuts import render, get_object_or_404
from django.core.files.uploadedfile import InMemoryUploadedFile



boto3.client('s3', region_name='us-east-2', config=Config(signature_version='s3v4'))

dotenv_path = join(dirname(__file__), 'awsCred.env')
load_dotenv(dotenv_path)

# TODO --------------- [ VARIABLES ] ---------- 
AUDITORIA_EQUIPOS_COMPUTO_POR_SEMANA = 2
AWS_ACCESS_KEY_ID=os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY=os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_DEFAULT_REGION=os.environ.get('AWS_DEFAULT_REGION')
AWS_BUCKET_NAME=str(os.environ.get('AWS_BUCKET_NAME'))

ALLOWED_FILE_EXTENSIONS = ['.jpg', '.jpeg', '.png']


# TODO --------------- [ VIEWS ] ----------
@login_required
def computer_equipment_view(request):
    context = user_data(request)
    module_id = 3
    subModule_id = 13
    request.session["last_module_id"] = module_id
    
    access = get_module_user_permissions(context, subModule_id)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]
    print("estos son los modulos permitidos", context["sidebar"])

    template = "computer-equipment/computer_equipment.html" if context["access"]["read"] and check_user_access_to_module(request, module_id, subModule_id) else "error/access_denied.html"
    return render(request, template , context)

@login_required
def computer_system_details(request, equipment_id = None):
    context = user_data(request)
    module_id = 3
    subModule_id = 13

    context["computerSystem_id"] = equipment_id
    access = get_module_user_permissions(context, subModule_id)
    sidebar = get_sidebar(context, [1, module_id])
    permisos = get_user_access(context)
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]
    context["permiso"] = permisos["data"]

    template = "computer-equipment/computer_system_details.html" if context["access"]["read"] and check_user_access_to_module(request, module_id, subModule_id) else "error/access_denied.html"
    return render(request, template , context)

@login_required
def computer_peripherals(request):
    context = user_data(request)
    module_id = 3
    subModule_id = 14

    access = get_module_user_permissions(context, subModule_id)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]
    
    template = "computer-equipment/computer_peripherals.html" if context["access"]["read"] and check_user_access_to_module(request, module_id, subModule_id) else "error/access_denied.html"
    return render(request, template , context)

@login_required
def computer_software(request):
    context = user_data(request)
    module_id = 3
    subModule_id = 15

    access = get_module_user_permissions(context, subModule_id)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]
    
    template = "computer-equipment/softwares.html" if context["access"]["read"] and check_user_access_to_module(request, module_id, subModule_id) else "error/access_denied.html"
    return render(request, template , context)


@login_required
def computer_equipment_audit_view(request):
    context = user_data(request)
    module_id = 3
    subModule_id = 16

    access = get_module_user_permissions(context, subModule_id)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]
    
    template = "computer-equipment/audit.html" if context["access"]["read"] and check_user_access_to_module(request, module_id, subModule_id) else "error/access_denied.html"
    return render(request, template , context)

@login_required
def computer_equipment_maintenance_view(request):
    context = user_data(request)
    module_id = 3
    subModule_id = 17

    access = get_module_user_permissions(context, subModule_id)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]
    
    template = "computer-equipment/maintenance.html" if context["access"]["read"] and check_user_access_to_module(request, module_id, subModule_id) else "error/access_denied.html"
    return render(request, template , context)

@login_required
def assigned_computer_equipment_view(request):
    context = user_data(request)
    module_id = 3
    subModule_id = 18

    access = get_module_user_permissions(context, subModule_id)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]
    
    template = "computer-equipment/assigned.html" if context["access"]["read"] and check_user_access_to_module(request, module_id, subModule_id) else "error/access_denied.html"
    return render(request, template , context)

@login_required
def computer_equipment_responsiva_view(request):
    context = user_data(request)
    module_id = 3
    subModule_id = 19

    access = get_module_user_permissions(context, subModule_id)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]
    
    template = "computer-equipment/responsiva.html" if context["access"]["read"] and check_user_access_to_module(request, module_id, subModule_id) else "error/access_denied.html"
    return render(request, template , context)

@login_required
def computer_equipment_responsiva_pdf_view(request):
    dt = request.GET
    context = user_data(request)
    context2 = {
        'title': 'Reporte',
        'user': { 'name': 'Nombre del usuario' },
        'data': [],
    }
    context2["data"] = []
    responsible_id = dt.get("user_id")

    if not responsible_id:
        responsible_id = context["user"]["id"]

    datos_usuario = User.objects.filter(id = responsible_id)

    if datos_usuario.exists():
        datos_usuario = datos_usuario.values()[0]
        context2["user"]["name"] = f"{datos_usuario['first_name']} {datos_usuario['last_name']}"

    # Paso 1. Obtener los equipos de computos que tiene el usuario
    datos_1 = ComputerSystem.objects.filter(current_responsible_id = responsible_id).values()
    for item in datos_1:
        model = item['model'] if item['model'] else "-----"
        serial_number = item['serial_number'] if item['serial_number'] else "-----"
        identifier = item['identifier'] if item['identifier'] else "-----"
        name = item['name'] if item['name'] else "-----"
        context2["data"].append({
            "amount": 1,
            "description": f"Equipo de cómputo marca {model} con nombre del equipo: {name}",
            "identifier" : identifier
        })

    # Paso 2. Obtener los perifericos que tiene el usuario
    datos_2 = ComputerPeripheral.objects.filter(responsible_id = responsible_id).values()
    for item in datos_2:
        tipo =  item['peripheral_type'] if item['peripheral_type'] else "-----"
        marca = item['brand'] if item['brand'] else "-----"
        identifier = item['identifier'] if item['identifier'] else "-----"
        context2["data"].append({
            "amount": 1,
            "description": f"{tipo} marca {marca}",
            "identifier" : identifier 
        })

    template = "computer-equipment/print/responsiva.html"
    template = get_template('computer-equipment/print/responsiva.html')

    html = template.render(context2)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="reporte.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Ocurrió un error al generar el PDF', status=400)
    return response

@login_required
def computer_equipment_deliverie_view(request):
    context = user_data(request)
    module_id = 3
    subModule_id = 20

    access = get_module_user_permissions(context, subModule_id)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]
    
    template = "computer-equipment/deliverie.html" if context["access"]["read"] and check_user_access_to_module(request, module_id, subModule_id) else "error/access_denied.html"
    return render(request, template , context)

def computer_equipment_deliverie_pdf_view(request):
    dt = request.GET
    context = user_data(request)
    context2 = {
        'title': 'Entrega de equipo',
        'user': { 'name': 'Nombre del usuario' },
        'data': [],
    }
    context2["data"] = []
    responsible_id = dt.get("user_id")

    if not responsible_id:
        responsible_id = context["user"]["id"]

    datos_usuario = User.objects.filter(id = responsible_id)

    if datos_usuario.exists():
        datos_usuario = datos_usuario.values()[0]
        context2["user"]["name"] = f"{datos_usuario['first_name']} {datos_usuario['last_name']}"

    # Paso 1. Obtener los equipos de computos que tiene el usuario
    datos_1 = ComputerSystem.objects.filter(current_responsible_id = responsible_id).values()
    print(datos_1)
    
    if datos_1:
        for item in datos_1:
            print(item)
            model = item['model'] if item['model'] else "-----"
            serial_number = item['serial_number'] if item['serial_number'] else "-----"
            identifier = item['identifier'] if item['identifier'] else "-----"
            comments = item['comments'] if item['comments'] else "-----"
            context2["data"].append({
                "type": "Equipo",
                "pk": item["id"],
                "fields": {
                    "model": model,
                    "serial_number": serial_number,
                    "identifier": identifier,
                    "comments" : comments
                }
            })

    # Paso 2. Obtener los perifericos que tiene el usuario
    datos_2 = ComputerPeripheral.objects.filter(responsible_id = responsible_id).values()
    print("estos son los datos de peri")
    print(datos_2)
    if datos_2:
        for item in datos_2:
            print(item)
            tipo = item['peripheral_type'] if item['peripheral_type'] else "-----"
            marca = item['brand'] if item['brand'] else "-----"
            model = item['model'] if 'model' in item and item['model'] else "-----"  # Asegura que 'model' existe
            serial_number = item['serial_number'] if 'serial_number' in item and item['serial_number'] else "-----"
            identifier = item['identifier'] if item['identifier'] else "-----"
            comments = item['comments'] if item['comments'] else "-----"
            context2["data"].append({
                "type": "Periférico",
                "pk": item["id"],
                "fields": {
                    "model": tipo,
                    "serial_number": serial_number,
                    "identifier" : identifier,
                    "comments" : comments
                }
            })
    print(json.dumps(context2, indent=4, ensure_ascii=False))


    template = "computer-equipment/print/deliverie.html"
    template = get_template('computer-equipment/print/deliverie.html')

    html = template.render(context2)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="reporte.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Ocurrió un error al generar el PDF', status=400)
    return response


# TODO --------------- [ REQUEST ] ----------

# TODO ----- [ COMPUTO ] -----

def add_computer_system(request):
    context = user_data(request)
    response = {"success": False}
    dt = request.POST
    company_id = context["company"]["id"]

    try:
        obj = ComputerSystem(
            is_active = dt.get("is_active", True),
            company_id = company_id,
            area_id = dt.get("area_id"),
            serial_number = dt.get("serial_number"),
            name = dt.get("name"),
            equipment_type = dt.get("equipment_type"),
            so = dt.get("so"),
            brand = dt.get("brand"),
            model = dt.get("model"),
            processor = dt.get("processor"),
            num_cores = dt.get("num_cores"),
            processor_speed = dt.get("processor_speed"),
            ram = dt.get("ram"),
            ram_type = dt.get("ram_type"),
            ram_speed = dt.get("ram_speed"),
            graphics_card = dt.get("graphics_card"),
            color = dt.get("color"),
            battery = dt.get("battery"),
            warranty = dt.get("warranty"),
            location = dt.get("location"),
            current_responsible_id = dt.get("current_responsible_id"),
            equipment_status = dt.get("equipment_status"),
            comments = dt.get("comments"),
            disk_type = dt.get("disk_type"),
            architecture = dt.get("architecture"),
            disk_capacity = dt.get("disk_capacity"),
        )
        obj.save()
        response["id"] = obj.id
        response["success"] = True
    except Exception as e:
        response["error"] = {"message": str(e)}

    try:
        num_cumputadoras = ComputerSystem.objects.filter(
            company_id = company_id,
            is_active = True
        ).count()
        num_auditorias = ComputerEquipment_Audit.objects.filter(
            computerSystem__company_id = company_id
        ).count()

        print("num_cumputadoras", num_cumputadoras)
        print("num_auditorias", num_auditorias)

        if num_cumputadoras >= 2 and num_auditorias == 0:
            """ Crear auditoria """
            generar_auditoria_de_equipo_de_computo(company_id)
        pass
    except Exception as e:
        pass

    return JsonResponse(response)

def get_computer_equipment(request):
    response = {"success": False}
    context = user_data(request)
    dt = request.GET
    computerSystem_id = dt.get("computerSystem_id", 0)

    datos = ComputerSystem.objects.filter(id = computerSystem_id).values(
        "id", "is_active",
        "company_id", "company__name",
        "area_id", "area__code", "area__name",
        "serial_number",
        "name", "equipment_type",
        "so", "brand", "model",
        "processor", "num_cores", "processor_speed", "architecture",
        "disk_type", "disk_capacity", 
        "ram", "ram_type", "ram_speed", "graphics_card",
        "color", "battery","warranty", "location",
        "current_responsible_id", "current_responsible__username",
        "current_responsible__first_name", "current_responsible__last_name",
        "previous_responsible_id", "previous_responsible__username",
        "previous_responsible__first_name", "previous_responsible__last_name",
        "equipment_status", "last_maintenance_date","comments", "identifier", "adquisition_date",
    )[0]

    response["data"] = datos
    return JsonResponse(response)

def get_computers_equipment(request):
    response = {"success": False}
    context = user_data(request)
    dt = request.GET
    subModule_id = 13
    isList = dt.get("isList", False)
    responsible_id = dt.get("responsible_id")

    datos = ComputerSystem.objects \
    .filter(company_id = context["company"]["id"]) \
    .values(
        "id", "is_active",
        "company_id", "company__name",
        "area_id", "area__code", "area__name",
        "serial_number",
        "name", "equipment_type",
        "so", "brand", "model",
        "processor", "num_cores", "processor_speed", "architecture",
        "disk_type", "disk_capacity", 
        "ram", "ram_type", "ram_speed", "graphics_card",
        "color", "battery","warranty", "location",
        "current_responsible_id", "current_responsible__username",
        "current_responsible__first_name", "current_responsible__last_name",
        "previous_responsible_id", "previous_responsible__username",
        "previous_responsible__first_name", "previous_responsible__last_name",
        "equipment_status", "last_maintenance_date","comments", "identifier", "adquisition_date",
    )

    if context["role"]["id"] not in [1,2,3]:
        datos = datos.filter(current_responsible_id = context["user"]["id"])
    
    if responsible_id and responsible_id != None:
        datos = datos.filter(current_responsible_id = responsible_id)

    if isList:
        datos = datos.values("id", "name")
    else:
        access = get_module_user_permissions(context, subModule_id)
        access = access["data"]["access"]
        for item in datos:
            item["btn_action"] = f"<a href='/computers-equipment/info/{item['id']}/' class='btn btn-icon btn-sm btn-primary-light' data-computer-system='show-info' aria-label='info'>" \
                "<i class=\"fa-solid fa-eye\"></i>" \
            "</a>\n"
            if access["update"]:
                item["btn_action"] += "<button type='button' name='update' class='btn btn-icon btn-sm btn-primary-light' data-computer-system='update-item' aria-label='info'>" \
                    "<i class=\"fa-solid fa-pen\"></i>" \
                "</button>\n"
            if access["delete"]:
                item["btn_action"] += "<button type='button' name='delete' class='btn btn-icon btn-sm btn-danger-light' data-computer-system='dalete-item' aria-label='delete'>" \
                    "<i class='fa-solid fa-trash'></i>" \
                "</button>"

    response["recordsTotal"] = datos.count()
    response["data"] = list(datos)
    return JsonResponse(response)

def update_computer_system(request):
    response = {"success": False}
    dt = request.POST

    computerSystem_id = dt.get("id", None)

    if not computerSystem_id:
        response["error"] = {"message": "No se proporcionó un ID de vehículo válido"}
        return JsonResponse(response)
    
    
    try:
        obj = ComputerSystem.objects.get(id = computerSystem_id)

        db_current_responsible_id = obj.current_responsible_id
        previous_responsible_id = None
        current_responsible_id = None

        if dt.get("current_responsible_id") != db_current_responsible_id:
            previous_responsible_id = db_current_responsible_id
            current_responsible_id = dt.get("current_responsible_id")

        obj.is_active = dt.get("is_active", True)
        obj.area_id = dt.get("area_id")
        obj.serial_number = dt.get("serial_number")
        obj.name = dt.get("name")
        obj.equipment_type = dt.get("equipment_type")
        obj.so = dt.get("so")
        obj.brand = dt.get("brand")
        obj.model = dt.get("model")
        obj.processor = dt.get("processor")
        obj.num_cores = dt.get("num_cores")
        obj.processor_speed = dt.get("processor_speed")
        obj.architecture = dt.get("architecture")
        obj.ram = dt.get("ram")
        obj.ram_type = dt.get("ram_type")
        obj.ram_speed = dt.get("ram_speed")
        obj.graphics_card = dt.get("graphics_card")
        obj.color = dt.get("color")
        obj.battery = dt.get("battery")
        obj.warranty = dt.get("warranty")
        obj.location = dt.get("location")
        obj.previous_responsible_id = previous_responsible_id
        obj.current_responsible_id = current_responsible_id
        obj.equipment_status = dt.get("equipment_status")
        obj.comments = dt.get("comments")
        obj.save()

        response["success"] = True
        response["message"] = "La computadora se actualizó correctamente"
        response["id"] = obj.id
    except ComputerSystem.DoesNotExist:
        response["success"] = False
        response["error"] = {"message": f"No existe ningúna computadora con el ID '{computerSystem_id}'"}
        return JsonResponse(response)
    except Exception as e:
        response["error"] = {"message": str(e)}
    return JsonResponse(response)

def delete_computer_system(request):
    response = {"success": False, "data": []}
    dt = request.POST
    id = dt.get("id", None)

    if id == None:
        response["error"] = {"message": "Proporcione un id valido"}
        return JsonResponse(response)
    try:
        obj = ComputerSystem.objects.get(id = id)
    except ComputerSystem.DoesNotExist:
        response["error"] = {"message": "El objeto no existe"}
        return JsonResponse(response)
    else:
        obj.delete()
    response["success"] = True
    return JsonResponse(response)

# TODO ----- [ PERIFERICOS ] -----

def get_computer_peripherals(request):
    context = user_data(request)
    response = {"success": False, "data": []}
    dt = request.GET
    subModule_id = 14
    isList = dt.get("isList", False)
    responsible_id = dt.get("responsible_id")

    datos = ComputerPeripheral.objects.filter(company_id = context["company"]["id"]).values(
        "id", "company_id",
        "name",
        "peripheral_type", "brand" , "model" ,
        "serial_number" ,
        "description",
        "acquisition_date",
        "location",
        "responsible_id", "responsible__first_name", "responsible__last_name",
        "peripheral_status", "comments","identifier"
    )

    if context["role"]["id"] not in [1,2,3]:
        datos = datos.filter(responsible_id = context["user"]["id"])

    if responsible_id and responsible_id != None:
        datos = datos.filter(responsible_id = responsible_id)

    if isList:
        datos = datos.values("id", "name")
    else:
        access = get_module_user_permissions(context, subModule_id)
        access = access["data"]["access"]
        for item in datos:
            item["btn_action"] = ""
            if access["update"]:
                item["btn_action"] += "<button class=\"btn btn-icon btn-sm btn-primary-light\" data-computer-peripheral=\"update-item\">" \
                    "<i class=\"fa-solid fa-pen\"></i>" \
                "</button>\n"
            if access["delete"]:
                item["btn_action"] += "<button class=\"btn btn-icon btn-sm btn-danger-light\" data-computer-peripheral=\"delete-item\">" \
                    "<i class=\"fa-solid fa-trash\"></i>"
                "</button>"
    response["recordsTotal"] = datos.count()
    response["data"] = list(datos)
    response["success"] = True
    return JsonResponse(response)

def add_computer_peripherals(request):
    context = user_data(request)
    response = {"success": False}
    dt = request.POST
    company_id = context["company"]["id"]

    try:
        obj = ComputerPeripheral(
            company_id = company_id,
            name = dt.get("name"),
            peripheral_type = dt.get("peripheral_type"),
            brand = dt.get("brand"),
            model = dt.get("model"),
            responsible_id = dt.get("responsible_id"),
            serial_number = dt.get("serial_number"),
            description = dt.get("description"),
            acquisition_date = dt.get("acquisition_date"),
            location = dt.get("location"),
            peripheral_status = dt.get("peripheral_status"),
            comments = dt.get("comments")
        )
        obj.save()
        response["id"] = obj.id
        response["success"] = True
    except Exception as e:
        response["error"] = {"message": str(e)}

    return JsonResponse(response)

def update_computer_peripheral(request):
    response = {"success": False}
    dt = request.POST

    id = dt.get("id", None)

    if not id:
        response["error"] = {"message": "No se proporcionó un ID válido"}
        return JsonResponse(response)
    
    try:
        obj = ComputerPeripheral.objects.get(id = id)
        obj.name = dt.get("name")
        obj.peripheral_type = dt.get("peripheral_type")
        obj.brand = dt.get("brand")
        obj.model = dt.get("model")
        obj.serial_number = dt.get("serial_number")
        obj.location = dt.get("location")
        obj.responsible_id = dt.get("responsible_id")
        obj.peripheral_status = dt.get("peripheral_status")
        obj.comments = dt.get("comments")
        obj.save()

        response["success"] = True
        response["message"] = "El periferico se actualizó correctamente"
    except ComputerSystem.DoesNotExist:
        response["error"] = {"message": f"No existe ningúna computadora con el ID '{id}'"}
        return JsonResponse(response)
    except Exception as e:
        response["error"] = {"message": str(e)}
    return JsonResponse(response)

def delete_computer_peripheral(request):
    response = {"success": False, "data": []}
    dt = request.POST
    id = dt.get("id", None)

    if id == None:
        response["error"] = {"message": "Proporcione un id valido"}
        return JsonResponse(response)
    try:
        obj = ComputerPeripheral.objects.get(id = id)
    except ComputerPeripheral.DoesNotExist:
        response["error"] = {"message": "El objeto no existe"}
        return JsonResponse(response)
    else:
        obj.delete()
    response["success"] = True
    return JsonResponse(response)

# TODO ----- [ SOFTWARE ] -----

def add_software(request):
    response = {"success": False}
    context = user_data(request)
    dt = request.POST
    company_id = context["company"]["id"]

    try:
        obj = Software(
            company_id = company_id,
            name = dt.get("name"),
            version = dt.get("version"),
            description = dt.get("description"),
            software_type = dt.get("software_type"),
            max_installations = dt.get("max_installations"),
            function = dt.get("function")
        )
        obj.save()
        response["id"] = obj.id
        response["success"] = True
    except Exception as e:
        response["success"] = False
        response["error"] = {"message": str(e)}
    return JsonResponse(response)

def get_softwares(request):
    context = user_data(request)
    response = {"success": False, "data": []}
    dt = request.GET
    subModule_id = 15
    isList = dt.get("isList", False)


    datos = Software.objects.filter(company_id = context["company"]["id"]).values(
        "id",
        "company_id", "company__name",
        "name", "version", "description", "software_type", 
        "is_unlimited", "max_installations", "function",
        "installation_count"
    )

    if context["role"]["id"] not in [1,2,3]:
        datos = datos.filter(responsible_id = context["user"]["id"])

    if isList:
        datos = datos.values("id", "name")
    else:
        access = get_module_user_permissions(context, subModule_id)
        access = access["data"]["access"]
        for item in datos:
            item["btn_action"] = ""
            if access["update"]:
                item["btn_action"] += "<button class=\"btn btn-icon btn-sm btn-primary-light\" data-computer-software=\"update-item\">" \
                    "<i class=\"fa-solid fa-pen\"></i>" \
                "</button>\n"
            if access["delete"]:
                item["btn_action"] += "<button class=\"btn btn-icon btn-sm btn-danger-light\" data-computer-software=\"delete-item\">" \
                    "<i class=\"fa-solid fa-trash\"></i>"
                "</button>"
    response["recordsTotal"] = datos.count()
    response["data"] = list(datos)
    response["success"] = True
    return JsonResponse(response)

def update_software(request):
    response = {"success": False}
    dt = request.POST

    id = dt.get("id", None)

    if not id:
        response["error"] = {"message": "No se proporcionó un ID válido"}
        return JsonResponse(response)
    
    try:
        obj = Software.objects.get(id = id)
    except Software.DoesNotExist:
        response["error"] = {"message": f"No existe ningúna software con el ID '{id}'"}
    
    try:
        obj.name = dt.get("name")
        obj.version = dt.get("version")
        obj.description = dt.get("description")
        obj.is_unlimited = dt.get("is_unlimited")
        obj.function = dt.get("function", "UWU")
        obj.save()
        

        response["success"] = True
        response["message"] = "Se actualizó correctamente"
    
        return JsonResponse(response)
    except Exception as e:
        response["error"] = {"message": str(e)}
    return JsonResponse(response)

# TODO ----- [ INSTALACIONES DE SOFTWARE ] -----

def add_software_installation(request):
    context = user_data(request)
    response = { "success": False }
    dt = request.POST
    subModule_id = 15

    try:
        obj = SoftwareInstallation(
            software_id = dt.get("software_id"),
            software_identifier = dt.get("software_identifier"),
            computerSystem_id = dt.get("computerSystem_id")
        )
        obj.save()
        response["id"] = obj.id
        response["success"] = True
    except Exception as e:
        response["success"] = False
        response["error"] = {"message": str(e)}
    return JsonResponse(response)

def get_software_installations(request):
    context = user_data(request)
    response = {"success": False, "data": []}
    dt = request.GET
    software_id = dt.get("software_id")
    computerSystem_id = dt.get("computerSystem_id")
    subModule_id = 15

    datos = SoftwareInstallation.objects \
    .filter(software__company_id = context["company"]["id"]) \
    .values(
        "id",
        "software_id",
        "software__function",
        "software__name",
        "software__installation_count",
        "software__version",
        "software__description",
        "computerSystem_id", "computerSystem__name",
        "computerSystem__current_responsible_id",
        "computerSystem__current_responsible__first_name",
        "computerSystem__current_responsible__last_name",
        "software_identifier",
        "installation_date"
    )

    if dt.get("mode") == "computer-to-software":
        datos = datos.filter(computerSystem_id = computerSystem_id)

    if context["role"]["id"] not in [1,2,3]:
        datos = datos.filter(computerSystem__current_responsible_id = context["user"]["id"])
    response["data"] = list(datos)

    access = get_module_user_permissions(context, subModule_id)
    access = access["data"]["access"]
    for item in response["data"]:
        item["btn_action"] = ""
        if access["update"]:
            item["btn_action"] += "<button class=\"btn btn-icon btn-sm btn-primary-light\" data-computer-software=\"update-item-installation\">" \
                "<i class=\"fa-solid fa-pen\"></i>" \
            "</button>\n"
        if access["delete"]:
            item["btn_action"] += "<button class=\"btn btn-icon btn-sm btn-danger-light\" data-computer-software=\"delete-item-installation\">" \
                "<i class=\"fa-solid fa-trash\"></i>"
            "</button>"
        pass
    return JsonResponse(response)

def update_software_installation(request):
    context = user_data(request)
    response = { "success": False }
    dt = request.POST
    subModule_id = 15

    id = dt.get("id", None)

    if not id:
        response["error"] = {"message": "No se proporcionó un ID válido"}
        return JsonResponse(response)
    
    try:
        obj = SoftwareInstallation.objects.get(id = id)
        pass
    except SoftwareInstallation.DoesNotExist:
        response["error"] = {"message": f"No existe ningúna Instalacion con el ID '{id}'"}
        return JsonResponse(response)
    
    try:
        obj.software_id = dt.get("software_id")
        obj.software_identifier = dt.get("software_identifier")
        obj.computerSystem_id = dt.get("computerSystem_id")
        obj.save()

        response["success"] = True
        response["message"] = "El periferico se actualizó correctamente"
    
    except Exception as e:
        response["error"] = {"message": str(e)}

    return JsonResponse(response)

def delete_software_installations(request):
    context = user_data(request)
    response = { "success": False }
    dt = request.POST
    id = dt.get("id")
    subModule_id = 15

    if id == None:
        response["error"] = {"message": "Proporcione un id valido", "id": id}
        return JsonResponse(response)
    try:
        obj = SoftwareInstallation.objects.get(id = id)
    except SoftwareInstallation.DoesNotExist:
        response["error"] = {"message": "El objeto no existe"}
        return JsonResponse(response)
    else:
        obj.delete()
    response["success"] = True
    return JsonResponse(response, status = 200)

# TODO ----- [ AUDITORIA ] -----

def add_computer_equipment_audit(request):
    context = user_data(request)
    response = {"success": False}
    dt = request.POST
    subModule_id = 16

    company_id = context["company"]["id"]
    is_checked = dt.get("is_checked", False)
    is_checked =  True if is_checked == "1" else False

    try:
        obj = ComputerEquipment_Audit(
            computerSystem_id = dt.get("computerSystem_id")
        )
        obj.save()
        response["id"] = obj.id
        response["success"] = True
    except Exception as e:
        response["success"] = False
        response["error"] = {"message": str(e)}

    return JsonResponse(response)

def get_computer_equipment_audits(request):
    context = user_data(request)
    response = {"success": False, "data": []}
    dt = request.GET
    computerSystem_id = dt.get("computerSystem_id")
    subModule_id = 17

    datos = ComputerEquipment_Audit.objects.values(
        "id",
        "computerSystem_id", "computerSystem__name", "computerSystem__serial_number",
        "audit_date",
        "pantalla_check", "pantalla_notas",
        "teclado_check", "teclado_notas",
        "puertos_check", "puertos_notas",
        "cargador_check", "cargador_notas",
        "carcasa_check", "carcasa_notas",
        "limpieza_check", "fecha_ultima_limpieza",
        "general_notes",
        "is_checked", "is_visible",
        "created_at", "updated_at"
    )

    if context["role"]["id"] in [1,2,3]:
        datos = datos.filter(computerSystem__company_id = context["company"]["id"])
    else:
        datos = datos.filter(computerSystem__current_responsible_id = context["user"]["id"])

    if not context["role"]["id"] in [1,2]:
        datos = datos.exclude(is_visible=False)

    if computerSystem_id and computerSystem_id != None:
        datos = datos.filter(computerSystem_id = computerSystem_id)

    access = get_module_user_permissions(context, subModule_id)
    access = access["data"]["access"]
    for item in datos:
        item["btn_action"] = ""
        if (access["create"] or access["update"]) and not item["is_checked"]:
            item["btn_action"] = "<button class=\"btn btn-icon btn-sm btn-primary-light\" data-sia-computer-equipment-audit=\"check-item\" aria-label=\"btn\">" \
                "<i class=\"fa-solid fa-list-check\"></i>" \
            "</button>\n"
        item["btn_action"] += "<button class=\"btn btn-sm btn-primary-light\" data-sia-computer-equipment-audit=\"show-info-details\" aria-label=\"btn\">" \
            "<i class=\"fa-solid fa-eye\"></i>" \
        "</button>\n"
        
        if access["update"]:
            item["btn_action"] += "<button class=\"btn btn-icon btn-sm btn-primary-light\" data-sia-computer-equipment-audit=\"update-item\" aria-label=\"btn\">" \
                "<i class=\"fa-solid fa-pen\"></i>" \
            "</button>\n"
        if access["delete"]:
            item["btn_action"] += "<button class=\"btn btn-icon btn-sm btn-danger-light\" data-sia-computer-equipment-audit=\"delete-item\" aria-label=\"btn\">" \
                "<i class=\"fa-solid fa-trash\"></i>"
            "</button>"
        pass
    response["data"] = list(datos)
    response["success"] = True
    return JsonResponse(response)

def update_computer_equipment_audit(request):
    context = user_data(request)
    response = {"success": False, "data": []}
    dt = request.POST
    subModule_id = 16

    id = dt.get("id")

    if not id:
        response["error"] = {"message": "No se proporcionó un ID de registro válido"}
        return JsonResponse(response)

    company_id = context["company"]["id"]
    is_checked = dt.get("is_checked", False)
    is_checked =  True if is_checked == "1" else False

    try:
        obj = ComputerEquipment_Audit.objects.get(id = id)
        obj.is_checked = is_checked
        if "pantalla_check" in dt and dt["pantalla_check"]: obj.pantalla_check = dt.get("pantalla_check")
        if "pantalla_notas" in dt and dt["pantalla_notas"]: obj.pantalla_notas = dt.get("pantalla_notas")
        if "teclado_check" in dt and dt["teclado_check"]: obj.teclado_check = dt.get("teclado_check")
        if "teclado_notas" in dt and dt["teclado_notas"]: obj.teclado_notas = dt.get("teclado_notas")
        if "puertos_check" in dt and dt["puertos_check"]: obj.puertos_check = dt.get("puertos_check")
        if "puertos_notas" in dt and dt["puertos_notas"]: obj.puertos_notas = dt.get("puertos_notas")
        if "cargador_check" in dt and dt["cargador_check"]: obj.cargador_check = dt.get("cargador_check")
        if "cargador_notas" in dt and dt["cargador_notas"]: obj.cargador_notas = dt.get("cargador_notas")
        if "carcasa_check" in dt and dt["carcasa_check"]: obj.carcasa_check = dt.get("carcasa_check")
        if "carcasa_notas" in dt and dt["carcasa_notas"]: obj.carcasa_notas = dt.get("carcasa_notas")
        if "general_notes" in dt and dt["general_notes"]: obj.general_notes = dt.get("general_notes")

        obj.save()
        response["success"] = True
    except ComputerEquipment_Audit.DoesNotExist:
        response["error"] = {"message": f"No existe ningúna Auditoria con el ID '{id}'"}
    except ValidationError as e:
        response["error"] = {"message": e.message_dict}
    except Exception as e:
        response["success"] = False
        response["error"] = {"message": str(e)}

    try:
        generar_auditoria_de_equipo_de_computo(company_id)
    except Exception as e:
        pass

    return JsonResponse(response)

def delete_computer_equipment_audit(request):
    context = user_data(request)
    response = { "success": False }
    dt = request.POST
    id = dt.get("id")
    subModule_id = 16

    if id == None:
        response["error"] = {"message": "Proporcione un id valido", "id": id}
        return JsonResponse(response)
    try:
        obj = ComputerEquipment_Audit.objects.get(id = id)
    except ComputerEquipment_Audit.DoesNotExist:
        response["error"] = {"message": "El objeto no existe"}
        return JsonResponse(response)
    else:
        obj.delete()
    response["success"] = True
    return JsonResponse(response)

# TODO ----- [ MANTENIMIENTO ] -----

def add_computer_equipment_maintenance(request):
    context = user_data(request)
    response = {"success": False, "data": []}
    dt = request.POST
    subModule_id = 17

    company_id = context["company"]["id"]
    array = dt.getlist("actions[]")
    actions = {accion: "PENDIENTE" for accion in array}
    actions = str(actions)

    try:
        with transaction.atomic():
            obj = ComputerEquipment_Maintenance(
                performed_by = dt.get("performed_by"),
                # user_id = dt.get("user_id")
                provider_id = dt.get("provider_id"),
                type = dt.get("type"),
                cost = dt.get("cost"),
                actions = actions,
                is_checked = False,
                date = dt.get("date")
            )
            obj.save()
            id = obj.id

            if 'document' in request.FILES and request.FILES['document']:
                load_file = request.FILES['document']
                folder_path = f"docs/{company_id}/computers-equipment/{id}/maintenance/"
                fs = FileSystemStorage(location=settings.MEDIA_ROOT)

                file_name, extension = os.path.splitext(load_file.name)
                new_name = f"doc_{id}{extension}"

                # Guardar archivo
                fs.save(folder_path + new_name, load_file)

                # Guardar ruta en la tabla
                obj.document = folder_path + new_name
                obj.save()

            response["id"] = id
        response["success"] = True
    except ValidationError as e:
        response["error"] = {"message": e.message_dict}
    except Exception as e:
        response["success"] = False
        response["error"] = {"message": str(e)}
    return JsonResponse(response)

def get_computer_equipment_maintenances(request):
    context = user_data(request)
    response = {"success": False, "data": []}
    dt = request.GET
    computerSystem_id = dt.get("computerSystem_id")
    subModule_id = 17

    datos = ComputerEquipment_Maintenance.objects.values(
        "id",
        "computerSystem_id", "computerSystem__name", "computerSystem__serial_number",
        "performed_by",
        "provider_id", "provider__name",
        "user_id",
        "type", "cost", "actions",
        "is_checked", "date", "document",
    )

    if computerSystem_id and computerSystem_id != None:
        datos = datos.filter(computerSystem_id = computerSystem_id)

    access = get_module_user_permissions(context, subModule_id)
    access = access["data"]["access"]
    for item in datos:
        item["btn_action"] = "<button class=\"btn btn-icon btn-sm btn-primary-light\" data-sia-computer-equipment-maintenance=\"show-info-details\">" \
            "<i class=\"fa-solid fa-eye\"></i>" \
        "</button>\n"
        if access["update"]:
            item["btn_action"] += "<button class=\"btn btn-icon btn-sm btn-primary-light\" data-sia-computer-equipment-maintenance=\"update-item\">" \
                "<i class=\"fa-solid fa-pen\"></i>" \
            "</button>\n"
        if access["delete"]:
            item["btn_action"] += "<button class=\"btn btn-icon btn-sm btn-danger-light\" data-sia-computer-equipment-maintenance=\"delete-item\">" \
                "<i class=\"fa-solid fa-trash\"></i>"
            "</button>"
        pass
    response["data"] = list(datos)
    response["success"] = True
    return JsonResponse(response)

def update_computer_equipment_maintenance(request):
    context = user_data(request)
    response = {"success": False, "data": []}
    dt = request.POST
    subModule_id = 17

    id = dt.get("id")

    if not id:
        response["error"] = {"message": "No se proporcionó un ID de registro válido"}
        return JsonResponse(response)

    company_id = context["company"]["id"]
    is_checked = dt.get("is_checked", False)
    is_checked =  True if is_checked == "true" else False
    if dt.getlist("actions[]"):
        array = dt.getlist("actions[]")
        actions = {accion: "PENDIENTE" for accion in array}
        actions = str(actions)
    elif "actionsformat2" in dt:
        actions = dt["actionsformat2"]
    else:
        actions = ""

    try:
        obj = ComputerEquipment_Maintenance.objects.get(id = id)
        if "type" in dt and dt["type"]: obj.type = dt.get("type")
        if "performed_by" in dt and dt["performed_by"]: obj.performed_by = dt.get("performed_by")
        if "cost" in dt and dt["cost"]: obj.cost = dt.get("cost")
        if "date" in dt and dt["date"]: obj.date = dt.get("date")
        # if "is_checked" in dt and dt["is_checked"]: obj.is_checked = dt.get("is_checked")

        # obj.user_id = dt.get("user_id")
        # obj.provider_id = dt.get("provider_id")
        obj.is_checked = is_checked
        obj.actions = actions
        obj.save()
        response["success"] = True
    except ValidationError as e:
        response["error"] = {"message": e.message_dict}
    except Exception as e:
        response["success"] = False
        response["error"] = {"message": str(e)}
    return JsonResponse(response)

def delete_computer_equipment_maintenance(request):
    response = {"success": False, "data": []}
    dt = request.POST
    id = dt.get("id", None)

    if id == None:
        response["error"] = {"message": "Proporcione un id valido"}
        return JsonResponse(response)
    try:
        obj = ComputerEquipment_Maintenance.objects.get(id = id)
    except ComputerEquipment_Maintenance.DoesNotExist:
        response["error"] = {"message": "El objeto no existe"}
        return JsonResponse(response)
    else:
        obj.delete()
    response["success"] = True
    return JsonResponse(response)



def add_computer_equipment_responsiva(request):
    context = user_data(request)
    response = {"status": "error", "message": "sin procesar" }
    dt = request.POST
    company_id = context["company"]["id"]

    try:
        responsible_id = dt.get("responsible_id")

        if responsible_id == None:
            response["message"] = "Sin Responsable"
            return JsonResponse(response)
        
        responsable = User_Access.objects.filter(user_id = responsible_id)

        if not responsable.exists():
            response["message"] = "El responsable no existe"
            return JsonResponse(response)

        responsable = responsable.values()[0]
        area_id = responsable["area_id"]

        registro = ComputerEquipment_Responsiva.objects.filter(responsible_id = responsible_id).count()

        if registro >= 1:
            response["message"] = f"Ya existen {registro} regitro(s) de la responsibla del usuario asignado"
            return JsonResponse(response)


        with transaction.atomic():
            obj = ComputerEquipment_Responsiva(
                responsible_id = responsible_id,
                area_id = area_id
            )
            obj.save()
            id = obj.id

        if 'responsibility_letter' in request.FILES and request.FILES['responsibility_letter']:
            load_file = request.FILES.get('responsibility_letter')
            folder_path = f"docs/{company_id}/computers-equipment/responsiva/{id}/"
            #fs = FileSystemStorage(location=settings.MEDIA_ROOT)

            file_name, extension = os.path.splitext(load_file.name)
            new_name = f"doc_1{extension}"
            s3Name = folder_path + new_name

            # Guardar archivo
            upload_to_s3(load_file, AWS_BUCKET_NAME, s3Name)
            #fs.save(folder_path + new_name, load_file)

            # Guardar ruta en la tabla
            obj.responsibility_letter = s3Name
            # obj.save()

            # Cargar y actualizar el historial existente
            try:
                historial = json.loads(obj.record)
            except (ValueError, TypeError):
                historial = []

            # Agregar el nuevo registro al historial
            count = len(historial) + 1
            historial.append({
                "id": count,
                "file_path": str(obj.responsibility_letter),
                "date": datetime.now().isoformat()
            })

            # Convertir el historial actualizado a cadena JSON
            historial_str = json.dumps(historial)
            obj.record = historial_str
            obj.save()
            response["id"] = id
        response["status"] = "success"
        response["message"] = "Guardado"
    except ValidationError as e:
        response["status"] = "error"
        response["message"] = e.message_dict
    except Exception as e:
        response["status"] = "error"
        response["message"] = str(e)
    return JsonResponse(response)


def get_computer_equipment_responsiva(request):
    context = user_data(request)
    response = {"status": "error", "message": "sin procesar", "data": [] }
    dt = request.GET
    isList = dt.get("isList", False)
    subModule_id = 19

    datos = ComputerEquipment_Responsiva.objects.values(
        "id",
        "responsible_id", "responsible__first_name", "responsible__last_name",
        "area_id", "area__name",
        "items",
        "responsibility_letter",
        "record",
        "created_at",
        "updated_at"
    )

    modified_data_list = []

    for data in datos:
        modified_data = data.copy()
        
        # Convertir record de JSON a lista de diccionarios
        record_string = data.get('record', '[]')  # Evita errores si record es None
        try:
            record_data = json.loads(record_string)
        except json.JSONDecodeError:
            record_data = []  # Si hay un error en el JSON, se deja vacío
        
        # Modificar cada file_path en la lista de records
        for record in record_data:
            file_path = record.get('file_path')
            if file_path:
                record['file_path'] = generate_presigned_url(AWS_BUCKET_NAME, file_path)

        # Convertir de nuevo a JSON
        modified_data['record'] = json.dumps(record_data)

        # Si también quieres actualizar responsibility_letter, puedes asignarlo al primer archivo
        if record_data:
            modified_data['responsibility_letter'] = record_data[-1].get('file_path')
        else:
            modified_data['responsibility_letter'] = data.get('responsibility_letter', None)
        modified_data_list.append(modified_data)

    if isList:
        datos = datos.values("id", "responsible_id", "responsible__first_name", "responsible__last_name")
    else:
        access = get_module_user_permissions(context, subModule_id)
        access = access["data"]["access"]
        for item in modified_data_list:
            item["btn_action"] = ""
            if access["update"]:
                item["btn_action"] += "<button class=\"btn btn-icon btn-sm btn-primary-light\" data-sia-computer-equipment-responsiva=\"update-item\" aria-label=\"Update\">" \
                    "<i class=\"fa-solid fa-pen\"></i>" \
                "</button>\n"
            if access["delete"]:
                item["btn_action"] += "<button class=\"btn btn-icon btn-sm btn-danger-light\" data-sia-computer-equipment-responsiva=\"delete-item\" aria-label=\"Delete\">" \
                    "<i class=\"fa-solid fa-trash\"></i>" \
                "</button>"

    response["data"] = list(modified_data_list)
    response["status"] = "success"
    return JsonResponse(response)


def update_computer_equipment_responsiva(request):
    context = user_data(request)
    response = {"status": "error", "message": "sin procesar"}
    dt = request.POST
    id = dt.get("id")
    company_id = context["company"]["id"]

    try:
        responsible_id = dt.get("responsible_id")

        if responsible_id == None:
            response["message"] = "Sin Responsable"
        
        responsable = User_Access.objects.filter(user_id = responsible_id)

        if not responsable.exists():
            response["message"] = "El responsable no existe"

        responsable = responsable.values()[0]
        area_id = responsable["area_id"]

        #print("ANtes de with")

        with transaction.atomic():
            obj = ComputerEquipment_Responsiva.objects.get(id = id)
            obj.responsible_id = responsible_id
            obj.area_id = area_id
            obj.save()
            # id = obj.id
            # id_str = str(id)

            if 'responsibility_letter' in request.FILES and request.FILES['responsibility_letter']:
                load_file = request.FILES.get('responsibility_letter')
                folder_path = f"docs/{company_id}/computers-equipment/responsiva/{id}/"
                #fs = FileSystemStorage(location=settings.MEDIA_ROOT)
                
                # Crear la ruta completa del directorio
                #full_folder_path = os.path.join(settings.MEDIA_ROOT, folder_path)

                # Crear el directorio si no existe
                #if not os.path.exists(full_folder_path):
                #    os.makedirs(full_folder_path)

                # Contar archivos en el directorio
                #existing_files = os.listdir(full_folder_path)
                #file_count = len(existing_files)
                # Cargar y actualizar el historial existente
                try:
                    historial = json.loads(obj.record)
                except (ValueError, TypeError):
                    historial = []

                file_name, extension = os.path.splitext(load_file.name)
                new_name = f"doc_{len(historial)+1}{extension}"
                s3name = folder_path + new_name

                # Guardar archivo
                upload_to_s3(load_file, AWS_BUCKET_NAME, s3name)
                #fs.save(os.path.join(folder_path, new_name), load_file)

                # Guardar ruta en la tabla
                obj.responsibility_letter = os.path.join(folder_path, new_name)
                obj.save()

                

                # Agregar el nuevo registro al historial
                historial.append({
                    "id": len(historial) + 1,
                    "file_path": str(obj.responsibility_letter),
                    "date": datetime.now().isoformat()
                })

                # Convertir el historial actualizado a cadena JSON
                historial_str = json.dumps(historial)
                obj.record = historial_str
                obj.save()
                # End
            response["id"] = id
        response["status"] = "success"
        response["message"] = "Guardado"
    except ComputerEquipment_Responsiva.DoesNotExist:
        response["error"] = {"message": f"No existe ningún registro con el ID '{id}'"}
        return JsonResponse(response)
    except ValidationError as e:
        response["status"] = "error"
        response["message"] = e.message_dict
    except Exception as e:
        response["status"] = "error"
        response["message"] = str(e)
    return JsonResponse(response)

def delete_computer_equipment_responsiva(request):
    response = {"success": False, "data": []}
    dt = request.POST
    id = dt.get("id", None)

    if id == None:
        response["error"] = {"message": "Proporcione un id valido"}
        response["status"] = "error"
        response["message"] = "Proporcione un id valido"
        return JsonResponse(response)
    try:
        obj = ComputerEquipment_Responsiva.objects.get(id = id)
    except ComputerEquipment_Responsiva.DoesNotExist:
        response["error"] = {"message": "El objeto no existe"}
        response["status"] = "error"
        response["message"] = "El objeto no existe"
        return JsonResponse(response)
    else:
        obj.delete()
    response["success"] = True
    response["status"] = "success"
    response["message"] = "Se ha borrado el registro"
    return JsonResponse(response)


# TODO ----- [ EQUIPOS ASIGNADOS U EQUIPOS OCUPADOS ] -----

def get_users_with_assigned_computer_equipment(request):
    context = user_data(request)
    response = { "success": False, "data": [] }

    unique_user_ids = ComputerSystem.objects \
                .values_list('current_responsible', flat=True)\
                .distinct() \
                .exclude(current_responsible = None)
    
    usuarios = User.objects.filter(id__in=unique_user_ids).values("id", "username", "first_name", "last_name",)
    response["success"] = True
    response["data"] = list(usuarios)
    return JsonResponse(response)

def add_computer_equipment_deliverie(request):
    context = user_data(request)
    response = { "status": "error", "message": "Solicitud sin procesar" }
    #print(context)
    dt = request.POST
    subModule_id = 20
    company_id = context["company"]["id"]
    responsible_id = dt.get("responsible_id")


    if responsible_id == None:
        response["status"] = "error"
        response["message"] = "Sin responsable"
        return JsonResponse(response)
        
    try:
        with transaction.atomic():
            obj = ComputerEquipment_Deliveries(
                responsible_id = responsible_id
            )
            print(f'segundo id: {obj}')
            obj.save()
            response["id"] = obj.id
            id = response["id"]

            if 'responsibility_letter' in request.FILES and request.FILES['responsibility_letter']:
                load_file = request.FILES.get('responsibility_letter')
                folder_path = f"docs/{company_id}/computers-equipment/deliveries/"
                #fs = FileSystemStorage(location=settings.MEDIA_ROOT)

                file_name, extension = os.path.splitext(load_file.name)
                new_name = f"doc_{id}{extension}"
                s3Name = folder_path + new_name

                # Eliminar archivo en caso de existir duplicado
                #old_files = glob.glob(os.path.join(settings.MEDIA_ROOT, folder_path, f"doc_{id}.*"))
                #for old_file_path in old_files:
                #    if os.path.exists(old_file_path):
                #        os.remove(old_file_path)

                # Guardar archivo
                #fs.save(folder_path + new_name, load_file)
                upload_to_s3(load_file, AWS_BUCKET_NAME, s3Name)

                # Guardar ruta en la tabla
                obj.responsibility_letter = folder_path + new_name
                obj.save()
        response["status"] = "success"
        response["message"] = "Guardado exitosamente"
    except Exception as e:
        response["status"] = "error"
        response["message"] = str(e)
    return JsonResponse(response)

def get_computer_equipment_deliveries(request):
    context = user_data(request)
    response = { "success": False, "data": [] }
    subModule_id = 20

    datos = ComputerEquipment_Deliveries.objects.values(
        "id",
        "responsibility_letter",
        "responsible_id", "responsible__first_name", "responsible__last_name",
    )

    modified_data_list = []

    for data in datos:
        modified_data = data.copy()

        file_path = data.get('responsibility_letter')
        tempLetterPath = generate_presigned_url(AWS_BUCKET_NAME, file_path)
        modified_responsibility_letter = tempLetterPath
        
        modified_data['responsibility_letter'] = modified_responsibility_letter
        modified_data_list.append(modified_data)

    response["success"] = True

    access = get_module_user_permissions(context, subModule_id)
    access = access["data"]["access"]
    for item in modified_data_list:
        item["btn_action"] = ""
        if access["update"]:
            item["btn_action"] += "<button class=\"btn btn-icon btn-sm btn-primary-light\" data-sia-computer-equipment-deliverie=\"update-item\" aria-label=\"Update\">" \
                "<i class=\"fa-solid fa-pen\"></i>" \
            "</button>\n"
        if access["delete"]:
            item["btn_action"] += "<button class=\"btn btn-icon btn-sm btn-danger-light\" data-sia-computer-equipment-deliverie=\"delete-item\" aria-label=\"Delete\">" \
                "<i class=\"fa-solid fa-trash\"></i>" \
            "</button>"
        pass
    response["data"] = list(modified_data_list)
    return JsonResponse(response)

def update_computer_equipment_deliverie(request):
    context = user_data(request)
    response = { "status": "error", "message": "Solicitud sin procesar" }
    dt = request.POST
    subModule_id = 20
    company_id = context["company"]["id"]
    responsible_id = dt.get("responsible_id")
    id = dt.get("id")

    if responsible_id == None:
        response["status"] = "error"
        response["message"] = "Sin responsable"
        return JsonResponse(response) 
    try:
        obj = ComputerEquipment_Deliveries.objects.get(id = id)

        obj.responsible_id = responsible_id,
        obj.save()
        response["id"] = obj.id
        response["status"] = "success"
        response["message"] = "actualizado correctamente"
    except Exception as e:
        response["status"] = "error"
        response["message"] = str(e)
    return JsonResponse(response)

def delete_computer_equipment_deliverie(request):
    response = { "status": "error", "message": "Solicitud sin procesar" }
    dt = request.POST
    id = dt.get("id", None)

    if id == None:
        response["error"] = {"message": "Proporcione un id valido"}
        return JsonResponse(response)
    try:
        obj = ComputerEquipment_Deliveries.objects.get(id = id)
    except ComputerEquipment_Deliveries.DoesNotExist:
        response["error"] = {"message": "El objeto no existe"}
        return JsonResponse(response)
    else:
        obj.delete()
    response["success"] = True
    return JsonResponse(response)


# TODO ----- [ NEXT ] -----    

# TODO --------------- [ HELPERS ] ----------
def upload_to_s3(file_name, bucket_name, object_name=None):
    """Upload a file to an S3 bucket.

    :param file_name: File to upload
    :param bucket_name: S3 bucket name
    :param object_name: S3 object name. If not specified, file_name is used
    :return: True if file was uploaded, else False
    """
    extension = file_name.name.split(".")[-1]
    print(extension)

    #print(file_name)
    #print(f'EXTENSION del archivo: {extension.split(".")[-1]}')
    s3 = boto3.client('s3', region_name='us-east-2', config=Config(signature_version='s3v4'))
    boto3.client('s3', region_name='us-east-2', config=Config(signature_version='s3v4'))
    if object_name is None:
        object_name = file_name.name

    try:
        if isinstance(file_name, io.BytesIO):
            print("The object is of type io.BytesIO")
        else:
            print("The object is NOT of type io.BytesIO")
            validate_image(file_name)
        #if extension != "zip":
        s3.upload_fileobj(file_name, bucket_name, object_name)
        print(f"File '{file_name}' uploaded to '{bucket_name}/{object_name}'")
        return True
    except FileNotFoundError:
        print("The file was not found.")
        return False
    except NoCredentialsError:
        print("Credentials not available.")
        return False

    
def generate_presigned_url(bucket_name, object_name, expiration=3600):
    s3 = boto3.client('s3', region_name='us-east-2', config=Config(signature_version='s3v4'))
    boto3.client('s3', region_name='us-east-2', config=Config(signature_version='s3v4'))
    return s3.generate_presigned_url('get_object',Params={'Bucket': bucket_name, 'Key': object_name}, ExpiresIn=expiration)

def validate_image(file):
    # Check file size (e.g., max 5 MB)
    if file.size > 10 * 1024 * 1024:
        raise ValidationError("Image file is too large ( > 10 MB ).")
    # Check content type (e.g., only allow PNG and JPEG)
    if file.content_type not in ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf']:
        raise ValidationError("Only JPEG, PNG and PDF files are allowed.")

def is_valid_file_type(file_name):
    """Check if the file is of an allowed type based on extension."""
    # Get the file extension
    file_extension = mimetypes.guess_extension(file_name.content_type)
    
    if file_extension and file_extension.lower() in ALLOWED_FILE_EXTENSIONS:
        return True
    return False

def delete_s3_object(bucket_name, object_name):
    """Delete an object from an S3 bucket.

    :param bucket_name: The name of the S3 bucket
    :param object_name: The name (key) of the object to delete
    :return: True if object was deleted, else False
    """
    # Initialize an S3 client
    s3 = boto3.client('s3')
    
    try:
        # Delete the object
        response = s3.delete_object(Bucket=bucket_name, Key=object_name)
        print(f"Object '{object_name}' deleted from bucket '{bucket_name}'.")
        return True
    except ClientError as e:
        print(f"Error occurred while deleting object: {e}")
        return False

def generar_auditoria_de_equipo_de_computo(company_id):
    response = { "success": False }

    try:
        # Obtener el objetos de los equipos de computo de la empresa
        obj_computerEquipment = ComputerSystem.objects.filter(
            company_id = company_id
        )

        # Obtener auditorias de los equipos de computo
        obj_audit = ComputerEquipment_Audit.objects.filter(
            computerSystem__company_id = company_id
        )

        obj_audit_no_check = obj_audit.filter(
            is_checked = False
        )

        if obj_audit_no_check.exists():
            response["success"] = False
            response["error"] = {"message": "Aún hay auditorías pendientes"}
            print("[SIA] Aún hay auditorías pendiente")
            return response

        """ Generar las nuevas auditorias """
        list_id_computerEquipment = list(obj_computerEquipment.values_list("id", flat=True))
        random.shuffle(list_id_computerEquipment)

        count = len(list_id_computerEquipment)
        partes_completas = count // AUDITORIA_EQUIPOS_COMPUTO_POR_SEMANA
        residuo = count % AUDITORIA_EQUIPOS_COMPUTO_POR_SEMANA
        total_partes = partes_completas + (1 if residuo != 0 else 0)

        # Obtener la fecha actual
        fecha_actual = datetime.now()
        
        # Calcular el número de días que debemos retroceder para llegar al último domingo
        dias_para_domingo = fecha_actual.weekday() + 1

        # Retroceder al último domingo
        ultimo_domingo = fecha_actual - timedelta(days=dias_para_domingo)

        # Calcular la fecha de inicio restando múltiplos de 7 días según sea necesario
        fecha_inicio = ultimo_domingo - timedelta(days=7 * total_partes)

        # [ message ]
        list_id_computerEquipment_auditados = obj_audit.filter(
            audit_date__gte=fecha_inicio,
            audit_date__lte=fecha_actual
        ).values_list("computerSystem_id", flat=True)

        # Buscar equipo de computos que aun no han sido auditados
        computerEquipment_no_auditados = set(list_id_computerEquipment) - set(list_id_computerEquipment_auditados)
        computerEquipment_no_auditados = list(computerEquipment_no_auditados)
        computerEquipment_no_auditados = computerEquipment_no_auditados[:AUDITORIA_EQUIPOS_COMPUTO_POR_SEMANA]

        # Rellenar en caso de faltar equipos para x numero de auditorias de la semana
        if len(computerEquipment_no_auditados) < AUDITORIA_EQUIPOS_COMPUTO_POR_SEMANA:
            for item in list_id_computerEquipment:
                if item not in computerEquipment_no_auditados:
                    computerEquipment_no_auditados.append(item)
                if len(computerEquipment_no_auditados) == AUDITORIA_EQUIPOS_COMPUTO_POR_SEMANA: break

        # ! Paso 2: generar fecha random para la auditoria de la semana

        # Función para obtener el rango de fechas de una semana dada una fecha base
        def obtener_semana(fecha):
            inicio_semana = fecha - timedelta(days=(fecha.weekday() + 1) % 7)
            return [inicio_semana + timedelta(days=i) for i in range(7)]
        
        # Función para obtener solo los días hábiles (lunes a viernes) de una semana
        def obtener_dias_habiles(semana):
            return [dia for dia in semana if dia.weekday() < 5]
        
        # Calcular la semana siguiente
        semana_siguiente = obtener_semana(fecha_actual + timedelta(days=7))

        # Obtener solo los días hábiles de la semana siguiente
        dias_habiles = obtener_dias_habiles(semana_siguiente)

        # Elegir un día al azar de los días hábiles de la siguiente semana
        dia_aleatorio = random.choice(dias_habiles)

        # ! Paso 3: Dar de alta la auditoria del equipo de computo

        for id in computerEquipment_no_auditados:
            obj = ComputerEquipment_Audit(
                computerSystem_id = id,
                audit_date = dia_aleatorio
            )
            obj.save()

        print("[SIA] Auditoría de Equipos de Cómputo Generada Exitosamente")
        print("[SIA] Id de los Equipos de Cómputo", computerEquipment_no_auditados)
        response["success"] = True
    except Exception as e:
        response["success"] = False
        response["error"] = {"message": str(e)}
    return response



def generate_qr_computer(request, qr_type, computerSystemId):
    try:
        context = user_data(request)
        company_id = context["company"]["id"]
        computer = get_object_or_404(ComputerSystem, id=computerSystemId)

        print(f"Generando QR para el equipo con ID: {computerSystemId}")

        if qr_type == "info" and computer.qr_info_computer:
            qr_url_info = generate_presigned_url(AWS_BUCKET_NAME, str(computer.qr_info_computer))
            print(f"QR ya generado. URL: {qr_url_info}")
            return JsonResponse({'status': 'generados', 'qr_url_info': qr_url_info})

        if qr_type == 'info':
            domain = request.build_absolute_uri('/')[:-1]  # Obtiene el dominio dinámicamente
            qr_content = f"{domain}/computers-equipment/info/{computerSystemId}/"
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid QR type'}, status=400)

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_content)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        s3Path = f'docs/{company_id}/computers-equipment/{computerSystemId}/qr/'
        s3Name = f"qr_info{computerSystemId}.png"
        full_s3_path = s3Path + s3Name

        print(f"Subiendo el QR a S3 en la ruta: {full_s3_path}")
        computer.qr_info_computer = full_s3_path

        img_file = InMemoryUploadedFile(
            buffer, None, s3Name, 'image/png', buffer.getbuffer().nbytes, None
        )

        upload_to_s3(img_file, AWS_BUCKET_NAME, full_s3_path)
        computer.save()

        print(f"QR guardado en la base de datos con URL: {full_s3_path}")
        qr_url = generate_presigned_url(AWS_BUCKET_NAME, full_s3_path)
        print(f"Generando URL del QR en S3: {qr_url}")

        return JsonResponse({'status': 'success', 'qr_url': qr_url})
    
    except Exception as e:
        print(f"Error al generar el QR: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)



def check_qr_computer(request, computerSystemId):
    try:
        computer = get_object_or_404(ComputerSystem, id=computerSystemId)

        if computer.qr_info_computer:
            qr_url_info = generate_presigned_url(AWS_BUCKET_NAME, str(computer.qr_info_computer))
            return JsonResponse({'status': 'success', 'qr_url_info': qr_url_info})
        else:
            return JsonResponse({'status': 'error', 'message': 'QR no generado'})
    except ComputerSystem.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Equipo no encontrado'}, status=404)



#funcion para descargar el qr
def descargar_qr_computer(request):
    try:
        id_computer = request.GET.get("computerSystemId")
        tipo_qr = request.GET.get("type")  

        computer = ComputerSystem.objects.filter(id=id_computer).first()
        if not computer:
            return JsonResponse({'error': 'Equipo no encontrado'}, status=404)

        if tipo_qr == "info":
            if not computer.qr_info_computer:
                return JsonResponse({'error': 'QR no generado'}, status=404)
            
            url_computer = computer.qr_info_computer  
        else:
            return JsonResponse({'error': 'Tipo de QR no válido'}, status=400)

        url_s3 = generate_presigned_url(AWS_BUCKET_NAME, str(url_computer))
        return JsonResponse({'url_computer': url_s3})
    
    except Exception as e:
        print(f"Error al descargar el QR: {e}")
        return JsonResponse({'error': str(e)}, status=500)


#funcion para eliminar el qr
def delete_qr_computer(request, qr_type, computerSystemId):
    computer = get_object_or_404(ComputerSystem, id=computerSystemId)
    url = ""
    if qr_type == 'info' and computer.qr_info_computer:
        url = str(computer.qr_info_computer)
        computer.qr_info_computer.delete()
    elif qr_type == 'access' and computer.qr_access:
        url = str(computer.qr_access)
        computer.qr_access.delete()
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid QR type or QR does not exist'}, status=400)
    
    delete_s3_object(AWS_BUCKET_NAME, url)
    return JsonResponse({'status':'success'})


# END