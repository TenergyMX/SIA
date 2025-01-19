from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from modules.models import *
from users.models import *
from modules.utils import * 
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.db import transaction
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.template.loader import get_template
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.core.files.storage import FileSystemStorage
from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from django.utils import timezone
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
import json, os
import calendar
from django.db.models import Sum, F
from django.db.models.functions import ExtractMonth, ExtractYear

# Llamar módulos y submódulos 
#submodulo de categorias de servicios 
@login_required
def category_services(request):
    context = user_data(request)
    module_id = 5
    subModule_id = 32
    request.session["last_module_id"] = module_id

    if not check_user_access_to_module(request, module_id, subModule_id):
        return render(request, "error/access_denied.html")

    access = get_module_user_permissions(context, subModule_id)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]

    #permisos para agregar categorias de servicios
    context["area"] = context["area"]["name"].lower()
    context["create"] = access["data"]["access"]["create"]
    context["tipo_user"] = context["role"]["name"].lower

    if context["access"]["read"]:
        template = "services/category_services.html"
    else:
        template = "error/access_denied.html"
    return render(request, template , context) 


#submodulo de servicios 
@login_required
def services(request):
    context = user_data(request)
    module_id = 5
    subModule_id = 33
    request.session["last_module_id"] = module_id

    if not check_user_access_to_module(request, module_id, subModule_id):
        return render(request, "error/access_denied.html")
    
    access = get_module_user_permissions(context, subModule_id)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]
    
    #permisos para agregar servicios
    context["area"] = context["area"]["name"].lower()
    context["create"] = access["data"]["access"]["create"]
    context["tipo_user"] = context["role"]["name"].lower


    
    if context["access"]["read"]:
        template = "services/services.html"
    else:
        template = "error/access_denied.html"
    return render(request, template , context) 


#submodulo de dashboard de servicios 
@login_required
def dashboard_services(request):
    context = user_data(request)
    module_id = 5
    subModule_id = 34
    request.session["last_module_id"] = module_id

    if not check_user_access_to_module(request, module_id, subModule_id):
        return render(request, "error/access_denied.html")

    access = get_module_user_permissions(context, subModule_id)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]
    
    if context["access"]["read"]:
        template = "services/dashboard_services.html"
    else:
        template = "error/access_denied.html"
    return render(request, template , context) 

#submodulo de historial depagos de servicios 
@login_required
def payments_history(request):
    context = user_data(request)
    module_id = 5
    subModule_id = 35
    request.session["last_module_id"] = module_id

    access = get_module_user_permissions(context, subModule_id)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]
    
    if context["access"]["read"]:
        template = "services/payments_history.html"
    else:
        template = "error/access_denied.html"
    return render(request, template , context) 

# Función para la tabla categorias de servicios
def get_table_category_service(request):
    response = {"status": "error", "message": "Sin procesar"}
    try:
        context = user_data(request)
        company_id = context.get("company", {}).get("id")
        isList = request.GET.get("isList", False)
        subModule_id = 32

        if not company_id:
            response["message"] = "No se encontró una empresa asociada al usuario"
            return JsonResponse(response, status=400)
        
        if isList:
            datos = list(Services_Category.objects.filter(
                    empresa=company_id 
                ).distinct().values("id", "name_category", "short_name_category"))
        else:
            access = get_module_user_permissions(context, subModule_id)  # contiene el crud
            access = access["data"]["access"]
            area = context["area"]["name"]
            editar = access["update"]
            eliminar = access["delete"]
            tipo_user = context["role"]["name"]

            datos = list(Services_Category.objects.filter(
                    empresa=company_id
                ).distinct().values())
            for item in datos:
                item["btn_action"] = ""
                if access["update"] is True and (area.lower() == "compras" or tipo_user.lower() in ["administrador", "super usuario"]):
                    item["btn_action"] += (
                        "<button type='button' name='update' class='btn btn-icon btn-sm btn-primary-light edit-btn' onclick='edit_category_services(this)' aria-label='info'>"
                        "<i class='fa-solid fa-pen'></i>"
                        "</button>\n"
                    )
                if access["delete"] is True and (area.lower() == "compras" or tipo_user.lower() in ["administrador", "super usuario"]):
                    item["btn_action"] += (
                        "<button type='button' name='delete' class='btn btn-icon btn-sm btn-danger-light delete-btn' onclick='delete_category_services(this)' aria-label='delete'>"
                        "<i class='fa-solid fa-trash'></i>"
                        "</button>"
                    )

        response["data"] = datos
        response["status"] = "success"
        response["message"] = "Datos cargados exitosamente"
    except Exception as e:
        response["message"] = str(e)

    return JsonResponse(response)


