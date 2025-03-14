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
from modules.models import *
from users.models import *
from modules.utils import *
import requests
from django.urls import resolve

# TODO --------------- [ VIEWS ] ---------- 
def home_view(request):
    context = {}
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
    print("este es el id de modulo:", id_module)
    if id_module == 6:
        
        area = unidecode(area.lower())
        if rol == 1 or rol == 2 or rol == 3 or area == "almacen":
            print("entre como administrador")
            obj_responsivas = Equipment_Tools_Responsiva.objects.filter(
                company_id = company_id         
            )
        elif rol == 4:
            obj_responsivas = Equipment_Tools_Responsiva.objects.filter(
                responsible_equipment=context["user"]["id"]
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

        # Notificaciones de estado "No devuelto"
        for responsiva in obj_responsivas.filter(status_equipment='No devuelto'):
            response["data"].append({
                "alert": "danger",
                "icon": "<i class=\"fa-solid fa-exclamation-circle fs-18\"></i>",
                "title": "Equipo no devuelto",
                "text": f"El equipo '{responsiva.equipment_name.equipment_name}' no ha sido devuelto.",
                "link": f"/equipment/info/{responsiva.equipment_name.id}/"
            })    
        print(response["data"])
        response["recordsTotal"] = len(response["data"])
        response["success"] = True
        return JsonResponse(response)
        
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

            # Notificaciones para servicios con pago "no pagado"
            for pago in obj_pagos_servicios.filter(status_payment='unpaid'):
                response["data"].append({
                    "alert": "danger",
                    "icon": "<i class=\"fa-sharp-duotone fa-solid fa-money-check-dollar fs-18\"></i>",
                    "title": f"Pago no realizado de servicio",
                    "text": f"El servicio '{pago.name_service_payment.name_service}' está en estado 'No Pagado'.",
                    "link": f"/get_payment_history_notifications/{pago.name_service_payment.id}/"
                })
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
    # !   /-----------------------------------------------/
    # !  /  VEHICULOS   / TENENCIA 
    # ! /-----------------------------------------------/
    # numero vehiculos
    if id_module == 2: 
            
        obj_vehicles = Vehicle.objects.filter(company_id=company_id).values().exclude(is_active=False)
        if context["role"]["id"] not in roles_usuario:
            obj_vehicles = obj_vehicles.filter(responsible_id = context["user"]["id"])
        
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
            pass
        # !   /-----------------------------------------------/
        # !  /  VEHICULOS / MANTENIMIENTO
        # ! /-----------------------------------------------/
        if 11 in access and access[11]["read"]:
            obj_mantenimiento = Vehicle_Maintenance.objects.filter(vehicle__company_id=company_id)

            # Filtrar por el rol del usuario
            if context["role"]["id"] not in roles_usuario:
                obj_mantenimiento = obj_mantenimiento.filter(vehicle__responsible_id=context["user"]["id"])
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
