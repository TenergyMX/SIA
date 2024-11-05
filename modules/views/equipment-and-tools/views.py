from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
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
from django.utils.dateparse import parse_date
from decimal import Decimal
from django.conf import settings
import logging
import json, os
import base64
import time
from django.template.loader import get_template
from io import BytesIO
from xhtml2pdf import pisa
import logging


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


    if context["access"]["read"]:
        print("esto contiene el context antes del html")
        print(context)
        template = "equipments-and-tools/equipments_and_tools.html"
    else:
        template = "error/access_denied.html"
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

    
    if context["access"]["read"]:
        template = "equipments-and-tools/equipments_tools.html"
    else:
        template = "error/access_denied.html"
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

#permisos para agregar responsivas
    context["area"] = context["area"]["name"].lower()
    context["create"] = access["data"]["access"]["create"]
    print("esto contiene mi create de responsivas")
    print(context)
    context["tipo_user"] = context["role"]["name"].lower()


    tipo_user = context["role"]["name"].lower()
    print("este es el rol de usuario con el que cuenta")
    print(tipo_user)
    user_name = context["user"]["username"].lower()
    print("este es el nombre del usuario con el que cuenta")
    print(user_name)
    
    if context["access"]["read"]:
        template = "equipments-and-tools/responsiva.html"
    else:
        template = "error/access_denied.html"
    return render(request, template, context)