#funcion para agregar las categorias de servicios 
@csrf_protect
@login_required
def add_category(request):
    context = user_data(request)
    subModule_id = 32
    access = get_module_user_permissions(context, subModule_id)  
    
    if request.method == 'POST':
        try:
            company_id = context["company"]["id"]
            name_category = request.POST.get('name').strip()
            short_name_category = request.POST.get('short_name').strip()
            description_category = request.POST.get('description').strip()
            is_active_category = True  # Asegurando que siempre esté activo

            # Validaciones
            if not name_category or not short_name_category or not description_category:
                return JsonResponse({'success': False, 'message': 'Todos los campos son obligatorios.'})

# Verificar duplicados (sin importar mayúsculas o minúsculas)
            if Services_Category.objects.filter(
                name_category__iexact=name_category, empresa_id=company_id
            ).exists():
                return JsonResponse({'success': False, 'message': 'El nombre de la categoría ya existe.'})

            if Services_Category.objects.filter(
                short_name_category__iexact=short_name_category, empresa_id=company_id
            ).exists():
                return JsonResponse({'success': False, 'message': 'El nombre corto de la categoría ya existe.'})

            # Crear una nueva categoría
            with transaction.atomic():
                Services_Category.objects.create(
                    empresa_id=company_id,
                    name_category=name_category,
                    short_name_category=short_name_category,
                    description_category=description_category,
                    is_active_category=is_active_category
                )
            
            return JsonResponse({'success': True, 'message': 'Categoría agregada correctamente!'})
        except ValidationError as e:
            return JsonResponse({'success': False, 'message': str(e)})
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Error inesperado: ' + str(e)})

    return JsonResponse({'success': False, 'message': 'Método de solicitud no válido'})


#funcion para editar las categorias 
@csrf_protect
@login_required
def edit_category_services(request):
    context = user_data(request)
    if request.method == 'POST':
        try:
            company_id = context["company"]["id"]
            _id = request.POST.get('id')
            name_category = request.POST.get('name').strip()
            short_name_category = request.POST.get('short_name').strip()
            description_category = request.POST.get('description').strip()
            is_active_category = request.POST.get('is_active') == '1'

            # Validaciones
            if not name_category or not short_name_category or not description_category:
                return JsonResponse({'success': False, 'message': 'Todos los campos son obligatorios.'})

            # Obtener la categoría existente
            category = get_object_or_404(Services_Category, id=_id)

            # Verificar duplicados 
            if Services_Category.objects.filter(
                name_category__iexact=name_category, empresa=company_id
            ).exclude(id=_id).exists():
                return JsonResponse({'success': False, 'message': 'El nombre de la categoría ya existe.'})

            if Services_Category.objects.filter(
                short_name_category__iexact=short_name_category, empresa=company_id
            ).exclude(id=_id).exists():
                return JsonResponse({'success': False, 'message': 'El nombre corto de la categoría ya existe.'})

            # Actualizar la categoría
            with transaction.atomic():
                category = get_object_or_404(Services_Category, id=_id)
                category.name_category = name_category
                category.short_name_category = short_name_category
                category.description_category = description_category
                category.is_active_category = is_active_category
                category.save()
            
            return JsonResponse({'success': True, 'message': 'Categoría editada correctamente!'})
        except ValidationError as e:
            return JsonResponse({'success': False, 'message': str(e)})
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Error inesperado: ' + str(e)})

    return JsonResponse({'success': False, 'message': 'Método de solicitud no válido'})


#funcion para eliminar las categorias de servicios
@login_required
@csrf_exempt
def delete_category_services(request):
    if request.method == 'POST':
        form = request.POST
        _id = form.get('id')

        if not _id:
            return JsonResponse({'success': False, 'message': 'No ID provided'})

        try:
            category = Services_Category.objects.get(id=_id)
        except Services_Category.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Category not found'})

        category.delete()

        return JsonResponse({'success': True, 'message': 'Categoría eliminada correctamente!'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})


