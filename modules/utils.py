from django.http import HttpResponse, JsonResponse
from django.views import View
from itsdangerous import URLSafeSerializer
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
from botocore.exceptions import BotoCoreError, ClientError
from os.path import join, abspath
from django.views.decorators.csrf import csrf_exempt

from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from uritools import uridecode
from django.db.models import F, Q, Value, Max, Sum, CharField, BooleanField
from django.db import transaction
import requests
import stripe
from datetime import date, timedelta


boto3.client('s3', region_name='us-east-2', config=Config(signature_version='s3v4'))

dotenv_path = abspath(join(os.path.dirname(__file__), '..', 'venv', '.env'))
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
    print("cargando el sidebar de la plataforma")

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
            "title": submodule.subModule.name if hasattr(submodule, 'subModule') else submodule.name,
            "icon": submodule.subModule.icon if hasattr(submodule, 'subModule') else submodule.icon,
            "link": submodule.subModule.link if hasattr(submodule, 'subModule') else submodule.link
        })

    sidebar_data = [{"title": module_name, "submodules": submodules_data} for module_name, submodules_data in modules.items()]

    response["data"] = sidebar_data
    print(response)
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
    print(AWS_BUCKET_NAME, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    print("breaker")
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


# def generate_presigned_url(bucket_name, object_name, expiration=3600):
#     try:
#         content_type, _ = mimetypes.guess_type(object_name)
#         if not content_type:
#             content_type = 'application/pdf'
#         disposition = 'inline'

#         s3 = boto3.client('s3', region_name='us-east-2', config=Config(signature_version='s3v4'))

#         url = s3.generate_presigned_url(
#             'get_object',
#             Params={
#                 'Bucket': bucket_name,
#                 'Key': object_name,
#                 'ResponseContentDisposition': disposition,
#                 'ResponseContentType': content_type
#             },
#             ExpiresIn=expiration
#         )
#         return url
#     except (BotoCoreError, ClientError) as e:
#         print(f"Error generating presigned URL: {e}")
#         return None



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

def create_notifications(id_module, user_id, company_id, area, rol, response, access, request):

    fecha_actual = datetime.now().date()
    current_year = datetime.today().year
    current_month = datetime.today().month
    roles_usuario = [1, 2, 3]
    domain = request.build_absolute_uri('/')[:-1]


    # EQUIPO Y HERRAMIENTAS (Módulo 6)
    if id_module == 6:
        print("Notificaciones de equipos y herramientas")
        area = uridecode(area.lower())
        if rol in [1, 2, 3] or area == "almacen":
            print("Acceso como administrador")
            obj_responsivas = Equipment_Tools_Responsiva.objects.filter(
                company_id=company_id       
            )
        elif rol == 4:
            obj_responsivas = Equipment_Tools_Responsiva.objects.filter(
                responsible_equipment=user_id
            )

        qsUser = User_Access.objects.filter(
            company__id=company_id, 
            area__company__id=company_id,
            area__name='Almacén'
        )

        # Notificaciones de estado "Solicitado"
        for responsiva in obj_responsivas.filter(status_equipment='Solicitado'):
            response["data"].append({
                "alert": "warning",
                "icon": "<i class=\"fa-solid fa-exclamation-triangle fs-18\"></i>",
                "title": "Equipo solicitado",
                "text": f"El equipo '{responsiva.equipment_name.equipment_name}' está en estado 'Solicitado'.",
                "link": f"/equipment/info/{responsiva.equipment_name.id}/"
            })
            
            recipient_emails = [item.user.email for item in qsUser]
            if not responsiva.email_responsiva and recipient_emails:
                message_data = {
                    "title": f"Solicitud del equipo: {responsiva.equipment_name.equipment_name}",
                    "body": f"El equipo <strong>{responsiva.equipment_name.equipment_name}</strong> ha sido solicitado por el empleado <strong>{responsiva.responsible_equipment.username}</strong>. Por favor, revisa la solicitud correspondiente."
                }
                # Send_Email(
                #     subject="Solicitud de equipo o herramienta",
                #     recipient=recipient_emails,
                #     model_instance=responsiva,
                #     message_data=message_data,
                #     model_name=Equipment_Tools_Responsiva,
                #     field_to_update="email_responsiva"
                # )
                context_email = {
                    "company": Company.objects.get(id=company_id).name,
                    "subject": "Correo de notificación",
                    "modulo": 6,
                    "submodulo": "Responsiva",
                    "item": responsiva.equipment_name.id,
                    "title": message_data["title"],
                    "body": message_data["body"]
                }
                # send_notification(context_email)
                print("Contexto del correo enviado (responsiva solicitada):", context_email)

                    
                # context_email = {
                #     "company" : Company.objects.get(id=company_id).name,
                #     "subject" : "Prueba de correos",#Titulo del mensaje
                #     "modulo" : 2,#modulo de sia
                #     "submodulo" : "Responsiva",#tipo
                #     "item" : 26,#id del vehiculo a registrar 
                #     "title" : "Esta es una prueba para el sistema de notificaciones",
                #     "body" : "Este es el contenido que se mostrara",
                # }
                # send_notification(context_email)
    

        # Notificaciones cuando la solicitud es aceptada
        for responsiva in obj_responsivas.filter(status_equipment__iexact='Aceptado'): 
            if not responsiva.email_responsiva_aceptada:
                response["data"].append({
                    "alert": "success",
                    "icon": "<i class='fa-solid fa-check-circle fs-18'></i>",
                    "title": "Solicitud aceptada",
                    "text": f"Tu solicitud del equipo '{responsiva.equipment_name.equipment_name}' ha sido aceptada.",
                    "link": f"/equipment/info/{responsiva.equipment_name.id}/"
                })

                message_data = {
                    "title": "Solicitud aceptada",
                    "body": f"Tu solicitud del equipo <strong>{responsiva.equipment_name.equipment_name}</strong> ha sido aceptada."
                }
                # Send_Email(
                #     subject="Solicitud de equipo aceptada",
                #     recipient=responsiva.responsible_equipment.email,
                #     model_instance=responsiva,
                #     message_data=message_data,
                #     model_name=Equipment_Tools_Responsiva,
                #     field_to_update="email_responsiva_aceptada"
                # )
                context_email = {
                    "company": Company.objects.get(id=company_id).name,
                    "subject": "Correo de notificación",
                    "modulo": 6,
                    "submodulo": "Responsiva",
                    "item": responsiva.equipment_name.id,
                    "title": message_data["title"],
                    "body": message_data["body"]
                }
                # send_notification(context_email)
                print("Contexto del correo enviado (responsiva aceptada):", context_email)

    # SERVICIOS (Módulo 5)
    elif id_module == 5:
        print("Notificaciones de servicios")
        if 33 in access and access[33]["read"]:  
            obj_pagos_servicios = Payments_Services.objects.filter(name_service_payment__company_id=company_id)
            
            if rol not in roles_usuario:
                obj_pagos_servicios = obj_pagos_servicios.filter(name_service_payment__responsible_id=user_id)

            qsUserServicios = User_Access.objects.filter(
                company__id=company_id, 
                area__company__id=company_id,
                area__name__icontains='Compras'
            )
            print("esto contiene los usuarios del area de compras para servicios:", qsUserServicios)
            recipient_emails_servicios = list(set(item.user.email for item in qsUserServicios if item.user.email))
            print("estos son los correos obtenidos para los pagos de servicios:", recipient_emails_servicios)
            
            
            # Notificaciones para servicios con pago "proximo"
            for pago in obj_pagos_servicios.filter(status_payment='upcoming'):
                response["data"].append({
                    "alert": "warning",
                    "icon": "<i class=\"fa-solid fa-comment-dollar fs-18\"></i>",
                    "title": f"Pago próximo de servicio",
                    "text": f"El servicio '{pago.name_service_payment.name_service}' tiene un pago próximo.",
                    "link": f"/get_payment_history_notifications/{pago.name_service_payment.id}/"
                })

                if not pago.email_payment:
                    message_data = {
                        "title": f"Recordatorio de Pago próximo: {pago.name_service_payment.name_service}",
                        "body": f"El servicio <strong>{pago.name_service_payment.name_service}</strong> tiene un pago próximo programado para el <strong>{pago.next_date_payment}</strong>. Por favor, realiza el pago correspondiente."
                    }
                    # Send_Email(
                    #     subject="Recordatorio de Pago de Servicio Próximo",
                    #     recipient=recipient_emails_servicios,
                    #     model_instance=pago,
                    #     message_data=message_data,
                    #     model_name=Payments_Services,
                    #     field_to_update="email_payment"
                    # )

                    context_email = {
                        "company": Company.objects.get(id=company_id).name,
                        "subject": "Correo de notificación",
                        "modulo": 5,
                        "submodulo": "Servicio",
                        "item": pago.name_service_payment.id,
                        "title": message_data["title"],
                        "body": message_data["body"]
                    }
                    # send_notification(context_email)
                    print("Contexto del correo enviado (servicio próximo):", context_email)

            # Notificaciones para servicios con pago "no pagado"
            for pago in obj_pagos_servicios.filter(status_payment='unpaid'):
                response["data"].append({
                    "alert": "danger",
                    "icon": "<i class=\"fa-sharp-duotone fa-solid fa-money-check-dollar fs-18\"></i>",
                    "title": f"Pago no realizado de servicio",
                    "text": f"El servicio '{pago.name_service_payment.name_service}' está en estado 'No Pagado'.",
                    "link": f"/get_payment_history_notifications/{pago.name_service_payment.id}/"
                })

                if not pago.email_payment_unpaid:
                    message_data = {
                        "title": f"Recordatorio de Servicio No Pagado: {pago.name_service_payment.name_service}",
                        "body": f"El servicio <strong>{pago.name_service_payment.name_service}</strong> tiene un pago no realizado programado para el <strong>{pago.next_date_payment}</strong>. Por favor, realiza el pago correspondiente."
                    }
                    # Send_Email(
                    #     subject="Recordatorio de Pago de Servicio",
                    #     recipient=recipient_emails_servicios,
                    #     model_instance=pago,
                    #     message_data=message_data,
                    #     model_name=Payments_Services,
                    #     field_to_update="email_payment_unpaid"
                    # )

                    context_email = {
                        "company": Company.objects.get(id=company_id).name,
                        "subject": "Correo de notificación",
                        "modulo": 5,
                        "submodulo": "Servicio",
                        "item": pago.name_service_payment.id,
                        "title": message_data["title"],
                        "body": message_data["body"]
                    }
                    # send_notification(context_email)
                    print("Contexto del correo enviado (servicio no pagado):", context_email)

    # VEHÍCULOS (Módulo 2)
    elif id_module == 2:
        # area = uridecode(area.lower())
        # if area == "almacen":
        obj_vehicles = Vehicle.objects.filter(company_id=company_id).values().exclude(is_active=False)
        if rol not in roles_usuario:
            obj_vehicles = obj_vehicles.filter(responsible_id=user_id)

        # # REFRENDO
        # REFRENDO
        if 6 in access and access[6]["read"]:
            obj_refrendo = Vehicle_Refrendo.objects.filter(
                vehiculo__company_id=company_id, vehiculo__is_active=True
            )

            if rol not in roles_usuario:
                obj_refrendo = obj_refrendo.filter(vehiculo__responsible_id=user_id)

            obj_refrendo = obj_refrendo.values('vehiculo__id', 'vehiculo__name').annotate(
                ultima_fecha=Max('fecha_pago')
            )

            vehicles_with_refrendo = set()

            # Definir periodo válido de refrendo (enero - marzo del año actual)
            inicio_periodo = date(current_year, 1, 1)
            fin_periodo = date(current_year, 3, 31)

            for item in obj_refrendo:
                ultima_fecha = item["ultima_fecha"]

                # Solo considerar refrendos en el periodo permitido
                if not (inicio_periodo <= ultima_fecha <= fin_periodo):
                    continue  

                vehicles_with_refrendo.add(item["vehiculo__id"])

                if ultima_fecha < fecha_actual:
                    response["data"].append({
                        "alert": "warning",
                        "icon": "<i class=\"fa-solid fa-car-side fs-18\"></i>",
                        "title": "Vehículo sin refrendo",
                        "text": f"Vehículo: {item['vehiculo__name']}",
                        "link": f"/vehicles/info/{item['vehiculo__id']}/"
                    })
                elif ultima_fecha <= fecha_actual + timedelta(days=5):
                    dias_restantes = (ultima_fecha - fecha_actual).days
                    response["data"].append({
                        "alert": "info",
                        "icon": "<i class=\"fa-solid fa-info fs-18\"></i>",
                        "title": f"Refrendo a punto de vencer en {abs(dias_restantes)} días",
                        "text": f"Vehículo: {item['vehiculo__name']}",
                        "link": f"/vehicles/info/{item['vehiculo__id']}/"
                    })

                    refrendo = Vehicle_Refrendo.objects.filter(
                        vehiculo__id=item["vehiculo__id"], fecha_pago=ultima_fecha
                    ).first()

                    # --- CORREO 1: REFRENDO A PUNTO DE VENCER ---
                    if refrendo and not refrendo.email_refrendo:
                        message_data = {
                            "title": f"Pago de refrendo del vehículo: {refrendo.vehiculo.name}",
                            "body": f"El refrendo para el vehículo <strong>{refrendo.vehiculo.name}</strong> está próximo, se encuentra programado para la fecha <strong>{refrendo.fecha_pago}</strong>. Por favor, verifica el refrendo."
                        }
                        context_email = {
                            "company": Company.objects.get(id=company_id).name,
                            "subject": "Refrendo a punto de vencer",
                            "modulo": 2,
                            "submodulo": "Refrendo",
                            "item": refrendo.vehiculo.id,
                            "title": message_data["title"],
                            "body": message_data["body"]
                        }
                        send_notification(context_email)
                        refrendo.email_refrendo = True
                        refrendo.save(update_fields=["email_refrendo"])

                    # --- CORREO 2: REFRENDO SIN COMPROBANTE ---
                    if refrendo and not refrendo.comprobante_pago and not refrendo.email_sin_comprobante:
                        context_email = {
                            "company": Company.objects.get(id=company_id).name,
                            "subject": "Alerta: Refrendo sin comprobante de pago",
                            "modulo": 2,
                            "submodulo": "Refrendo",
                            "item": refrendo.vehiculo.id,
                            "title": f"Refrendo sin comprobante de pago - {refrendo.vehiculo.name}",
                            "body": (
                                f"El refrendo del vehículo <strong>{refrendo.vehiculo.name}</strong> "
                                f"no cuenta con un comprobante de pago cargado en el sistema. "
                                f"Por favor, sube el comprobante o regulariza la situación."
                            )
                        }
                        send_notification(context_email)
                        refrendo.email_sin_comprobante = True
                        refrendo.save(update_fields=["email_sin_comprobante"])

            # --- CORREO 3: VEHÍCULOS SIN REFRENDO REGISTRADO ---
            vehicles_without_refrendo = obj_vehicles.exclude(id__in=vehicles_with_refrendo).values('id', 'name')
            
            for vehicle in vehicles_without_refrendo:
                response["data"].append({
                    "alert": "danger",
                    "icon": "<i class=\"fa-solid fa-car-side fs-18\"></i>",
                    "title": "Vehículo sin refrendo",
                    "text": f"Vehículo: {vehicle['name']}",
                    "link": f"/vehicles/info/{vehicle['id']}/"
                })

                vehicle_instance = Vehicle.objects.get(id=vehicle["id"])
                if not vehicle_instance.email_sin_refrendo:
                    message_data = {
                        "title": f"Refrendo no registrado para el vehículo: {vehicle['name']}",
                        "body": f"El vehículo <strong>{vehicle_instance.name}</strong> no tiene un refrendo registrado. Por favor, verifica esta información en el sistema."
                    }
                    context_email = {
                        "company": Company.objects.get(id=company_id).name,
                        "subject": "Alerta de Vehículo sin Refrendo",
                        "modulo": 2,
                        "submodulo": "Refrendo",
                        "item": vehicle_instance.id,
                        "title": message_data["title"],
                        "body": message_data["body"]
                    }
                    send_notification(context_email)
                    vehicle_instance.email_sin_refrendo = True
                    vehicle_instance.save(update_fields=["email_sin_refrendo"])
        
        

        # VERIFICACIÓN
        if 8 in access and access[8]["read"]:
            try:
                today = date.today()

                for item in obj_vehicles:
                    vehicle_instance = Vehicle.objects.get(id=item["id"])
                    link_vehiculo = f"{domain}/vehicles/info/{item['id']}/"

                    # Buscar registro de verificación vigente en el año actual
                    registro = Vehicle_Verificacion.objects.filter(
                        vehiculo_id=item["id"],
                        fecha_pago__year=current_year
                    ).order_by("-fecha_pago").first()

                    if not registro:
                        # 🚨 Vehículo sin verificación en el año actual
                        if not vehicle_instance.email_sin_verificacion:
                            response["data"].append({
                                "alert": "warning",
                                "icon": "<i class='fa-regular fa-calendar-clock fs-18'></i>",
                                "title": f"Vehículo sin verificación",
                                "text": f"Vehículo: {item['name']} no cuenta con ningún registro de verificación en {current_year}",
                                "link": link_vehiculo
                            })

                            context_email = {
                                "company": Company.objects.get(id=company_id).name,
                                "subject": "Alerta de vehículo sin verificación",
                                "modulo": 2,
                                "submodulo": "Verificaciones",
                                "item": vehicle_instance.id,
                                "title": f"Vehículo {vehicle_instance.name} sin verificación",
                                "body": (
                                    f"El vehículo <strong>{vehicle_instance.name}</strong> no tiene un registro "
                                    f"de verificación en el año <strong>{current_year}</strong>. "
                                    f"<a href='{link_vehiculo}'>Ver detalles del vehículo</a>"
                                )
                            }
                            send_notification(context_email)
                            vehicle_instance.email_sin_verificacion = True
                            vehicle_instance.save(update_fields=["email_sin_verificacion"])
                        continue

                    # Ya tiene registro este año → calcular diferencia de días
                    dias_restantes = (registro.fecha_pago - today).days

                    # -------- 1️⃣ Falta un mes o menos --------
                    if 0 < dias_restantes <= 30 and not registro.email_verificacion:
                        response["data"].append({
                            "alert": "info",
                            "icon": "<i class='fa-regular fa-calendar-clock fs-18'></i>",
                            "title": f"Próximo pago de verificación",
                            "text": f"Vehículo: {item['name']} → Pago en menos de un mes",
                            "link": link_vehiculo
                        })

                        context_email = {
                            "company": Company.objects.get(id=company_id).name,
                            "subject": "Aviso de próximo pago de verificación",
                            "modulo": 2,
                            "submodulo": "Verificaciones",
                            "item": vehicle_instance.id,
                            "title": f"Próximo pago de verificación - Vehículo: {vehicle_instance.name}",
                            "body": (
                                f"El vehículo <strong>{vehicle_instance.name}</strong> debe realizar su verificación "
                                f"el <strong>{registro.fecha_pago}</strong>.<br>"
                                f"<a href='{link_vehiculo}'>Ver detalles del vehículo</a>"
                            )
                        }
                        send_notification(context_email)
                        registro.email_verificacion = True
                        registro.save(update_fields=["email_verificacion"])

                    # -------- 2️⃣ Faltan 3 días o menos --------
                    elif 0 <= dias_restantes <= 3 and not registro.email_verificacion_days:
                        response["data"].append({
                            "alert": "warning",
                            "icon": "<i class='fa-regular fa-bell fs-18'></i>",
                            "title": f"Recordatorio urgente",
                            "text": f"Vehículo: {item['name']} → Faltan {dias_restantes} días",
                            "link": link_vehiculo
                        })

                        context_email = {
                            "company": Company.objects.get(id=company_id).name,
                            "subject": "Recordatorio: verificación próxima a vencer",
                            "modulo": 2,
                            "submodulo": "Verificaciones",
                            "item": vehicle_instance.id,
                            "title": f"Recordatorio de verificación - Vehículo: {vehicle_instance.name}",
                            "body": (
                                f"El vehículo <strong>{vehicle_instance.name}</strong> debe realizar su verificación el "
                                f"<strong>{registro.fecha_pago}</strong>. Solo faltan {dias_restantes} días.<br>"
                                f"<a href='{link_vehiculo}'>Ver detalles del vehículo</a>"
                            )
                        }
                        send_notification(context_email)
                        registro.email_verificacion_days = True
                        registro.save(update_fields=["email_verificacion_days"])

                    # -------- 3️⃣ Ya venció --------
                    elif dias_restantes < 0 and registro.status != "Vencido":
                        response["data"].append({
                            "alert": "danger",
                            "icon": "<i class='fa-regular fa-circle-xmark fs-18'></i>",
                            "title": f"Pago de verificación vencido",
                            "text": f"Vehículo: {item['name']} - NO se realizó en el periodo",
                            "link": link_vehiculo
                        })

                        context_email = {
                            "company": Company.objects.get(id=company_id).name,
                            "subject": "Alerta: verificación vencida",
                            "modulo": 2,
                            "submodulo": "Verificaciones",
                            "item": vehicle_instance.id,
                            "title": f"Verificación vencida - Vehículo: {vehicle_instance.name}",
                            "body": (
                                f"El vehículo <strong>{vehicle_instance.name}</strong> no realizó su verificación "
                                f"en la fecha <strong>{registro.fecha_pago}</strong>. Actualmente se encuentra vencido.<br>"
                                f"<a href='{link_vehiculo}'>Ver detalles del vehículo</a>"
                            )
                        }
                        send_notification(context_email)
                        registro.status = "Vencido"
                        registro.save(update_fields=["status"])

            except Exception as e:
                print("Error en verificaciones:", str(e))


        # SEGUROS
        if 9 in access and access[9]["read"]:
            
            obj_seguros = Vehicle_Insurance.objects.filter(vehicle__company_id=company_id,  vehicle__is_active=True)

            if rol not in roles_usuario:
                obj_seguros = obj_seguros.filter(vehicle__responsible_id=user_id)

            obj_seguros = obj_seguros.values('vehicle__id', 'vehicle__name').annotate(ultima_fecha=Max('end_date'))

            vehicles_with_seguro = set()
            for item in obj_seguros:
                ultima_fecha = item["ultima_fecha"]
                if ultima_fecha < fecha_actual:
                    response["data"].append({
                        "alert": "warning",
                        "icon": "<i class=\"fa-solid fa-car-side fs-18\"></i>",
                        "title": "Vehículo sin seguro",
                        "text": f"Vehículo: {item['vehicle__name']}",
                        "link": f"/vehicles/info/{item['vehicle__id']}/"
                    })
                elif ultima_fecha <= fecha_actual + timedelta(days=5):
                    dias_restantes = (ultima_fecha - fecha_actual).days
                    response["data"].append({
                        "alert": "info",
                        "icon": "<i class=\"fa-solid fa-info fs-18\"></i>",
                        "title": f"Seguro a punto de vencer en {dias_restantes} días",
                        "text": f"Vehículo: {item['vehicle__name']}",
                        "link": f"/vehicles/info/{item['vehicle__id']}/"
                    })

                    insurance = Vehicle_Insurance.objects.filter(vehicle__id=item["vehicle__id"], end_date=item["ultima_fecha"]).first()
                    if insurance and not insurance.email_insurance:
                        message_data = {
                            "title": f"Recordatorio de Pago de seguro del vehículo: {insurance.vehicle.name}",
                            "body": f"El seguro para el vehículo <strong>{insurance.vehicle.name}</strong> esta programada para la fecha <strong>{insurance.end_date}</strong>. Por favor, verifica el pago de seguro."
                        }
                        # Send_Email(
                        #     subject="Pago de seguro",
                        #     recipient=recipient_emails_vehiculos,
                        #     model_instance=insurance,
                        #     message_data=message_data,
                        #     model_name=Vehicle_Insurance,
                        #     field_to_update="email_insurance"
                        # )
                        # print("coreo enviado correctamente y campo actualizado de seguro")
                        
                        context_email = {
                            "company": Company.objects.get(id=company_id).name,
                            "subject": "Pago de seguro",
                            "modulo": 2,
                            "submodulo": "Seguro",
                            "item": insurance.vehicle.id,  
                            "title": message_data["title"],
                            "body": message_data["body"]
                        }
                        send_notification(context_email)
                        insurance.email_insurance = True
                        insurance.save(update_fields=["email_insurance"])
                        # print("Contexto del correo enviado (seguro):", context_email)

                vehicles_with_seguro.add(item['vehicle__id'])

            vehicles_without_seguro = obj_vehicles.exclude(id__in=vehicles_with_seguro).values('id', 'name')
            for vehicle in vehicles_without_seguro:
                response["data"].append({
                    "alert": "danger",
                    "icon": "<i class=\"fa-solid fa-car-side fs-18\"></i>",
                    "title": "Vehículo sin seguro",
                    "text": f"Vehículo: {vehicle['name']}",
                    "link": f"/vehicles/info/{vehicle['id']}/"
                })

                vehicle_instance = Vehicle.objects.get(id=vehicle["id"])
                if not vehicle_instance.email_sin_insurance: 

                    message_data = {
                        "title": f"Seguro no registrado para el vehículo: {vehicle['name']}",
                        "body": f"El vehículo <strong>{vehicle['name']}</strong> no tiene un seguro registrado. Por favor, verifica esta información en el sistema."
                    }

                    # Send_Email(
                    #     subject="Alerta de Vehículo sin Seguro",
                    #     recipient=recipient_emails_vehiculos,
                    #     model_instance=vehicle_instance,
                    #     message_data=message_data,
                    #     model_name=Vehicle,
                    #     field_to_update="email_sin_insurance"  
                    # )
                    # print("Correo enviado para vehículo sin seguro y campo actualizado")

                    context_email = {
                        "company": Company.objects.get(id=company_id).name,
                        "subject": "Alerta de Vehículo sin Seguro",  
                        "modulo": 2,
                        "submodulo": "Seguro",
                        "item": vehicle_instance.id,
                        "title": message_data["title"],
                        "body": message_data["body"]
                    }

                    send_notification(context_email)
                    vehicle_instance.email_sin_insurance = True
                    vehicle_instance.save(update_fields=["email_sin_insurance"])
                    # print("Contexto del correo enviado (sin seguro):", context_email)

        # AUDITORÍAS - recordatorio de hoy
        if 10 in access and access[10]["read"]:
            obj_auditorias = Vehicle_Audit.objects.filter(
                vehicle__company_id=company_id,
                vehicle__is_active=True,
                audit_date=fecha_actual
            )
            
            obj_auditorias.filter(is_visible=False).update(is_visible=True)

            for auditoria in obj_auditorias:
                response["data"].append({
                    "alert": "info",
                    "icon": "<i class='fa-solid fa-clipboard-check fs-18'></i>",
                    "title": "Auditoría programada para hoy",
                    "text": f"Vehículo: {auditoria.vehicle.name}",
                    "link": f"/vehicles/info/{auditoria.vehicle.id}/"
                })

                # Enviar recordatorio solo si no se ha enviado antes
                if not auditoria.email_audit:
                    context_email = {
                        "company": Company.objects.get(id=company_id).name,
                        "subject": "Recordatorio: auditoría programada para hoy",
                        "modulo": 2,
                        "submodulo": "Auditoría",
                        "item": auditoria.vehicle.id,
                        "title": f"Auditoría programada para hoy - {auditoria.vehicle.name}",
                        "body": f"Se ha registrado una auditoría para el vehículo <strong>{auditoria.vehicle.name}</strong> con fecha <strong>{auditoria.audit_date}</strong>. Por favor verifica la auditoría."
                    }
                    send_notification(context_email)
                    auditoria.email_audit = True
                    auditoria.save(update_fields=["email_audit"])
                    # print("Recordatorio enviado para auditoría:", auditoria.id)

        # MANTENIMIENTO
        if 11 in access and access[11]["read"]:
            hoy = timezone.now().date()

            obj_mantenimiento = Vehicle_Maintenance.objects.filter(vehicle__company_id=company_id,  vehicle__is_active=True)

            if rol not in roles_usuario:                obj_mantenimiento = obj_mantenimiento.filter(vehicle__responsible_id=user_id)


            for mantenimiento in obj_mantenimiento:

                # Si ya pasó la fecha y no tiene comprobante → NO PAGADO
                if mantenimiento.date and mantenimiento.date < hoy and not mantenimiento.comprobante:
                    mantenimiento.status = "NO PAGADO"
                    mantenimiento.save()

                # Si está próximo (ej. 7 días antes) → PRÓXIMO
                elif mantenimiento.date and hoy <= mantenimiento.date <= (hoy + timedelta(days=7)):
                    mantenimiento.status = "PRÓXIMO"
                    mantenimiento.save()

                # Si es nuevo y aún no ha sido atendido
                elif mantenimiento.status == "blank":
                    mantenimiento.status = "NUEVO"
                    mantenimiento.save()

            # --- 2. ENVIAR CORREOS SEGÚN EL ESTADO ---
            for mantenimiento in obj_mantenimiento:
                campo_email = None
                
                # URL completa al vehículo

                link_vehiculo = f"{domain}/vehicles/info/{mantenimiento.vehicle.id}/"
                
                # Mensajes según estado
                if mantenimiento.status == "NUEVO" and not mantenimiento.email_maintenance:
                    campo_email = "email_maintenance"
                    descripcion = (
                        f"Se ha creado un nuevo mantenimiento para el vehículo <strong>{mantenimiento.vehicle.name}</strong>. "
                        f"Aún no ha sido atendido. Puedes ver los detalles y actualizar el mantenimiento aquí: "
                        f"<a href='{link_vehiculo}'>Ver mantenimiento</a>."
                    )

                elif mantenimiento.status == "PRÓXIMO" and not mantenimiento.email_maintenance_proximo:
                    campo_email = "email_maintenance_proximo"
                    descripcion = (
                        f"El mantenimiento del vehículo <strong>{mantenimiento.vehicle.name}</strong> esta en estado próximo. "
                        f"Revisa y realiza las acciones necesarias aquí: <a href='{link_vehiculo}'>Ver mantenimiento</a>."
                    )

                elif mantenimiento.status == "NO PAGADO" and not mantenimiento.email_maintenance_recordatorio:
                    campo_email = "email_maintenance_recordatorio"
                    descripcion = (
                        f"El mantenimiento del vehículo <strong>{mantenimiento.vehicle.name}</strong> ha vencido y aún no se ha registrado el pago. "
                        f"Por favor realiza el mantemiento, y sube el comprobante aquí: <a href='{link_vehiculo}'>Ver mantenimiento</a>."
                    )


                if campo_email:
                    response["data"].append({
                        "alert": "danger",
                        "icon": "<i class=\"fa-solid fa-tools fs-18\"></i>",
                        "title": f"Mantenimiento en estado {mantenimiento.status}",
                        "text": f"Vehículo: {mantenimiento.vehicle.name}",
                        "link": link_vehiculo
                    })

                    message_data = {
                        "title": f"Notificación de Mantenimiento: {mantenimiento.vehicle.name}",
                        "body": descripcion
                    }


                    # print(f"Enviando correo para mantenimiento ID {mantenimiento.id}")
                    # Send_Email(
                    #     subject="Pago de Mantenimiento",
                    #     recipient=recipient_emails_vehiculos,
                    #     model_instance=mantenimiento,
                    #     message_data=message_data,
                    #     model_name=Vehicle_Maintenance,
                    #     field_to_update=campo_email                    
                    # )
                    context_email = {
                        "company": Company.objects.get(id=company_id).name,
                        "subject": f"Notificación de Mantenimiento - {mantenimiento.status}",
                        "modulo": 2,
                        "submodulo": "Mantenimiento",
                        "item": mantenimiento.vehicle.id,
                        "title": message_data["title"],
                        "body": message_data["body"]
                    }
                    send_notification(context_email)
                    setattr(mantenimiento, campo_email, True)
                    mantenimiento.save(update_fields=[campo_email])
                    # print("el corro se envio correctamente")
        # Respuesta final
        response["recordsTotal"] = len(response["data"])
        response["success"] = True
        return response


# send_notification(context_email)
def es_correo_valido(valor):
    """Verifica si el valor tiene formato de correo electrónico."""
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", str(valor)))

def send_notification(context):
    try:
        # Si viene destinatario explícito en el contexto, usar solo eso
        if "to" in context and context["to"]:
            destinatarios_finales = context["to"]
        else:
            # Obtener nombre del módulo
            modulo = Module.objects.get(pk=context["modulo"]).name
            # print(modulo)
            # print(context["company"])
            

            # Filtrar por empresa y módulo
            emails = Notification_System.objects.filter(
                company__name=context["company"],
                mods=modulo
            )
            # print(emails.first().itemsID, type(emails.first().itemsID[0]))
            # Filtrar por ID de ítem o comodín (0)
            emails = emails.filter(
                Q(itemsID__contains=[context["item"]]) | Q(itemsID__contains=[0])
            )
            # print(emails)
            # print(context["submodulo"])
            # print("-----------")
            # Separar notificaciones generales y específicas
            emails_all = emails.filter(cats="todos")
            emails_one = emails.filter(cats=context["submodulo"])
            # print(emails_all)
            # print(emails_one)
            emails_responsable = Vehicle.objects.filter(id=context["item"]).values_list('responsible__email', flat=True).distinct()

            # Unificar lista inicial
            usuarios_raw = list(set(
                list(emails_all.values_list("usuario", flat=True)) +
                list(emails_one.values_list("usuario", flat=True)) + 
                list(emails_responsable)
            ))
            # print("_____________________________-----")
            # print(usuarios_raw)
            destinatarios_finales = []

            for usuario_val in usuarios_raw:
                # print(usuario_val)
                
                if es_correo_valido(usuario_val):
                    # Es correo, lo agregamos directo
                    destinatarios_finales.append(usuario_val)
                else:
                    # Es un área, buscamos todos los usuarios de esa empresa y área
                    accesos = User_Access.objects.filter(
                        company__name=context["company"],
                        area__name=usuario_val
                    ).select_related("user")
                    
                    for acceso in accesos:
                        if acceso.user.email:
                            destinatarios_finales.append(acceso.user.email)

            # Eliminar duplicados
            destinatarios_finales = list(set(destinatarios_finales))

        # print("esto contiene los destinatarios finales:", destinatarios_finales)
        
        # Verificar si hay destinatarios
        if not destinatarios_finales:
            print("No hay destinatarios para esta notificación.")
            return
        
        # Crear HTML del mensaje
        from_email = settings.EMAIL_HOST_USER
        subject = context["title"]
        
        # Color opcional
        header_color = context.get("color", "#A5C334")  

        html_content = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    background-color: #f4f4f4;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    background-color: #ffffff;
                    border-radius: 12px;
                    max-width: 600px;
                    margin: 30px auto;
                    padding: 0;
                    box-shadow: 0px 3px 12px rgba(0,0,0,0.1);
                }}
                .header {{
                    background-color: {header_color};
                    padding: 15px;
                    border-radius: 12px 12px 0 0;
                    text-align: center;
                }}
                .header h2 {{
                    color: #000000;
                    margin: 0;
                    font-size: 22px;
                }}
                .content {{
                    padding: 20px;
                    text-align: center;
                }}
                .content p {{
                    color: #555;
                    font-size: 15px;
                    line-height: 1.6;
                }}
                .footer {{
                    text-align: center;
                    font-size: 12px;
                    color: #999;
                    margin: 15px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>{context['title']}</h2>
                </div>
                <div class="content">
                    <p>{context['body']}</p>
                </div>
                <div class="footer">
                    Este mensaje fue enviado automáticamente por el sistema. No responda a este correo.
                </div>
            </div>
        </body>
        </html>
        """

        # Enviar correo
        email = EmailMultiAlternatives(subject, "", from_email, destinatarios_finales)
        email.attach_alternative(html_content, "text/html")
        email.send()
        # print(f"Correo enviado correctamente a: {destinatarios_finales}")
    
    except Exception as e:
        print(f"Error al enviar el correo: {e}")


def Send_Email(subject, recipient, model_instance, message_data, model_name, field_to_update):
    if isinstance(recipient, str):
        recipient = [recipient]
    """
    Función global para enviar correos electrónicos y actualizar un campo en la base de datos.

    Parámetros:
        - subject (str): Asunto del correo.
        - recipient (str): Correo destinatario.
        - model_instance (object): Instancia del modelo correspondiente (ejemplo: Payments_Services, Equipment_Tools_Responsiva).
        - message_data (dict): Datos a incluir en el cuerpo del correo.
        - model_name (Model): Modelo a actualizar.
        - field_to_update (str): Campo booleano a actualizar después del envío.

    """
    try:
        
        from_email = settings.EMAIL_HOST_USER
        text_content = "Este es el cuerpo del mensaje."

        email = EmailMultiAlternatives(subject, text_content, from_email, recipient)

        html_content = f"""
            <html>
            <head>
                <style>
                    body {{ background-color: #FFFAFA; font-family: Arial, sans-serif; text-align: center; }}
                    .container {{ background-color: #A5C334; padding: 36px; border-radius: 18px; width: 80%; max-width: 600px; margin: auto; }}
                    h2 {{ color: #333333; }}
                    p {{ color: #555555; line-height: 1.5; }}
                    strong {{ color: #000000; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>{message_data['title']}</h2>
                    <p>{message_data['body']}</p>
                </div>
            </body>
            </html>
        """

        email.attach_alternative(html_content, "text/html")

        # Enviar y verificar
        sent_count = email.send()
        if sent_count > 0:
            # print(f"Correo enviado exitosamente a {recipient}.")

            # Actualizar el campo solo si se envió
            with transaction.atomic():
                instance = model_name.objects.get(pk=model_instance.pk)
                setattr(instance, field_to_update, True)
                instance.save()
            # print(f"Campo {field_to_update} actualizado correctamente.")
        else:
            print(f"No se pudo enviar el correo a {recipient}. No se actualiza el campo.")

        # email.send()
        # print("Correo enviado exitosamente.")

        # Actualizar el campo de notificación en la base de datos
        # with transaction.atomic():
        #     instance = model_name.objects.get(pk=model_instance.pk)
        #     setattr(instance, field_to_update, True)
        #     instance.save()
        # print(f"Campo {field_to_update} actualizado correctamente.")

    except model_name.DoesNotExist:
        print("No se encontró un registro correspondiente en la base de datos.")
    except Exception as e:
        print(f"Error al enviar el correo o actualizar el campo: {e}")
        
def Send_Informative_Stripe(recipient, username, password, request):
    """
    Envía un correo electrónico informativo con el usuario y contraseña proporcionados.

    Parámetros:
        - recipient (str): Correo del destinatario.
        - username (str): Nombre del usuario.
        - password (str): Contraseña del usuario.
    """
    try:
        from_email = settings.EMAIL_HOST_USER
        subject = "Credenciales de acceso"
        text_content = "Este es un mensaje con tus credenciales."

        email = EmailMultiAlternatives(subject, text_content, from_email, [recipient])

        url = request.build_absolute_uri('/')[:-1] 
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ background-color: #F8F8F8; font-family: Arial, sans-serif; }}
                .container {{ background-color: #E0F7FA; padding: 30px; border-radius: 10px; width: 80%; max-width: 600px; margin: auto; }}
                h2 {{ color: #00796B; }}
                p {{ color: #333333; }}
                strong {{ color: #000000; }}
                .warning {{
                    background-color: #fff3cd;
                    color: #856404;
                    border: 1px solid #ffeeba;
                    padding: 15px;
                    border-radius: 5px;
                    margin-top: 20px;
                }}
                .button {{
                    display: inline-block;
                    padding: 10px 20px;
                    margin-top: 20px;
                    background-color: #00796B;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                }}
                .button:hover {{
                    background-color: #005f56;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Bienvenido, {username}</h2>
                <p>Estas son tus credenciales de acceso:</p>
                <p><strong>Usuario:</strong> {username}</p>
                <p><strong>Contraseña:</strong> {password}</p>
                <p>Por favor, cambia tu contraseña después de iniciar sesión.</p>

                <div class="warning">
                    ⚠️ Antes de continuar, asegúrate de cerrar cualquier sesión activa en el navegador.  
                    Luego, inicia sesión por primera vez con el usuario y contraseña proporcionados arriba.  
                    Después de iniciar sesión correctamente, puedes hacer clic en el botón de abajo para cambiar tu contraseña.
                </div>

                <a href="{url}/reset-password/" class="button">Cambiar contraseña</a>
            </div>
        </body>
        </html>
        """


        email.attach_alternative(html_content, "text/html")
        email.send()
        # print("Correo enviado exitosamente.")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")