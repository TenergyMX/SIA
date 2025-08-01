from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.http import HttpResponseRedirect, HttpResponse
from modules.models import *
from users.models import *
from modules.utils import * 
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.db import transaction
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.utils.dateparse import parse_date
from decimal import Decimal
from django.conf import settings
import logging
import json, os
import base64
import time
import requests
from django.template.loader import get_template
from io import BytesIO
from xhtml2pdf import pisa
import logging
from dotenv import load_dotenv
from os.path import join, dirname
from pathlib import Path
from dateutil.parser import parse

dotenv_path = join(dirname(dirname(dirname(__file__))), 'awsCred.env')
#dotenv_path = join(os.path.dirname(os.path.abspath(__file__)), 'awsCred.env')
load_dotenv(dotenv_path)

AWS_BUCKET_NAME=str(os.environ.get('AWS_BUCKET_NAME'))
print(AWS_BUCKET_NAME)
bucket_name=AWS_BUCKET_NAME

# Llamar módulos y submódulos 
#submodulo de categorias 
@login_required
def equipments_and_tools(request):
    context = user_data(request)
    module_id = 6
    subModule_id = 29
    request.session["last_module_id"] = module_id

    access = get_module_user_permissions(context, subModule_id)
    sidebar = get_sidebar(context, [1, module_id])

    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]

#permisos para agregar categorias
    context["area"] = context["area"]["name"].lower()
    context["create"] = access["data"]["access"]["create"]
    context["tipo_user"] = context["role"]["name"].lower


    template = "equipments-and-tools/equipments_and_tools.html" if context["access"]["read"] and check_user_access_to_module(request, module_id, subModule_id) else "error/access_denied.html"
    return render(request, template, context)
    
#submodulo de equipos y herramientas
@login_required
def equipments_tools(request):
    context = user_data(request)
    module_id = 6
    subModule_id = 30
    request.session["last_module_id"] = module_id

    access = get_module_user_permissions(context, subModule_id)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]

    #permisos para agregar categorias
    context["area"] = context["area"]["name"].lower()
    context["create"] = access["data"]["access"]["create"]
    context["tipo_user"] = context["role"]["name"].lower

    
    template = "equipments-and-tools/equipments_tools.html" if context["access"]["read"] and check_user_access_to_module(request, module_id, subModule_id) else "error/access_denied.html"
    return render(request, template, context)
#submodulo de responsivas
@login_required
def responsiva(request):
    context = user_data(request)
    module_id = 6
    subModule_id = 31
    request.session["last_module_id"] = module_id

    access = get_module_user_permissions(context, subModule_id)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]

#permisos para agregar responssivas
    context["area"] = context["area"]["name"].lower()
    context["create"] = access["data"]["access"]["create"]
    context["tipo_user"] = context["role"]["name"].lower()


    tipo_user = context["role"]["name"].lower()
    user_name = context["user"]["username"].lower()
    template = "equipments-and-tools/responsiva.html" if context["access"]["read"] and check_user_access_to_module(request, module_id, subModule_id) else "error/access_denied.html"
    return render(request, template, context)

#-------------------------------------------------------------
# Tabla de datos para las categorias 
def get_equipments_tools_categorys(request):
    response = {"status": "error", "message": "Sin procesar"}
    context = user_data(request)
    isList = request.GET.get("isList", False)
    subModule_id = 29

    try:
        empresa_id = context["company"]["id"]
        if not empresa_id:
            response["message"] = "No se encontró la empresa asociada al usuario"
            return JsonResponse(response, status=400)

        if isList:
            datos = list(Equipement_category.objects.filter(
                        empresa__id=empresa_id
                    ).distinct().values("id", "name", "short_name"))
        else:
            access = get_module_user_permissions(context, subModule_id)#contiene el crud
            access = access["data"]["access"]
            area = context["area"]["name"]
            editar = access["update"]
            eliminar = access["delete"]
            tipo_user = context["role"]["name"]
   

            datos = list(Equipement_category.objects.filter(
                        empresa__id=empresa_id
                    ).distinct().values())
            for item in datos:
                item["btn_action"] = ""
                if access["update"] is True and (area.lower() == "almacen" or tipo_user.lower() in ["administrador", "super usuario"]):
                    item["btn_action"] += (
                        "<button type='button' name='update' class='btn btn-icon btn-sm btn-primary-light edit-btn' onclick='edit_category_category(this)' aria-label='info'>"
                        "<i class='fa-solid fa-pen'></i>"
                        "</button>\n"
                    )
                if access["delete"] is True and (area.lower() == "almacen" or tipo_user.lower() in ["administrador", "super usuario"]):
                    item["btn_action"] += (
                        "<button type='button' name='delete' class='btn btn-icon btn-sm btn-danger-light delete-btn' onclick='delete_category(this)' aria-label='delete'>"
                        "<i class='fa-solid fa-trash'></i>"
                        "</button>"
                    )

        response["data"] = datos
        response["status"] = "success"
        response["message"] = "Datos cargados exitosamente"
        return JsonResponse(response)
    except Exception as e:
        response["message"] = f"Error: {str(e)}"
        return JsonResponse(response, status=500)
    
