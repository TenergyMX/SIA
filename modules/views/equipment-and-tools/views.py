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

from modules.templates.pdf.weasy import WeasyPDF    

from django.db.models import Count, Q

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
                        empresa__id=empresa_id, is_active=True
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

            # validacion
            categoria_existente = Equipement_category.objects.filter(
                empresa=empresa,
                is_active=True
            ).filter(
                Q(name__iexact=name) |
                Q(short_name__iexact=short_name)
            ).first()

            if categoria_existente:
                raise ValidationError(
                    "Ya existe una categoría activa con ese nombre o nombre corto."
                )

            # Crear una nueva categoría
            with transaction.atomic():
                Equipement_category.objects.create(
                    empresa=empresa,
                    name=name,
                    short_name=short_name,
                    description=description,
                    is_active=True
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
    if request.method != 'POST':

        return JsonResponse({
            'success': False,
            'message': 'Método de solicitud inválido.' 
        }, status=405)

    _id = request.POST.get('id')

    if not _id:
        return JsonResponse({
            'success': False, 
            'message': 'No se proporciono el ID de la categoría.'
        }, status=400)
    
    try:
        category = Equipement_category.objects.get(id=_id)

    except Equipement_category.DoesNotExist:
        return JsonResponse({
            'success': False, 
            'message': 'La categoría no existe'
            }, status=404)

    # validar si la categoria tiene equipos o herramienats registradas
    has_equipment = Equipment_Tools.objects.filter(
        equipment_category=category,
        is_active=True
    ).exists()

    if has_equipment:
        return JsonResponse({
            'success': False,
            'message': (
                'No se puede eliminar esta categoría, porque tiene equipos o herramientas registrados.'
            )
        }, status=400)

    # Desactivar la categoria
    category.is_active = False
    category.save(update_fields=['is_active'])

    return JsonResponse({
        'success': True, 
        'message': 'Categoría eliminada correctamente!'
    })


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
        ).filter(company_id=company_id, is_active=True).annotate(available_amount=Count('details', filter=Q( details__company_id=company_id, details__is_active=True, details__is_deactivated=False, details__state='DISPONIBLE'))).values(
            'id',
            'equipment_category__id',
            'equipment_category__name',
            'equipment_name',
            'equipment_type',
            'equipment_brand',
            'equipment_description',
            'cost',
            # 'amount',
            'available_amount',
            'equipment_area__id',
            'equipment_area__name',
            'equipment_responsible__id',
            'equipment_responsible__username',
            'equipment_location__id',
            'equipment_location__location_name',
            'equipment_technical_sheet',
            'document_factura_equipment',
            'image',
            'comments',
            'has_serial_number'
            )
        )

        for item in equipments:
            # cantidad
            item["amount"] = item["available_amount"]

            item["btn_equipment_image"] = ""

            if item["image"]:

                tempImage = generate_presigned_url(
                    AWS_BUCKET_NAME,
                    str(item["image"])
                )

                item["btn_equipment_image"] = f"""
                    <a href="{tempImage}"
                       target="_blank"
                       title="Ver fotografía">
                        <img
                            src="{tempImage}"
                            alt="Fotografía de {item['equipment_name']}"
                            class="rounded border"
                            style="
                                width: 70px;
                                height: 70px;
                                object-fit: cover;
                                cursor: pointer;
                            "
                        >
                    </a>
                """

            else:

                item["btn_equipment_image"] = """
                    <span class="text-muted">
                        <i class="fa-solid fa-image-slash"></i>
                        Sin imagen
                    </span>
                """



            # Botón Ver Ficha Técnica
            item["btn_equipment_technical_sheet"] = ""

            if item["equipment_technical_sheet"]:

                tempDoc = generate_presigned_url(
                    AWS_BUCKET_NAME,
                    str(item["equipment_technical_sheet"])
                )

                item["btn_equipment_technical_sheet"] = f"""
                    <a href="{tempDoc}"
                    target="_blank"
                    class="btn btn-sm btn-primary">
                        <i class="fa-solid fa-file-lines"></i>
                        Ver
                    </a>
                """

            # Botón Ver Factura
            item["btn_document_factura_equipment"] = ""

            if item["document_factura_equipment"]:

                tempDoc = generate_presigned_url(
                    AWS_BUCKET_NAME,
                    str(item["document_factura_equipment"])
                )

                item["btn_document_factura_equipment"] = f"""
                    <a href="{tempDoc}"
                    target="_blank"
                    class="btn btn-sm btn-info">
                        <i class="fa-solid fa-eye"></i>
                        Ver
                    </a>
                """

            # Botón Desglose de equipo
            item["btn_equipment_breakdown"] = ""

            if access["read"] is True and (
                area.lower() == "almacen"
                or tipo_user.lower() in ["administrador", "super usuario"]
            ):
                item["btn_equipment_breakdown"] = (
                    f"<button type='button' "
                    f"name='identifiers' "
                    f"class='btn btn-icon btn-sm btn-success-light' "
                    f"data-equipments-tools='view-identifiers' "
                    f"data-id='{item['id']}' "
                    f"aria-label='Desglose de equipo' "
                    f"title='Desglose de equipo'>"
                    f"<i class='fa-solid fa-list'></i>"
                    f"</button>"
                )

            # Botones de acciones
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
        if Equipment_Tools.objects.filter(equipment_name__iexact=equipment_name, company_id=company_id, is_active=True).exists():
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
                    comments = request.POST.get('comments'),
                    has_serial_number = request.POST.get("has_serial_number") == "1"
                )

                if not all([obj.company_id, obj.equipment_category, obj.equipment_name, obj.equipment_type, 
                        obj.equipment_brand, obj.equipment_description, obj.cost, obj.amount, 
                        obj.equipment_area, obj.equipment_responsible, obj.equipment_location]):
                    return JsonResponse({'success': False, 'message': 'Faltan campos obligatorios.'}, status=400)
                obj.save()
                equipment_id = obj.id

                generate_identificador_equipment_tool(
                    equipment_id,
                    company_id,
                    obj.amount
                )

                # IMAGEN DEL EQUIPO / HERRAMIENTA
                if "image" in request.FILES and request.FILES["image"]:

                    image = request.FILES.get("image")

                    folder_path = (
                        f"docs/{company_id}/"
                        f"Equipments_tools/{equipment_id}/"
                        f"image/{equipment_id}/"
                    )

                    file_name, extension = os.path.splitext(image.name)

                    new_name = (
                        f"equipment_image_{obj.equipment_name}"
                        f"{extension}"
                    )

                    s3Name = folder_path + new_name

                    upload_to_s3(
                        image,
                        bucket_name,
                        s3Name
                    )

                    obj.image = s3Name
                    obj.save(update_fields=["image"])

                if 'equipment_technical_sheet' in request.FILES and request.FILES['equipment_technical_sheet']:
                    equipment_technical_sheet = request.FILES.get('equipment_technical_sheet')

                    folder_path = (
                        f"docs/{company_id}/"
                        f"Equipments_tools/{equipment_id}/"
                        f"technical_sheet/{equipment_id}/"
                    )

                    file_name, extension = os.path.splitext(equipment_technical_sheet.name)

                    new_name = f'equipment_technical_sheet_{obj.equipment_name}{extension}'
                    s3Name = folder_path + new_name

                    upload_to_s3(equipment_technical_sheet, bucket_name, s3Name)
                    obj.equipment_technical_sheet = s3Name
                    obj.save()

                if 'document_factura_equipment' in request.FILES and request.FILES['document_factura_equipment']:
                    document_factura_equipment = request.FILES.get('document_factura_equipment')

                    folder_path = (
                        f"docs/{company_id}/"
                        f"Equipments_tools/{equipment_id}/"
                        f"document_factura_equipment/{equipment_id}/"
                    )

                    file_name, extension = os.path.splitext(document_factura_equipment.name)

                    new_name = f'document_factura_equipment{obj.equipment_name}{extension}'
                    s3Name = folder_path + new_name

                    upload_to_s3(document_factura_equipment, bucket_name, s3Name)
                    obj.document_factura_equipment = s3Name
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