#funcíon para la tabla de servicios
def get_table_services (request):
    response = {"status": "error", "message": "Sin procesar"}
    context = user_data(request)
    isList = request.GET.get("isList", False)
    subModule_id = 33
    company_id = context["company"]["id"] 
    access = get_module_user_permissions(context, subModule_id)["data"]["access"]
    area = context["area"]["name"]
    tipo_user = context["role"]["name"]
    editar = access["update"]
    eliminar = access["delete"]
    agregar = access["create"]
    try:
        company_id = context["company"]["id"] 
        datos = list(Services.objects.filter(
            company_id=company_id
        ).select_related(
            'category_service', 'provider_service'
        ).values(
            "id", 
            "category_service__id",
            "category_service__name_category",
            "name_service",
            "description_service",
            "provider_service__id",
            "provider_service__name",
            "start_date_service",
            "time_quantity_service",
            "time_unit_service",
            "price_service",
        ))

        # Mapa de traducción para unidades de tiempo
        time_unit_translation = {
            'day': ('día', 'días'),
            'month': ('mes', 'meses'),
            'year': ('año', 'años')
        }
        for item in datos:
            item["btn_action"] = ""
            item["btn_history"] = ""
            
            # Botón de historial
            if tipo_user.lower() in ["administrador", "super usuario"] or area.lower() == "compras":
                item["btn_history"] += (
                    "<button type='button' name='btn_history' class='btn btn-icon btn-sm btn-primary-light btn-btn' onclick='show_history_payments(this)' aria-label='info'>"
                    "<i class='fa-solid fa-eye'></i>"
                    "</button>\n"
                )
            if access["update"] is True and (area.lower() == "compras" or tipo_user.lower() in ["administrador", "super usuario"]):
                item["btn_action"] += (
                    "<button type='button' name='update' class='btn btn-icon btn-sm btn-primary-light edit-btn' onclick='edit_services(this)' aria-label='info'>"
                    "<i class='fa-solid fa-pen'></i>"
                    "</button>\n"
                )
            if access["delete"] is True and (area.lower() == "almacen" or tipo_user.lower() in ["administrador", "super usuario"]):
                item["btn_action"] += (
                    "<button type='button' name='delete' class='btn btn-icon btn-sm btn-danger-light delete-btn' onclick='delete_services(this)' aria-label='delete'>"
                    "<i class='fa-solid fa-trash'></i>"
                    "</button>"
                )     

            # Formatear el periodo
            quantity = item.get("time_quantity_service", 0)
            unit = item.get("time_unit_service", "")
            if unit in time_unit_translation:
                unit_display = time_unit_translation[unit][0] if quantity == 1 else time_unit_translation[unit][1]
                item["periodo"] = f"{quantity} {unit_display}"

            # Calcular la fecha de pago
            payment_date = calculate_payment_date(item.get("start_date_service"), quantity, unit)
            item["payment_date"] = payment_date.strftime('%Y-%m-%d') if payment_date else "N/A"

        response["data"] = datos
        response["status"] = "success"
        response["message"] = "Datos cargados exitosamente"
    except Exception as e:
        response["status"] = "error"
        response["message"] = str(e)
    print("esto contiene mi response")
    print(response)
    return JsonResponse(response)


# Vista para obtener las categorías de servicios
@login_required
def get_services_categories(request):
    try:
        context = user_data(request)
        company_id = context["company"]["id"]  

        if not company_id:
            return JsonResponse({'success': False, 'message': 'No se encontró la empresa asociada al usuario'}, status=400)
    # Obtener las categorías de equipo asociadas a la empresa y activas
        categories = Services_Category.objects.filter(
            empresa_id=company_id, is_active_category=True
        ).values('id', 'name_category') 
        data = list(categories)

        return JsonResponse({'data': data}, safe=False)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


# Funcion para obtener los nombres de los proveedores
@login_required
@csrf_exempt
def get_services_providers(request):
    try:
        context = user_data(request)
        company_id = context["company"]["id"]
        print("este es el id de la compañia: ", company_id)
        company_name = context["company"]["name"]
        print("este es el nombre de la compañia de servicios: ", company_name)

        if not company_id:
            return JsonResponse({'success': False, 'message': 'No se encontró la empresa asociada al usuario'}, status=400)
        
        provedores = Provider.objects.filter(company_id=company_id).distinct().values('id', 'name')  
        data = list(provedores)
        return JsonResponse({'data': data}, safe=False)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