#funcion para agregar las categorias 
@csrf_protect
@login_required
def add_equipment_category(request):
    context = user_data(request)
    subModule_id = 29
    access = get_module_user_permissions(context, subModule_id)  

    access = access["data"]["access"]
    area = context["area"]["name"]
    create = access["create"]
    tipo_user = context["role"]["name"]

    empresa_id = context["company"]["id"]
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            short_name = request.POST.get('short_name')
            description = request.POST.get('description')
            is_active = request.POST.get('is_active') == '1'

            empresa = Company.objects.get(pk=empresa_id)

            if not name or not short_name:
                raise ValidationError("Nombre y nombre corto son obligatorios.")
            
            # Crear una nueva categoría
            with transaction.atomic():
                Equipement_category.objects.create(
                    empresa=empresa,
                    name=name,
                    short_name=short_name,
                    description=description,
                    is_active=is_active
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
def edit_category(request):
    if request.method == 'POST':
        try:
            _id = request.POST.get('id')
            name = request.POST.get('name')
            short_name = request.POST.get('short_name')
            description = request.POST.get('description')
            is_active = request.POST.get('is_active') == '1'
            
            if not _id or not name or not short_name:
                raise ValidationError("ID, nombre y nombre corto son obligatorios.")
            
            # Actualizar la categoría
            with transaction.atomic():
                category = get_object_or_404(Equipement_category, id=_id)
                category.name = name
                category.short_name = short_name
                category.description = description
                category.is_active = is_active
                category.save()
            
            return JsonResponse({'success': True, 'message': 'Categoría editada correctamente!'})
        except ValidationError as e:
            return JsonResponse({'success': False, 'message': str(e)})
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Error inesperado: ' + str(e)})

    return JsonResponse({'success': False, 'message': 'Método de solicitud no válido'})

#funcion para eliminar las categorias de equipos
@login_required
@csrf_exempt
def delete_category(request):
    if request.method == 'POST':
        form = request.POST
        _id = form.get('id')

        if not _id:
            return JsonResponse({'success': False, 'message': 'No ID provided'})

        try:
            category = Equipement_category.objects.get(id=_id)
        except Equipement_category.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Category not found'})

        category.delete()

        return JsonResponse({'success': True, 'message': 'Categoría eliminada correctamente!'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

#-------------------------------------------------------------------------------
# Tabla de datos para los equipos y herramientas
def get_doc(request):
    file_path = request.GET.get("s3path", "sin informacion")
    print(f'get_doc_path: {file_path}')
    s3DocPatch = generate_presigned_url(AWS_BUCKET_NAME, file_path)
    return HttpResponseRedirect(s3DocPatch)


def get_equipments_tools(request):
    response = {"status": "error", "message": "Sin procesar"}
    context = user_data(request)
    subModule_id = 30

    try:

        access = get_module_user_permissions(context, subModule_id)["data"]["access"]
        area = context["area"]["name"]
        tipo_user = context["role"]["name"]
        company_id = context["company"]["id"]

        editar = access["update"]
        eliminar = access["delete"]
        agregar = access["create"]
        leer = access["read"]

        equipments = list(Equipment_Tools.objects.select_related(
            'equipment_category', 'equipment_area', 'equipment_responsible', 'equipment_location'
        ).filter(company_id=company_id).values(
            'id',
            'equipment_category__id',
            'equipment_category__name',
            'equipment_name',
            'equipment_type',
            'equipment_brand',
            'equipment_description',
            'cost',
            'amount',
            'equipment_area__id',
            'equipment_area__name',
            'equipment_responsible__id',
            'equipment_responsible__username',
            'equipment_location__id',
            'equipment_location__location_name',
            'equipment_technical_sheet'
        ))

        modified_data_list = []
        for data in equipments:
            modified_data = data.copy()

            file_path = data.get('equipment_technical_sheet')
            if file_path:
                technical_sheet = generate_presigned_url(AWS_BUCKET_NAME, file_path)
                modified_path = technical_sheet
            else:
                modified_path = None
            modified_data['responsibility_letter'] = modified_path
            modified_data_list.append(modified_data)
       
        for item in equipments:
            item["btn_action"] = ""
            if access["update"] is True and (area.lower() == "almacen" or tipo_user.lower() in ["administrador", "super usuario"]):
                item["btn_action"] += (
                    "<button type='button' class='btn btn-icon btn-sm btn-primary-light edit-btn' "
                    "onclick='edit_button(this)' aria-label='info'>"
                    "<i class='fa-solid fa-pen'></i>"
                    "</button> "
                )
            if access["delete"] is True and (area.lower() == "almacen" or tipo_user.lower() in ["administrador", "super usuario"]):
                item["btn_action"] += (
                    "<button type='button' class='btn btn-icon btn-sm btn-danger-light delete-btn' "
                    "onclick='delete_equipment_tool(this)' aria-label='delete'>"
                    "<i class='fa-solid fa-trash'></i>"
                    "</button> "
                )
            
            # Botón Agregar Responsiva (visible para todos)
            if access["create"] is True:
                item["btn_action"] += (
                    "<button type='button' class='btn btn-icon btn-sm btn-info-light add-responsiva-btn' "
                    "onclick='modal_responsiva(this)' aria-label='responsiva'>"
                    "<i class='fa-solid fa-file-circle-plus'></i>"
                    "</button>"
                )

            if access["read"] is True and (area.lower() == "almacen" or tipo_user.lower() in ["administrador", "super usuario"]):
                item["btn_action"] += (
                    "<button type='button' class='btn btn-icon btn-sm btn-info-light history-btn' "
                    "onclick='modal_history(this)' aria-label='history'>"
                    "<i class='fa-solid fa-rectangle-history'></i>"
                    "</button>"
                )

        response["data"] = equipments
        response["status"] = "success"
        response["message"] = "Datos cargados exitosamente"
    except Exception as e:
        response["status"] = "error"
        response["message"] = str(e)

    return JsonResponse(response)

# Vista para obtener las categorías de equipos
@login_required
@csrf_exempt
def get_equipment_categories(request):
    try:
        context = user_data(request)
        company_id = context["company"]["id"]  

        if not company_id:
            return JsonResponse({'success': False, 'message': 'No se encontró la empresa asociada al usuario'}, status=400)

        # Obtener las categorías de equipo asociadas a la empresa y activas
        categories = Equipement_category.objects.filter(
            empresa_id=company_id, is_active=True
        ).values('id', 'name') 
        data = list(categories)

        return JsonResponse({'data': data}, safe=False)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


# Funcion para obtener los nombres de los usuarios que ya han sido cargados para agregar un equipo 
@login_required
@csrf_exempt
def get_responsible_users(request):
    try:
        context = user_data(request)
        company_id = context["company"]["id"]
        if not company_id:
            return JsonResponse({'success': False, 'message': 'No se encontró la empresa asociada al usuario'}, status=400)
        
        users = User.objects.filter(
            id__in=User_Access.objects.filter(company_id=company_id).values('user_id')
        ).distinct().values('id', 'username')  
        data = list(users)
        return JsonResponse({'data': data}, safe=False)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

# Funcion para obtener los nombres de las areas
@login_required
@csrf_exempt
def get_equipment_areas(request):
    try:
        context = user_data(request)
        company_id = context["company"]["id"]
        if not company_id:
            return JsonResponse({'success': False, 'message': 'No se encontró la empresa asociada al usuario'}, status=400)
        
        areas = Area.objects.filter(company_id=company_id).distinct().values('id', 'name')  
        data = list(areas)
        return JsonResponse({'data': data}, safe=False)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

# Funcion para obtener los nombres de las ubicaciones
@login_required
@csrf_exempt
def get_locations(request):
    try:
        context = user_data(request)
        company_id = context["company"]["id"]

        if not company_id:
            return JsonResponse({'success': False, 'message': 'No se encontró la empresa asociada al usuario'}, status=400)

        ubicaciones = Equipmets_Tools_locations.objects.filter(
            location_company_id=company_id
        ).values('id', 'location_name')  
        data = list(ubicaciones)
        return JsonResponse({'data': data}, safe=False)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

# Funcion para obtener los nombres de las empresas
@login_required
@csrf_exempt
def get_company(request):
    try:
        empresas = Company.objects.values('id', 'name')  
        data = list(empresas)
        return JsonResponse({'data': data}, safe=False)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

# Función para agregar una nueva ubicación
@login_required
@csrf_protect
def add_location(request):
    if request.method == 'POST':
        try:
            location_name = request.POST.get('location_name')
            location_company_id = request.POST.get('location_company')

            print(f"Nombre de ubicación: {location_name}, ID de empresa: {location_company_id}")

            if not location_name or not location_company_id:
                return JsonResponse({'success': False, 'message': 'Los campos son requeridos.'}, status=400)

            # Verificar que no exista una ubicación con el mismo nombre
            if Equipmets_Tools_locations.objects.filter(location_name__iexact=location_name).exists():
                print('Ya existe una ubicación con ese nombre para esta empresa.') 
                return JsonResponse({'success': False, 'message': 'Ya existe una ubicación con ese nombre para esta empresa.'}, status=400)

            company = get_object_or_404(Company, id=location_company_id)

            # Crear la nueva ubicación
            new_location = Equipmets_Tools_locations.objects.create(
                location_name=location_name,
                location_company=company,
            )

            # Retornar la nueva ubicación para actualizar el select
            return JsonResponse({'success': True, 'message': 'Ubicación agregada exitosamente.', 'new_location': {
                'id': new_location.id,
                'name': new_location.location_name
            }})

        except Exception as e:
            print(f"Error al agregar ubicación: {str(e)}")
            return JsonResponse({'success': False, 'message': 'Error interno del servidor.'}, status=500)

    return JsonResponse({'success': False, 'message': 'Método de solicitud no válido.'}, status=405)

# Función para agregar un nuevo equipo o herramienta
@login_required
@csrf_exempt
def add_equipment_tools(request):
    context = user_data(request)
    response = {"status": "error", "message": "sin procesar" }
    dt = request.POST
    company_id = context["company"]["id"]
    subModule_id = 30
    access = get_module_user_permissions(context, subModule_id)  
    

    access = access["data"]["access"]
    area = context["area"]["name"]
    create = access["create"]
    tipo_user = context["role"]["name"]


    if request.method == 'POST':
        equipment_name = request.POST.get('equipment_name')
        
        # Check if equipment_name already exists
        if Equipment_Tools.objects.filter(equipment_name__iexact=equipment_name, company_id=company_id).exists():
            return JsonResponse({'success': False, 'message': 'Este nombre ya se encuentra regristado para esta empresa, ingresa otro diferente.'})
        
        try:
            with transaction.atomic():
                obj = Equipment_Tools(
                    # Obtener datos del POST
                    company_id = company_id,
                    equipment_category_id = request.POST.get('equipment_category'),
                    equipment_name = request.POST.get('equipment_name'),
                    equipment_type = request.POST.get('equipment_type'),
                    equipment_brand = request.POST.get('equipment_brand'),
                    equipment_description = request.POST.get('equipment_description'),
                    cost = request.POST.get('cost'),
                    amount = request.POST.get('amount'),
                    equipment_area_id = request.POST.get('equipment_area'),
                    equipment_responsible_id = request.POST.get('responsible_equipment'),
                    equipment_location_id = request.POST.get('equipment_location'),
                    
                )
                if not all([obj.company_id, obj.equipment_category, obj.equipment_name, obj.equipment_type, 
                        obj.equipment_brand, obj.equipment_description, obj.cost, obj.amount, 
                        obj.equipment_area, obj.equipment_responsible, obj.equipment_location]):
                    return JsonResponse({'success': False, 'message': 'Faltan campos obligatorios.'}, status=400)
                obj.save()
                id = obj.id

                if 'equipment_technical_sheet' in request.FILES and request.FILES['equipment_technical_sheet']:
                    equipment_technical_sheet = request.FILES.get('equipment_technical_sheet')

                    folder_path = f"docs/{company_id}/Equipments_tools/technical_sheet/{id}/"

                    file_name, extension = os.path.splitext(equipment_technical_sheet.name)

                    new_name = f'equipment_technical_sheet_{obj.equipment_name}{extension}'
                    s3Name = folder_path + new_name

                    upload_to_s3(equipment_technical_sheet, bucket_name, s3Name)
                    obj.equipment_technical_sheet = s3Name
                    obj.save()

            response["status"] = "success"
            response["message"] = "Guardado"
        except ValidationError as e:
            response["status"] = "error"
            response["message"] = e.message_dict
        except Exception as e:
            response["status"] = "error"
            response["message"] = str(e)
        return JsonResponse(response) 
    
#el nombre y siempre lo marca como el nombre ya existe, y solo quiero modificar la cantidad
# Función para editar los registros de los equipos o herramientas
@login_required
@csrf_exempt
def edit_equipments_tools(request):
    context = user_data(request)
    company_id = context["company"]["id"]
    if request.method == 'POST':
        _id = request.POST.get('id')
        equipment_category_id = request.POST.get('equipment_category')
        equipment_name = request.POST.get('equipment_name').strip()
        equipment_type = request.POST.get('equipment_type')
        equipment_brand = request.POST.get('equipment_brand')
        equipment_description = request.POST.get('equipment_description')
        cost = request.POST.get('cost')
        amount = request.POST.get('amount')
        equipment_area = request.POST.get('equipment_area')
        equipment_responsible = request.POST.get('responsible_equipment')
        equipment_location = request.POST.get('equipment_location')
        equipment_technical_sheet = request.FILES.get('equipment_technical_sheet')

        # Validar que el nombre del equipo no esté en uso por otro equipo dentro de la misma empresa, 
        if Equipment_Tools.objects.filter(equipment_name__iexact=equipment_name, company_id=company_id).exclude(id=_id).exists():
            return JsonResponse({'success': False, 'message': 'Este nombre ya se encuentra registrado para esta empresa, ingresa otro diferente.'})

        try:
            equipment_tool = Equipment_Tools.objects.get(id=_id)
            equipment_tool.equipment_category_id = equipment_category_id
            equipment_tool.equipment_name = equipment_name
            equipment_tool.equipment_type = equipment_type
            equipment_tool.equipment_brand = equipment_brand
            equipment_tool.equipment_description = equipment_description
            equipment_tool.cost = cost
            equipment_tool.amount = amount
            equipment_tool.equipment_area_id = equipment_area
            equipment_tool.equipment_responsible_id = equipment_responsible
            equipment_tool.equipment_location_id = equipment_location

            # Actualizar ficha técnica solo si se proporciona un archivo nuevo
            if equipment_technical_sheet:
                folder_path = f"docs/{equipment_tool.company_id}/Equipments_tools/technical_sheet/{id}/"
                file_name, extension = os.path.splitext(equipment_technical_sheet.name)
                new_name = f'equipment_technical_sheet_{equipment_tool.equipment_name}{extension}'
                s3Name = folder_path + new_name
                upload_to_s3(equipment_technical_sheet, AWS_BUCKET_NAME, s3Name)
                equipment_tool.equipment_technical_sheet = s3Name

            equipment_tool.save()

            return JsonResponse({'success': True, 'message': 'Equipo editado correctamente!'})

        except Equipment_Tools.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Equipo no encontrado'}, status=404)

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error interno del servidor: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'message': 'Método de solicitud inválido'})

#funcion para eliminar los equipos
@login_required
@csrf_exempt
def delete_equipment_tool(request):
    if request.method == 'POST':
        form = request.POST
        _id = form.get('id')

        if not _id:
            return JsonResponse({'success': False, 'message': 'No ID provided'})

        try:
            equipment_tool = Equipment_Tools.objects.get(id=_id)
        except Equipment_Tools.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'equipments and tools not found'})

        equipment_tool.delete()

        return JsonResponse({'success': True, 'message': 'Equipo eliminado correctamente!'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

#funcion para agregar una responsiva
@login_required
@csrf_exempt  
def add_responsiva(request):
    context = user_data(request)
    module_id = 6
    subModule_id = 31
    request.session["last_module_id"] = module_id

    access = get_module_user_permissions(context, subModule_id)  
    access = access["data"]["access"]
    area = context["area"]["name"].lower()
    create = access["create"]

    tipo_user = context["role"]["name"].lower()
    company_id = context["company"]["id"]

    user_name = context["user"]["username"].lower()

    if request.method == 'POST':
        # Extraer datos del formulario
        equipment_name = request.POST.get('equipment_name')
        equipment_responsible_id = request.POST.get('equipment_responsible')
        amount = float(request.POST.get('amount', 0))
        fecha_entrega = request.POST.get('fecha_entrega')
        times_requested_responsiva = request.POST.get('times_requested_responsiva')
        comments = request.POST.get('comments', '')
    
        if not fecha_entrega or not isinstance(fecha_entrega, str):
            return JsonResponse({'success': False, 'message': 'Fecha de entrega no proporcionada.'})
        try:
            fecha_entrega_date = datetime.strptime(fecha_entrega, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Fecha de entrega inválida.'})

        # Obtener la fecha de inicio
        fecha_inicio_str = request.POST.get('fecha_inicio', '')
        fecha_inicio = parse_date(fecha_inicio_str) if fecha_inicio_str else datetime.now().date()

        # Verificar que la fecha de entrega sea mayor a la fecha de inicio
        if fecha_entrega_date <= fecha_inicio:
            return JsonResponse({'success': False, 'message': 'La fecha de entrega debe ser mayor a la fecha de inicio.'})

        try:
            with transaction.atomic():
                # Obtener el equipo solicitado
                requested_amount = Equipment_Tools.objects.filter(equipment_name=equipment_name, company_id=company_id).first()
                
                # Verificar la cantidad disponible
                available_amount = float(requested_amount.amount)
                if amount > available_amount:
                    return JsonResponse({'success': False, 'message': 'No contamos con la cantidad seleccionada.'})

                # Determinar el estado del equipo basado en la fecha de entrega
                status_equipment = 'Atrasado' if fecha_entrega_date < fecha_inicio else 'Aceptado'

                # Verificar si el usuario puede seleccionar un responsable
                if tipo_user in ['administrador', 'super usuario'] or area == 'almacen':
                    responsible = get_object_or_404(User, id=equipment_responsible_id)
                else:
                    responsible = get_object_or_404(User, username=context['user']['username'])


                signature_file = request.FILES.get('signature')

                # Verifica que signature_file no sea None
                if not signature_file or signature_file.size == 0:
                    return JsonResponse({'success': False, 'message': 'Es necesario que el responsable firme, el campo está vacío.'})

                # Verificar que la firma es una imagen válida
                if signature_file.content_type not in ['image/png', 'image/jpeg']:
                    return JsonResponse({'success': False, 'message': 'El archivo de firma debe ser una imagen PNG o JPEG válida.'})

                # Leer los primeros bytes del archivo
                file_data = signature_file.read()
                if len(file_data) == 0:
                    return JsonResponse({'success': False, 'message': 'La firma no puede estar vacía.'})

                # Volver a mover el puntero al principio del archivo para que se pueda guardar después
                signature_file.seek(0)


                # Verificar si la imagen es completamente blanca
                if signature_file.content_type == 'image/png':
                    if file_data[0:8] == b'\x89PNG\r\n':
                        # Comprobar que no sea completamente blanca
                        if file_data.count(b'\xFF') == len(file_data) - 12:  # Ignora los primeros 12 bytes de la cabecera
                            return JsonResponse({'success': False, 'message': 'La firma no puede ser completamente blanca.'})
 
 
                # Usar un timestamp para el nombre del archivo de la firma
                timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
                folder_path = f"docs/{company_id}/Equipments_tools/signatureResponsivas/{timestamp}/"  # Ruta de la firma

                # Generar un nombre único para la firma
                new_name = f"signature_{timestamp}.png"
                s3Name = folder_path + new_name
                upload_to_s3(signature_file, AWS_BUCKET_NAME, s3Name)
                #fs = FileSystemStorage(location=settings.MEDIA_ROOT)
                #fs.save(os.path.join(folder_path, new_name), signature_file)
                

                # Crear la nueva responsiva del equipo
                Equipment_Tools_Responsiva.objects.create(
                    company_id = company_id,
                    equipment_name=requested_amount,
                    responsible_equipment=responsible,
                    amount=amount,
                    status_equipment='Solicitado', 
                    fecha_inicio=fecha_inicio,
                    fecha_entrega=fecha_entrega_date,
                    times_requested_responsiva=times_requested_responsiva,
                    signature_responsible=s3Name, 
                    comments=comments,
                )


                # Actualizar la cantidad del equipo
                requested_amount.amount = available_amount - amount
                requested_amount.save()


                # Retornar la respuesta JSON
                return JsonResponse({
                    'success': True,
                    'message': 'Responsiva agregada correctamente',
                    #'pdf_url': pdf_url  
                })

        except Equipment_Tools.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Equipo no encontrado'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Método de solicitud no válido'})



def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)

    result = BytesIO()
    result.name = "responsiva.pdf"
    pdf = pisa.CreatePDF(html, dest=result)

    if pdf.err:
        return None  # Devuelve None si hay un error al crear el PDF

    result.seek(0)
    return result