# generar identificador de cada registro
def generate_identificador_equipment_tool(item_id, company_id, cantidad):
    try:
        item = Equipment_Tools.objects.get(id=item_id)
        company = Company.objects.get(id=company_id)
        base_name = item.equipment_name.replace(' ', '').upper()[:3]
        company_code = company.name.replace(' ', '').upper()[:3]
        prefix = f"{company_code}-{base_name}-"

        print(f"Generando identificadores para {cantidad} items de '{item.equipment_name}'")

        # Buscar el último número usado con ese prefijo
        last_detail = (
            Equipments_Tools_Detail.objects
            .filter(company=company, identifier__startswith=prefix)
            .order_by("-identifier")
            .first()
        )

        if last_detail:
            match = re.search(rf"{prefix}(\d+)", last_detail.identifier)
            last_number = int(match.group(1)) if match else 0
        else:
            last_number = 0

        cantidad = int(cantidad)

        detalles_creados = []

        for i in range(1, int(cantidad) + 1):
            number = last_number + i
            identifier = f"{prefix}{str(number).zfill(4)}"

            detalle = Equipments_Tools_Detail.objects.create(
                equipment_tool=item,
                company=company,
                name=item.equipment_name,
                identifier=identifier,
                serial_number=None,
                is_active=True,
                is_deactivated=False,
                state="DISPONIBLE",
            )

            detalles_creados.append(detalle)
            print(f"Identificador generado y guardado: {identifier}")

        return detalles_creados

    except Equipment_Tools.DoesNotExist:
        print(
            f"Error: Equipment_Tools {item_id} no encontrado."
        )
        return []

    except Company.DoesNotExist:
        print(
            f"Error: Company {company_id} no encontrada."
        )
        return []

    except Exception as e:
        print(
            f"Error al generar identificadores: {str(e)}"
        )
        return []

# Función para editar los registros de los equipos o herramientas
@login_required
@csrf_exempt
def edit_equipments_tools(request):
    context = user_data(request)
    company_id = context["company"]["id"]

    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Método de solicitud inválido'
        })

    _id = request.POST.get('id')

    if not _id:
        return JsonResponse({
            'success': False,
            'message': 'No se recibió el ID del equipo.'
        }, status=400)

    equipment_category_id = request.POST.get('equipment_category')
    equipment_name = request.POST.get('equipment_name', '').strip()
    equipment_type = request.POST.get('equipment_type')
    equipment_brand = request.POST.get('equipment_brand')
    equipment_description = request.POST.get('equipment_description')
    cost = request.POST.get('cost')
    amount = request.POST.get('amount')
    equipment_area = request.POST.get('equipment_area')
    equipment_responsible = request.POST.get('responsible_equipment')
    equipment_location = request.POST.get('equipment_location')

    equipment_technical_sheet = request.FILES.get(
        'equipment_technical_sheet'
    )
    document_factura_equipment = request.FILES.get(
        'document_factura_equipment'
    )

    image = request.FILES.get('image')

    comments = request.POST.get('comments', '').strip()
    has_serial_number = (
        request.POST.get('has_serial_number') == '1'
    )

    try:
        cantidad_nueva = int(amount or 0)

        if cantidad_nueva < 0:
            return JsonResponse({
                'success': False,
                'message': 'La cantidad no puede ser negativa.'
            }, status=400)

        with transaction.atomic():

            # OBTENER EL EQUIPO
            equipment_tool = (
                Equipment_Tools.objects
                .select_for_update()
                .get(
                    id=_id,
                    company_id=company_id
                )
            )

            # VALIDAR NOMBRE DUPLICADO
            if (
                Equipment_Tools.objects
                .filter(
                    equipment_name__iexact=equipment_name,
                    is_active=True,
                    company_id=company_id
                )
                .exclude(id=equipment_tool.id)
                .exists()
            ):

                return JsonResponse({
                    'success': False,
                    'message': (
                        'Este nombre ya se encuentra registrado '
                        'para esta empresa, ingresa otro diferente.'
                    )
                })

            # OBTENER DESGLOSE
            detalles = (
                Equipments_Tools_Detail.objects
                .select_for_update()
                .filter(
                    equipment_tool=equipment_tool,
                    company_id=company_id
                )
            )

            # CONTAR CANTIDAD ACTIVA REAL
            cantidad_actual = detalles.filter(
                is_active=True,
                is_deactivated=False
            ).count()
            # SI LA CANTIDAD AUMENTÓ
            if cantidad_nueva > cantidad_actual:
                faltantes = cantidad_nueva - cantidad_actual
                generate_identificador_equipment_tool(
                    equipment_tool.id,
                    company_id,
                    faltantes
                )

            # SI LA CANTIDAD DISMINUYÓ
            elif cantidad_nueva < cantidad_actual:
                sobrantes = cantidad_actual - cantidad_nueva
             
                disponibles_para_desactivar = (
                    detalles
                    .filter(
                        is_active=True,
                        is_deactivated=False,
                        state='DISPONIBLE'
                    )
                    .order_by('-id')
                )
                cantidad_disponible = (
                    disponibles_para_desactivar.count()
                )
                if cantidad_disponible < sobrantes:
                    return JsonResponse({
                        'success': False,
                        'message': (
                            f'No es posible reducir la cantidad '
                            f'a {cantidad_nueva}. '
                            f'Se necesitan desactivar {sobrantes} '
                            f'equipo(s), pero únicamente hay '
                            f'{cantidad_disponible} disponible(s). '
                            f'Los equipos asignados no pueden '
                            f'desactivarse automáticamente.'
                        )
                    })

                detalles_a_desactivar = list(
                    disponibles_para_desactivar[:sobrantes]
                )

                for detalle in detalles_a_desactivar:
                    detalle.is_active = False
                    detalle.is_deactivated = True
                    detalle.state = 'BAJA'
                    detalle.deactivated_at = timezone.now()

                    detalle.save(
                        update_fields=[
                            'is_active',
                            'is_deactivated',
                            'state',
                            'deactivated_at'
                        ]
                    )

                
            # VOLVER A CALCULAR LA CANTIDAD REAL
            cantidad_activa_final = (
                Equipments_Tools_Detail.objects
                .filter(
                    equipment_tool=equipment_tool,
                    company_id=company_id,
                    is_active=True,
                    is_deactivated=False
                )
                .count()
            )


            # ACTUALIZAR INFORMACIÓN DEL EQUIPO PRINCIPAL
            equipment_tool.equipment_category_id = (
                equipment_category_id
            )
            equipment_tool.equipment_name = equipment_name
            equipment_tool.equipment_type = equipment_type
            equipment_tool.equipment_brand = equipment_brand

            equipment_tool.equipment_description = (
                equipment_description
            )
            equipment_tool.cost = cost
            # GuardaR la cantidad reaL de detalles activos.
            equipment_tool.amount = cantidad_activa_final

            equipment_tool.equipment_area_id = equipment_area
            equipment_tool.equipment_responsible_id = (
                equipment_responsible
            )
            equipment_tool.equipment_location_id = (
                equipment_location
            )
            equipment_tool.comments = comments
            equipment_tool.has_serial_number = (
                has_serial_number
            )
            # FICHA TÉCNICA
            if equipment_technical_sheet:

                folder_path = (
                    f"docs/{equipment_tool.company_id}/"
                    f"Equipments_tools/{equipment_tool.id}/"
                    f"technical_sheet/{equipment_tool.id}/"
                )

                file_name, extension = os.path.splitext(
                    equipment_technical_sheet.name
                )

                new_name = (
                    f'equipment_technical_sheet_'
                    f'{equipment_tool.equipment_name}'
                    f'{extension}'
                )

                s3Name = folder_path + new_name

                upload_to_s3(
                    equipment_technical_sheet,
                    AWS_BUCKET_NAME,
                    s3Name
                )

                equipment_tool.equipment_technical_sheet = (
                    s3Name
                )

            # FACTURA
            if document_factura_equipment:
                folder_path = (
                    f"docs/{equipment_tool.company_id}/"
                    f"Equipments_tools/{equipment_tool.id}/"
                    f"document_factura_equipment/"
                    f"{equipment_tool.id}/"
                )

                file_name, extension = os.path.splitext(
                    document_factura_equipment.name
                )
                new_name = (
                    f'document_factura_equipment'
                    f'{equipment_tool.equipment_name}'
                    f'{extension}'
                )
                s3Name = folder_path + new_name
                upload_to_s3(
                    document_factura_equipment,
                    AWS_BUCKET_NAME,
                    s3Name
                )
                equipment_tool.document_factura_equipment = (
                    s3Name
                )


            # IMAGEN DEL EQUIPO / HERRAMIENTA
            if image:

                folder_path = (
                    f"docs/{equipment_tool.company_id}/"
                    f"Equipments_tools/{equipment_tool.id}/"
                    f"image/{equipment_tool.id}/"
                )

                file_name, extension = os.path.splitext(image.name)

                new_name = (
                    f"equipment_image_{equipment_tool.equipment_name}"
                    f"{extension}"
                )

                s3Name = folder_path + new_name

                upload_to_s3(
                    image,
                    AWS_BUCKET_NAME,
                    s3Name
                )

                equipment_tool.image = s3Name
            # GUARDAR
            equipment_tool.save()
           
        return JsonResponse({
            'success': True,
            'message': 'Equipo editado correctamente!',
            'amount': cantidad_activa_final
        })

    except Equipment_Tools.DoesNotExist:

        return JsonResponse({
            'success': False,
            'message': 'Equipo no encontrado'
        }, status=404)

    except ValueError:

        return JsonResponse({
            'success': False,
            'message': 'La cantidad debe ser un número válido.'
        }, status=400)

    except Exception as e:

        print(f"ERROR EDITANDO EQUIPO: {str(e)}")

        return JsonResponse({
            'success': False,
            'message': (
                f'Error interno del servidor: {str(e)}'
            )
        }, status=500)




