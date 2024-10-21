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
from django.db.models import Sum



# Llamar módulos y submódulos 
#submodulo de categorias de servicios 
@login_required
def category_services(request):
    context = user_data(request)
    module_id = 5
    subModule_id = 32
    request.session["last_module_id"] = module_id

    access = get_module_user_permissions(context, subModule_id)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]
    
    if context["access"]["read"]:
        template = "services/category_services.html"
    else:
        template = "error/access_denied.html"
    return render(request, template , context) 


#submodulo de categorias de servicios 
@login_required
def services(request):
    context = user_data(request)
    module_id = 5
    subModule_id = 33
    request.session["last_module_id"] = module_id

    access = get_module_user_permissions(context, subModule_id)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]


    # Llamar a la función para actualizar los estados de los pagos
    update_payment_statuses()  # Actualiza los estados de los pagos
    
    if context["access"]["read"]:
        template = "services/services.html"
    else:
        template = "error/access_denied.html"
    return render(request, template , context) 



#submodulo de categorias de servicios 
@login_required
def dashboard_services(request):
    context = user_data(request)
    module_id = 5
    subModule_id = 34
    request.session["last_module_id"] = module_id

    access = get_module_user_permissions(context, subModule_id)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]
    
    if context["access"]["read"]:
        template = "services/dashboard_services.html"
    else:
        template = "error/access_denied.html"
    return render(request, template , context) 