#-------------------------------------------------------------------------------
# Funcion para obtener los nombres de los usuarios para la responsiva
@login_required
@csrf_exempt
def get_responsible_user(request):

    try:
        context = user_data(request)
        company_id = context["company"]["id"]
        if not company_id:
            return JsonResponse({'success': False, 'message': 'No se encontró la empresa asociada al usuario'}, status=400)
        
        area = context["area"]["name"].lower()
        tipo_user = context["role"]["name"].lower()

        if tipo_user in ['administrador', 'super usuario'] or area == 'almacen':
            users = User.objects.filter(
                id__in=User_Access.objects.filter(company_id=company_id).values('user_id')
            ).distinct().values('id', 'username')

        else:
            users = User.objects.filter(id=request.user.id).values('id', 'username')

        data = list(users)
        return JsonResponse({'data': data}, safe=False)

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

# Tabla de datos para responsivas
def get_responsiva(request):
    response = {"status": "error", "message": "Sin procesar"}
    context = user_data(request)
    print("esta informacion contiene el context de tabla de resposnisvs:", context)
    isList = request.GET.get("isList", False)
    subModule_id = 31
    access = get_module_user_permissions(context, subModule_id)
    access = access["data"]["access"]
    area = context["area"]["name"].lower()
    tipo_user = context["role"]["name"].lower()
    company_id = context["company"]["id"] 

    company_name = context["company"]["name"].lower()
    editar = access["update"]
    create = access["create"]
    user_name = context["user"]["username"].lower()
    print("este es el usuario que ha iniciado sesion:", user_name)

    try:
        if tipo_user in ["administrador", "almacen", "super usuario"]:

            responsiva = list(Equipment_Tools_Responsiva.objects.select_related(
                'equipment_name', 'responsible_equipment'
            ).filter(
                company_id=company_id,
            ).values(
                'id', 
                'equipment_name__equipment_name',  # nombre del equipo
                'responsible_equipment__username',  # nombre del usuario
                'amount',
                'status_equipment',
                'fecha_inicio',
                'fecha_entrega',
                'times_requested_responsiva',
                'date_receipt',
                'comments',
                'status_modified',
            ))
        else:
            print(f"Consultando registros para el usuario: {user_name}")

            responsiva = list(Equipment_Tools_Responsiva.objects.select_related(
                'equipment_name', 'responsible_equipment'
            ).filter(responsible_equipment__username__iexact=user_name).values(
                'id',
                'equipment_name__equipment_name',
                'responsible_equipment__username',
                'amount',
                'status_equipment',
                'fecha_inicio',
                'fecha_entrega',
                'times_requested_responsiva',
                'date_receipt',
                'comments',
                'status_modified',
            ))
            
            print(f"Registros encontrados: {responsiva}")

        for item in responsiva:
            item["btn_action"] = ""
            item["boton_action"] = ""


            if access["update"] and (area.lower() == "almacen" or tipo_user.lower() in ["administrador", "super usuario"]):
                if item['status_equipment'] == 'Solicitado':
                    item["btn_action"] += (
                        "<button type='button' class='btn btn-icon btn-sm btn-primary-light approve-btn' "
                        "onclick='approve_button(this)' aria-label='info'>"
                        "<i class='fa-solid fa-circle-check'></i>"
                        "</button> "
                    )
                    item["btn_action"] += (
                        "<button type='button' class='btn btn-icon btn-sm btn-danger-light cancel-btn' "
                        "onclick='cancel_button(this)' aria-label='info'>"
                        "<i class='fa-sharp fa-solid fa-circle-xmark'></i>"
                        "</button> "
                    )
                elif item['status_equipment'] == 'Aceptado' or item['status_equipment'] == 'Atrasado':
                    item["btn_action"] += (
                        "<button type='button' class='btn btn-icon btn-sm btn-info-light chek-btn' "
                        "onclick='chek_responsiva_button(this)' aria-label='status'>"
                        "<i class='fa-solid fa-clipboard-list-check'></i>"
                        "</button> "
                    )

            # Incluir el botón de editar en la columna de date_receipt
            if access["update"] and (area.lower() == "almacen" or tipo_user.lower() in ["administrador", "super usuario"]):
                if item['status_equipment'] in ['Aceptado', 'Atrasado']:
                    edit_button = (
                        "<button type='button' class='btn btn-icon btn-sm btn-primary-light edit-btn' "
                        "onclick='edit_date(this)' aria-label='info'>"
                        "<i class='fa-solid fa-pen'></i>"
                        "</button> "
                    )
                    item['date_receipt'] = (str(item['date_receipt']) if item['date_receipt'] else '') + edit_button
                else:
                    # Mostrar solo la fecha como texto si el estado no es Aceptado o Atrasado
                    item['date_receipt'] = str(item['date_receipt']) if item['date_receipt'] else ''
            else:
                # Mostrar solo la fecha como texto si no tiene permisos
                item['date_receipt'] = str(item['date_receipt']) if item['date_receipt'] else ''



            # Mapeo de estado a clase
            if item['status_equipment'] == 'Regresado':
                item['status_equipment'] = '<span class="badge bg-outline-success">Regresado</span>'
            elif item['status_equipment'] == 'Atrasado':
                item['status_equipment'] = '<span class="badge bg-outline-warning">Atrasado</span>'
            elif item['status_equipment'] == 'Solicitado':
                item['status_equipment'] = '<span class="badge bg-outline-info">Solicitado</span>'
            elif item['status_equipment'] == 'Aceptado':
                item['status_equipment'] = '<span class="badge bg-outline-success">Aceptado</span>'
            elif item['status_equipment'] == 'Cancelado':
                item['status_equipment'] = '<span class="badge bg-outline-danger">Cancelado</span>'
            elif item['status_equipment'] == 'No devuelto':
                item['status_equipment'] = '<span class="badge bg-outline-danger">No devuelto</span>'
            elif item['status_equipment'] in ['Incompleto', 'Dañado']:
                item['status_equipment'] = '<span class="badge bg-outline-warning">{}</span>'.format(item['status_equipment'])
            else:
                item['status_equipment'] = ''  

        response["data"] = responsiva
        response["status"] = "success"
        response["message"] = "Datos cargados exitosamente"
    except Exception as e:
        response["status"] = "error"
        response["message"] = str(e)

    return JsonResponse(response)