#funcion para eliminar los equipos
@login_required
@csrf_exempt
def delete_equipment_tool(request):
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Método de solicitud inválido.'
        }, status=405)

    _id = request.POST.get('id')

    if not _id:
        return JsonResponse({
            'success': False, 
            'message': 'No se proporcionó el Id del equipo o herramienta.'
        }, status=400)

    try:
        equipment_tool = Equipment_Tools.objects.get(id=_id)

    except Equipment_Tools.DoesNotExist:
        return JsonResponse({
            'success': False, 
            'message': 'El equipo o herramienta no existe'
        }, status=404)

    # validar si el equipo tiene desgloses activos 
    has_details = Equipments_Tools_Detail.objects.filter(
        equipment_tool=equipment_tool,
        is_active=True
    ).exists()

    if has_details:
        return JsonResponse({
            'success': False,
            'message': (
                'No se puede eliminar este registro, porque tiene registros en su desglose,'
                'desactiva cada uno.'
            )
        }, status=400)

    # si no tiene desglose desactivar
    equipment_tool.is_active = False
    equipment_tool.save(update_fields=['is_active'])

    return JsonResponse({
        'success': True, 
        'message': 'Equipo desactivado correctamente'
    })




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
                requested_amount = Equipment_Tools.objects.filter(equipment_name=equipment_name, company_id=company_id, is_active=True).first()
                if not requested_amount:
                    return JsonResponse({
                        'success': False,
                        'message': 'El equipo o herramienta no existe.'
                    })
                
                # Verificar la cantidad disponible
                available_amount = Equipments_Tools_Detail.objects.filter(
                    equipment_tool=requested_amount,
                    company_id=company_id,
                    is_active=True,
                    is_deactivated=False,
                    state="DISPONIBLE"
                ).count()

                if amount > available_amount:
                    return JsonResponse({
                        'success': False,
                        'message': (
                            f'No contamos con la cantidad solicitada. '
                            f'Actualmente hay {available_amount} equipos disponibles.'
                        )
                    })
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
                        if file_data.count(b'\xFF') == len(file_data) - 12:  
                            return JsonResponse({'success': False, 'message': 'La firma no puede ser completamente blanca.'})
 
 
                # Usar un timestamp para el nombre del archivo de la firma
                timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
                folder_path = f"docs/{company_id}/Equipments_tools/signatureResponsivas/{timestamp}/"  

                # Generar un nombre único para la firma
                new_name = f"signature_{timestamp}.png"
                s3Name = folder_path + new_name
                upload_to_s3(signature_file, AWS_BUCKET_NAME, s3Name)
                

                # Crear la nueva responsiva del equipo
                responsiva = Equipment_Tools_Responsiva.objects.create(
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
                    fecha_registro = timezone.now() - timedelta(hours=6)

                )

                # Retornar la respuesta JSON
                return JsonResponse({
                    'success': True,
                    'message': 'Responsiva agregada correctamente',
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
        return None  

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
    isList = request.GET.get("isList", False)
    responsiva_id = request.GET.get("responsiva_id")
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

            filtros = {
                "company_id": company_id,
            }
            if responsiva_id:
                filtros["id"] = responsiva_id

            responsiva = list(Equipment_Tools_Responsiva.objects.select_related(
                'equipment_name', 'responsible_equipment', 'status_modified_by'
            ).filter(
                **filtros
            ).order_by('-fecha_registro').values(
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
                'fecha_registro',
                'status_modified_by__username',
            )
        )
        else:
            filtros = {
                "responsible_equipment__username__iexact": user_name,
            }
            if responsiva_id:
                filtros["id"] = responsiva_id

            responsiva = list(Equipment_Tools_Responsiva.objects.select_related(
                'equipment_name', 'responsible_equipment', 'status_modified_by'
            ).filter(**filtros).order_by('-fecha_registro').values(
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
                'fecha_registro',
                'status_modified_by__username',
            )
        )
        print(f"Registros encontrados: {responsiva}")

        for item in responsiva:
            item["btn_action"] = ""
            item["boton_action"] = ""

            is_user_applicant = (
                item['responsible_equipment__username'] and
                item['responsible_equipment__username'].lower() == user_name
            )

            can_edit_date = (
                access["update"] and
                (
                    area.lower() == "almacen" or
                    tipo_user.lower() in ["administrador", "super usuario"] or
                    is_user_applicant
                )
            )

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
            if can_edit_date:
                if item['status_equipment'] in ['Aceptado', 'Atrasado']:
                    edit_button = (
                        "<button type='button' class='btn btn-icon btn-sm btn-primary-light edit-btn' "
                        "onclick='edit_date(this)' aria-label='Editar feccha de recepción'>"
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
    user_id = context["user"]["id"]
    if request.method == 'POST':
        try:
            equipment_id = request.POST.get('id') 
            status_value = request.POST.get('status_equipment')
            comments = request.POST.get('comments')
            return_amount = request.POST.get('return_amount')

            # id de los equipos a dar de baja
            details_to_deactivate = request.POST.getlist("details_to_deactivate")

            signature_almacen_file = request.FILES.get('signature_almacen')

            # Obtener la responsiva
            responsiva = Equipment_Tools_Responsiva.objects.get(id=equipment_id, company_id=company_id)

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

            if status_name not in ['Regresado', 'Incompleto', 'Dañado', 'No devuelto']:
                return JsonResponse({
                    'success': False,
                    'message': 'El estado seleccionado no es válido para devolver el equipo.'
                }, status=400)

           
            with transaction.atomic():

                equipment_tool = responsiva.equipment_name

                # Detalles actuales asignados a la responsiva
                detalles_asignados = Equipments_Tools_Detail.objects.filter(
                    responsiva=responsiva,
                    equipment_tool=equipment_tool,
                    company_id=company_id,
                    state="ASIGNADO",
                    is_active=True,
                    is_deactivated=False
                ).order_by("id")

                total_detalles = detalles_asignados.count()


                # REGRESADO
                if status_name == "Regresado":

                    detail_ids = list(
                        detalles_asignados.values_list("id", flat=True)
                    )
                    
                    detalles_asignados.update(
                        state="DISPONIBLE",
                        responsible=None,
                        responsiva=None
                    )
                    #actualiza los registros de la responsiva
                    Detail_Responsiva.objects.filter(
                        responsiva=responsiva,
                        details_equipment_tool__in=detail_ids
                    ).update(
                        status_equipment_tool="REGRESADO"
                    )
                # INCOMPLETO
                elif status_name == "Incompleto":

                    if return_amount <= 0:
                        return JsonResponse({
                            "success": False,
                            "message": "La cantidad devuelta debe ser mayor a cero."
                        }, status=400)

                    if return_amount >= responsiva.amount:
                        return JsonResponse({
                            "success": False,
                            "message": (
                                "La cantidad devuelta debe ser menor "
                                "a la cantidad prestada."
                            )
                        }, status=400)

                    # Cantidad de equipos que NO fueron devueltos
                    cantidad_a_desactivar = responsiva.amount - return_amount

                    try:
                        detail_ids = [
                            int(detail_id)
                            for detail_id in details_to_deactivate
                        ]
                    except (TypeError, ValueError):

                        return JsonResponse({
                            "success": False,
                            "message": "Los equipos seleccionados no son válidos."
                        }, status=400)


                    if len(detail_ids) != cantidad_a_desactivar:

                        return JsonResponse({
                            "success": False,
                            "message": (
                                f"Debes seleccionar exactamente "
                                f"{cantidad_a_desactivar} equipo(s) "
                                f"para dar de baja."
                            )
                        }, status=400)

                    # Buscar equipos configurados para dar de baja
                    detalles_a_desactivar = Equipments_Tools_Detail.objects.filter(
                        id__in=detail_ids,
                        equipment_tool=equipment_tool,
                        company_id=company_id,
                        responsiva=responsiva,
                        is_active=False,
                        is_deactivated=True,
                        state="BAJA"
                    )

                    # Verificar que todos estén correctamente configurados
                    if detalles_a_desactivar.count() != cantidad_a_desactivar:

                        return JsonResponse({
                            "success": False,
                            "message": (
                                "Uno o más equipos seleccionados "
                                "no han sido configurados correctamente "
                                "para darse de baja."
                            )
                        }, status=400)

                    # Equipos devueltos
                    detalles_a_regresar = detalles_asignados.exclude(
                        id__in=detail_ids
                    )

                    ids_regresados = list(
                        detalles_a_regresar.values_list(
                            "id",
                            flat=True
                        )
                    )

                    # editar equipos regresados
                    detalles_a_regresar.update(
                        state="DISPONIBLE",
                        responsible=None,
                        responsiva=None
                    )

                    # equipos no devueltos
                    actualizados_no_devueltos = Detail_Responsiva.objects.filter(
                        responsiva_id=responsiva.id,
                        details_equipment_tool_id__in=detail_ids
                    ).update(
                        status_equipment_tool="NO DEVUELTO"
                    )

                    # actualizar equipos regresados
                    actualizados_regresados = Detail_Responsiva.objects.filter(
                        responsiva_id=responsiva.id,
                        details_equipment_tool_id__in=ids_regresados
                    ).update(
                        status_equipment_tool="REGRESADO"
                    )

                # DAÑADO
                elif status_name == "Dañado":

                    if not details_to_deactivate:

                        return JsonResponse({
                            "success": False,
                            "message": (
                                "Debes seleccionar al menos un equipo "
                                "dañado para continuar."
                            )
                        }, status=400)

                    try:
                        detail_ids = [
                            int(detail_id)
                            for detail_id in details_to_deactivate
                        ]
                    except (TypeError, ValueError):

                        return JsonResponse({
                            "success": False,
                            "message": ( f"No puedes seleccionar más de " f"{total_detalles} equipo(s)." )
                        }, status=400)

                    # equipos configurados para baja
                    detalles_a_desactivar = Equipments_Tools_Detail.objects.filter(
                        id__in=detail_ids,
                        equipment_tool=equipment_tool,
                        company_id=company_id,
                        responsiva=responsiva,
                        is_active=False,
                        is_deactivated=True,
                        state="BAJA"
                    )

                    # validar equipos a dar de baja
                    if detalles_a_desactivar.count() != len(detail_ids):

                        return JsonResponse({
                            "success": False,
                            "message": (
                                "Uno o más equipos seleccionados "
                                "no han sido configurados correctamente "
                                "para darse de baja."
                            )
                        }, status=400)

                    # Al menos una imagen por equipo
                    for detalle in detalles_a_desactivar: 
                        if not detalle.evidence1_image and not detalle.evidence2_image: 
                            return JsonResponse({ 
                                "success": False, 
                                "message": ( f"El equipo {detalle.identifier} " "debe tener al menos una imagen " "como evidencia del daño." 
                            ) 
                        }, status=400)

                    # equipos devueltos 
                    detalles_a_regresar = detalles_asignados.exclude(
                        id__in=detail_ids
                    )

                    ids_regresados = list(
                        detalles_a_regresar.values_list(
                            "id",
                            flat=True
                        )
                    )

                    # regresar equipos no dañados
                    detalles_a_regresar.update(
                        state="DISPONIBLE",
                        responsible=None,
                        responsiva=None
                    )

                    # actualizar historial de equipos dañados
                    Detail_Responsiva.objects.filter(
                        responsiva_id=responsiva.id,
                        details_equipment_tool_id__in=detail_ids
                    ).update(
                        status_equipment_tool="DAÑADO"
                    )

                    # actualizar historial de equipos regresados
                    Detail_Responsiva.objects.filter(
                        responsiva_id=responsiva.id,
                        details_equipment_tool_id__in=ids_regresados
                    ).update(
                        status_equipment_tool="REGRESADO"
                    )

                # NO DEVUELTO
                elif status_name == "No devuelto":

                    # Obtener los IDs antes de modificar los detalles
                    detail_ids = list(
                        detalles_asignados.values_list("id", flat=True)
                    )

                    detalles_asignados.update(
                        state="BAJA",
                        is_active=False,
                        is_deactivated=True,
                        deactivation_reason="PERDIDO",
                        deactivation_description=(
                            "Equipo no devuelto por el responsable."
                        ),
                        deactivated_at=timezone.now(),
                        responsible=None,
                        #assignment_date=None,
                        responsiva=None
                    )

                    #actualiza los registros de la responsiva
                    Detail_Responsiva.objects.filter(
                        responsiva=responsiva,
                        details_equipment_tool__in=detail_ids
                    ).update(
                        status_equipment_tool="NO DEVUELTO"
                    )

                    print(
                        f"{total_detalles} detalle(s) marcado(s) como BAJA."
                    )

                # ACTUALIZAR RESPONSIVA
                responsiva.status_equipment = status_name
                responsiva.comments = comments
                responsiva.date_receipt = timezone.now().date()
                responsiva.signature_almacen = s3Name
                responsiva.status_modified = True
                responsiva.status_modified_by_id = user_id
                responsiva.save()

                cantidad_disponible = ( 
                    Equipments_Tools_Detail.objects 
                    .filter( 
                        equipment_tool=equipment_tool, 
                        company_id=company_id, is_active=True, 
                        is_deactivated=False, 
                        state="DISPONIBLE" ) 
                        .count() 
                    ) 
                    
                equipment_tool.amount = cantidad_disponible 
                equipment_tool.save( 
                    update_fields=['amount'] 
                )

                return JsonResponse({ 
                    'success': True, 
                    'message': 'La responsiva ha sido actualizada correctamente.' 
                }, status=200)
            
        except Equipment_Tools_Responsiva.DoesNotExist: 
            return JsonResponse({ 
                'success': False, 
                'message': 'La responsiva no existe.' 
            }, status=404) 
        except Exception as e: 
            logger.error( 
                'Error en status_responsiva: %s', 
                str(e) 
            ) 
            
        return JsonResponse({ 
            'success': False, 
            'message': 'Error interno del servidor.' 
        }, status=500) 
    return JsonResponse({ 
        'success': False, 
        'message': 'Método no permitido.' }, 
    status=405)


# Función para aprobar la responsiva del equipo
@login_required
@csrf_exempt
def approve_responsiva(request):

        if request.method != 'POST': return JsonResponse({ 'success': False, 'message': 'Método no permitido.' }, status=405)
        try:
            responsiva_id = request.POST.get('id')
            if not responsiva_id: return JsonResponse({ 'success': False, 'message': 'No se recibió el ID de la responsiva.' }, status=400)

            # obtener responsiva
            responsiva = Equipment_Tools_Responsiva.objects.select_related('equipment_name', 'responsible_equipment').get(id=responsiva_id)

            # Validar que no se puede aprobar si ya fue cancelada
            if responsiva.status_equipment == 'Cancelado':
                return JsonResponse({'success': False, 'message': 'La responsiva fue cancelada, no se puede aprobar.'}, status=400)

            # Validar que solo se puede aprobar una vez la responsiva
            if responsiva.status_modified:
                return JsonResponse({'success': False, 'message': 'La responsiva ya fue aprobada, no puede ser aprobada de nuevo.'}, status=400)

            # Validar que no se puede aprobar si ya fue aceptada
            if responsiva.status_equipment == 'Aceptado':
                return JsonResponse({'success': False, 'message': 'La responsiva ya ha sido aceptada, no puede ser aprobada de nuevo.'}, status=400)

            # datos de la solicitud
            equipment_tool = responsiva.equipment_name 
            responsable = responsiva.responsible_equipment 
            cantidad_solicitada = int(responsiva.amount)

            # transaccion
            with transaction.atomic():
            # BUSCAR EQUIPOS DISPONIBLES

                detalles_disponibles = list(
                    Equipments_Tools_Detail.objects
                    .select_for_update()
                    .filter(
                        equipment_tool=equipment_tool,
                        company_id=responsiva.company_id,
                        is_active=True,
                        is_deactivated=False,
                        state="DISPONIBLE",
                    )
                    .order_by('id')[:cantidad_solicitada]
                )

                cantidad_disponible = len(detalles_disponibles)

                # VALIDAR CANTIDAD
                if cantidad_disponible < cantidad_solicitada:
                    return JsonResponse({
                        'success': False,
                        'message': (
                            f'No hay suficientes equipos disponibles. '
                            f'Solicitados: {cantidad_solicitada}. '
                            f'Disponibles: {cantidad_disponible}.'
                        )
                    }, status=400)

                # ASIGNAR EQUIPOS
                fecha_asignacion = timezone.now().date()

                for detalle in detalles_disponibles:

                    detalle.responsible = responsable
                    detalle.assignment_date = fecha_asignacion
                    detalle.state = "ASIGNADO"
                    detalle.responsiva = responsiva

                    detalle.save(
                        update_fields=[
                            'responsible',
                            'assignment_date',
                            'state',
                            'responsiva'
                        ]
                    )


                    with transaction.atomic():
                        Detail_Responsiva.objects.create(
                            responsiva=responsiva,
                            details_equipment_tool=detalle,
                            status_equipment_tool="ASIGNADO"
                           
                        )

                # Actualizar responsiva
                responsiva.status_equipment = 'Aceptado'
                responsiva.status_modified = True 
                responsiva.save(update_fields=[
                    'status_equipment',
                    'status_modified'
                ])

                # actualizar la cantidad disponible del equipo principal
                cantidad_disponible_restante = (
                    Equipments_Tools_Detail.objects.filter(
                        equipment_tool=equipment_tool,
                        company_id=responsiva.company_id,
                        is_active=True,
                        state="DISPONIBLE"
                    )
                    .count()
                )

                equipment_tool.amount = cantidad_disponible_restante
                equipment_tool.save(update_fields=['amount'])

                return JsonResponse({ 
                    'success': True, 
                    'message': ( 
                        f'La responsiva fue aceptada correctamente. ' 
                        f'Se asignaron {cantidad_solicitada} ' 
                        f'equipos al usuario.' 
                        ), 
                    'assigned': cantidad_solicitada, 
                    'available': cantidad_disponible_restante 
                })

        except Equipment_Tools_Responsiva.DoesNotExist: 
            return JsonResponse({ 
                'success': False, 
                'message': 'La responsiva no existe.' 
            }, status=404)

        except ValueError: 
            return JsonResponse({ 
                'success': False, 
                'message': 'La cantidad solicitada no es válida.' 
            }, status=400)

        except Exception as e: 
            logger.error( 
                'Error en approve_responsiva: %s', 
                str(e) 
            ) 
            return JsonResponse({ 
                'success': False, 
                'message': 'Error interno del servidor.' 
            }, status=500)
        

# Función para cancelar la responsiva del usuario
@login_required
@csrf_exempt
def cancel_responsiva(request):

    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Método no permitido.'
        }, status=405)

    try:
        responsiva_id = request.POST.get('id')

        if not responsiva_id:
            return JsonResponse({
                'success': False,
                'message': 'No se recibió el ID de la responsiva.'
            }, status=400)

        # Obtener la responsiva
        responsiva = (
            Equipment_Tools_Responsiva.objects
            .select_related('equipment_name')
            .get(id=responsiva_id)
        )

        # VALIDAR SI YA ESTÁ CANCELADA
        if responsiva.status_equipment == 'Cancelado':

            return JsonResponse({
                'success': False,
                'message': (
                    'La responsiva ya ha sido cancelada, '
                    'no puede ser cancelada de nuevo.'
                )
            }, status=400)

        # VALIDAR SI YA FUE ACEPTADA
        if responsiva.status_equipment == 'Aceptado':

            return JsonResponse({
                'success': False,
                'message': (
                    'La responsiva ya ha sido aceptada, '
                    'no puede ser cancelada.'
                )
            }, status=400)

        with transaction.atomic():

            equipment_tool = responsiva.equipment_name
            # CANCELAR LA RESPONSIVA
            responsiva.status_equipment = 'Cancelado'
            responsiva.status_modified = True

            responsiva.save(
                update_fields=[
                    'status_equipment',
                    'status_modified'
                ]
            )

            # RECALCULAR CANTIDAD DISPONIBLE
            cantidad_disponible = (
                Equipments_Tools_Detail.objects
                .filter(
                    equipment_tool=equipment_tool,
                    company_id=responsiva.company_id,
                    is_active=True,
                    is_deactivated=False,
                    state="DISPONIBLE"
                )
                .count()
            )

            # Actualizar la cantidad de la tabla principal
            equipment_tool.amount = cantidad_disponible

            equipment_tool.save(
                update_fields=['amount']
            )

        return JsonResponse({
            'success': True,
            'message': (
                'La responsiva ha sido cancelada correctamente.'
            ),
            'available': cantidad_disponible
        }, status=200)

    except Equipment_Tools_Responsiva.DoesNotExist:

        return JsonResponse({
            'success': False,
            'message': 'La responsiva no existe.'
        }, status=404)

    except Exception as e:

        logger.error(
            'Error en cancel_responsiva: %s',
            str(e)
        )

        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}'
        }, status=500)


