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
from datetime import datetime, timedelta
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

dotenv_path = join(dirname(dirname(__file__)), 'awsCred.env')
load_dotenv(dotenv_path)

# TODO --------------- [ VARIABLES ] ---------- 

AUDITORIA_VEHICULAR_POR_MES = 2
AWS_ACCESS_KEY_ID=os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY=os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_DEFAULT_REGION=os.environ.get('AWS_DEFAULT_REGION')
AWS_BUCKET_NAME=str(os.environ.get('AWS_BUCKET_NAME'))
bucket_name=AWS_BUCKET_NAME

ALLOWED_FILE_EXTENSIONS = ['.jpg', '.jpeg', '.png']

#s3 = boto3.client('s3', config=Config(signature_version='s3v4'))
#s3 = boto3.client('s3', region_name='us-east-2', config=Config(signature_version='s3v4'))
boto3.client('s3', region_name='us-east-2', config=Config(signature_version='s3v4'))
#boto3.set_stream_logger('')
#s3 = boto3.client('s3')
#session = boto3.session.Session(region_name='us-east-2')
#s3client = session.client('s3', config= boto3.session.Config(signature_version='s3v4'))

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
    print('Estos son los permisos')
    print(access)
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
def module_vehicle_responsiva(request):
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

# TODO --------------- [ HELPER ] ----------

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
            #print(f"nombre del bucket {bucket_name}")
            #print(f"nombre del folder {load_file.name}")
            #print(f"nombre del archivo {load_file}")
            #print(f"access key {AWS_ACCESS_KEY_ID}")
            #print(f"aws region {AWS_DEFAULT_REGION}")
            #print(f"secret access key {AWS_SECRET_ACCESS_KEY}")
            
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
    print(f'database route{data["image_path"]}')
    data["image_path"] = tempImgPath
    print(f'S3 rute{tempImgPath}')
    print(f'S3 rute{tempImgPath}')
    
    response["data"] = data
    response["success"] = True
    response["imgPath"] = tempImgPath
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
            #item["image_path"] = "/" + item["image_path"]
            tempImgPath = generate_presigned_url(bucket_name, item["image_path"])
            item["image_path"] = tempImgPath
            #print(item["image_path"])
            #print(generate_presigned_url(bucket_name, item["image_path"]))
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
    print("este es el id: ")
    print(id)
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
                
                new_name = f"signature{extension}"
                s3Name = folder_path + new_name
                #fs.save(folder_path + new_name, load_file)

                obj.signature = folder_path + new_name
                upload_to_s3(load_file, bucket_name, s3Name)
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
        response["status"] = "success"
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

                print("upload succed")

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
    if not context["role"]["id"] in [1,2,3]:
        lista = lista.exclude(is_visible=False)

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
    print("este es el tipo de usuario:")
    print(tipo_user)

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
                load_file = request.FILES['payment_receipt']
                folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/fuel/"
                fs = FileSystemStorage(location=settings.MEDIA_ROOT)

                file_name, extension = os.path.splitext(load_file.name)                
                new_name = f"payment_receipt_{id}{extension}"

                # Eliminar archivos anteriores usando glob
                old_files = glob.glob(os.path.join(settings.MEDIA_ROOT, folder_path, f"payment_receipt{id}.*"))
                for old_file_path in old_files:
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                fs.save(folder_path + new_name, load_file)
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
                load_file = request.FILES['payment_receipt']
                folder_path = f"docs/{company_id}/vehicle/{vehicle_id}/fuel/"
                fs = FileSystemStorage(location=settings.MEDIA_ROOT)

                file_name, extension = os.path.splitext(load_file.name)                
                new_name = f"payment_receipt_{id}{extension}"

                # Eliminar archivos anteriores usando glob
                old_files = glob.glob(os.path.join(settings.MEDIA_ROOT, folder_path, f"payment_receipt{id}.*"))
                for old_file_path in old_files:
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                fs.save(folder_path + new_name, load_file)
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
        obj.delete()
    response["success"] = True
    return JsonResponse(response)



@csrf_exempt
def add_option(request):
    if request.method == 'POST':
        try:
            print('Recibiendo petición POST')
            
            # Cargar datos del cuerpo del request
            data = json.loads(request.body)
            print(f'Datos recibidos: {data}')
            
            option_name = data.get('option_maintenance_name', '').strip()
            maintenance_type = data.get('maintenance_type', '').strip()

            if not option_name or not maintenance_type:
                print('Datos faltantes en el request')
                return JsonResponse({'status': 'error', 'message': 'Faltan datos necesarios'}, status=400)

            print(f"Se va a agregar la opción: {option_name}")
            print(f"Tipo de mantenimiento: {maintenance_type}")

            # Definir la ruta del archivo JSON
            directorio_actual = os.path.dirname(os.path.abspath(__file__))
            directorio_json = os.path.join(directorio_actual, '..', '..', 'static', 'assets', 'json', 'vehicles-maintenance.json')
            print(f"Ruta del archivo JSON: {directorio_json}")

            # Cargar el JSON desde el archivo
            with open(directorio_json, 'r') as file:
                json_data = json.load(file)
                print('JSON cargado correctamente')

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
                print('Datos actualizados, guardando el archivo')
                # Guardar el JSON actualizado
                with open(directorio_json, 'w') as file:
                    json.dump(data_actualizada, file, indent=4)

                # Ejecutar python manage.py collectstatic
                try:
                    print('Ejecutando collectstatic...')
                    subprocess.run(['python', 'manage.py', 'collectstatic', '--noinput'], check=True)
                    print('Collectstatic ejecutado correctamente')
                except subprocess.CalledProcessError as e:
                    print(f'Error al ejecutar collectstatic: {e}')
                    return JsonResponse({'status': 'error', 'message': 'Error al ejecutar collectstatic'}, status=500)

                return JsonResponse({'status': 'success', 'message': 'Mantenimiento agregado correctamente'})
            else:
                print('Tipo de mantenimiento no encontrado')
                return JsonResponse({'status': 'error', 'message': 'Tipo de mantenimiento no encontrado'}, status=400)
            
        except json.JSONDecodeError:
            print('Error al decodificar el JSON')
            return JsonResponse({'status': 'error', 'message': 'Error en el formato de JSON'}, status=400)
        except Exception as e:
            print(f'Error interno: {str(e)}')
            return JsonResponse({'status': 'error', 'message': f'Error interno: {str(e)}'}, status=500)

    print('Método no permitido')
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'},status=405)


def obtener_opciones(request):
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    directorio_json = os.path.join(directorio_actual, '..', '..', 'static', 'assets', 'json', 'vehicles-maintenance.json')

    try:
        with open(directorio_json, 'r') as file:
            json_data = json.load(file)
            print("este es el json")
            print(json_data)

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

# TODO --------------- [ END ] ----------
# ! Este es el fin