# Mapeo de valores a nombres
STATUS_CHOICES = {
    '0': 'Regresado',
    '1': 'Incompleto',
    '2': 'Dañado',
    '3': 'No devuelto',
    '4': 'Aceptado',
    '5': 'Solicitado',
    '6': 'Cancelado',
    '7': 'Atrasado'
}

logger = logging.getLogger(__name__)


# Función para editar el estado de la responsiva
@login_required
@csrf_exempt
def status_responsiva(request):
    context = user_data(request)
    company_id = context["company"]["id"]
    if request.method == 'POST':
        try:
            company_id = company_id
            equipment_id = request.POST.get('id')
            status_value = request.POST.get('status_equipment')
            comments = request.POST.get('comments')
            return_amount = request.POST.get('return_amount')
            signature_almacen_file = request.FILES.get('signature_almacen')

            # Obtener la responsiva
            responsiva = Equipment_Tools_Responsiva.objects.get(id=equipment_id)

            # Validaciones de la firma del almacén
            if not signature_almacen_file or signature_almacen_file.size == 0:
                return JsonResponse({'success': False, 'message': 'Es necesario que el responsable firme, el campo está vacío.'})
            if signature_almacen_file.content_type not in ['image/png', 'image/jpeg']:
                return JsonResponse({'success': False, 'message': 'El archivo de firma debe ser una imagen PNG o JPEG válida.'})

            file_data = signature_almacen_file.read()
            if len(file_data) == 0:
                return JsonResponse({'success': False, 'message': 'La firma no puede estar vacía.'})

            # Verificar si la imagen es completamente blanca (opcional)
            signature_almacen_file.seek(0)
            if signature_almacen_file.content_type == 'image/png':
                if file_data.count(b'\xFF') == len(file_data) - 12:
                    return JsonResponse({'success': False, 'message': 'La firma no puede ser completamente blanca.'})

            # Usar un timestamp para el nombre del archivo de la firma
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            folder_path = f"docs/{company_id}/Equipments_tools/signatureAlmacen/{timestamp}/"

            new_name = f"signature_almacen_{timestamp}.png"
            s3Name = folder_path + new_name
            upload_to_s3(signature_almacen_file, AWS_BUCKET_NAME, s3Name)

            try:
                return_amount = int(return_amount) if return_amount else 0
            except ValueError:
                return JsonResponse({'success': False, 'message': 'Cantidad devuelta inválida.'}, status=400)

            status_name = STATUS_CHOICES.get(status_value, 'Desconocido')

            with transaction.atomic():
                # Cambiar el estado siempre que no sea el mismo
                if responsiva.status_equipment != status_name:
                    responsiva.status_equipment = status_name
                    responsiva.comments = comments
                    responsiva.date_receipt = timezone.now().date()
                    responsiva.signature_almacen = s3Name

                    # Solo marcar como modificado si el estado cambia
                    responsiva.status_modified = True
                    responsiva.save()

                    # Actualiza el equipo relacionado
                    equipment_tool = responsiva.equipment_name
                    if status_name == 'Regresado':
                        equipment_tool.amount += responsiva.amount
                    elif status_name == 'Incompleto':
                        if return_amount >= responsiva.amount:
                            return JsonResponse({'success': False, 'message': 'No es posible que esté incompleto, te prestamos menos.'}, status=400)
                        equipment_tool.amount += return_amount
                    equipment_tool.save()

                    return JsonResponse({'success': True, 'message': 'La responsiva ha sido actualizada correctamente.'}, status=200)
                else:
                    return JsonResponse({'success': False, 'message': 'No se realizaron cambios en el estado del equipo.'}, status=400)

        except Equipment_Tools_Responsiva.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'La responsiva no existe.'}, status=404)

        except Exception as e:
            logger.error('Error en status_responsiva: %s', str(e))
            return JsonResponse({'success': False, 'message': 'Error interno del servidor.'}, status=500)

    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)