#función para obtener la fecha actual del servidor 
def get_server_date(request):
    # Obtén la fecha actual del servidor en formato YYYY-MM-DD
    server_date = timezone.now().astimezone().date().isoformat()  # Usa la zona horaria local
    return JsonResponse({'server_date':server_date})

#funcion para actualizar la fecha de entrega y actualizar el tiempo requerido
@login_required
@csrf_exempt
def edit_date_responsiva(request):

    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Método no permitido.'
        })

    try:

        # obtener datos
        fecha_entrega = request.POST.get('fecha_edit')
        id_responsiva = request.POST.get('id')
        reason_date_change = request.POST.get('reason_date_change')
        # Firma enviada 
        signature_almacen = request.FILES.get('signature_almacen')
        # Usuario que está realizando el cambio
        usuario_actual = request.user
        # Fecha actual
        fecha_actual = timezone.now().date()
        fecha_entrega_date = parse_date(fecha_entrega)

        if not fecha_entrega_date:
            return JsonResponse({
                'success': False,
                'message': 'La fecha de entrega no es válida.'
            })
        if fecha_entrega_date <= fecha_actual:
            return JsonResponse({
                'success': False,
                'message': 'La fecha de entrega debe ser mayor a la fecha actual.'
            })

        # validar motivo
        if not reason_date_change or not reason_date_change.strip():
            return JsonResponse({
                'success': False,
                'message': 'El motivo de cambio es obligatorio.'
            })
        # obtener responsiva
        try:

            responsiva = Equipment_Tools_Responsiva.objects.get(
                id=id_responsiva
            )

        except Equipment_Tools_Responsiva.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Responsiva no encontrada.'
            })


        # comprobar si es el mismo usuario
        mismo_usuario = (
            usuario_actual.id == responsiva.responsible_equipment_id
        )
        # validar la firma de almacen
        if not mismo_usuario and not signature_almacen:
            return JsonResponse({
                'success': False,
                'message': 'La firma de almacén es obligatoria para este cambio.'
            })
        # calcular el tiempo solicitdo
        if responsiva.fecha_inicio:
            tiempo_requerido = (
                fecha_entrega_date - fecha_actual
            ).days
        else:
            tiempo_requerido = 0

        with transaction.atomic():

            # Guardar detalles actuales
            detalles_anterior = list(
                Detail_Responsiva.objects.filter(
                    responsiva=responsiva
                )
            )

            # cerrar responsiva anterior
            responsiva.status_equipment = "Regresado"
            responsiva.status_modified = True
            responsiva.status_modified_by = usuario_actual
            responsiva.reason_date_change = reason_date_change
            # Fecha en la que se recibió/cerró la responsiva
            responsiva.date_receipt = fecha_actual

            # Guardar firma de almacén
            if signature_almacen:
                responsiva.signature_almacen = signature_almacen
            responsiva.save()

            # crear nueva responsiva
            nueva_responsiva = Equipment_Tools_Responsiva.objects.create(
                company=responsiva.company,
                equipment_name=responsiva.equipment_name,
                responsible_equipment=responsiva.responsible_equipment,
                amount=responsiva.amount,
                # Nueva fecha de inicio
                fecha_inicio=fecha_actual,
                # Nueva fecha de entrega
                fecha_entrega=fecha_entrega_date,
                # nuevo tiempo calculado
                times_requested_responsiva=tiempo_requerido,

                # Conservar la firma del empleado
                signature_responsible=responsiva.signature_responsible,

                comments=responsiva.comments,

                # NUEVA RESPONSIVA
                status_equipment="Aceptado",

                status_modified=True,

                status_modified_by=usuario_actual,

                reason_date_change=reason_date_change,

                fecha_registro=timezone.now() - timedelta(hours=6)
            )


            # copiar los equipos de manera individual
            for detalle in detalles_anterior:

                #obtener el detalle especifico del equipo
                detalle_equipo = detalle.details_equipment_tool
                #actualizar la relacion del equipo con la nueva responsiva
                detalle_equipo.responsiva = nueva_responsiva
                detalle_equipo.state = "ASIGNADO"
                detalle_equipo.is_active = True
                detalle_equipo.is_deactivated=False
                detalle_equipo.save(
                    update_fields=[
                        "responsiva",
                        "state",
                        "is_active",
                        "is_deactivated"
                    ]
                )

                #crear el nuevo registro historico de la responsiva
                Detail_Responsiva.objects.create(
                    responsiva=nueva_responsiva,
                    details_equipment_tool=detalle_equipo,
                    status_equipment_tool="ASIGNADO"
                )

        return JsonResponse({
            'success': True,
            'message': (
                'La fecha fue actualizada correctamente.'
                'La responsiva anterior fue cerrada y se creó '
                'una nueva responsiva con el mismo desglose.'
            ),
            'old_responsiva_id': responsiva.id,
            'new_responsiva_id': nueva_responsiva.id,
            'same_user': mismo_usuario
        })

    except Exception as e:
        print(
            "ERROR AL ACTUALIZAR FECHA DE RESPONSIVA:",
            str(e)
        )

        return JsonResponse({
            'success': False,
            'message': (
                'Ocurrió un error al actualizar '
                'la fecha de entrega.'
            )
        })