#-------------------------------------------------------------
# Tabla de datos para las categorias 
def get_equipments_tools_categorys(request):
    response = {"status": "error", "message": "Sin procesar"}
    context = user_data(request)
    isList = request.GET.get("isList", False)
    subModule_id = 29

    if isList:
        datos = list(Equipement_category.objects.values("id", "name", "short_name"))
    else:
        access = get_module_user_permissions(context, subModule_id)#contiene el crud
        access = access["data"]["access"]
        area = context["area"]["name"]
        editar = access["update"]
        eliminar = access["delete"]
        tipo_user = context["role"]["name"]
   

        datos = list(Equipement_category.objects.values())
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

   

    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            short_name = request.POST.get('short_name')
            description = request.POST.get('description')
            is_active = request.POST.get('is_active') == '1'

            if not name or not short_name:
                raise ValidationError("Nombre y nombre corto son obligatorios.")

            # Crear una nueva categoría
            with transaction.atomic():
                Equipement_category.objects.create(
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
def get_equipments_tools(request):
    response = {"status": "error", "message": "Sin procesar"}
    context = user_data(request)
    subModule_id = 30
    access = get_module_user_permissions(context, subModule_id)["data"]["access"]
    print("esto contiene mi access:", access)
    area = context["area"]["name"]
    tipo_user = context["role"]["name"]
    editar = access["update"]
    eliminar = access["delete"]
    agregar = access["create"]
    leer = access["read"]
    print("Permiso de crear, es el siguinete:", access["create"])
    print("Tipo de usuario:", tipo_user)
    print("Área del usuario:", area)

    try:
        equipments = list(Equipment_Tools.objects.select_related(
            'equipment_category', 'equipment_area', 'equipment_responsible', 'equipment_location'
        ).values(
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
            if access["create"] is True and not (tipo_user.lower() in ["administrador", "super usuario"] or area.lower() == "almacen"):

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
def get_equipment_categories(request):
    if request.method == 'GET':
        categories = Equipement_category.objects.filter(is_active=True).values('id', 'name')
        return JsonResponse({'data': list(categories)}, safe=False)
    return JsonResponse({'success': False, 'message': 'Método de solicitud no válido'})

# Funcion para obtener los nombres de los usuarios que ya han sido cargados para agregar un equipo 
@login_required
@csrf_exempt
def get_responsible_users(request):
    try:
        users = User.objects.values('id', 'username')  
        data = list(users)
        return JsonResponse({'data': data}, safe=False)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

# Funcion para obtener los nombres de las areas
@login_required
@csrf_exempt
def get_equipment_areas(request):
    try:
        areas = Area.objects.values('id', 'name')  
        data = list(areas)
        return JsonResponse({'data': data}, safe=False)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

# Funcion para obtener los nombres de las ubicaciones
@login_required
@csrf_exempt
def get_locations(request):
    try:
        ubicaciones = Equipmets_Tools_locations.objects.values('id', 'location_name')  
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
    subModule_id = 30
    access = get_module_user_permissions(context, subModule_id)  

    access = access["data"]["access"]
    area = context["area"]["name"]
    create = access["create"]
    tipo_user = context["role"]["name"]

    if request.method == 'POST':
        try:
            # Obtener datos del POST
            equipment_category_id = request.POST.get('equipment_category')
            equipment_name = request.POST.get('equipment_name')
            equipment_type = request.POST.get('equipment_type')
            equipment_brand = request.POST.get('equipment_brand')
            equipment_description = request.POST.get('equipment_description')
            cost = request.POST.get('cost')
            amount = request.POST.get('amount')
            equipment_area_id = request.POST.get('equipment_area')
            equipment_responsible_id = request.POST.get('responsible_equipment')
            equipment_location_id = request.POST.get('equipment_location')
            equipment_technical_sheet = request.FILES.get('equipment_technical_sheet')

            # Validar campos obligatorios
            if not equipment_category_id or not equipment_name or not equipment_responsible_id:
                return JsonResponse({'success': False, 'message': 'Faltan campos obligatorios.'}, status=400)

            # Verificar que el nombre del equipo no esté en uso
            if Equipment_Tools.objects.filter(equipment_name__iexact=equipment_name).exists():
                return JsonResponse({'success': False, 'message': 'El registro ya existe en la base de datos. Intenta con otro nombre.'}, status=400)

            # Obtener objetos relacionados
            category = get_object_or_404(Equipement_category, id=equipment_category_id)
            area = get_object_or_404(Area, id=equipment_area_id)
            responsible = get_object_or_404(User, id=equipment_responsible_id)
            location = get_object_or_404(Equipmets_Tools_locations, id=equipment_location_id)

            # Crear el nuevo equipo o herramienta
            Equipment_Tools.objects.create(
                equipment_category=category,
                equipment_name=equipment_name,
                equipment_type=equipment_type,
                equipment_brand=equipment_brand,
                equipment_description=equipment_description,
                cost=cost,
                amount=amount,
                equipment_area=area,
                equipment_responsible=responsible,
                equipment_location=location,
                equipment_technical_sheet=equipment_technical_sheet
            )

            return JsonResponse({'success': True, 'message': 'Equipo o herramienta agregado exitosamente.'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error interno del servidor: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'message': 'Método de solicitud no válido'}, status=405)

# Función para editar los registros de los equipos o herramientas
@login_required
@csrf_exempt
def edit_equipments_tools(request):
    if request.method == 'POST':
        _id = request.POST.get('id')
        equipment_category_id = request.POST.get('equipment_category')
        equipment_name = request.POST.get('equipment_name')
        equipment_type = request.POST.get('equipment_type')
        equipment_brand = request.POST.get('equipment_brand')
        equipment_description = request.POST.get('equipment_description')
        cost = request.POST.get('cost')
        amount = request.POST.get('amount')
        equipment_area = request.POST.get('equipment_area')
        equipment_responsible = request.POST.get('responsible_equipment')
        equipment_location = request.POST.get('equipment_location')
        equipment_technical_sheet = request.FILES.get('equipment_technical_sheet')

        # Validar que el nombre del equipo no esté en uso por otro equipo
        if Equipment_Tools.objects.exclude(pk=_id).filter(equipment_name__iexact=equipment_name).exists():
            return JsonResponse({'success': False, 'message': 'Este nombre ya se encuentra en la base de datos, ingresa otro diferente.'})

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
                equipment_tool.equipment_technical_sheet = equipment_technical_sheet

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
    print("esto contiene tu comtext:")
    print(context)
    module_id = 6
    subModule_id = 31
    request.session["last_module_id"] = module_id

    access = get_module_user_permissions(context, subModule_id)  
    access = access["data"]["access"]
    area = context["area"]["name"].lower()
    create = access["create"]

    tipo_user = context["role"]["name"].lower()
    print("este es el rol de usuario con el que cuenta")
    print(tipo_user)
    user_name = context["user"]["username"].lower()
    print("este es el nombre del usuario con el que cuenta")
    print(user_name)

    if request.method == 'POST':
        # Extraer datos del formulario
        equipment_name = request.POST.get('equipment_name')
        equipment_responsible_id = request.POST.get('equipment_responsible')
        amount = float(request.POST.get('amount', 0))
        fecha_entrega = request.POST.get('fecha_entrega')
        times_requested_responsiva = request.POST.get('times_requested_responsiva')
        comments = request.POST.get('comments', '')

        print(f"Fecha de entrega recibida: {fecha_entrega}") 

    
        print(f"Datos recibidos a traves del formulario: {request.POST}")  

        if not fecha_entrega or not isinstance(fecha_entrega, str):
            return JsonResponse({'success': False, 'message': 'Fecha de entrega no proporcionada.'})
        try:
            fecha_entrega_date = datetime.strptime(fecha_entrega, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Fecha de entrega inválida.'})

        # Obtener la fecha de inicio
        fecha_inicio_str = request.POST.get('fecha_inicio', '')
        fecha_inicio = parse_date(fecha_inicio_str) if fecha_inicio_str else datetime.now().date()

        print(f"Fecha de inicio: {fecha_inicio}, Fecha de entrega: {fecha_entrega_date}") 

        # Verificar que la fecha de entrega sea mayor a la fecha de inicio
        if fecha_entrega_date <= fecha_inicio:
            return JsonResponse({'success': False, 'message': 'La fecha de entrega debe ser mayor a la fecha de inicio.'})

        try:
            with transaction.atomic():
                # Obtener el equipo solicitado
                requested_amount = Equipment_Tools.objects.get(equipment_name=equipment_name)
                
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
                folder_path = f"docs/Equipments_tools/responsivas/{timestamp}/"  # Ruta de la firma

                # Crear la ruta completa
                full_path = os.path.join(settings.MEDIA_ROOT, folder_path)

                # Crea la carpeta si no existe
                if not os.path.exists(full_path):
                    os.makedirs(full_path)

                # Generar un nombre único para la firma
                new_name = f"signature_{timestamp}.png"
                fs = FileSystemStorage(location=settings.MEDIA_ROOT)
                fs.save(os.path.join(folder_path, new_name), signature_file)

                # Crear la nueva responsiva del equipo
                Equipment_Tools_Responsiva.objects.create(
                    equipment_name=requested_amount,
                    responsible_equipment=responsible,
                    amount=amount,
                    status_equipment='Solicitado',  # Establece el estado inicial
                    fecha_inicio=fecha_inicio,
                    fecha_entrega=fecha_entrega_date,
                    times_requested_responsiva=times_requested_responsiva,
                    signature_responsible=os.path.join(folder_path, new_name),  # Aquí se asigna el archivo de la firma
                    comments=comments,
                )


                # Actualizar la cantidad del equipo
                requested_amount.amount = available_amount - amount
                requested_amount.save()

                responsiva_instance = Equipment_Tools_Responsiva.objects.latest('id')  # Obtiene la última responsiva

               # Generar el PDF después de guardar la responsiva
                pdf_context = {
                    'responsiva': responsiva_instance,
                    'responsible_name': responsiva_instance.responsible_equipment.username,  # Nombre del responsable
                    'signature_responsible': request.build_absolute_uri(responsiva_instance.signature_responsible.url) if responsiva_instance.signature_responsible else None,  # URL absoluta de la firma
                }

                # Generar y guardar el PDF
                pdf_file = render_to_pdf('equipments-and-tools/responsiva/responsiva_equipments.html', pdf_context)
                pdf_folder_path = f"docs/Equipments_tools/pdfs/{timestamp}/"  # Ruta para el PDF
                
                # Crear la ruta completa para el PDF
                full_pdf_path = os.path.join(settings.MEDIA_ROOT, pdf_folder_path)

                # Crea la carpeta si no existe
                if not os.path.exists(full_pdf_path):
                    os.makedirs(full_pdf_path)

                # Guardar el PDF en el servidor
                pdf_file_name = f"responsiva_{timestamp}.pdf"
                with open(os.path.join(full_pdf_path, pdf_file_name), 'wb') as f:
                    f.write(pdf_file.getvalue())  # Guarda el PDF en el servidor

                # Retornar la URL del PDF (si decides usarla en el futuro)
                pdf_url = f"{request.scheme}://{request.get_host()}/{pdf_folder_path}{pdf_file_name}"
                # Actualiza el objeto de la responsiva para incluir la URL del PDF
                responsiva_instance.pdf_url = pdf_url

                # Retornar la respuesta JSON
                return JsonResponse({
                    'success': True,
                    'message': 'Responsiva agregada correctamente',
                    'pdf_url': pdf_url  
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
        area = context["area"]["name"].lower()
        tipo_user = context["role"]["name"].lower()

        if tipo_user in ['administrador', 'super usuario'] or area == 'almacen':
            users = User.objects.values('id', 'username')  
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
    editar = access["update"]
    create = access["create"]
    user_name = context["user"]["username"].lower()
    print("este es el usuario que ha iniciado sesion:", user_name)

    try:
        if tipo_user in ["administrador", "almacen", "super usuario"]:

            responsiva = list(Equipment_Tools_Responsiva.objects.select_related(
                'equipment_name', 'responsible_equipment'
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
    if request.method == 'POST':
        try:
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
            folder_path = f"docs/Equipments_tools/responsivas/{timestamp}/"
            full_path = os.path.join(settings.MEDIA_ROOT, folder_path)

            # Crear la ruta completa
            if not os.path.exists(full_path):
                os.makedirs(full_path)

            new_name = f"signature_almacen_{timestamp}.png"
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            fs.save(os.path.join(folder_path, new_name), signature_almacen_file)

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
                    responsiva.signature_almacen = os.path.join(folder_path, new_name)

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
                responsiva.save()

                # Calcular el tiempo requerido
                tiempo_requerido = (fecha_entrega_date - responsiva.fecha_inicio).days
                responsiva.times_requested_responsiva = tiempo_requerido
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
            'signature_responsible': request.build_absolute_uri(responsiva_instance.signature_responsible.url) if responsiva_instance.signature_responsible else None,
            'signature_almacen': request.build_absolute_uri(responsiva_instance.signature_almacen.url) if responsiva_instance.signature_almacen else None,
            'header_image': header_image_base64,
            'footer_image': footer_image_base64,
        }

        # Generar PDF
        pdf_file = render_to_pdf('equipments-and-tools/responsiva/responsiva_equipments.html', pdf_context)

        if pdf_file is None:
            logger.error("Error al generar el PDF.")
            return JsonResponse({'success': False, 'message': 'Error al generar el PDF.'})

        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        pdf_folder_path = f"docs/Equipments_tools/pdfs_responsiva/{timestamp}/"
        full_pdf_path = os.path.join(settings.MEDIA_ROOT, pdf_folder_path)

        # Crear la carpeta si no existe
        if not os.path.exists(full_pdf_path):
            os.makedirs(full_pdf_path)

        # Guardar el PDF en el servidor
        pdf_file_name = f"responsiva_{timestamp}.pdf"
        try:
            with open(os.path.join(full_pdf_path, pdf_file_name), 'wb') as f:
                f.write(pdf_file.getvalue())
            logger.info("PDF guardado en: %s", os.path.join(full_pdf_path, pdf_file_name))
        except Exception as e:
            logger.error("Error al guardar el PDF: %s", str(e))
            return JsonResponse({'success': False, 'message': 'Error al guardar el PDF.'})

        # URL del PDF
        pdf_url = f"{request.scheme}://{request.get_host()}/{pdf_folder_path}{pdf_file_name}"
        responsiva_instance.pdf_url = pdf_url  # Actualiza la responsiva si es necesario

        return JsonResponse({
            'success': True,
            'message': 'Responsiva generada correctamente',
            'pdf_url': pdf_url
        })

    except Equipment_Tools_Responsiva.DoesNotExist:
        logger.error("Responsiva no encontrada. ")
        return JsonResponse({'success': False, 'message': 'Responsiva no encontrada.'})