# Función para aprobar la responsiva del equipo
@login_required
@csrf_exempt
def approve_responsiva(request):
    if request.method == 'POST':
        try:
            equipment_id = request.POST.get('id')
            responsiva = Equipment_Tools_Responsiva.objects.get(id=equipment_id)  # Obtener la responsiva

            # Validar que no se puede aprobar si ya fue cancelada
            if responsiva.status_equipment == 'Cancelado':
                return JsonResponse({'success': False, 'message': 'La responsiva fue cancelada, no se puede aprobar.'}, status=400)

            # Validar que solo se puede aprobar una vez la responsiva
            if responsiva.status_modified:
                return JsonResponse({'success': False, 'message': 'La responsiva ya fue aprobada, no puede ser aprobada de nuevo.'}, status=400)

            # Validar que no se puede aprobar si ya fue aceptada
            if responsiva.status_equipment == 'Aceptado':
                return JsonResponse({'success': False, 'message': 'La responsiva ya ha sido aceptada, no puede ser aprobada de nuevo.'}, status=400)

            with transaction.atomic():
                # Cambiar el estado de la responsiva
                responsiva.status_equipment = 'Aceptado'
                responsiva.status_modified = True  # Marcar como modificada
                responsiva.save()

                # Actualiza el estado en Equipment_Tools también
                equipment_tool = responsiva.equipment_name
                equipment_tool.status = 'Aceptado'  # Cambia el estado del equipo
                equipment_tool.save()

                return JsonResponse({'success': True, 'message': 'La responsiva fue aceptada correctamente.'})
        
        except Equipment_Tools_Responsiva.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'La responsiva no existe.'}, status=404)
        
        except Exception as e:
            logger.error('Error en approve_responsiva: %s', str(e))
            return JsonResponse({'success': False, 'message': 'Error interno del servidor.'}, status=500)

    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)