#funcion para obtener el historial de los equipos y herramientas
@csrf_exempt
def get_equipment_history(request):
    if request.method == 'POST':
        equipment_id = request.POST.get('equipment_id')
        
        try:
            responsivas = Equipment_Tools_Responsiva.objects.filter(equipment_name__id=equipment_id).exclude(
                status_equipment='Cancelado').values(
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


# Generar PDF de responsiva de Equipo y Herramienta
@login_required
def equipment_tools_responsiva_pdf_view(request, responsiva_id):
    responsiva = get_object_or_404(
        Equipment_Tools_Responsiva.objects.select_related(
            "equipment_name",
            "responsible_equipment",
            "company",
        ),
        id=responsiva_id
    )
    # Obtener el desglose de la responsiva
    detalles_responsiva = (
        Detail_Responsiva.objects
        .filter(
            responsiva=responsiva,
            details_equipment_tool__isnull=False
        )
        .select_related(
            "details_equipment_tool",
            "details_equipment_tool__equipment_tool",
            "details_equipment_tool__equipment_location",
        )
        .order_by("details_equipment_tool__id")
    )

    detalles = []

    for detalle_responsiva in detalles_responsiva:

        detalle = detalle_responsiva.details_equipment_tool


        print("==========================================")
        print("RESPONSIVA:", responsiva.id)
        print("DETAIL RESPONSIVA ID:", detalle_responsiva.id)
        print("DETALLE EQUIPO ID:", detalle.id)
        print("IDENTIFICADOR:", detalle.identifier)
        print("STATUS DETAIL RESPONSIVA:", detalle_responsiva.status_equipment_tool)
        print("STATE EQUIPO:", detalle.state)

        detalles.append({
            "id": detalle.id,

            # Información individual
            "identifier": detalle.identifier,
            "name": detalle.name,
            "serial_number": detalle.serial_number,

            # Fechas
            "assignment_date": detalle.assignment_date,
            "modification_date": detalle.modification_date,

            # Responsable
            "responsible": (
                detalle.responsible.get_full_name()
                if detalle.responsible
                else None
            ),

            # Estado individual dentro de la responsiva
            "status": detalle_responsiva.status_equipment_tool,

            # Estado actual del detalle
            "state": detalle.state,

            # Ubicación
            "location": (
                str(detalle.equipment_location)
                if detalle.equipment_location
                else None
            ),

            # Fotografía
            "photo": (
                generate_presigned_url(
                    AWS_BUCKET_NAME,
                    str(detalle.photo)
                )
                if detalle.photo
                else None
            ),
        })

    # RESPONSABLE
    responsible_name = (
        responsiva.responsible_equipment.get_full_name()
        or responsiva.responsible_equipment.username
    )
    # FIRMAS
    signature_responsible = (
        generate_presigned_url(
            AWS_BUCKET_NAME,
            str(responsiva.signature_responsible)
        )
        if responsiva.signature_responsible
        else None
    )

    signature_almacen = (
        generate_presigned_url(
            AWS_BUCKET_NAME,
            str(responsiva.signature_almacen)
        )
        if responsiva.signature_almacen
        else None
    )
    # Contexto
    context = {

        "title": "Responsiva de Equipo y Herramienta",
        "responsiva": responsiva,
        # Responsable temporal
        "responsible_name": responsible_name,
        # Fechas de la responsiva
        "fecha_inicio": responsiva.fecha_inicio,
        "fecha_entrega": responsiva.fecha_entrega,
        # Tiempo solicitado
        "times_requested": responsiva.times_requested_responsiva,
        # Cantidad
        "amount": responsiva.amount,
        # Estado
        "status": responsiva.status_equipment,
        # Fecha de recibido
        "date_receipt": responsiva.date_receipt,
        # Comentarios
        "comments": responsiva.comments,
        # Equipo padre
        "equipment": responsiva.equipment_name,
        # Desglose individual
        "details": detalles,
        # Cantidad real de detalles
        "details_count": len(detalles),
        # Firmas
        "signature_responsible": signature_responsible,
        "signature_almacen": signature_almacen,
    }
    return WeasyPDF(
        "pdf/equipment_tools_responsiva.html",
        context
    ).render()


# tabla de informacion de un equipo o herramienta
def get_equipment_tools_details(request):
    equipment_tool_id = request.GET.get("id")
    data = []

    if equipment_tool_id:
        try:
            equipment_tool = Equipment_Tools.objects.get(
                id = equipment_tool_id
            )

            has_serial_number = equipment_tool.has_serial_number

            registros = (
                Equipments_Tools_Detail.objects
                .filter(equipment_tool=equipment_tool)
                .values(
                    "id",
                    "identifier",
                    "responsible__id",
                    "responsible__first_name",
                    "responsible__last_name",
                    "assignment_date",
                    "serial_number",
                    "equipment_location__location_name",
                    "is_active",
                    "is_deactivated",
                    "state",
                    "photo"
                )
            )

            for r in registros:
                # RESPONSABLE
                tiene_responsable = (
                    r["responsible__first_name"]
                    or r["responsible__last_name"]
                )

                responsable = (
                    f"{r['responsible__first_name'] or ''} "
                    f"{r['responsible__last_name'] or ''}"
                ).strip()

                if not responsable:
                    responsable = "Disponible"

                # NÚMERO DE SERIE
                serial_number = r["serial_number"] or ""

                equipment_location = (
                    r["equipment_location__location_name"]
                    or "Sin ubicación"
                )

                # FECHA
                fecha_asignacion = (
                    r["assignment_date"].strftime("%Y-%m-%d")
                    if r["assignment_date"]
                    else ""
                )

                # FOTOGRAGIA
                fotografia = False
                if r["photo"]:
                    tUrl = generate_presigned_url( AWS_BUCKET_NAME, str(r["photo"]))
                    fotografia = f"""
                    <a href="{tUrl}"
                       target="_blank"
                       title="Ver fotografía">
                        <img
                            src="{tUrl}"
                            alt="Fotografía de {r['identifier']}"
                            class="rounded border"
                            style="
                                width: 70px;
                                height: 70px;
                                object-fit: cover;
                                cursor: pointer;
                            "
                        >
                    </a>
                """
                # AGREGAR REGISTRO
                data.append({

                    "id": r["id"],
                    "identificador": r["identifier"],
                    "state": r["state"],
                    "responsable": responsable,
                    "responsable_id": (
                        r["responsible__id"]
                        if tiene_responsable
                        else None
                    ),
                    "tiene_responsable": bool(
                        tiene_responsable
                    ),
                    "fotografia" : fotografia if fotografia else None,
                    "fecha_asignacion": fecha_asignacion,
                    "serial_number": serial_number,
                    "equipment_location": equipment_location,
                    "is_active": r["is_active"],
                    "is_deactivated": r["is_deactivated"],

                })

            return JsonResponse({
                "success": True,
                # numero de serie del equipo
                "has_serial_number": has_serial_number,
                "data": data
            })
        except Equipment_Tools.DoesNotExist:
            return JsonResponse({
                "success": False,
                "message": "El equipo o herramienta no existe."
            }, status=404)
    return JsonResponse({
        "success": True,
        "has_serial_number": False,
        "data": data
    })


# guardar numero de serie
@login_required
@csrf_exempt
def save_equipment_tool_serial_number(request):
    context = user_data(request)
    company_id = context["company"]["id"]

    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "Método no permitido."
        }, status=405)


    detalle_id = request.POST.get("detalle_id")
    
    numero_serie = request.POST.get("serial_number", "").strip()

    detalle = Equipments_Tools_Detail.objects.get(
        id=detalle_id, company_id=company_id
    )


    # image
    if "photo" in request.FILES:
    
        image = request.FILES.get("photo")

        if image:

            folder_path = (
                f"docs/{company_id}/"
                f"Equipments_tools/{detalle_id}/"
                f"image/{detalle_id}/"
            )

            file_name, extension = os.path.splitext(image.name)

            new_name = (
                f"equipment_image_{detalle_id}"
                f"{extension}"
            )

            s3Name = folder_path + new_name

            if detalle.photo:
                delete_s3_object(AWS_BUCKET_NAME, str(detalle.photo))

            upload_to_s3(
                image,
                bucket_name,
                s3Name
            )

            detalle.photo = s3Name
            detalle.save(update_fields=["photo"])

        return JsonResponse({
            "success": True,
            "message":
                "Imagen guardada correctamente."
        })
    
    # VALIDACIONES
    if not detalle_id:
        return JsonResponse({
            "success": False,
            "message": "No se recibió el detalle del equipo."
        })

    if not numero_serie:
        return JsonResponse({
            "success": False,
            "message": "El número de serie es obligatorio."
        })

    try:
        detalle = Equipments_Tools_Detail.objects.get(
            id=detalle_id
        )
        # VALIDAR DUPLICADO
        existe = (
            Equipments_Tools_Detail.objects
            .filter(
                serial_number=numero_serie
            )
            .exclude(
                id=detalle.id
            )
            .exists()
        )

        if existe:
            return JsonResponse({
                "success": False,
                "message":
                    "Este número de serie ya está registrado en otro equipo."
            })

        # GUARDAR
        detalle.serial_number = numero_serie

        detalle.save(
            update_fields=[
                "serial_number"
            ]
        )

        return JsonResponse({
            "success": True,
            "message":
                "Número de serie guardado correctamente.",
            "data": {
                "id": detalle.id,
                "serial_number":
                    detalle.serial_number
            }

        })

    except Equipments_Tools_Detail.DoesNotExist:
        return JsonResponse({
            "success": False,
            "message":
                "No se encontró el detalle del equipo."
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message":
                f"Error al guardar el número de serie: {str(e)}"
        })