# Función para calcular la fecha de pago
def calculate_payment_date(start_date, quantity, unit):

    try:
        if not start_date:
            start_date = timezone.now()
            print("esto contiene mi fecha:", start_date)

        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')

        if unit == 'day':
            payment_date = start_date + timedelta(days=quantity)
            return payment_date  
        elif unit == 'month':
            return start_date + relativedelta(months=quantity)
        elif unit == 'year':
            return start_date + relativedelta(years=quantity)

        return None
    except Exception as e:
        print(f"Error al calcular la fecha de pago: {str(e)}")
        return None  


# Función para crear el registro de pago inicial
def create_payment(service):

    try:
        today = timezone.now().date()
        print("esta es mi fecha actual de hoy:", today)
        next_payment_date = service.start_date_service  

        # llamr a la función para calcular la fecha del primer pago
        next_payment_date = calculate_payment_date(
            service.start_date_service, 
            service.time_quantity_service, 
            service.time_unit_service
        )

        # Crear el primer pago
        payment = Payments_Services.objects.create(
            name_service_payment=service,
            total_payment=service.price_service, 
            next_date_payment=next_payment_date,
            status_payment='pending',  
        )
        print(f"Primer pago creado para el servicio {service.name_service}.")
    except Exception as e:
        print(f"Error al crear el pago del servicio {service.name_service}: {str(e)}")
        return None 


# Función para actualizar el estado de los pagos
def update_payment_status():
    try:
        today = timezone.now().date()

        # Obtener los pagos con estado pendiente y cuya fecha de pago es mayor o igual a la fecha actual
        payments = Payments_Services.objects.filter(status_payment='pending', next_date_payment__gte=today)

        for payment in payments:
            days = (payment.next_date_payment - today).days
            service = payment.name_service_payment
            quantity = service.time_quantity_service
            unit = service.time_unit_service

            # Día: Actualizar pagos que estan en dias 
            if unit == 'day' and days <= 1:
                payment.status_payment = 'upcoming'
                payment.save()

                # Calcular la nueva fecha de pago
                next_payment_date = calculate_payment_date(payment.next_date_payment, quantity, unit)

                # Crear el siguiente pago
                Payments_Services.objects.create(
                    name_service_payment=service,
                    total_payment=payment.total_payment,
                    next_date_payment=next_payment_date,
                    status_payment='pending',
                )

            # Mes o año: Actualizar pagos mensuales o anuales que deben estar cerca de su vencimiento
            elif (unit in ['month', 'year']) and days <= 7:
                payment.status_payment = 'upcoming'
                payment.save()

                # Calcular la nueva fecha de pago
                next_payment_date = calculate_payment_date(payment.next_date_payment, quantity, unit)

                # Crear el siguiente pago
                Payments_Services.objects.create(
                    name_service_payment=service,
                    total_payment=payment.total_payment,
                    next_date_payment=next_payment_date,
                    status_payment='pending',
                )

        # revisar los pagos con estado "upcoming" para ver si la fecha ya pasó y no tienen comprobante
        upcoming_payments = Payments_Services.objects.filter(status_payment='upcoming')

        for payment in upcoming_payments:
            # Si la fecha ya pasó y no tiene comprobante de pago, cambiar el estado a "unpaid"
            if payment.next_date_payment < today and not payment.proof_payment:
                print(f"Cambiando el estado del pago {payment.id} a 'unpaid' porque no se ha subido comprobante.")
                payment.status_payment = 'unpaid'
                payment.save()

        print("Pagos actualizados correctamente.")
    except Exception as e:
        print(f"Error al actualizar los pagos: {str(e)}")