# Función para cancelar la responsiva del usuario
@login_required
@csrf_exempt
def cancel_responsiva(request):
    if request.method == 'POST':
        try:
            equipment_id = request.POST.get('id')
            responsiva = Equipment_Tools_Responsiva.objects.get(id=equipment_id)

            # Verificar si la responsiva ya fue cancelada
            if responsiva.status_equipment == 'Cancelado':  
                return JsonResponse({'success': False, 'message': 'La responsiva ya ha sido cancelada, no puede ser cancelada de nuevo.'}, status=400)

            # Verificar si la responsiva ya fue aceptada
            if responsiva.status_equipment == 'Aceptado':
                return JsonResponse({'success': False, 'message': 'La responsiva ya ha sido aceptada, no puede ser cancelada.'}, status=400)

            with transaction.atomic():
                equipment_tool = responsiva.equipment_name
                equipment_tool.amount += responsiva.amount  # Regresar la cantidad al equipo
                equipment_tool.save()

                # Marcar la responsiva como cancelada
                responsiva.status_equipment = 'Cancelado'
                responsiva.save()

            return JsonResponse({'success': True, 'message': 'La responsiva ha sido cancelada y la cantidad ha sido regresada.'}, status=200)

        except Equipment_Tools_Responsiva.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'La responsiva no existe.'}, status=404)

        except Exception as e:
            logger.error('Error en cancel_responsiva: %s', str(e))
            return JsonResponse({'success': False, 'message': 'Error interno del servidor.'}, status=500)

    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)