@login_required
def modal_equipment_tool_detail(request):
    detail_id = request.GET.get("id")
    if not detail_id:
        return JsonResponse({
            "success": False,
            "message": "No se recibió el identificador."
        })

    try:
        context = user_data(request)
        company_id = context["company"]["id"]
        detail = Equipments_Tools_Detail.objects.get(
            id=detail_id,
            company_id=company_id
        )

        return JsonResponse({
            "success": True,
            "data": {
                "id": detail.id,
                "identifier": detail.identifier,
                "name": detail.name,
            }
        })

    except Equipments_Tools_Detail.DoesNotExist:

        return JsonResponse({
            "success": False,
            "message": "El detalle no existe."
        }, status=404)

# dar de baja / habilitar un equipo
@login_required
def disable_equipment_tool_detail(request):

    detail_id = request.POST.get("detail_id")
    action = request.POST.get("action")

    if not detail_id:
        return JsonResponse({
            "success": False,
            "message": "No se recibió el ID del detalle."
        })

    try:
        context = user_data(request)
        company_id = context["company"]["id"]
        detail = Equipments_Tools_Detail.objects.get(id=detail_id, company_id=company_id)

        # DESHABILITAR
        if action == "disable":
            reason = request.POST.get("reason")
            description = request.POST.get(
                "description",
                ""
            ).strip()
            # Archivos
            evidence1 = request.FILES.get("evidence1_image")
            evidence2 = request.FILES.get("evidence2_image")

            if not reason:
                return JsonResponse({
                    "success": False,
                    "message": "Debe seleccionar un motivo de baja."
                })

            if not description:
                return JsonResponse({
                    "success": False,
                    "message": "Debe ingresar una descripción."
                })

            if not evidence1 and not evidence2:
                return JsonResponse({
                    "success": False,
                    "message": "Debe adjuntar al menos una imagen como evidencia de la baja."
                })

            # Cambiar estado
            detail.is_active = False
            detail.is_deactivated = True
            detail.state = "BAJA"

            # Información de la baja
            detail.deactivation_reason = reason
            detail.deactivation_description = description
            detail.deactivated_at = timezone.now() - timedelta(hours=6)

            # Usuario que realizó la baja
            detail.user_modification = request.user

            # Ruta base
            equipment_id = detail.equipment_tool_id

            # Evidencia 1
            if evidence1:

                folder_path = (
                    f"docs/{company_id}/"
                    f"Equipments_tools/{equipment_id}/"
                    f"evidence1_image/{detail.id}/"
                )

                file_name, extension = os.path.splitext(
                    evidence1.name
                )

                new_name = (
                    f"evidence1_image"
                    f"{detail.identifier}"
                    f"{extension}"
                )

                s3Name = folder_path + new_name

                upload_to_s3(
                    evidence1,
                    bucket_name,
                    s3Name
                )

                detail.evidence1_image = s3Name

            # Evidencia 2
            if evidence2:

                folder_path = (
                    f"docs/{company_id}/"
                    f"Equipments_tools/{equipment_id}/"
                    f"evidence2_image/{detail.id}/"
                )

                file_name, extension = os.path.splitext(
                    evidence2.name
                )

                new_name = (
                    f"evidence2_image"
                    f"{detail.identifier}"
                    f"{extension}"
                )

                s3Name = folder_path + new_name

                upload_to_s3(
                    evidence2,
                    bucket_name,
                    s3Name
                )

                detail.evidence2_image = s3Name

            detail.save()

            return JsonResponse({
                "success": True,
                "message": (
                    "El equipo o herramienta "
                    "ha sido dado de baja correctamente."
                )
            })

        # HABILITAR
        elif action == "enable":

            # Cambiar estado
            detail.is_active = True
            detail.is_deactivated = False
            detail.state = "DISPONIBLE"

            # Registrar usuario de activación
            detail.user_activation = request.user

            # Registrar fecha y hora de activación
            detail.modification_date = timezone.now() - timedelta(hours=6)

            # Limpiar información de baja
            detail.deactivation_reason = None
            detail.deactivation_description = None
            detail.deactivated_at = None

            detail.save()

            return JsonResponse({ "success": True, "message": ("El equipo o herramienta " "ha sido habilitado correctamente.")})

        # ACCIÓN NO VÁLIDA
        else:

            return JsonResponse({"success": False, "message": "Acción no válida."})

    except Equipments_Tools_Detail.DoesNotExist:

        return JsonResponse({
            "success": False,
            "message": "El equipo o herramienta no existe."
        }, status=404)

    except Exception as e:

        return JsonResponse({
            "success": False,
            "message": f"Error interno: {str(e)}"
        }, status=500)