# Función para agregar un servicio
@csrf_protect
@login_required
def add_service(request):
    context = user_data(request)
    subModule_id = 33
    access = get_module_user_permissions(context, subModule_id)  
    company_id = context["company"]["id"]

    if request.method == 'POST':
        try:
            category_service_id = request.POST.get('category_service')
            name_service = request.POST.get('name_service').strip()
            description_service = request.POST.get('description_service').strip()
            provider_service_id = request.POST.get('provider_service')
            start_date_service = request.POST.get('start_date_service')
            time_quantity_service = int(request.POST.get('time_quantity_service'))  
            time_unit_service = request.POST.get('time_unit_service')
            price_service = request.POST.get('price_service')

            # Validaciones
            if not all([category_service_id, name_service, description_service, provider_service_id, 
                        start_date_service, time_quantity_service, time_unit_service, price_service]):
                return JsonResponse({'success': False, 'message': 'Todos los campos son obligatorios.'})

            # Verificar duplicados (sin importar mayúsculas o minúsculas)
            if Services.objects.filter(name_service__iexact=name_service, company_id=company_id).exists():
                return JsonResponse({'success': False, 'message': 'El nombre del servicio ya existe para esta empresa, ingresa uno diferente.'})

            # Obtener objetos relacionados
            category_service = get_object_or_404(Services_Category, id=category_service_id)
            provider_service = get_object_or_404(Provider, id=provider_service_id)

            # Crear un nuevo servicio
            with transaction.atomic():
                service = Services.objects.create(
                    company_id = company_id,
                    category_service=category_service,
                    name_service=name_service,
                    description_service=description_service,
                    provider_service=provider_service,
                    start_date_service=start_date_service,
                    time_quantity_service=time_quantity_service,
                    time_unit_service=time_unit_service,
                    price_service=price_service,    
                )

                # Generar el primer pago al registrar el servicio
                create_payment(service)

                # Actualizar los pagos
                #update_payment_status()  

            return JsonResponse({'success': True, 'message': 'Servicio agregado correctamente!'})
        except ValidationError as e:
            print(f"Error de validación: {str(e)}")
            return JsonResponse({'success': False, 'message': str(e)})
        except Exception as e:
            print(f"Error inesperado al agregar el servicio: {str(e)}")
            return JsonResponse({'success': False, 'message': 'Error inesperado: ' + str(e)})

    return JsonResponse({'success': False, 'message': 'Método de solicitud no válido'})

# Función para editar los servicios
def edit_services(request):
    context = user_data(request)
    company_id = context["company"]["id"]
    try:
        if request.method == 'POST':
            _id = request.POST.get('id')
            category_service_id = request.POST.get('category_service')
            name_service = request.POST.get('name_service').strip()
            description_service = request.POST.get('description_service').strip()
            provider_service = request.POST.get('provider_service')
            start_date_service = request.POST.get('start_date_service')
            time_quantity_service = request.POST.get('time_quantity_service')
            time_unit_service = request.POST.get('time_unit_service')
            price_service = request.POST.get('price_service')

            # Validaciones
            if not all([_id, category_service_id, name_service, description_service, provider_service,
                        start_date_service, time_quantity_service, time_unit_service, price_service]):
                return JsonResponse({'success': False, 'message': 'Todos los campos son obligatorios.'})

            services = Services.objects.get(id=_id)

            # Convertir `time_quantity_service` a entero
            time_quantity_service = int(time_quantity_service)

            
            # Verificar duplicados (sin importar mayúsculas o minúsculas)
            if Services.objects.filter(name_service__iexact=name_service, company_id=company_id).exclude(id=_id).exists():
                return JsonResponse({'success': False, 'message': 'El nombre del servicio ya existe para esta empresa, ingresa uno diferente.'})

           # Guardar el precio antiguo para compararlo
            old_price = services.price_service


            # actualizar los campos del servicio
            company_id = company_id
            services.category_service_id = category_service_id
            services.name_service = name_service
            services.description_service = description_service
            services.provider_service_id = provider_service
            services.start_date_service = start_date_service
            services.time_quantity_service = time_quantity_service
            services.time_unit_service = time_unit_service
            services.price_service = price_service

            services.save()

            # Crear un nuevo registro de pago con el nuevo precio
            create_new_payment_for_service(services, price_service)



            return JsonResponse({'success': True, 'message': 'Servicio editado correctamente!'})

    except Services.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Servicio no encontrado'}, status=404)

    except ValueError as ve:
        return JsonResponse({'success': False, 'message': f'Error de valor: {str(ve)}'}, status=400)

    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error interno del servidor: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'message': 'Método de solicitud inválido'})


