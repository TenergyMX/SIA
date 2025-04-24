from django.http import HttpResponse
from users.models import *
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.template.loader import render_to_string
from decouple import config
import json, os
from os.path import join, dirname
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
from django.core.exceptions import ValidationError
from modules.models import *

boto3.client('s3', region_name='us-east-2', config=Config(signature_version='s3v4'))

dotenv_path = join(dirname(__file__), 'awsCred.env')
load_dotenv(dotenv_path)

AUDITORIA_VEHICULAR_POR_MES = 2
AWS_ACCESS_KEY_ID=os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY=os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_DEFAULT_REGION=os.environ.get('AWS_DEFAULT_REGION')
AWS_BUCKET_NAME=str(os.environ.get('AWS_BUCKET_NAME'))


ALLOWED_FILE_EXTENSIONS = ['.jpg', '.jpeg', '.png']

def get_module_user_permissions(_datos, _subModule_id):
    response = {"success": True, "data": {"info":{}, "access": {}}}
    response["data"]["access"] = {"create": False, "read": False, "update": False, "delete": False}

    if _datos["role"]["id"] in [1,2]:
        response["data"]["access"] = {key: True for key in response["data"]["access"]}
    else:
        obj = SubModule_Permission.objects.filter(user__user__id = _datos["user"]["id"], subModule_id = _subModule_id)
        
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
            user__user__id = data["user"]["id"]
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
            "title": submodule.subModule.short_name if hasattr(submodule, 'subModule') else submodule.name,
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
            user__user__id = context["user"]["id"]
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

def upload_to_s3(file_name, bucket_name, object_name=None):
    """Upload a file to an S3 bucket.

    :param file_name: File to upload
    :param bucket_name: S3 bucket name
    :param object_name: S3 object name. If not specified, file_name is used
    :return: True if file was uploaded, else False
    """
    print(f'EL NOMBRE ESSS: {file_name}')
    extension = file_name.name.split(".")[-1]

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

    


# def generate_presigned_url(bucket_name, object_name, expiration=3600):
#     s3 = boto3.client('s3', region_name='us-east-2', config=Config(signature_version='s3v4'))
#     return s3.generate_presigned_url(
#         'get_object',
#         Params={
#             'Bucket': bucket_name,
#             'Key': object_name,
#             'ResponseContentDisposition': 'inline',
#             'ResponseContentType': 'application/pdf'  
#         },
#         ExpiresIn=expiration
#     )


def generate_presigned_url(bucket_name, object_name, expiration=3600):
    content_type, _ = mimetypes.guess_type(object_name)
    if not content_type:
        content_type = 'application/pdf'
    disposition = 'inline'
    s3 = boto3.client('s3', region_name='us-east-2', config=Config(signature_version='s3v4'))
    return s3.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': bucket_name,
            'Key': object_name,
            'ResponseContentDisposition': disposition,
            'ResponseContentType': content_type
        },
        ExpiresIn=expiration
    )




def validate_image(file):
    # Check file size (e.g., max 5 MB)
    if file.size > 10 * 1024 * 1024:
        raise ValidationError("Image file is too large ( > 10 MB ).")
    # Check content type (e.g., only allow PNG and JPEG)
        print(f'el content type es: {file.content_type}')
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
    
    
def check_user_access_to_module(request, module_id, submodule_id):
    context = user_data(request)
    print("Esto contiene el context:", context)

    user_company = context["company"]["id"]
    name_company = context["company"]["name"]
    print("Esta es la compañía del usuario:", user_company)
    print("Este es el nombre de la compañía del usuario:", name_company)

    if not user_company:
        return False

    try:
        active_plans = Plans.objects.filter(company=user_company, status_payment_plan=True)

        if not active_plans.exists():
            return False

        has_access_to_module = active_plans.filter(module__id=module_id).exists()

        if not has_access_to_module:
            print(f"La empresa '{name_company}' no tiene acceso al módulo con ID {module_id}")
            return False

        print(f"Los módulos para la empresa '{name_company}' con el ID {user_company} son:")
        for plan in active_plans:
            print(f"- {plan.module.name}")  

    except Plans.DoesNotExist:
        return False

    access = get_module_user_permissions(context, submodule_id)
    if not access["data"]["access"]["read"]:
        return False

    return True
