from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F, Q, Value, Max, Sum, CharField, BooleanField
from django.http import JsonResponse
from django.conf import settings
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

from django.utils.timezone import now

# TODO -- EMAIL --
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


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
            <img src="https://sia-tenergy.com/staticfiles/assets/images/brand-logos/logo.png" alt="Logo">
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
    roles_usuario = [1,2,3]

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
    
    # !   /-----------------------------------------------/
    # !  /  EQUIPO Y HERRAMIENTAS
    # ! /-----------------------------------------------/
    # numero #6
    if id_module == 6:
        area = uridecode(area.lower())
        if rol in [1, 2, 3] or area == "almacen":
            obj_responsivas = Equipment_Tools_Responsiva.objects.filter(company_id=company_id)
        elif rol == 4:
            obj_responsivas = Equipment_Tools_Responsiva.objects.filter(responsible_equipment=context["user"]["id"])

        # Notificaciones de estado "Solicitado"
        for responsiva in obj_responsivas.filter(status_equipment='Solicitado'):
            response["data"].append({
                "alert": "warning",
                "icon": "<i class=\"fa-solid fa-exclamation-triangle fs-18\"></i>",
                "title": "Equipo solicitado",
                "text": f"El equipo '{responsiva.equipment_name.equipment_name}' está en estado 'Solicitado'.",
                "link": f"/equipment/info/{responsiva.equipment_name.id}/"
            })
            
            # Enviar correo si aún no ha sido enviado
            if not responsiva.email_responsiva:
                message_data = {
                    "title": f"Solicitud del equipo: {responsiva.equipment_name.equipment_name}",
                    "body": f"El equipo <strong>{responsiva.equipment_name.equipment_name}</strong> ha sido solicitado por el empleado <strong>{responsiva.responsible_equipment.username}</strong>. Por favor, revisa la solicitud correspondiente."
                }
                Send_Email(
                    subject="Solicitud de equipo o herramienta",
                    recipient="elizabeth.pascual@tenergy.com.mx",
                    model_instance=responsiva,
                    message_data=message_data,
                    model_name=Equipment_Tools_Responsiva,
                    field_to_update="email_responsiva"
                )

        # Notificaciones cuando la solicitud es aceptada
        for responsiva in obj_responsivas.filter(status_equipment__iexact='Aceptado'):
            print(f"Agregando notificación para: {responsiva.equipment_name.equipment_name}")  

            if not responsiva.email_responsiva_aceptada:
                response["data"].append({
                    "alert": "success",
                    "icon": "<i class='fa-solid fa-check-circle fs-18'></i>",
                    "title": "Solicitud aceptada",
                    "text": f"Tu solicitud del equipo '{responsiva.equipment_name.equipment_name}' ha sido aceptada.",
                    "link": f"/equipment/info/{responsiva.equipment_name.id}/"
                })

                print("✅ Notificación agregada:", response["data"][-1])

            if not responsiva.email_responsiva_aceptada:
                print(f"Enviando correo de aceptacion_responsiva: {responsiva.responsible_equipment.email}") 
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
                print("Correo enviado y campo actualizado para la aceptacion de solicitudes de equipos y herramientas.")

        # # Notificaciones un día antes de la fecha de entrega
        # tomorrow = now().date() + timedelta(days=1)
        # for responsiva in obj_responsivas.filter(fecha_entrega=tomorrow, status_equipment__iexact='Aceptado'):
        #     if not responsiva.email_responsiva_next:
        #         message_data = {
        #             "title": "Recordatorio de devolución",
        #             "body": f"El equipo <strong>{responsiva.equipment_name.equipment_name}</strong> debe ser devuelto mañana."
        #         }
        #         Send_Email(
        #             subject="Recordatorio de devolución de equipo",
        #             recipient=responsiva.responsible_equipment.email,
        #             model_instance=responsiva,
        #             message_data=message_data,
        #             model_name=Equipment_Tools_Responsiva,
        #             field_to_update="email_responsiva_next"
        #         )

        # # Notificaciones de equipos no devueltos a tiempo
        # for responsiva in obj_responsivas.filter(status_equipment__iexact='Atrasado'):
        #     if not responsiva.email_responsiva_late:
        #         to_send = [responsiva.responsible_equipment.email]
        #         almacen_responsable = User_Access.objects.filter(
        #             company__id=request.session["company"]["id"],
        #             area__company__id=request.session["company"]["id"],
        #             area__name='Almacén',
        #             role__name="Encargado"
        #         ).first()
        #         if almacen_responsable:
        #             to_send.append(almacen_responsable.email)
                
        #         message_data = {
        #             "title": "Equipo no devuelto a tiempo",
        #             "body": f"El equipo <strong>{responsiva.equipment_name.equipment_name}</strong> no ha sido devuelto en la fecha establecida."
        #         }
        #         for email in to_send:
        #             Send_Email(
        #                 subject="Equipo no devuelto a tiempo",
        #                 recipient=email,
        #                 model_instance=responsiva,
        #                 message_data=message_data,
        #                 model_name=Equipment_Tools_Responsiva,
        #                 field_to_update="email_responsiva_late"
        #             )

        # # Notificaciones cuando la fecha de entrega ha sido actualizada
        # for responsiva in obj_responsivas.filter(status_modified=True):
        #     if not responsiva.email_responsiva_date:
        #         to_send = [responsiva.responsible_equipment.email]
        #         if almacen_responsable:
        #             to_send.append(almacen_responsable.email)
                
        #         message_data = {
        #             "title": "Fecha de entrega actualizada",
        #             "body": f"La fecha de entrega del equipo <strong>{responsiva.equipment_name.equipment_name}</strong> ha sido modificada. Por favor, revisa la nueva fecha de entrega."
        #         }
        #         for email in to_send:
        #             Send_Email(
        #                 subject="Fecha de entrega de equipo actualizada",
        #                 recipient=email,
        #                 model_instance=responsiva,
        #                 message_data=message_data,
        #                 model_name=Equipment_Tools_Responsiva,
        #                 field_to_update="email_responsiva_date"
        #             )


        # !   /-----------------------------------------------/
        # !  /  SERVICIOS / PAGOS PENDIENTES Y NO PAGADOS
        # ! /-----------------------------------------------/
        # servicios numero 5 
        if id_module == 5:
            print("entramos a servicios")
            if 33 in access and access[33]["read"]:  
                obj_pagos_servicios = Payments_Services.objects.filter(name_service_payment__company_id=company_id)
                # Filtrar por el rol del usuario
                if context["role"]["id"] not in roles_usuario:
                    obj_pagos_servicios = obj_pagos_servicios.filter(name_service_payment__responsible_id=context["user"]["id"])
                print(obj_pagos_servicios.filter(status_payment = 'unpaid'))
                print(obj_pagos_servicios.filter(status_payment = 'upcoming'))
                print(obj_pagos_servicios.filter(status_payment = 'pending'))
                print(obj_pagos_servicios.filter(status_payment = 'paid')) 
                # Notificaciones para servicios con pago "proximo"
                for pago in obj_pagos_servicios.filter(status_payment='upcoming'):
                    response["data"].append({
                        "alert": "warning",
                        "icon": "<i class=\"fa-solid fa-comment-dollar fs-18\"></i>",
                        "title": f"Pago próximo de servicio",
                        "text": f"El servicio '{pago.name_service_payment.name_service}' tiene un pago próximo.",
                        "link": f"/get_payment_history_notifications/{pago.name_service_payment.id}/"

                    })

                    if pago.email_payment == False:
                        print(f"Enviando correo para: {pago.name_service_payment} con fecha {pago.next_date_payment}")
                        
                        message_data = {
                            "title": f"Recordatorio de Pago: {pago.name_service_payment.name_service}",
                            "body": f"El servicio <strong>{pago.name_service_payment.name_service}</strong> tiene un pago próximo programado para el <strong>{pago.next_date_payment}</strong>. Por favor, realiza el pago correspondiente."
                        }

                        Send_Email(
                            subject="Recordatorio de Pago de Servicio",
                            recipient="elizabeth.pascual@tenergy.com.mx",
                            model_instance=pago,
                            message_data=message_data,
                            model_name=Payments_Services,
                            field_to_update="email_payment"
                        )
                        print("Correo enviado y campo actualizado.")

                # Notificaciones para servicios con pago "no pagado"
                for pago in obj_pagos_servicios.filter(status_payment='unpaid'):
                    response["data"].append({
                        "alert": "danger",
                        "icon": "<i class=\"fa-sharp-duotone fa-solid fa-money-check-dollar fs-18\"></i>",
                        "title": f"Pago no realizado de servicio",
                        "text": f"El servicio '{pago.name_service_payment.name_service}' está en estado 'No Pagado'.",
                        "link": f"/get_payment_history_notifications/{pago.name_service_payment.id}/"
                    })

                    if pago.email_payment_unpaid == False:
                        print(f"Enviando correo para: {pago.name_service_payment} con fecha {pago.next_date_payment}")
                        
                        message_data = {
                            "title": f"Recordatorio de Servicio No Pago: {pago.name_service_payment.name_service}",
                            "body": f"El servicio <strong>{pago.name_service_payment.name_service}</strong> tiene un pago no realizado programado para el <strong>{pago.next_date_payment}</strong>. Por favor, realiza el pago correspondiente."
                        }

                        Send_Email(
                            subject="Recordatorio de Pago de Servicio",
                            recipient="elizabeth.pascual@tenergy.com.mx",
                            model_instance=pago,
                            message_data=message_data,
                            model_name=Payments_Services,
                            field_to_update="email_payment_unpaid"
                        )
                        print("Correo enviado y campo actualizado.")

            print("estos son los daros que retorna")
            print(response["data"])
            print(len(response["data"]))

            response["recordsTotal"] = len(response["data"])
            response["success"] = True
            return JsonResponse(response)

        # !   /-----------------------------------------------/
        # !  /  VEHICULOS   / INFO
        # ! /-----------------------------------------------/
        # Nada de nada
     
        # numero vehiculos
        if id_module == 2: 
                
            obj_vehicles = Vehicle.objects.filter(company_id=company_id).values().exclude(is_active=False)
            if context["role"]["id"] not in roles_usuario:
                obj_vehicles = obj_vehicles.filter(responsible_id = context["user"]["id"])
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

                            print(f"Enviando correo para: {tenencia.vehiculo.name} con fecha {tenencia.fecha_pago}")
                            
                            message_data = {
                                "title": f"Recordatorio de Pago de tenencia del vehículo: {tenencia.vehiculo.name}",
                                "body": f"La licencia para el vehículo <strong>{tenencia.vehiculo.name}</strong> esta programada para la fecha <strong>{tenencia.fecha_pago}</strong>. Por favor, verifica la tenencia."
                            }

                            Send_Email(
                                subject="Recordatorio de Tenencia",
                                recipient="elizabeth.pascual@tenergy.com.mx",
                                model_instance=tenencia,
                                message_data=message_data,
                                model_name=Vehicle_Tenencia,
                                field_to_update="email_tenencia"
                            )
                            print("Correo enviado y campo actualizado de tenencia.")

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

                            print(f"Enviando correo para pago de refrendo: {refrendo.vehiculo.name} con fecha {refrendo.fecha_pago}")
                            
                            message_data = {
                                "title": f"Recordatorio de Pago de refrendo del vehículo: {refrendo.vehiculo.name}",
                                "body": f"El refrendo para el vehículo <strong>{refrendo.vehiculo.name}</strong> esta programada para la fecha <strong>{refrendo.fecha_pago}</strong>. Por favor, verifica el refrendo."
                            }

                            Send_Email(
                                subject="Recordatorio de refrendo",
                                recipient="elizabeth.pascual@tenergy.com.mx",
                                model_instance=refrendo,
                                message_data=message_data,
                                model_name=Vehicle_Refrendo,
                                field_to_update="email_refrendo"
                            )
                            print("Correo enviado y campo actualizado de refrendo.")


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
                            Q(fecha_pago_month_in = payment_months) &
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
                                "link": f"/vehicles/info/{item['id']}/"
                            })
                        elif (current_month + 1)  == cv[d]["s1"][0]["month_code"]:
                            """" Falta un mes para el pago del 1er Semestre """
                            month_name_ES = cv[d]["s1"][0]["month_name_ES"]
                            response["data"].append({
                                "alert": "info",
                                "icon": "<i class=\"fa-regular fa-money-bill-wave fs-18\"></i>",
                                "title": f"Próximo pago de verificación en {month_name_ES}",
                                "text": f"Vehículo: {item['name']}",
                                "link": f"/vehicles/info/{item['id']}/"
                            })

                            verificacion = Vehicle_Verificacion.objects.filter(vehiculo__id=item["vehiculo__id"], fecha_pago=item["ultima_fecha"]).first()

                        
                            if verificacion and not verificacion.email_verificacion:

                                print(f"Enviando correo para pago de verificacion: {verificacion.vehiculo.name} con fecha {verificacion.fecha_pago}")
                                
                                message_data = {
                                    "title": f"Recordatorio de Pago de verificacion del vehículo: {verificacion.vehiculo.name}",
                                    "body": f"La verificacion para el vehículo <strong>{vehicle.vehiculo.name}</strong> esta programada para la fecha <strong>{verificacion.fecha_pago}</strong>. Por favor, verifica la verificación."
                                }

                                Send_Email(
                                    subject="Recordatorio de verificación",
                                    recipient="elizabeth.pascual@tenergy.com.mx",
                                    model_instance=verificacion,
                                    message_data=message_data,
                                    model_name=Vehicle_Verificacion,
                                    field_to_update="email_verificacion"
                                )
                                print("Correo enviado y campo actualizado de verificacion.")

                        elif current_month  == cv[d]["s2"][0]["month_code"] or current_month  == cv[d]["s2"][1]["month_code"]:
                            """" Estamos en el mes para el pago del 2do Semestre """
                            response["data"].append({
                                "alert": "warning",
                                "icon": "<i class=\"fa-regular fa-money-bill-wave fs-18\"></i>",
                                "title": f"Realizar el pago de la verificación 2do Sem.",
                                "text": f"Vehículo: {item['name']}",
                                "link": f"/vehicles/info/{item['id']}/"
                            })
                        elif (current_month + 1)  == cv[d]["s2"][0]["month_code"]:
                            """" Falta un mes para el pago del 2er Semestre """
                            month_name_ES = cv[d]["s2"][0]["month_name_ES"]
                            response["data"].append({
                                "alert": "info",
                                "icon": "<i class=\"fa-regular fa-money-bill-wave fs-18\"></i>",
                                "title": f"Próximo pago de verificación en {month_name_ES}",
                                "text": f"Vehículo: {item['name']}",
                                "link": f"/vehicles/info/{item['id']}/"
                            })

                            verificacion = Vehicle_Verificacion.objects.filter(vehiculo__id=item["vehiculo__id"], fecha_pago=item["ultima_fecha"]).first()

                        
                            if verificacion and not verificacion.email_verificacion:

                                print(f"Enviando correo para pago de verificacion: {verificacion.vehiculo.name} con fecha {verificacion.fecha_pago}")
                                
                                message_data = {
                                    "title": f"Recordatorio de Pago de verificacion del vehículo: {verificacion.vehiculo.name}",
                                    "body": f"La verificacion para el vehículo <strong>{vehicle.vehiculo.name}</strong> esta programada para la fecha <strong>{verificacion.fecha_pago}</strong>. Por favor, verifica la verificación."
                                }

                                Send_Email(
                                    subject="Recordatorio de verificación",
                                    recipient="elizabeth.pascual@tenergy.com.mx",
                                    model_instance=verificacion,
                                    message_data=message_data,
                                    model_name=Vehicle_Verificacion,
                                    field_to_update="email_verificacion"
                                )
                                print("Correo enviado y campo actualizado de verificacion.")
                                
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
                            "link": f"/vehicles/info/{vehicle['id']}/"
                        })
                    elif ultima_fecha <= fecha_actual + timedelta(days=5):
                        dias_restantes = (ultima_fecha - fecha_actual).days
                        response["data"].append({
                            "alert": "info",
                            "icon": "<i class=\"fa-solid fa-info fs-18\"></i>",
                            "title": f"Seguro a punto de vencer en {dias_restantes} días",
                            "text": f"Vehículo: {item['vehicle__name']}",
                            "link": f"/vehicles/info/{vehicle['id']}/"
                        })

                        insurance = Vehicle_Insurance.objects.filter(vehicle__id=item["vehicle__id"], end_date=item["ultima_fecha"]).first()

                        
                        if insurance and not insurance.email_insurance:

                            print(f"Enviando correo para pago de seguro: {insurance.vehicle.name} con fecha {insurance.end_date}")
                            
                            message_data = {
                                "title": f"Recordatorio de Pago de seguro del vehículo: {insurance.vehicle.name}",
                                "body": f"El seguro para el vehículo <strong>{insurance.vehicle.name}</strong> esta programada para la fecha <strong>{insurance.end_date}</strong>. Por favor, verifica el pago de seguro."
                            }

                            Send_Email(
                                subject="Recordatorio de pago de seguro",
                                recipient="elizabeth.pascual@tenergy.com.mx",
                                model_instance=insurance,
                                message_data=message_data,
                                model_name=Vehicle_Insurance,
                                field_to_update="email_insurance"
                            )
                            print("Correo enviado y campo actualizado de seguro.")

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
                        "link": f"/vehicles/info/{vehicle['id']}/"
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
                obj_auditorias_hoy.filter(is_visible=False).update(is_visible=True)

                for auditoria in obj_auditorias_hoy:
                    response["data"].append({
                        "alert": "info",
                        "icon": "<i class=\"fa-solid fa-clipboard-check fs-18\"></i>",
                        "title": "Auditoría programada para hoy",
                        "text": f"Vehículo: {auditoria.vehicle.name}",
                        "link": f"/vehicles/info/{auditoria.vehicle.id}/"
                    })

                    auditoria = Vehicle_Audit.objects.filter(vehicle__id=auditoria.vehicle.id, audit_date=auditoria.audit_date).first()

                        
                    if auditoria and not auditoria.email_audit:

                        print(f"Enviando correo para pago de auditoria: {auditoria.vehicle.name} con fecha {auditoria.audit_date}")
                        
                        message_data = {
                            "title": f"Recordatorio de Pago de auditoria del vehículo: {auditoria.vehicle.name}",
                            "body": f"La auditoria para el vehículo <strong>{auditoria.vehicle.name}</strong> esta programada para la fecha <strong>{auditoria.audit_date}</strong>. Por favor, verifica la auditoria."
                        }

                        Send_Email(
                            subject="Recordatorio de auditoria",
                            recipient="elizabeth.pascual@tenergy.com.mx",
                            model_instance=auditoria,
                            message_data=message_data,
                            model_name=Vehicle_Audit,
                            field_to_update="email_audit"
                        )
                        print("Correo enviado y campo actualizado de auditoria.")


                pass
            
            # !   /-----------------------------------------------/
            # !  /  VEHICULOS / MANTENIMIENTO
            # ! /-----------------------------------------------/
            if 11 in access and access[11]["read"]:
                obj_mantenimiento = Vehicle_Maintenance.objects.filter(vehicle__company_id=company_id)

                # Filtrar por el rol del usuario
                if context["role"]["id"] not in roles_usuario:
                    obj_mantenimiento = obj_mantenimiento.filter(vehicle__responsible_id=context["user"]["id"])

                obj_mantenimiento_alerta = obj_mantenimiento.filter(
                    Q(status__iexact="ALERTA") | Q(status__iexact="NUEVO") | Q(status__iexact="GENERADO")

                )

                for mantenimiento in obj_mantenimiento_alerta:
                    response["data"].append({
                        "alert": "danger",
                        "icon": "<i class=\"fa-solid fa-tools fs-18\"></i>",
                        "title": f"Mantenimiento en estado{mantenimiento.status}",
                        "text": f"Vehículo: {mantenimiento.vehicle.name}",
                        "link": f"/vehicles/info/{mantenimiento.vehicle.id}/"
                    })

                    # Enviar correo si aún no se ha enviado
                    if not mantenimiento.email_maintenance:
                        print(f"Enviando correo para mantenimiento de {mantenimiento.vehicle.name} en estado {mantenimiento.status}")

                        message_data = {
                            "title": f"Recordatorio de Mantenimiento: {mantenimiento.vehicle.name}",
                            "body": f"El mantenimiento del vehículo <strong>{mantenimiento.vehicle.name}</strong> está en estado <strong>{mantenimiento.status}</strong>. Por favor, revisa el mantenimiento."
                        }

                        Send_Email(
                            subject="Recordatorio de Mantenimiento",
                            recipient="@tenergy.com.mx",
                            model_instance=mantenimiento,
                            message_data=message_data,
                            model_name=Vehicle_Maintenance,
                            field_to_update="email_maintenance"
                        )
                        print("Correo enviado y campo actualizado de mantenimiento.")

                pass
            # ! -----------------------------------------------
        
            print(response["data"])
            response["recordsTotal"] = len(response["data"])
            response["success"] = True
            return JsonResponse(response)

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
        email = EmailMultiAlternatives(subject, text_content, from_email, [recipient])

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