#funcion para eliminar servicios
@login_required
@csrf_exempt
def delete_services(request):
    if request.method == 'POST':
        form = request.POST
        _id = form.get('id')

        if not _id:
            return JsonResponse({'success': False, 'message': 'No ID provided'})

        try:
            services = Services.objects.get(id=_id)
        except Services.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Service not found'})

        services.delete()

        return JsonResponse({'success': True, 'message': 'Servicio eliminado correctamente!'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})


# Función para subir el documento de pago y actualizar el estado 
@login_required
@csrf_exempt
def upload_payment_proof(request, payment_id):
    if request.method == 'POST' and request.FILES.get('proof_payment'):
        try:
            # Obtener el pago asociado al ID
            payment = Payments_Services.objects.get(id=payment_id)
            load_file = request.FILES['proof_payment']
            
            # Obtener datos relacionados al servicio
            company_id = payment.name_service_payment.company.id
            service_name = payment.name_service_payment.name_service.replace(' ', '_')

            # Establecer la ruta donde se guardará el archivo
            folder_path = f"docs/{company_id}/services/proof_payment/{service_name}/"
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, folder_path))

            # Generar el nombre único para el archivo
            current_date = datetime.now().strftime('%Y%m%d')
            file_name, extension = os.path.splitext(load_file.name)
            new_name = f"comprobante_pago_{service_name}_{current_date}{extension}"

            # Guardar el archivo en el sistema de archivos
            fs.save(new_name, load_file)

            # Actualizar la ruta del archivo en la tabla de pagos
            payment.proof_payment = os.path.join(folder_path, new_name)

            # Cambiar el estado del pago a "Pagado"
            payment.status_payment = 'paid'
            payment.save()

            # Llamar a la función de actualización de estado
            # update_payment_status()

            return JsonResponse({'success': True, 'message': 'Comprobante subido correctamente y estado actualizado.'})

        except Payments_Services.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Pago no encontrado.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error inesperado: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)


#funcion de la tabla historial
@login_required
def get_payment_history(request, service_id):
    try:
        payments = Payments_Services.objects.filter(name_service_payment_id=service_id).order_by('-next_date_payment').values(
            'id',
            'name_service_payment__name_service',
            'proof_payment',
            'total_payment',
            'next_date_payment',
            'status_payment'
        )

        return JsonResponse(list(payments), safe=False)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error inesperado: {str(e)}'}, status=500)


# funcion para obtener el comprobante
@login_required
def get_proof_payment(request, payment_id):
    try:
        payment = Payments_Services.objects.get(id=payment_id)
        
        # Verificar si el comprobante de pago existe
        if payment.proof_payment:
            proof_url = payment.proof_payment.url  
            return JsonResponse({'success': True, 'proof_payment': proof_url})
        else:
            return JsonResponse({'success': False, 'message': 'Comprobante no encontrado.'})

    except Payments_Services.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Pago no encontrado.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error inesperado: {str(e)}'}, status=500)


def create_new_payment_for_service(service, new_price):
    try:
        # Calcular la nueva fecha de pago
        new_payment_date = calculate_payment_date(
            service.start_date_service,
            service.time_quantity_service,
            service.time_unit_service
        )

        # Verificar si ya existe un registro de pago para esa fecha
        if Payments_Services.objects.filter(
            name_service_payment=service,
            next_date_payment=new_payment_date
        ).exists():
            raise ValueError(f"Ya existe un pago programado para el servicio {service.name_service} en la fecha {new_payment_date}.")


        # Crear un nuevo registro de pago con estado pendiente
        Payments_Services.objects.create(
            name_service_payment=service,
            next_date_payment=new_payment_date,
            total_payment=new_price,  
            status_payment='pending',
        )
    except Exception as e:
        raise Exception(f'Error al crear el nuevo pago: {str(e)}')

#funcion para actulizar el estado de los pagos
def update_payment_status_view(request):
    try:
        print("Iniciando la actualización de pagos...") 
        update_payment_status()  
        print("Pagos actualizados correctamente.") 
        return JsonResponse({'status': 'success', 'message': 'Pagos actualizados correctamente en la pagina principal'})
    except Exception as e:
        print(f"Error al actualizar los pagos: {str(e)}")  
        return JsonResponse({'status': 'error', 'message': f'Error al actualizar los pagos: {str(e)}'})