#función para obtener la fecha actual del servidor 
def get_server_date(request):
    # Obtén la fecha actual del servidor en formato YYYY-MM-DD
    server_date = timezone.now().astimezone().date().isoformat()  # Usa la zona horaria local
    return JsonResponse({'server_date':server_date})

#funcion para actualizar la fecha de entrega y actualizar el tiempo requerido
def edit_date_responsiva(request):
    if request.method == 'POST':
        try:
            fecha_entrega = request.POST.get('fecha_edit')
            id_responsiva = request.POST.get('id')
            
            # Obtener la fecha actual
            fecha_actual = timezone.now().date()

            # Validar la fecha de entrega
            fecha_entrega_date = parse_date(fecha_entrega)
            if not fecha_entrega_date or fecha_entrega_date <= fecha_actual:
                return JsonResponse({'success': False, 'message': 'La fecha de entrega debe ser mayor a la fecha actual.'})
            
            try:
                responsiva = Equipment_Tools_Responsiva.objects.get(id=id_responsiva)
                responsiva.fecha_entrega = fecha_entrega_date
                # Calcular el tiempo requerido
                tiempo_requerido = (fecha_entrega_date - responsiva.fecha_inicio).days
                responsiva.times_requested_responsiva = tiempo_requerido
                responsiva.status_equipment = "Aceptado"
                responsiva.save()

                return JsonResponse({'success': True, 'message': 'Fecha de entrega actualizada exitosamente.'})
            except Equipment_Tools_Responsiva.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Responsiva no encontrada.'})

        except ValueError:
            return JsonResponse({'success': False, 'message': 'Fecha de entrega inválida.'})
    return JsonResponse({'success': False, 'message': 'Método no permitido.'})


