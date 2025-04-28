from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F, Q, Value, Max, Sum, CharField, BooleanField
from django.http import JsonResponse
from core.settings import EMAIL_HOST_PASSWORD, EMAIL_HOST_USER
from django.apps import apps
from django.db import transaction
import json, os
from datetime import datetime, timedelta

from uritools import uridecode
from modules.models import *
from users.models import *
from modules.utils import *
import requests
from django.urls import resolve
from unidecode import unidecode

from django.utils.timezone import now

# TODO -- EMAIL --
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import json


# TODO --------------- [ VIEWS ] ---------- 
def home_view(request):
    context = {}
    if request.user.is_authenticated:
        context["user"] = request.user

    #CONDITIONAL TO SEND EMAIL
    if request.method == "POST":
        form = request.POST
        asunto = f'Correo enviado por {form.get("email", "sin correo")}'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [settings.EMAIL_HOST_USER]

        #body-text
        text_content = f'{form.get("name", "Nombre no proporcionado")}, de la empresa {form.get("name_company", "Empresa no especificada")}: {form.get("message", "Sin mensaje")}'
        domain = request.build_absolute_uri('/')[:-1]  # Obtiene el dominio dinámicamente
        #html
        html_content = f"""
        <html>
        <head>
            <style>
            body {{
                background-color: #FFFAFA;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                font-family: Arial, sans-serif;
            }}
            .container {{
                background-color: #A5C334;
                padding: 36px;
                border-radius: 18px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                text-align: center;
                width: 80%;
                max-width: 600px;
            }}
            img {{
                max-width: 150px;
                margin-bottom: 20px;
            }}
            h2 {{
                color: #333333;
            }}
            p {{
                color: #555555;
                line-height: 1.5;
            }}
            strong {{
                color: #000000;
            }}
            </style>
        </head>
        <body>
            <div class="container">
            <img src="{domain}/staticfiles/assets/images/brand-logos/CS_LOGO.png" alt="Logo">
            <h2>Nuevo mensaje de {form.get("name", "Nombre no proporcionado")}</h2>
            <p><strong>Empresa:</strong> {form.get("name_company", "Empresa no especificada")}</p>
            <p><strong>Correo:</strong> {form.get("email", "sin correo")}</p>
            <p><strong>Mensaje:</strong></p>
            <p>{form.get("message", "Sin mensaje")}</p>
            </div>
        </body>
        </html>
        """

        context["sendEmail"] = True

        # Crear el email
        email = EmailMultiAlternatives(asunto, text_content, from_email, recipient_list)
        email.attach_alternative(html_content, "text/html")
        email.send()

    return render(request, "home/index.html", context)

def error_404_view(request, exception):
    # Aquí va tu lógica para manejar el error 404
    return render(request, 'error/404.html', status=404)

def error_500_view(request):
    # Aquí va tu lógica para manejar el error 500
    return render(request, 'error/500.html', status=500)

def develop_view(request):
    context = user_data(request)
    last_module_id = request.session.get("last_module_id", 2)
    sidebar = get_sidebar(context, [1, last_module_id])
    context["sidebar"] = sidebar["data"]
    return render(request, "develop/main.html", context)


# TODO --------------- [ REQUEST ] ----------