# Función para la tabla categorias de servicios
def get_table_category_service(request):
    response = {"status": "error", "message": "Sin procesar"}
    try:
        context = user_data(request)
        isList = request.GET.get("isList", False)
        subModule_id = 32

        if isList:
            datos = list(Services_Category.objects.values("id", "name_category", "short_name_category"))
        else:
            access = get_module_user_permissions(context, subModule_id)  # contiene el crud
            access = access["data"]["access"]
            area = context["area"]["name"]

            datos = list(Services_Category.objects.values())
            for item in datos:
                item["btn_action"] = ""
                item["btn_action"] += (
                    "<button type='button' name='update' class='btn btn-icon btn-sm btn-primary-light edit-btn' onclick='edit_category_services(this)' aria-label='info'>"
                    "<i class='fa-solid fa-pen'></i>"
                    "</button>\n"
                )
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
            name_category = request.POST.get('name').strip()
            short_name_category = request.POST.get('short_name').strip()
            description_category = request.POST.get('description').strip()
            is_active_category = True  # Asegurando que siempre esté activo

            # Validaciones
            if not name_category or not short_name_category or not description_category:
                return JsonResponse({'success': False, 'message': 'Todos los campos son obligatorios.'})

            # Verificar duplicados (sin importar mayúsculas o minúsculas)
            if Services_Category.objects.filter(
                name_category__iexact=name_category
            ).exists():
                return JsonResponse({'success': False, 'message': 'El nombre de la categoría ya existe.'})

            if Services_Category.objects.filter(
                short_name_category__iexact=short_name_category
            ).exists():
                return JsonResponse({'success': False, 'message': 'El nombre corto de la categoría ya existe.'})


            # Crear una nueva categoría
            with transaction.atomic():
                Services_Category.objects.create(
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
    if request.method == 'POST':
        try:
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
                name_category__iexact=name_category
            ).exclude(id=_id).exists():
                return JsonResponse({'success': False, 'message': 'El nombre de la categoría ya existe.'})

            if Services_Category.objects.filter(
                short_name_category__iexact=short_name_category
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

    try:
        datos = list(Services.objects.select_related(
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
            item["btn_history"] += (
                "<button type='button' name='btn_history' class='btn btn-icon btn-sm btn-primary-light btn-btn' onclick='show_history_payments(this)' aria-label='info'>"
                "<i class='fa-solid fa-eye'></i>"
                "</button>\n"
            )

            item["btn_action"] += (
                "<button type='button' name='update' class='btn btn-icon btn-sm btn-primary-light edit-btn' onclick='edit_services(this)' aria-label='info'>"
                "<i class='fa-solid fa-pen'></i>"
                "</button>\n"
            )
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


#función para calcular la fecha de pago 
def calculate_payment_date(start_date, quantity, unit):
    # Si no se proporciona una fecha de inicio, usar la fecha actual del servidor
    if not start_date:
        start_date = timezone.now()
    
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')

    if unit == 'day':
        return start_date + timedelta(days=quantity)
    elif unit == 'month':
        return start_date + relativedelta(months=quantity)
    elif unit == 'year':
        return start_date + relativedelta(years=quantity)
    
    return None


# Vista para obtener las categorías de servicios
@login_required
def get_services_categories(request):
    if request.method == 'GET':
        categories = Services_Category.objects.filter(is_active_category=True).values('id', 'name_category')
        return JsonResponse({'data': list(categories)}, safe=False)
    return JsonResponse({'success': False, 'message': 'Método de solicitud no válido'})


# Funcion para obtener los nombres de los proveedores
@login_required
@csrf_exempt
def get_services_providers(request):
    try:
        provedores = Provider.objects.values('id', 'name')  
        data = list(provedores)
        return JsonResponse({'data': data}, safe=False)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


#funcion para agregar servicios 
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
            time_quantity_service = int(request.POST.get('time_quantity_service'))  # Convertir a int
            time_unit_service = request.POST.get('time_unit_service')
            price_service = request.POST.get('price_service')

            # Validaciones
            if not all([category_service_id, name_service, description_service, provider_service_id, 
                        start_date_service, time_quantity_service, time_unit_service, price_service]):
                return JsonResponse({'success': False, 'message': 'Todos los campos son obligatorios.'})

            # Verificar duplicados (sin importar mayúsculas o minúsculas)
            if Services.objects.filter(name_service__iexact=name_service).exists():
                return JsonResponse({'success': False, 'message': 'El nombre del servicio ya existe.'})

            # Obtener objetos relacionados
            category_service = get_object_or_404(Services_Category, id=category_service_id)
            provider_service = get_object_or_404(Provider, id=provider_service_id)

            # Crear un nuevo servicio
            with transaction.atomic():
                service = Services.objects.create(
                    company_id = company_id,
                    category_service=category_service,
                    name_service = name_service,
                    description_service = description_service,
                    provider_service = provider_service,
                    start_date_service = start_date_service,
                    time_quantity_service = time_quantity_service,
                    time_unit_service = time_unit_service,
                    price_service = price_service,    
                )

                # Generar las fechas de pago
                create_payment(service)
            
            return JsonResponse({'success': True, 'message': ' Servicio agregado correctamente!'})
        except ValidationError as e:
            return JsonResponse({'success': False, 'message': str(e)})
        except Exception as e:
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
            if Services.objects.filter(name_service__iexact=name_service).exclude(id=_id).exists():
                return JsonResponse({'success': False, 'message': 'El nombre del servicio ya existe.'})

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



# Función para crear los registros de los pagos
def create_payment(service):
    try:
        if not Services.objects.filter(id=service.id).exists():
            raise ValueError(f"El servicio con ID {service.id} no existe.")

        # Obtener la fecha de pago inicial
        start_date = service.start_date_service
        next_payment_date = calculate_payment_date(start_date, 
            service.time_quantity_service, service.time_unit_service)

        # Crear un nuevo registro de pago con estado pendiente
        Payments_Services.objects.create(
            name_service_payment=service,
            next_date_payment=next_payment_date,
            total_payment=service.price_service,
            status_payment=False  # Estado inicial como "pendiente"
        )

    except ValueError as ve:
        # Manejo de errores específicos
        raise ve  # Se puede volver a lanzar o manejar según sea necesario

    except Exception as e:
        # Manejo de errores generales
        raise Exception(f'Error al crear el pago: {str(e)}')



#funcion para enviar alerta 7 dias antes de la fecha de pago y crear un nuevo registro de pago
def check_and_create_payments():
    try:
        current_date = timezone.now().date()
        pending_payments = Payments_Services.objects.filter(status_payment=False)

        for payment in pending_payments:
            if payment.next_date_payment <= current_date + timedelta(days=7):

                send_alert(payment)

                payment.status_payment = True  # Cambiar a "próximo"
                payment.save()

                # Crear nuevo pago para el próximo periodo
                create_payment(payment.name_service_payment)
                

            elif payment.next_date_payment < current_date:
                payment.status_payment = False  # Cambiar a "no pagado"
                payment.save()

    except Exception as e:
        # Manejo de errores generales
        raise Exception(f'Error al verificar y crear pagos: {str(e)}')

#generar alerta de pago:

def send_alert(payment):
    # Implementa aquí el envío de alerta (correo, notificación, etc.)
    print(f"Alerta: El pago para el servicio {payment.name_service_payment.name_service} es inminente.")





#función para cambiar el estado de los pagos
def update_payment_statuses():

    try:
        now = timezone.now().date()
        payments = Payments_Services.objects.all()

        for payment in payments:
              # Imprimir información relevante antes de cambiar el estado
            print(f'Pago ID: {payment.id}, Estado actual: {payment.status_payment}, '
                  f'Fecha siguiente: {payment.next_date_payment}, Comprobante: {payment.proof_payment}')

            if payment.next_date_payment < now:
                if payment.proof_payment:  # Si hay comprobante subido
                    payment.status_payment = True  # Cambiar a "pagado"
                else:
                    payment.status_payment = False  # Cambiar a "no pagado"
            elif payment.next_date_payment <= now + timedelta(days=7):
                payment.status_payment = True  # Cambiar a "próximo"
            else:
                payment.status_payment = False  # Asegúrate de resetear el estado si no aplica

            payment.save()

    except Exception as e:
        print(f'Error al actualizar el estado de los pagos: {str(e)}')


#funcion para subir el documento
@login_required
@csrf_exempt  
def upload_payment_proof(request, payment_id):
    if request.method == 'POST' and request.FILES.get('proof_payment'):
        try:
            payment = Payments_Services.objects.get(id=payment_id)
            load_file = request.FILES['proof_payment']
           
            company_id = payment.name_service_payment.company.id
            service_name = payment.name_service_payment.name_service.replace(' ', '_')

            folder_path = f"docs/{company_id}/services/proof_payment/{service_name}/"

            #s3Path = f'docs/{company_id}/services/{id}/'
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, folder_path))

            current_date = datetime.now().strftime('%Y%m%d')
            file_name, extension = os.path.splitext(load_file.name)
            new_name = f"comprobante_pago_{service_name}_{current_date}{extension}"

            # Guardar el archivo
            fs.save(new_name, load_file)
            #s3Name = s3Path + new_name

            # Actualizar el campo del comprobante de pago en el modelo
            #upload_to_s3(load_file, bucket_name, s3Name)

            payment.proof_payment = os.path.join(folder_path, new_name)
            payment.status_payment = True
            payment.save()

            return JsonResponse({'success': True, 'message': 'Comprobante subido correctamente.'})
        
        except Payments_Services.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Pago no encontrado.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error inesperado: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)



#funcion de la tabla historial
@login_required
def get_payment_history(request, service_id):
    try:
        payments = Payments_Services.objects.filter(name_service_payment_id=service_id).values(
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
            total_payment=new_price,  # Usar el nuevo precio
            status_payment=False  # Estado inicial como "pendiente"
        )
    except Exception as e:
        raise Exception(f'Error al crear el nuevo pago: {str(e)}')




def dashboard_data(request):
    total_servicios = Services.objects.count()
    total_egresos = Payments_Services.objects.aggregate(Sum('total_payment'))['total_payment__sum'] or 0
    pagos_vencidos = Payments_Services.objects.filter(next_date_payment__lt=timezone.now(), status_payment=False).count()

    data = {
        'total_servicios': total_servicios,
        'total_egresos': total_egresos,
        'pagos_vencidos': pagos_vencidos,
    }
    return JsonResponse(data)