# submodulo de equipos y herramientas eliminadas
@login_required
def equipment_tools_removed(request):
    context = user_data(request)
    module_id = 6
    subModule_id = 40
    request.session["last_module_id"] = module_id

    sidebar = get_sidebar(context, [1, module_id])
    access = get_module_user_permissions(context, subModule_id)
    for module in sidebar["data"]:
        for submodule in module.get("submodules", []):
            submodule["title"] = submodule["title"].strip() 
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]
    template = "equipments-and-tools/equipment_tools_removed.html" if context["access"]["read"] and check_user_access_to_module(request, module_id, subModule_id) else "error/access_denied.html"
    return render(request, template, context)


# Funcion para obtener los equipos y herramientas dadas de baja
@csrf_exempt
def get_equipment_tools_removed(request):

    response = {
        "status": "error",
        "message": "Sin procesar",
        "data": []
    }

    context = user_data(request)

    try:
        company_id = context["company"]["id"]

        bajas = list(
            Equipments_Tools_Detail.objects
            .select_related(
                "equipment_tool",
                "company",
                "user_modification",
            )
            .filter(
                company_id=company_id,
                is_deactivated=True,
                state = "BAJA"
            ).order_by("-id")
            .values(
                "id",
                "identifier",
                "state",
                "evidence1_image",
                "evidence2_image",
                "deactivation_reason",
                "deactivation_description",
                "deactivated_at",

                "user_modification__id", 
                "user_modification__first_name", 
                "user_modification__last_name", 
                "user_modification__username",

                "equipment_tool__equipment_name",
            )


        )


        for item in bajas:
            #obtener el ultimo detalle
            ultimo_detalle_responsiva = (
                Detail_Responsiva.objects.filter(details_equipment_tool_id=item["id"]).select_related(
                    "responsiva",
                    "responsiva__responsible_equipment"
                ).order_by("-id").first()
            ) 
            if (
                ultimo_detalle_responsiva
                and ultimo_detalle_responsiva.responsiva
                and ultimo_detalle_responsiva.responsiva.responsible_equipment
            ):          
                responsable = (
                    ultimo_detalle_responsiva
                    .responsiva
                    .responsible_equipment
                )

                nombre = (
                    f"{responsable.first_name} "
                    f"{responsable.last_name}"
                ).strip()

                item["last_responsible"] = (
                    nombre
                    if nombre
                    else responsable.username
                )



            else:
                item["last_responsible"] = ""

        # Catálogo de motivos
        motivos = dict(
            Equipments_Tools_Detail.DEACTIVATION_REASONS
        )

        for item in bajas: 
            # ESTADO
            item["state"] = item["state"] or ""

            # USUARIO QUE REALIZÓ LA BAJA 
            if item["user_modification__id"]: 
                nombre = ( 
                    f"{item['user_modification__first_name']} " 
                    f"{item['user_modification__last_name']}" 
                ).strip() 
                item["user_modification"] = ( 
                    nombre 
                    if nombre 
                    else item["user_modification__username"] 
                ) 
            else: 
                item["user_modification"] = ""

            # EVIDENCIA 1
            if item["evidence1_image"]:

                try:
                    item["evidence1_image"] = generate_presigned_url(
                        AWS_BUCKET_NAME,
                        str(item["evidence1_image"])
                    )
                except Exception as e:
                    item["evidence1_image"] = ""

            else:
                item["evidence1_image"] = ""

            # EVIDENCIA 2
            if item["evidence2_image"]:

                try:
                    item["evidence2_image"] = generate_presigned_url(
                        AWS_BUCKET_NAME,
                        str(item["evidence2_image"])
                    )
                except Exception as e:
                    item["evidence2_image"] = ""

            else:
                item["evidence2_image"] = ""

            # MOTIVO DE BAJA
            item["deactivation_reason"] = motivos.get(
                item["deactivation_reason"],
                item["deactivation_reason"] or ""
            )

            # DESCRIPCIÓN
            item["deactivation_description"] = (
                item["deactivation_description"] or ""
            )

            # FECHA DE BAJA 
            if item["deactivated_at"]: 
                item["deactivated_at_sort"] = ( 
                    item["deactivated_at"].strftime("%Y-%m-%d %H:%M:%S") 
                ) 
                item["deactivated_at"] = ( 
                    item["deactivated_at"].strftime("%d/%m/%Y %H:%M") 
                ) 
            else: 
                item["deactivated_at_sort"] = "" 
                item["deactivated_at"] = ""

        response["data"] = bajas
        response["status"] = "success"
        response["message"] = (
            "Equipos y herramientas dadas de baja "
            "cargados correctamente"
        )

    except Exception as e:
        response["status"] = "error"
        response["message"] = str(e)

    return JsonResponse(response)