#funcion para los contadores
def get_dashboard_data(request):
    try:
        context = user_data(request)
        company_id = context["company"]["id"]
        if not company_id:
            return JsonResponse({"status": "error", "message": "No se encontró la empresa asociada al usuario"}, status=400)

        # Total de servicios
        total_services = Services.objects.filter(company_id=company_id).count()

        # Total de egresos: 
        total_egresos = Payments_Services.objects.filter(
            status_payment='paid', 
            name_service_payment__company_id=company_id
        ).aggregate(total=Sum('total_payment'))['total'] or 0.0

        # Total de pagos no pagados
        total_non_paid_payments = Payments_Services.objects.filter(
            status_payment='unpaid',
            name_service_payment__company_id=company_id 
        ).count()

        # Formatear la respuesta
        response_data = {
            "total_services": total_services,
            "total_egresos": total_egresos,
            "total_non_paid_payments": total_non_paid_payments
        }

        return JsonResponse({"status": "success", "data": response_data})

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


#Función para la grafica principal de egresos por categoria 
def get_dashboard_grafica(request):
    try:
        # Obtener el contexto del usuario
        context = user_data(request)
        company_id = context["company"]["id"]

        # Verificar company
        if not company_id:
            return JsonResponse({"status": "error", "message": "No se encontró la empresa asociada al usuario"}, status=400)

        # categorías de servicios activas
        categories = Services_Category.objects.filter(
            is_active_category=True,
            services__company_id=company_id
        ).distinct()

        # Lista para almacenar los datos de cada categoría
        category_data = []

        # Iterar y sumar los pagos pagados
        for category in categories:
            # Sumar los pagos "pagados" de cada categoría
            total_payment = Payments_Services.objects.filter(
                name_service_payment__category_service=category,
                name_service_payment__company_id=company_id, 
                status_payment='paid'
            ).aggregate(total=Sum('total_payment'))['total'] or 0
            print(f"Total de pago para la categoría {category.name_category}: {total_payment}")

            category_data.append({
                'category': category.name_category,
                'total_payment': total_payment
            })

        return JsonResponse({'status': 'success', 'data': category_data})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
    

# Función para obtener los servicios y egresos por categoría
def get_services_by_category(request, category_id):
    try:

        context = user_data(request)
        company_id = context["company"]["id"]

        if not company_id:
            return JsonResponse({"status": "error", "message": "No se encontró la empresa asociada al usuario"}, status=400)

        services = Services.objects.filter(category_service_id=category_id, company_id=company_id)
        
        # Obtener los pagos "pagados" de los servicios filtrados
        service_data = []
        for service in services:
            total_payment = Payments_Services.objects.filter(
                name_service_payment=service,
                status_payment='paid'
            ).aggregate(total=Sum('total_payment'))['total'] or 0
            service_data.append({
                'service_name': service.name_service,
                'total_payment': total_payment
            })

        return JsonResponse({'status': 'success', 'data': service_data})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)



# Función para obtener los servicios y egresos por proveedor
def get_services_by_provider(request, provider_id):
    try:
        # Obtener los servicios del proveedor seleccionado
        context = user_data(request)
        company_id = context["company"]["id"]

        provider = Provider.objects.get(id=provider_id) 

        services = Services.objects.filter(provider_service_id=provider_id, company_id=company_id)
        
        # Obtener los pagos "pagados" de los servicios filtrados
        service_data = []
        for service in services:
            total_payment = Payments_Services.objects.filter(
                name_service_payment=service,
                status_payment='paid'
            ).aggregate(total=Sum('total_payment'))['total'] or 0
            service_data.append({
                'service_name': service.name_service,
                'total_payment': total_payment
            })

        return JsonResponse({'status': 'success', 'data': service_data, 'provider_name': provider.name})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)