def get_notifications(request):
    response = {"success": False, "data": []}
    context = user_data(request)
    company_id = context["company"]["id"]
    fecha_actual = datetime.now().date()
    current_year = datetime.today().year
    current_month = datetime.today().month
    roles_usuario = [1, 2, 3]

    area = context["area"]["name"]
    rol = context["role"]["id"]

    access = get_user_access(context)
    access = access["data"]

    url_path = request.GET.get('url', '')
    match = resolve(f'{url_path}')
    module = match.func.__module__
    module_parts = module.split('.')
    if len(module_parts) > 1:
        url_modulo = module_parts[2]
    else:
        url_modulo = None
    
    id_module = 0

    if url_modulo == "vehicles":
        id_module = 2
    elif url_modulo == "services":
        id_module = 5
    elif url_modulo == "equipment-and-tools":
        id_module = 6
    
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
                responsible_equipment=context["user"]["id"]
            )

        qsUser = User_Access.objects.filter(
            company__id=request.session["company"]["id"], 
            area__company__id=request.session["company"]["id"],
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
                Send_Email(
                    subject="Solicitud de equipo o herramienta",
                    recipient=recipient_emails,
                    model_instance=responsiva,
                    message_data=message_data,
                    model_name=Equipment_Tools_Responsiva,
                    field_to_update="email_responsiva"
                )

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
                Send_Email(
                    subject="Solicitud de equipo aceptada",
                    recipient=responsiva.responsible_equipment.email,
                    model_instance=responsiva,
                    message_data=message_data,
                    model_name=Equipment_Tools_Responsiva,
                    field_to_update="email_responsiva_aceptada"
                )

    # SERVICIOS (Módulo 5)
    elif id_module == 5:
        print("Notificaciones de servicios")
        if 33 in access and access[33]["read"]:  
            obj_pagos_servicios = Payments_Services.objects.filter(name_service_payment__company_id=company_id)
            
            if context["role"]["id"] not in roles_usuario:
                obj_pagos_servicios = obj_pagos_servicios.filter(name_service_payment__responsible_id=context["user"]["id"])

            qsUserServicios = User_Access.objects.filter(
                company__id=request.session["company"]["id"], 
                area__company__id=request.session["company"]["id"],
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
                    Send_Email(
                        subject="Recordatorio de Pago de Servicio Próximo",
                        recipient=recipient_emails_servicios,
                        model_instance=pago,
                        message_data=message_data,
                        model_name=Payments_Services,
                        field_to_update="email_payment"
                    )

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
                    Send_Email(
                        subject="Recordatorio de Pago de Servicio",
                        recipient=recipient_emails_servicios,
                        model_instance=pago,
                        message_data=message_data,
                        model_name=Payments_Services,
                        field_to_update="email_payment_unpaid"
                    )


    # VEHÍCULOS (Módulo 2)
    elif id_module == 2:
        print("Notificaciones de vehículos")
        # area = uridecode(area.lower())
        # if area == "almacen":
        obj_vehicles = Vehicle.objects.filter(company_id=company_id).values().exclude(is_active=False)
        if context["role"]["id"] not in roles_usuario:
            obj_vehicles = obj_vehicles.filter(responsible_id=context["user"]["id"])

       

        qsUserAlmacen = User_Access.objects.filter(
            company__id=request.session["company"]["id"], 
            area__company__id=request.session["company"]["id"],
            area__name='Almacén'
        )
        
        print("esto contiene los usuarios que cuentan con el area de almacen para vehiculos:", qsUserAlmacen)
        emails_almacen = (set(item.user.email for item in qsUserAlmacen if item.user.email))
        print("estos son los correos obtenidos para los vehiculos:", emails_almacen)

        # Correos de responsables de vehículos
        responsible_users = set(obj_vehicles.values_list("responsible__email", flat=True))
        print("estos son los responsables del vehiculo:", responsible_users)
        emails_responsables = set(email for email in responsible_users if email)
        print("este es el correo del reponsable:", emails_responsables)

        # agrupar
        recipient_emails_vehiculos = list(emails_almacen.union(emails_responsables))
        print("estos son los correos recibidos para enviar las notificaciones de vehículos", recipient_emails_vehiculos)

        # TENENCIA
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
                        "link": f"/vehicles/info/{item['vehiculo__id']}/"
                    })
                elif fecha_actual <= ultima_fecha_pago <= fecha_actual + timedelta(days=5):
                    dias_restantes = (ultima_fecha_pago - fecha_actual).days
                    response["data"].append({
                        "alert": "info",
                        "icon": "<i class=\"fa-solid fa-info fs-18\"></i>",
                        "title": f"Tenencia a punto de vencer en {dias_restantes} días",
                        "text": f"Vehículo: {item['vehiculo__name']}",
                        "link": f"/vehicles/info/{item['vehiculo__id']}/"
                    })

                    tenencia = Vehicle_Tenencia.objects.filter(vehiculo__id=item["vehiculo__id"], fecha_pago=ultima_fecha_pago).first()
                    if tenencia and not tenencia.email_tenencia:
                        message_data = {
                            "title": f"Recordatorio de Pago de tenencia del vehículo: {tenencia.vehiculo.name}",
                            "body": f"La licencia para el vehículo <strong>{tenencia.vehiculo.name}</strong> esta programada para la fecha <strong>{tenencia.fecha_pago}</strong>. Por favor, verifica la tenencia."
                        }
                        Send_Email(
                            subject="Recordatorio de Tenencia",
                            recipient=recipient_emails_vehiculos,
                            model_instance=tenencia,
                            message_data=message_data,
                            model_name=Vehicle_Tenencia,
                            field_to_update="email_tenencia"
                        )
                        print("coreo enviado correctamente y campo actualizado de tenencia")

                vehicles_with_tenencia.add(item['vehiculo__id'])

            vehicles_without_tenencia = obj_vehicles.exclude(id__in=vehicles_with_tenencia)
            for vehicle in vehicles_without_tenencia:
                response["data"].append({
                    "alert": "danger",
                    "icon": "<i class=\"fa-solid fa-car-side fs-18\"></i>",
                    "title": "Vehículo sin tenencia",
                    "text": f"Vehículo: {vehicle['name']}",
                    "link": f"/vehicles/info/{vehicle['id']}/"
                })


                
                vehicle_instance = Vehicle.objects.get(id=vehicle["id"])
                if not vehicle_instance.email_sin_tenencia:

                    message_data = {
                        "title": f"Tenencia no registrada para el vehículo: {vehicle['name']}",
                        "body": f"El vehículo <strong>{vehicle['name']}</strong> no tiene una tenencia registrada. Por favor, verifica esta información en el sistema."
                    }
        
                    Send_Email(
                        subject="Alerta de Vehículo sin Tenencia",
                        recipient=recipient_emails_vehiculos,
                        model_instance=vehicle_instance,
                        message_data=message_data,
                        model_name=Vehicle,
                        field_to_update="email_sin_tenencia" 
                    )
                    print("Correo enviado para vehículo sin tenencia y campo sin tenenecia actualizado")

        # REFRENDO
        if 6 in access and access[6]["read"]:
            obj_refrendo = Vehicle_Refrendo.objects.filter(vehiculo__company_id=company_id)

            if context["role"]["id"] not in roles_usuario:
                obj_refrendo = obj_refrendo.filter(vehiculo__responsible_id=context["user"]["id"])

            obj_refrendo = obj_refrendo.values('vehiculo__id', 'vehiculo__name').annotate(ultima_fecha=Max('fecha_pago'))
            
            vehicles_with_refrendo = set()
            for item in obj_refrendo:
                if item["ultima_fecha"] < fecha_actual:
                    response["data"].append({
                        "alert": "warning",
                        "icon": "<i class=\"fa-solid fa-car-side fs-18\"></i>",
                        "title": "Vehículo sin refrendo (Vencido)",
                        "text": f"Vehículo: {item['vehiculo__name']}",
                        "link": f"/vehicles/info/{item['vehiculo__id']}/"
                    })
                elif item["ultima_fecha"] <= fecha_actual + timedelta(days=5):
                    dias_restantes = (item["ultima_fecha"] - fecha_actual).days
                    response["data"].append({
                        "alert": "info",
                        "icon": "<i class=\"fa-solid fa-info fs-18\"></i>",
                        "title": f"refrendo a punto de vencer en {abs(dias_restantes)} días",
                        "text": f"Vehículo: {item['vehiculo__name']}",
                        "link": f"/vehicles/info/{item['vehiculo__id']}/"
                    })

                    refrendo = Vehicle_Refrendo.objects.filter(vehiculo__id=item["vehiculo__id"], fecha_pago=item["ultima_fecha"]).first()
                    if refrendo and not refrendo.email_refrendo:
                        message_data = {
                            "title": f"Recordatorio de Pago de refrendo del vehículo: {refrendo.vehiculo.name}",
                            "body": f"El refrendo para el vehículo <strong>{refrendo.vehiculo.name}</strong> esta programada para la fecha <strong>{refrendo.fecha_pago}</strong>. Por favor, verifica el refrendo."
                        }
                        Send_Email(
                            subject="Recordatorio de refrendo",
                            recipient=recipient_emails_vehiculos,
                            model_instance=refrendo,
                            message_data=message_data,
                            model_name=Vehicle_Refrendo,
                            field_to_update="email_refrendo"
                        )
                        print("coreo enviado correctamente y campo actualizado de refrendo")


            
            vehicles_without_refrendo = obj_vehicles.exclude(id__in=vehicles_with_refrendo).values_list('name', flat=True)
            for name in vehicles_without_refrendo:
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
                        "body": f"El vehículo <strong>{vehicle['name']}</strong> no tiene un refrendo registrado. Por favor, verifica esta información en el sistema."
                    }

                    Send_Email(
                        subject="Alerta de Vehículo sin Refrendo",
                        recipient=recipient_emails_vehiculos,
                        model_instance=vehicle_instance,
                        message_data=message_data,
                        model_name=Vehicle,
                        field_to_update="email_sin_refrendo"  
                    )
                    print("Correo enviado para vehículo sin refrendo y campo actualizado")


        # VERIFICACIÓN
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
                    d = obtener_ultimo_digito(item)
                    payment_months = [cv[d]["s1"][0]["month_code"], cv[d]["s1"][1]["month_code"]]
                    payment_months_ES = [cv[d]["s1"][0]["month_name_ES"], cv[d]["s1"][1]["month_name_ES"]]

                    registro = Vehicle_Verificacion.objects.filter(
                        Q(fecha_pago__year=current_year) &
                        Q(fecha_pago_month_in=payment_months) &
                        Q(vehiculo_id=item["id"])
                    )
                    if not registro.exists() and current_month in payment_months:
                        print(f"[ALERTA] Verificación 1er Semestre - Vehículo: {item['name']}")
                        response["data"].append({
                            "alert": "warning",
                            "icon": "<i class=\"fa-regular fa-money-bill-wave fs-18\"></i>",
                            "title": f"Realizar el pago de la verificación 1er Sem.",
                            "text": f"Vehículo: {item['name']}",
                            "link": f"/vehicles/info/{item['id']}/"
                        })

                        if not vehicle_instance.email_verificacion_s1:
                            message_data = {
                                "title": f"Pago de verificación 1er semestre - Vehículo: {vehicle_instance.name}",
                                "body": f"El vehículo <strong>{vehicle_instance.name}</strong> no tiene registrada la verificación del 1er semestre. Por favor, realiza el pago correspondiente."
                            }

                            Send_Email(
                                subject="Alerta de verificación 1er semestre",
                                recipient=recipient_emails_vehiculos,
                                model_instance=vehicle_instance,
                                message_data=message_data,
                                model_name=Vehicle,
                                field_to_update="email_verificacion_s1"
                            )
                            print("Correo enviado para verificación 1er semestre y campo actualizado")


                    elif (current_month + 1) == cv[d]["s1"][0]["month_code"]:
                        month_name_ES = cv[d]["s1"][0]["month_name_ES"]
                        print(f"[INFO] Próximo pago 1er Sem. en {month_name_ES} - Vehículo: {item['name']}")
                        response["data"].append({
                            "alert": "info",
                            "icon": "<i class=\"fa-regular fa-money-bill-wave fs-18\"></i>",
                            "title": f"Próximo pago de verificación en {month_name_ES}",
                            "text": f"Vehículo: {item['name']}",
                            "link": f"/vehicles/info/{item['id']}/"
                        })
                    elif current_month == cv[d]["s2"][0]["month_code"] or current_month == cv[d]["s2"][1]["month_code"]:
                        print(f"[ALERTA] Verificación 2do Semestre - Vehículo: {item['name']}")

                        response["data"].append({
                            "alert": "warning",
                            "icon": "<i class=\"fa-regular fa-money-bill-wave fs-18\"></i>",
                            "title": f"Realizar el pago de la verificación 2do Sem.",
                            "text": f"Vehículo: {item['name']}",
                            "link": f"/vehicles/info/{item['id']}/"
                        })

                        if not vehicle_instance.email_verificacion_s2:
                            message_data = {
                                "title": f"Pago de verificación 2do semestre - Vehículo: {vehicle_instance.name}",
                                "body": f"El vehículo <strong>{vehicle_instance.name}</strong> no tiene registrada la verificación del 2do semestre. Por favor, realiza el pago correspondiente."
                            }
                            Send_Email(
                                subject="Alerta de verificación 2do semestre",
                                recipient=recipient_emails_vehiculos,
                                model_instance=vehicle_instance,
                                message_data=message_data,
                                model_name=Vehicle,
                                field_to_update="email_verificacion_s2"
                            )
                            print("Correo enviado para verificación 2do semestre y campo actualizado")

                    elif (current_month + 1) == cv[d]["s2"][0]["month_code"]:
                        month_name_ES = cv[d]["s2"][0]["month_name_ES"]
                        print(f"[INFO] Próximo pago 2do Sem. en {month_name_ES} - Vehículo: {item['name']}")
                        response["data"].append({
                            "alert": "info",
                            "icon": "<i class=\"fa-regular fa-money-bill-wave fs-18\"></i>",
                            "title": f"Próximo pago de verificación en {month_name_ES}",
                            "text": f"Vehículo: {item['name']}",
                            "link": f"/vehicles/info/{item['id']}/"
                        })
            except Exception as e:
                print("Error en verificaciones:", str(e))

        # SEGUROS
        if 9 in access and access[9]["read"]:
            obj_seguros = Vehicle_Insurance.objects.filter(vehicle__company_id=company_id)

            if context["role"]["id"] not in roles_usuario:
                obj_seguros = obj_seguros.filter(vehicle__responsible_id=context["user"]["id"])

            obj_seguros = obj_seguros.values('vehicle__id', 'vehicle__name').annotate(ultima_fecha=Max('end_date'))

            vehicles_with_seguro = set()
            for item in obj_seguros:
                ultima_fecha = item["ultima_fecha"]
                if ultima_fecha < fecha_actual:
                    response["data"].append({
                        "alert": "warning",
                        "icon": "<i class=\"fa-solid fa-car-side fs-18\"></i>",
                        "title": "Vehículo sin seguro (Vencido)",
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
                        Send_Email(
                            subject="Recordatorio de pago de seguro",
                            recipient=recipient_emails_vehiculos,
                            model_instance=insurance,
                            message_data=message_data,
                            model_name=Vehicle_Insurance,
                            field_to_update="email_insurance"
                        )
                        print("coreo enviado correctamente y campo actualizado de seguro")


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

                    Send_Email(
                        subject="Alerta de Vehículo sin Seguro",
                        recipient=recipient_emails_vehiculos,
                        model_instance=vehicle_instance,
                        message_data=message_data,
                        model_name=Vehicle,
                        field_to_update="email_sin_insurance"  
                    )
                    print("Correo enviado para vehículo sin seguro y campo actualizado")


        # AUDITORÍAS
        if 10 in access and access[10]["read"]:
            obj_auditorias = Vehicle_Audit.objects.filter(vehicle__company_id=company_id)

            if context["role"]["id"] not in roles_usuario:
                obj_auditorias = obj_auditorias.filter(vehicle__responsible_id=context["user"]["id"])

            obj_auditorias_hoy = obj_auditorias.filter(audit_date=fecha_actual)
            obj_auditorias_hoy.filter(is_visible=False).update(is_visible=True)

            for auditoria in obj_auditorias_hoy:
                response["data"].append({
                    "alert": "info",
                    "icon": "<i class=\"fa-solid fa-clipboard-check fs-18\"></i>",
                    "title": "Auditoría programada para hoy",
                    "text": f"Vehículo: {auditoria.vehicle.name}",
                    "link": f"/vehicles/info/{auditoria.vehicle.id}/"
                })

                if not auditoria.email_audit:
                    message_data = {
                        "title": f"Recordatorio de Pago de auditoria del vehículo: {auditoria.vehicle.name}",
                        "body": f"La auditoria para el vehículo <strong>{auditoria.vehicle.name}</strong> esta programada para la fecha <strong>{auditoria.audit_date}</strong>. Por favor, verifica la auditoria."
                    }
                    Send_Email(
                        subject="Recordatorio de auditoria",
                        recipient=recipient_emails_vehiculos,
                        model_instance=auditoria,
                        message_data=message_data,
                        model_name=Vehicle_Audit,
                        field_to_update="email_audit"
                    )

        # MANTENIMIENTO

        # Agregar correos del área de Compras
        qsUserCompras = User_Access.objects.filter(
            company__id=request.session["company"]["id"], 
            area__company__id=request.session["company"]["id"],
            area__name='Compras'
        )

        print("Usuarios con acceso al área de Compras:", qsUserCompras)
        emails_compras = set(item.user.email for item in qsUserCompras if item.user.email)
        print("Correos electrónicos del área de Compras:", emails_compras)

        # Agregar correos a la lista final de destinatarios para mantenimiento
        recipient_emails_vehiculos = list(set(recipient_emails_vehiculos).union(emails_compras))
        print("Lista final de correos (vehículos + compras):", recipient_emails_vehiculos)


        if 11 in access and access[11]["read"]:
            obj_mantenimiento = Vehicle_Maintenance.objects.filter(vehicle__company_id=company_id)

            if context["role"]["id"] not in roles_usuario:
                obj_mantenimiento = obj_mantenimiento.filter(vehicle__responsible_id=context["user"]["id"])

            obj_mantenimiento_alerta = obj_mantenimiento.filter(
                Q(status__iexact="ALERTA") | Q(status__iexact="NUEVO") | Q(status__iexact="GENERADO")
            )

            for mantenimiento in obj_mantenimiento_alerta:

                mantenimiento_programado = (
                    Vehicle_Maintenance_Kilometer.objects
                    .filter(vehiculo=mantenimiento.vehicle)
                    .order_by("-kilometer")
                    .first()
                )

                kilometraje_objetivo = mantenimiento_programado.kilometer if mantenimiento_programado else "desconocido"

                response["data"].append({
                    "alert": "danger",
                    "icon": "<i class=\"fa-solid fa-tools fs-18\"></i>",
                    "title": f"Mantenimiento en estado {mantenimiento.status}",
                    "text": f"Vehículo: {mantenimiento.vehicle.name}",
                    "link": f"/vehicles/info/{mantenimiento.vehicle.id}/"
                })

                if not mantenimiento.email_maintenance:

                    message_data = {
                        "title": f"Recordatorio de Mantenimiento: {mantenimiento.vehicle.name}",
                        "body": (
                            f"El mantenimiento del vehículo <strong>{mantenimiento.vehicle.name}</strong> está en estado de "
                            f"<strong>{mantenimiento.status}</strong>, ya que el kilometraje se encuentra por debajo de los "
                            f"<strong>{kilometraje_objetivo}</strong> kilometros. Por favor, revisa el mantenimiento generado para "
                            f"actualizar su fecha. <br><br>"
                            f"<a href='http://localhost/vehicles/info/{mantenimiento.vehicle.id}/' style='color: #1a73e8;'>"
                            f"Ver información del vehículo</a>" 
                        )
                    }

                    print(f"Enviando correo para mantenimiento ID {mantenimiento.id}")
                    Send_Email(
                        subject="Recordatorio de Mantenimiento",
                        recipient=recipient_emails_vehiculos,
                        model_instance=mantenimiento,
                        message_data=message_data,
                        model_name=Vehicle_Maintenance,
                        field_to_update="email_maintenance"
                    )


            # Alerta anticipada (2 días antes del mantenimiento programado)
            fecha_actual = datetime.now().date()
            print ("esta es lafecha actual:", fecha_actual)

            for mantenimiento in obj_mantenimiento:
                if mantenimiento.email_maintenance_proximo:
                    continue

                date = getattr(mantenimiento, "date", None)
                print("esta es la fecha programada:", date)
                if date:
                    dias_restantes = (date - fecha_actual).days

                    if dias_restantes == 2:
                        response["data"].append({
                            "alert": "warning",
                            "icon": "<i class=\"fa-solid fa-calendar-days fs-18\"></i>",
                            "title": "Mantenimiento próximo en 2 días",
                            "text": f"Vehículo: {mantenimiento.vehicle.name}",
                            "link": f"/vehicles/info/{mantenimiento.vehicle.id}/"
                        })

                        message_data = {
                            "title": f"Mantenimiento programado para {mantenimiento.vehicle.name}",
                            "body": (
                                f"Se tiene programado un mantenimiento para el vehículo <strong>{mantenimiento.vehicle.name}</strong> "
                                f"el día <strong>{date}</strong>. Por favor revisa los detalles en el sistema. <br><br>"
                                f"<a href='http://localhost/vehicles/info/{mantenimiento.vehicle.id}/' style='color: #1a73e8;'>"
                                f"Ver información del vehículo</a>"
                            )
                        }

                        print(f"Enviando recordatorio anticipado para {mantenimiento.vehicle.name}")

                        Send_Email(
                            subject="Mantenimiento Próximo",
                            recipient=recipient_emails_vehiculos,
                            model_instance=mantenimiento,
                            message_data=message_data,
                            model_name=Vehicle_Maintenance,
                            field_to_update="email_maintenance_proximo"
                        )

    # Respuesta final
    response["recordsTotal"] = len(response["data"])
    response["success"] = True
    return JsonResponse(response)



@require_POST
def update_or_create_records(request):
    response = {'status': "error", "message": "Sin Procesar"}
    dt = request.POST

    if request.method != 'POST':
        response["message"] = "Método de solicitud no permitido."
        return JsonResponse(response, status=405)

    if 'records' not in request.FILES:
        response["message"] = "No se ha proporcionado el archivo JSON."
        return JsonResponse(response, status=400)
    
    try:
        archivo = request.FILES['records']
        archivo.seek(0)
        archivo_data = archivo.read()
        archivo_str = archivo_data.decode('utf-8')
        contenido_json = json.loads(archivo_str)
    except UnicodeDecodeError:
        response["message"] = "El archivo no está codificado en UTF-8."
        return JsonResponse(response, status=400)
    except json.JSONDecodeError:
        response["message"] = "El archivo no tiene un formato JSON válido."
        return JsonResponse(response, status=400)
    
    if not isinstance(contenido_json, list):
        response["message"] = "El JSON debe ser una lista de objetos."
        return JsonResponse(response, status=400)

    response["data"] = []


    with transaction.atomic():
        for item in contenido_json:
            model_name = item.get("model")
            pk = item.get("pk")
            fields = item.get("fields", {})

            if not model_name or not fields:
                response["data"].append({
                    "status": "error",
                    "message": f"El registro con PK {pk} no tiene un formato válido." if pk else "Faltan datos obligatorios.",
                    "model": model_name
                })
                continue

            try:
                app_label, model_label = model_name.split(".")
                model = apps.get_model(app_label, model_label)
            except (ValueError, LookupError):
                response["data"].append({
                    "status": "error",
                    "message": f"El modelo {model_name} no existe.",
                    "model": model_name
                })
                continue

            # Convertir campos relacionados a campo_id
            for key in list(fields.keys()):
                if key in [f.name for f in model._meta.fields if f.is_relation]:
                    fields[f"{key}_id"] = fields.pop(key)

            if pk:
                try:
                    obj = model.objects.get(pk=pk)
                    for key, value in fields.items():
                        setattr(obj, key, value)
                    obj.save()
                    message = f"El registro {pk} fue actualizado en el modelo '{model_name}' exitosamente."
                except model.DoesNotExist:
                    obj = model(pk=pk, **fields)
                    obj.save()
                    message = f"El registro {pk} fue creado y recuperado en el modelo '{model_name}' exitosamente."
            else:
                obj = model(**fields)
                obj.save()
                pk = obj.pk
                message = f"Se creó un nuevo registro con PK {pk} en el modelo '{model_name}' exitosamente."
            
            response["data"].append({
                "status": "success",
                "message": message,
                "model": model_name,
                "pk": pk
            })
    # Responder
    response["status"] = "success"
    response["message"] = "Se han realizado las operaciones exitosamente."
    return JsonResponse(response, status=200)



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
        
        from_email = EMAIL_HOST_USER
        password = EMAIL_HOST_PASSWORD
        text_content = "Este es el cuerpo del mensaje."
        print(from_email)
        print(subject)
        print(password)
        print(recipient)
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
        email.send()
        print("Correo enviado exitosamente.")

        # Actualizar el campo de notificación en la base de datos
        with transaction.atomic():
            instance = model_name.objects.get(pk=model_instance.pk)
            setattr(instance, field_to_update, True)
            instance.save()
        print(f"Campo {field_to_update} actualizado correctamente.")

    except model_name.DoesNotExist:
        print("No se encontró un registro correspondiente en la base de datos.")
    except Exception as e:
        print(f"Error al enviar el correo o actualizar el campo: {e}")



def enviar_cotizacion(request):
    body_response = {
        "technology" : "Acceso a la plataforma de Equipos de cómputo",
        "data" : "Acceso a la plataforma de Infraestructura",
        "transports" : "Acceso a la plataforma de Vehículos",
        "assets-and-tools" : "Acceso a la plataforma de Equipos y herramientas",
        "services" : "Acceso a la plataforma de Servicios",
        "sm" : "Gestión para 10 trabajadores",
        "md" : "Gestión para 29 trabajadores",
        "lg" : "Gestión ilimitada",
        "minimum" : "Solo 1000 recursos administrables",
        "medio" : "Solo 5000 recursos administrables",
        "unlimited" : "recursos ilimitados administrables",        
        "local" : "Administración para un local",
        "store" : "Administración para una Sucursal",
        "corporation" : "Administración para un Corporativo",
        "storage" : "Administración para un Almacén",
        "multinational" : "Administración para una empresa"
    }

    form = request.POST
    details = form.get("details") if form.get("details") != "" else "Sin información adicional"
    body = form.get("options_quotations")[:-1].split(",")
    
    html_quotation = ""
    for item in body:
        print(item)
        html_quotation += f'<p>{body_response[item]}</p>'
    
    print(html_quotation)
    asunto = f'Correo enviado por {form.get("email", "sin correo")}'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [settings.EMAIL_HOST_USER]
    
    #body-text
    text_content = f'{form.get("name", "Nombre no proporcionado")}, de la empresa {form.get("name_company", "Empresa no especificada")}: {form.get("message", "Sin mensaje")}'

    #html
    html_content = f"""
    <html>
        <head>
            <style>
                body {{
                    background-color: #FFFAFA;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    font-family: Arial, sans-serif;
                }}
                .container {{
                    background-color: #A5C334;
                    padding: 36px;
                    border-radius: 18px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    text-align: center;
                    width: 80%;
                    max-width: 600px;
                }}
                img {{
                    max-width: 150px;
                    margin-bottom: 20px;
                }}
                h2 {{
                    color: #333333;
                }}
                p {{
                    color: #555555;
                    line-height: 1.5;
                    font-weight: 500;
                }}
                strong {{
                    color: #000000;
                }}
            </style>
        </head>
        <body>
            <div class="container">
            <img src="https://sia-tenergy.com/staticfiles/assets/images/brand-logos/CS_LOGO.png" alt="Logo">
            <h2>Nuevo mensaje de {form.get("name", "Nombre no proporcionado")}</h2>
            <p><strong>Empresa:</strong> {form.get("company", "Empresa no especificada")}</p>
            <p><strong>Correo:</strong> {form.get("email", "sin correo")}</p>
            <p><strong>Detalles de cotización:</strong></p>
            {html_quotation}
            <p><strong>Información adicional:</strong></p>
            <p>{details}</p>
            </div>
        </body>
    </html>"""


    #Crear el email
    email = EmailMultiAlternatives(asunto, text_content, from_email, recipient_list)
    email.attach_alternative(html_content, "text/html")
    email.send()
    return JsonResponse({'mensaje': 'Cotización enviada correctamente'})