@login_required
@csrf_exempt
def get_responsiva_details(request):
    response = {
        "success": False,
        "message": "Sin procesar",
        "data": []
    }

    context = user_data(request)
    company_id = context["company"]["id"]

    try:
        responsiva_id = request.GET.get("responsiva_id")

        print("GET RESPONSIVA DETAILS")
        print("Responsiva ID:", responsiva_id)
        print("Company ID:", company_id)

        if not responsiva_id:
            return JsonResponse({
                "success": False,
                "message": "No se recibió el ID de la responsiva.",
                "data": []
            }, status=400)

        # Buscar la responsiva perteneciente a la empresa
        responsiva = Equipment_Tools_Responsiva.objects.get(
            id=responsiva_id,
            company_id=company_id
        )

        equipment_tool = responsiva.equipment_name

        # Obtener únicamente los detalles que están asignados a esta responsiva
        detalles_asignados = Equipments_Tools_Detail.objects.filter(
            responsiva=responsiva,
            equipment_tool=equipment_tool,
            company_id=company_id,
            state="ASIGNADO",
            is_active=True,
            is_deactivated=False
        ).order_by("id")

        data = []

        for detalle in detalles_asignados:
            data.append({
                "id": detalle.id,
                "identifier": detalle.identifier,
            })

        print("Detalles encontrados:", len(data))

        for detalle in data:
            print(
                "Detalle:",
                detalle["id"],
                "| Identificador:",
                detalle["identifier"]
            )


        return JsonResponse({
            "success": True,
            "message": "Detalles obtenidos correctamente.",
            "data": data
        })

    except Equipment_Tools_Responsiva.DoesNotExist:
        return JsonResponse({
            "success": False,
            "message": "La responsiva no existe.",
            "data": []
        }, status=404)

    except Exception as e:
        logger.error(
            "Error en get_responsiva_details: %s",
            str(e)
        )

        print("ERROR get_responsiva_details:", str(e))

        return JsonResponse({
            "success": False,
            "message": "Error interno del servidor.",
            "data": []
        }, status=500)