#funcion para obtener el historial de los equipos y herramientas
@csrf_exempt
def get_equipment_history(request):
    if request.method == 'POST':
        equipment_id = request.POST.get('equipment_id')
        
        try:
            responsivas = Equipment_Tools_Responsiva.objects.filter(equipment_name__id=equipment_id).values(
                'id',
                'equipment_name__equipment_name', 
                'responsible_equipment__username',
                'date_receipt',
                'status_equipment'
            )
            return JsonResponse({'success': True, 'data': list(responsivas)}, safe=False)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)


@login_required
@csrf_exempt
def validar_fecha(request):
    if request.method == 'GET':
        try:
            current_date = timezone.now().date()
            responsivas = Equipment_Tools_Responsiva.objects.all()

            for responsiva in responsivas:
                if not responsiva.date_receipt and responsiva.fecha_entrega < current_date:
                    responsiva.status_equipment = 'Atrasado'
                    responsiva.save()

            return JsonResponse({'success': True, 'message': 'Estados actualizados correctamente.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)


logger = logging.getLogger(__name__)

def image_to_base64(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    except Exception as e:
        logger.error("Error al leer la imagen: %s", str(e))
        return None

#funcion para generar el pdf
@login_required
def generate_pdf(request, responsiva_id):
    logger.info("Se ha llamado a la función generate_pdf con ID: %s", responsiva_id)
    
    try:
        responsiva_instance = get_object_or_404(Equipment_Tools_Responsiva, id=responsiva_id)
        logger.info("Responsiva encontrada, generando PDF...")

        # Convertir imágenes a Base64
        header_image_base64 = None
        footer_image_base64 = None

        header_image_path = os.path.join(settings.MEDIA_ROOT, 'modules/templates/equipments-and-tools/responsiva/img/encabezado.png')
        footer_image_path = os.path.join(settings.MEDIA_ROOT, 'modules/templates/equipments-and-tools/responsiva/img/pie.png')


        logger.info("Ruta de la imagen de encabezado: %s", header_image_path)
        logger.info("Ruta de la imagen de pie de página: %s", footer_image_path)

        if os.path.exists(header_image_path):
            header_image_base64 = f"data:image/png;base64,{image_to_base64(header_image_path)}"
            logger.info("Imagen de encabezado cargada exitosamente.")
        else:
            logger.warning("No se encontró la imagen de encabezado en: %s", header_image_path)

        if os.path.exists(footer_image_path):
            footer_image_base64 = f"data:image/png;base64,{image_to_base64(footer_image_path)}"
            logger.info("Imagen de pie de página cargada exitosamente.")
        else:
            logger.warning("No se encontró la imagen de pie de página en: %s", footer_image_path)

        # Contexto para el PDF
        pdf_context = {
            'responsiva': responsiva_instance,
            'responsible_name': responsiva_instance.responsible_equipment.username,
            'signature_responsible': generate_presigned_url(AWS_BUCKET_NAME, str(responsiva_instance.signature_responsible)) if responsiva_instance.signature_responsible else None,
            'signature_almacen': generate_presigned_url(AWS_BUCKET_NAME, str(responsiva_instance.signature_almacen)) if responsiva_instance.signature_almacen else None,
            'header_image': header_image_base64,
            'footer_image': footer_image_base64,
        }

        # Generar PDF
        pdf_file = render_to_pdf('equipments-and-tools/responsiva/responsiva_equipments.html', pdf_context)

        if pdf_file is None:
            logger.error("Error al generar el PDF.")
            return JsonResponse({'success': False, 'message': 'Error al generar el PDF.'})

        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        pdf_folder_path = f"docs/{responsiva_instance.company_id}/Equipments_tools/pdfs_responsiva/{timestamp}/"

        # Guardar el PDF en AWS S3 Bucket
        pdf_file_name = f"responsiva_{timestamp}.pdf"
        s3Name = pdf_folder_path + pdf_file_name

        try:
            upload_to_s3(pdf_file, AWS_BUCKET_NAME, s3Name)
            url = generate_presigned_url(AWS_BUCKET_NAME, s3Name)
            response = requests.get(url)
    
            # Store the PDF content in memory using BytesIO
            pdfFile = BytesIO(response.content)
    
            # Prepare the response
            pdf_response = HttpResponse(pdfFile.getvalue(), content_type='application/pdf')
    
            # Set headers to open the file in a new browser tab
            pdf_response['Content-Disposition'] = 'inline; filename="responsiva.pdf"'
        
        except Exception as e:
            logger.error("Error al guardar el PDF: %s", str(e))
            return JsonResponse({'success': False, 'message': 'Error al guardar el PDF.'})

        # URL del PDF
        pdf_url = f"{request.scheme}:{s3Name}"
        responsiva_instance.pdf_url = pdf_url  # Actualiza la responsiva si es necesario
        return pdf_response
    
        #return JsonResponse({
        #    'success': True,
        #    'message': 'Responsiva generada correctamente',
        #    'pdf_url': pdf_response
        #})

    except Equipment_Tools_Responsiva.DoesNotExist:
        logger.error("Responsiva no encontrada. ")
        return JsonResponse({'success': False, 'message': 'Responsiva no encontrada.'})