# Función para obtener los egresos por rango de fecha
def get_services_by_date_range(request):
    try:
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        context = user_data(request)
        company_id = context["company"]["id"]

        if not company_id:
            return JsonResponse({"status": "error", "message": "No se encontró la empresa asociada al usuario"}, status=400)

        payments = Payments_Services.objects.filter(
            status_payment='paid',  
            next_date_payment__range=[start_date, end_date],
            name_service_payment__company_id=company_id
        )

       
        service_data_dict = {}

        for payment in payments:
            service_name = payment.name_service_payment.name_service  
            total_payment = payment.total_payment  

            
            if service_name in service_data_dict:
                service_data_dict[service_name] += total_payment
            else:
                service_data_dict[service_name] = total_payment

        service_data = [{'service_name': service, 'total_payment': total} for service, total in service_data_dict.items()]

        # Retornar la respuesta en formato JSON
        return JsonResponse({'status': 'success', 'data': service_data})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# Vista para mostrar el historial de pagos desde una notificación
@login_required
def get_payment_history_notifications(request, service_id):
    context = user_data(request)
    module_id = 5
    subModule_id = 33
    request.session["last_module_id"] = module_id

    access = get_module_user_permissions(context, subModule_id)
    sidebar = get_sidebar(context, [1, module_id])

    print("esto contiene mi sidebar de servicios:", sidebar)
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]



    try:
        # Obtener los pagos asociados al servicio
        payments = Payments_Services.objects.filter(name_service_payment_id=service_id).order_by('-next_date_payment').values(
            'id',
            'name_service_payment__name_service',
            'proof_payment',
            'total_payment',
            'next_date_payment',
            'status_payment'
        )

        for payment in payments:
            if payment['proof_payment']:
                # Documento
                payment['proof_payment_url'] = settings.MEDIA_URL + payment['proof_payment']
            else:
                payment['proof_payment_url'] = None
        return render(request, 'services/payment_details.html', {'payments': payments, 'sidebar': sidebar["data"]})

    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error al cargar los pagos: {str(e)}'}, status=500)


# Vista para obtener las categorías de servicios para la grafica del historial de pagos 
@login_required
def get_services_categories_payments(request):
    try:
        context = user_data(request)
        company_id = context["company"]["id"]  

        if not company_id:
            return JsonResponse({'success': False, 'message': 'No se encontró la empresa asociada al usuario'}, status=400)
    # Obtener las categorías de equipo asociadas a la empresa y activas
        categories = Services_Category.objects.filter(
            empresa_id=company_id, is_active_category=True
        ).values('id', 'name_category') 
        data = list(categories)
        print("Categories Data:", data)

        return JsonResponse({'data': data}, safe=False)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


#Función para la gráfica del historial de egresos por categoria
@login_required
def get_payment_history_grafic(request):
    try:
        category_id = request.GET.get('category_id')
        start_month = request.GET.get('start_month')
        end_month = request.GET.get('end_month')

        
        # Validar que el ID sea un número
        try:
            category_id = int(category_id)
        except ValueError:
            return JsonResponse({'success': False, 'message': 'ID de categoría inválido'}, status=400)

        # Validar fechas
        try:
            start_date = datetime.strptime(start_month, '%Y-%m')
            end_date = datetime.strptime(end_month, '%Y-%m')
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Formato de fechas inválido'}, status=400)

        # Verificar si la categoría existe
        if not Services_Category.objects.filter(id=category_id).exists():
            return JsonResponse({'success': False, 'message': 'La categoría no existe'}, status=404)

        # Obtener los servicios relacionados con la categoría
        services_ids = Services.objects.filter(category_service_id=category_id).values_list('id', flat=True)

        if not services_ids:
            return JsonResponse({'success': False, 'message': 'No hay servicios asociados a esta categoría'}, status=404)

        # Consultar pagos agrupados por mes y año
        payments = Payments_Services.objects.filter(
            name_service_payment_id__in=services_ids,
            next_date_payment__gte=start_date,
            next_date_payment__lte=end_date,
            status_payment='paid'
        ).annotate(
            year=ExtractYear('next_date_payment'),
            month=ExtractMonth('next_date_payment')
        ).values(
            'year', 'month'
        ).annotate(
            total_payments=Sum('total_payment')
        ).order_by('year', 'month')

        
        # Preparar datos para la respuesta con nombres de meses
        months = [
            f"{calendar.month_name[payment['month']]} {payment['year']}" 
            for payment in payments
        ]
        totals = [payment['total_payments'] for payment in payments]

        return JsonResponse({'success': True, 'months': months, 'total_payments': totals})

    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error interno: {str(e)}'}, status=500)
