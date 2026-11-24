from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect, HttpResponse
from django.db.models import F, Q, Value, Max, Sum, CharField, BooleanField
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from django.template.loader import get_template
from modules.models import *
from users.models import *
from datetime import datetime, timedelta, date
import json, os
import requests
import random
import calendar
import glob
from xhtml2pdf import pisa
# py personalizado
from modules.utils import *

from django.utils.timezone import now
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.shortcuts import render, get_object_or_404
from django.core.files.uploadedfile import InMemoryUploadedFile
# import qrcode

from django.views.decorators.csrf import csrf_exempt
import subprocess

from django.core.serializers.json import DjangoJSONEncoder
from django.core.exceptions import ObjectDoesNotExist

from modules.templates.pdf.weasy import WeasyPDF

from weasyprint import HTML

from datetime import datetime, time
from django.views.decorators.http import require_GET
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils import get_column_letter
from django.db import IntegrityError

from django.http import JsonResponse, Http404
from django.utils.dateparse import parse_date

# dotenv_path = join(dirname(dirname(dirname(_file_))), 'awsCred.env')
# load_dotenv(dotenv_path)
AWS_BUCKET_NAME=str(os.environ.get('AWS_BUCKET_NAME'))
bucket_name=AWS_BUCKET_NAME

ALLOWED_FILE_EXTENSIONS = ['.jpg', '.jpeg', '.png']
# TODO --------------- [ VIEWS ] ----------
@login_required
def infrastructure_category_view(request):
    context = user_data(request)
    module_id = 4
    subModule_id = 23
    request.session["last_module_id"] = module_id
    
    access = get_module_user_permissions(context, subModule_id)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]
    
    template = "infrastructure/infrastructure-category.html" if context["access"]["read"] and check_user_access_to_module(request, module_id, subModule_id) else "error/access_denied.html"
    return render(request, template , context)

@login_required
def infrastructure_item_view(request):
    context = user_data(request)
    module_id = 4
    subModule_id = 24
    request.session["last_module_id"] = module_id

    access = get_module_user_permissions(context, subModule_id)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]
    
    template = "infrastructure/infrastructure-items.html" if context["access"]["read"] and check_user_access_to_module(request, module_id, subModule_id) else "error/access_denied.html"
    return render(request, template , context)

@login_required
def infrastructure_maintenance_view(request):
    context = user_data(request)
    module_id = 4
    subModule_id = 25
    request.session["last_module_id"] = module_id

    access = get_module_user_permissions(context, subModule_id)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]
    
    template = "infrastructure/maintenance.html" if context["access"]["read"] and check_user_access_to_module(request, module_id, subModule_id) else "error/access_denied.html"
    return render(request, template , context)


# TODO --------------- [ REQUEST ] ----------

def get_infrastructure_categorys(request):
    response = { "status"   : "error", "message": "Sin procesar" }
    context = user_data(request)
    dt = request.GET
    subModule_id = 23
    isList = dt.get("isList", False)
    company_id = context["company"]["id"]
    datos = Infrastructure_Category.objects.filter(empresa__id=company_id, is_active=True).distinct().values()

    if isList:
        datos = datos.values("id", "name", "short_name")
    else:
        access = get_module_user_permissions(context, subModule_id)
        access = access["data"]["access"]
        for item in datos:
            item["btn_action"] = ""
            if access["update"]:
                item["btn_action"] += "<button type='button' name='update' class='btn btn-icon btn-sm btn-primary-light' data-infrastructure-category='update-item' aria-label='info'>" \
                    "<i class=\"fa-solid fa-pen\"></i>" \
                "</button>\n"
            if access["delete"]:
                item["btn_action"] += "<button type='button' name='delete' class='btn btn-icon btn-sm btn-danger-light' data-infrastructure-category='delete-item' aria-label='delete'>" \
                    "<i class='fa-solid fa-trash'></i>" \
                "</button>"

    response["data"] = list(datos)
    response["status"] = "success"
    response["message"] = "Datos cargados exitosamente"
    return JsonResponse(response)


def add_infrastructure_item(request):
    response = { "status": "error", "message": "Sin procesar" }
    context = user_data(request)
    dt = request.POST
    
    company_id = context["company"]["id"]

    print("Contexto del usuario:", context)
    print("Datos recibidos del formulario:", dt)

    category_id = dt.get("category_id", None)
    location_id = dt.get("item_location", None) 
    area_id = dt.get("item_area") or None
    responsible_id = dt.get("responsible_item")or None

    name = dt.get("name", "").strip()
    item_type = dt.get("type", "").strip()
    item_brand = dt.get("equipment_brand", "").strip()
    comments = dt.get("comments", "").strip()

    description = dt.get("description", "").strip()
    quantity = dt.get("quantity") or 1
    cost = dt.get("cost") or 0
    start_date = dt.get("start_date") or None

   # Validar categoría
    if not category_id:
        response["status"] = "warning"
        response["message"] = "Seleccione una categoría válida"
        return JsonResponse(response)

    if not name:
        response["status"] = "warning"
        response["message"] = "Ingrese el nombre del activo"
        return JsonResponse(response)

    # Validar que no exista otro activo con el mismo nombre
    if Infrastructure_Item.objects.filter(
        name__iexact=name,
        company_id=company_id
    ).exists():
        response["status"] = "warning"
        response["message"] = (
            "Ya existe un registro con ese nombre en la empresa"
        )
        return JsonResponse(response)

    try:
        category = Infrastructure_Category.objects.get(
            id=category_id
        )

        obj = Infrastructure_Item(
            company_id=company_id,
            category=category,
            name=name,
            description=description,
            quantity=quantity,
            cost=cost,
            start_date=start_date,
            location_id=location_id,
            is_active=True,
            item_type=item_type or "Regular",
            item_brand=item_brand or "Regular",
            item_area_id=area_id,
            item_responsible_id=responsible_id,
            comments=comments
        )

        obj.save()
        _id = obj.id

        # Guardar archivos en S3 si existen
        if 'technical_sheet' in request.FILES and request.FILES['technical_sheet']:
            load_file = request.FILES.get('technical_sheet')
            folder_path = f"docs/{company_id}/infrastructure_items/{_id}/technical_sheet/"
            file_name, extension = os.path.splitext(load_file.name)
            new_name = f"technical_sheet_{_id}{extension}"
            s3_path = folder_path + new_name

            upload_to_s3(load_file, bucket_name, s3_path)
            obj.technical_sheet = s3_path

        if 'invoice' in request.FILES and request.FILES['invoice']:
            load_file = request.FILES.get('invoice')
            folder_path = f"docs/{company_id}/infrastructure_items/{_id}/invoice/"
            file_name, extension = os.path.splitext(load_file.name)
            new_name = f"invoice_{_id}{extension}"
            s3_path = folder_path + new_name

            upload_to_s3(load_file, bucket_name, s3_path)
            obj.invoice = s3_path

        if 'image' in request.FILES and request.FILES['image']:
            load_file = request.FILES.get('image')
            folder_path = f"docs/{company_id}/infrastructure_items/{_id}/image/"
            file_name, extension = os.path.splitext(load_file.name)
            new_name = f"image_{_id}{extension}"
            s3_path = folder_path + new_name

            upload_to_s3(load_file, bucket_name, s3_path)
            obj.image = s3_path

        obj.save()

        generate_identificador(_id,company_id, quantity)

        response["id"] = obj.id
        response["status"] = "success"
        response["message"] = "Registro guardado exitosamente"
    except Exception as e:
        print("Error al guardar el Infrastructure_Item:", str(e))
        response["status"] = "error"
        response["message"] = str(e)

    return JsonResponse(response)


def generate_identificador(item_id, company_id, quantity):
    try:
        item = Infrastructure_Item.objects.get(id=item_id)
        company = Company.objects.get(id=company_id)

        
        company_code = company.name.replace(' ', '').upper()[:3]
        prefix = f"{company_code}-{item_id}-"

        # Buscar el último número usado con ese prefijo
        # TEN-SIL
        # TEN-SIL
        last_detail = (
            InfrastructureItemDetail.objects
            .filter(identifier__startswith=prefix)
            .order_by("-identifier")
            .first()
        )

        if last_detail:
            match = re.search(rf"{prefix}(\d+)", last_detail.identifier)
            last_number = int(match.group(1)) if match else 0
        else:
            last_number = 0

        for i in range(1, int(quantity) + 1):
            number = last_number + i
            identifier = f"{prefix}{str(number)}"

            InfrastructureItemDetail.objects.create(
                item=item,
                company=company,
                name=item.name,
                identifier=identifier, 
            )
            print(f"Identificador generado y guardado: {identifier}")

    except Infrastructure_Item.DoesNotExist:
        print("Error: Infrastructure_Item no encontrado.")
    except Company.DoesNotExist:
        print("Error: Company no encontrado.")
    except Exception as e:
        print(f"Error al generar identificadores: {str(e)}")


def get_infrastructure_items(request):
    response = {"success": False}
    context = user_data(request)
    dt = request.GET
    subModule_id = 24
    company_id = context["company"]["id"]
    isList = dt.get("isList", False)
    category_id = dt.get("category_id", 1)
    category_name = dt.get("category_name", "Infraestructura de Seguridad")
    responsible_id = dt.get("responsible_id")

    datos = Infrastructure_Item.objects.filter(company_id = company_id, is_active = True ).values(
        "id",
        "company_id", 
        "company__name",
        "category_id", 
        "category__name",

        "name", 
        "item_type",
        "item_brand",
        "description", 
        "quantity",
        "cost",
        "start_date",

        "item_area_id",
        "item_area__name",
        "item_responsible_id",
        "item_responsible__username",
        "item_responsible__first_name",
        "item_responsible__last_name",

        "location_id", 
        "location__name",
        "comments",

        "technical_sheet",
        "invoice", 
        "image",

        "is_active", 
        "created_at",
        "updated_at",
    )

    if isList:
        datos = datos.filter(is_active = True).values("id", "category_id", "category__name", "name")
        if category_id:
            datos = datos.filter(category_id = category_id)
    else:
        access = get_module_user_permissions(context, subModule_id)
        access = access["data"]["access"]
        for item in datos:
            item["row_id"] = item["id"] 

            nombre_responsable = " ".join(
                filter(
                    None,
                    [
                        item.pop("item_responsible__first_name"),
                        item.pop("item_responsible__last_name"),
                    ]
                )
            )

            username = item.pop("item_responsible__username")

            item["responsible_name"] = (
                nombre_responsable or username or ""
            )

            if item["technical_sheet"]:
                item["technical_sheet"] = generate_presigned_url(bucket_name, item["technical_sheet"])  
            else:
                item["technical_sheet"] = None
            if item["invoice"]:
                item["invoice"] = generate_presigned_url(bucket_name, item["invoice"])

            if item["image"]:
                item["image"] = generate_presigned_url(
                    bucket_name,
                    item["image"]
                )
            else:
                item["image"] = None

            # Desglose
            item["btn_identifiers"] = (
                f"<button type='button' "
                f"class='btn btn-icon btn-sm btn-success-light' "
                f"data-infrastructure-item='view-identifiers' "
                f"data-id='{item['id']}' "
                f"aria-label='Ver desglose'>"
                f"<i class='fa-solid fa-list'></i>"
                f"</button>"
            )

            item["btn_action"] = ""            
            if access["update"]:
                item["btn_action"] += "<button type='button' name='update' class='btn btn-icon btn-sm btn-primary-light' data-infrastructure-item='update-item' aria-label='info'>" \
                    "<i class=\"fa-solid fa-pen\"></i>" \
                "</button>\n"
            if access["delete"]:
                item["btn_action"] += "<button type='button' name='delete' class='btn btn-icon btn-sm btn-danger-light' data-infrastructure-item='delete-item' aria-label='delete'>" \
                    "<i class='fa-solid fa-trash'></i>" \
                "</button>\n"

    response["data"] = list(datos)
    response["status"] = "success"
    return JsonResponse(response)


def update_infrastructure_item(request):
    response = {"status": "error", "message": "Sin procesar"}
    context = user_data(request)
    dt = request.POST
    company_id = context["company"]["id"]
    category_id = dt.get("category_id")
    is_active = dt.get("is_active", True)
    item_id = dt.get("id")

    if not category_id:
        response["status"] = "warning"
        response["message"] = "Ingrese una categoría válida"
        return JsonResponse(response)

    try:
        with transaction.atomic():
            # Obtener el objeto principal
            obj = Infrastructure_Item.objects.get(id=item_id)
            old_quantity = obj.quantity
            requested_quantity = int(dt.get("quantity")or 0)

            # Validar que no se disminuya la cantidad
            if requested_quantity < old_quantity:
                response["status"] = "warning"
                response["message"] = (
                    f"No puedes disminuir la cantidad de {old_quantity} "
                    f"a {requested_quantity}. "
                    "Para reducir la cantidad debes desactivar los detalles correspondientes."
                )
                return JsonResponse(response)

            # Actualizar campos
            obj.category_id = category_id
            obj.name = dt.get("name")
            obj.quantity = requested_quantity


            obj.description = dt.get("description")

            obj.is_active = is_active

            obj.start_date = dt.get("start_date") or None
            obj.cost = dt.get("cost") or 0

            obj.item_type = dt.get("type") or "Regular"
            obj.item_brand = dt.get("equipment_brand") or "Regular"

            obj.item_area_id = dt.get("item_area") or None
            obj.item_responsible_id = dt.get("responsible_item") or None

            obj.location_id = dt.get("item_location") or None
            obj.comments = dt.get("comments") or None


            obj.time_quantity = dt.get("time_quantity")
            obj.time_unit = dt.get("time_unit")

            if 'technical_sheet' in request.FILES and request.FILES['technical_sheet']:
                load_file = request.FILES.get('technical_sheet')
                folder_path = f"docs/{company_id}/infrastructure_items/{obj.id}/technical_sheet/"
                file_name, extension = os.path.splitext(load_file.name)
                new_name = f"technical_sheet_{obj.id}{extension}"
                s3_path = folder_path + new_name

                print(f"Subiendo technical_sheet a: {s3_path}")
                upload_to_s3(load_file, bucket_name, s3_path)
                obj.technical_sheet = s3_path
                print("Technical sheet subida exitosamente.")

            if 'invoice' in request.FILES and request.FILES['invoice']:
                load_file = request.FILES.get('invoice')
                folder_path = f"docs/{company_id}/infrastructure_items/{obj.id}/invoice/"
                file_name, extension = os.path.splitext(load_file.name)
                new_name = f"invoice_{obj.id}{extension}"
                s3_path = folder_path + new_name

                print(f"Subiendo invoice a: {s3_path}")
                upload_to_s3(load_file, bucket_name, s3_path)
                obj.invoice = s3_path
                print("Invoice subida exitosamente.")

            if 'image' in request.FILES and request.FILES['image']:
                load_file = request.FILES.get('image')
                folder_path = f"docs/{company_id}/infrastructure_items/{obj.id}/image/"
                file_name, extension = os.path.splitext(load_file.name)
                new_name = f"image_{obj.id}{extension}"
                s3_path = folder_path + new_name

                print(f"Subiendo image a: {s3_path}")
                upload_to_s3(load_file, bucket_name, s3_path)
                obj.image = s3_path
                print("Image subida exitosamente.")

            obj.save()

            new_name = obj.id
            new_quantity = obj.quantity

            # Manejo de detalles
            current_count = InfrastructureItemDetail.objects.filter(item=obj, is_active=True).count()

            company = Company.objects.get(id=company_id)

            if new_quantity > current_count:
                # Agregar los que faltan
                company_code = company.name.replace(' ', '').upper()[:3]
                prefix = f"{company_code}-{obj.id}-"

                existing_identifiers = (
                    InfrastructureItemDetail.objects
                    .filter(identifier__startswith=prefix)
                    .values_list("identifier", flat=True)
                )

                existing_numbers = []
                for ident in existing_identifiers:
                    try:
                        existing_numbers.append(int(ident.split("-")[-1]))
                    except ValueError:
                        pass

                next_number = max(existing_numbers, default=0) + 1

                for i in range(new_quantity - current_count):
                    identifier = f"{prefix}{str(next_number + i)}"
                    InfrastructureItemDetail.objects.create(
                        item=obj,
                        company_id=company_id,
                        name=obj.id,
                        identifier=identifier
                    )

        response["id"] = obj.id
        response["status"] = "success"
        response["message"] = "Registro actualizado exitosamente"

    except Infrastructure_Item.DoesNotExist:
        response["status"] = "error"
        response["message"] = "No existe ningún registro con ese id"
    except Exception as e:
        response["status"] = "error"
        response["message"] = str(e)

    return JsonResponse(response)


def delete_infrastructure_item(request):
    response = {"status": "error", "message": "Sin procesar"}
    context = user_data(request)
    dt = request.POST
    item_id = dt.get("id")

    if not item_id:
        response["error"] = {"message": "Proporcione un id valido"}
        response["message"] = "Proporcione un id valido"
        return JsonResponse(response, status=400)

    try:
        obj = Infrastructure_Item.objects.get(id = item_id)
    except Infrastructure_Item.DoesNotExist:
        response["error"] = {"message": "El objeto no existe"}
        response["message"] = "El objeto no existe"
        return JsonResponse(response, status=404)

    # validar si el registro tiene desgloses activos 
    has_details = InfrastructureItemDetail.objects.filter(
        item=obj,
        is_active=True
    ).exists()

    if has_details:
        return JsonResponse({
            'success': False,
            'error': {
                "message": (
                    "No se puede desactivar este registro porque "
                    "tiene registros activos en su desglose. "
                    "Desactiva cada uno antes de desactivar el activo principal."
                )
            }
        })

    # si no tiene desglose desactivar
    obj.is_active = False
    obj.save(update_fields=['is_active'])

    return JsonResponse({
        'success': True, 
        'message': 'Equipo desactivado correctamente'
    })



def add_infrastructure_category(request):
    response = { "status": "error", "message": "Sin procesar" }
    context = user_data(request)
    dt = request.POST
    company_id = context["company"]["id"]
    is_active = dt.get("is_active", True)
    
    # Validar que no exista ni el nombre ni el nombre corto de manera insensible a mayúsculas y minúsculas
    existing_category = Infrastructure_Category.objects.filter(
        Q(name__iexact=dt.get("name"), empresa__id=company_id) |
        Q(short_name__iexact=dt.get("short_name"), empresa__id=company_id)
    ).first()

    
    if existing_category:
        response["message"] = "El nombre o nombre corto ya para esta empresa."
        return JsonResponse(response)
    
    try:
        obj = Infrastructure_Category(
            empresa_id=company_id,
            name=dt.get("name"),
            short_name=dt.get("short_name"),
            description=dt.get("description"),
            is_active=is_active,
        )
        obj.save()
        
        response["id"] = obj.id
        response["status"] = "success"
        response["message"] = "Registro guardado exitosamente"
    except Exception as e:
        response["message"] = str(e)

    return JsonResponse(response)

def update_infrastructure_category(request):
    response = {"status": "error", "message": "Sin procesar"}
    context = user_data(request)
    dt = request.POST
    company_id = context["company"]["id"]
    category_id = dt.get("category_id", None)
    is_active = dt.get("is_active", True)
    id = dt.get("id")

    try:
        # Obtener el objeto de infraestructura existente
        
        obj = Infrastructure_Category.objects.get(id = id)
        
        existing_category = Infrastructure_Category.objects.filter(
            Q(name__iexact=dt.get("name"), empresa__id=company_id) |
            Q(short_name__iexact=dt.get("short_name"), empresa__id=company_id)
        ).exclude(id=id).first()

        if existing_category:
            response["message"] = "El nombre o el nombre corto ya existen en esta empresa."
            return JsonResponse(response)
        
        # Actualizar los campos del objeto
        obj.category_id = category_id
        obj.name = dt.get("name")
        obj.short_name = dt.get("short_name")  
        obj.quantity = dt.get("quantity")
        obj.description = dt.get("description")
        obj.is_active = is_active
        obj.start_date = dt.get("start_date")
        obj.time_quantity = dt.get("time_quantity")
        obj.time_unit = dt.get("time_unit")
        obj.save()

        response["id"] = obj.id
        response["status"] = "success"
        response["message"] = "Registro actualizado exitosamente"
    except Infrastructure_Item.DoesNotExist:
        response["success"] = False
        response["error"] = {"message": f"No existe ningún registro con ese id"}
        return JsonResponse(response)
    except Exception as e:
        response["status"] = "error"
        response["message"] = str(e)

    return JsonResponse(response)


def delete_infrastructure_category(request):
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Método de solicitud inválido'
        }, status=405)
    
    _id = request.POST.get('id')

    if not _id:
        return JsonResponse({
            'success': False,
            'message': 'No se proporciono el Id de la categoría'
        }, status=400)

    try: 
        category = Infrastructure_Category.objects.get(id=_id)

    except Infrastructure_Category.DoesNotExist: 
        return JsonResponse({
            'success': False,
            'message': 'La categoría no existe.'
        }, status=404)

    #validar que la categoria tiene una infraestructura registrada.
    has_infraestructure = Infrastructure_Item.objects.filter(
        category=category,
        is_active=True
    ).exists()

    if has_infraestructure:
        return JsonResponse({
            'success': False,
            'error':{
                'message': ( 
                    'No se puede eliminar esta categoría porque tiene infraestructura registrada'
                )
            }
        })


    # Desactivar la categoría
    category.is_active = False
    category.save(update_fields=['is_active'])

    return JsonResponse({
        'success': True,
        'message': 'Categoría eliminada correctamente.'
    })


def check_qr_infraestructure(request, itemId):
    try:
        infraestructure = get_object_or_404(InfrastructureItemDetail, id=itemId)

        if infraestructure.qr_info_infrastructure:
            qr_url_info = generate_presigned_url(AWS_BUCKET_NAME, str(infraestructure.qr_info_infrastructure))
            return JsonResponse({'status': 'success', 'qr_url_info': qr_url_info})
        else:
            return JsonResponse({'status': 'error', 'message': 'QR no generado'})
    except InfrastructureItemDetail.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Equipo no encontrado'}, status=404)

#función para generar el código qr
def generate_qr_infraestructure(request, qr_type, itemId):
    print("entramos a la funcion para descargar un qr")
    context = user_data(request)
    company_id = context["company"]["id"]
    infraestructure = get_object_or_404(InfrastructureItemDetail, id=itemId)

    print(f"Generando QR para el equipo con ID: {itemId}")

    
    if qr_type == "info" and infraestructure.qr_info_infrastructure:
        qr_url_info = generate_presigned_url(AWS_BUCKET_NAME, str(infraestructure.qr_info_infrastructure))
        print(f"QR ya generado. URL: {qr_url_info}")

        return JsonResponse({'status': 'generados', 'qr_url_info': qr_url_info})

    # Contenido del QR
    domain = request.build_absolute_uri('/')[:-1]  # Obtiene el dominio dinámicamente
    if qr_type == 'info':
        qr_content = f"{domain}/infrastructure/{itemId}/"
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid QR type'}, status=400)

    # Generar el QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_content)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')

    # Guardar la imagen en un buffer
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    # Definir la ruta del archivo en S3
    s3Path = f'docs/{company_id}/infrastructure/{itemId}/qr/'
    s3Name = f"qr_info{itemId}.png"
    full_s3_path = s3Path + s3Name

    print(f"Subiendo el QR a S3 en la ruta: {full_s3_path}")

    # Asignar la ruta al modelo
    infraestructure.qr_info_infrastructure = full_s3_path

    # Crear un InMemoryUploadedFile
    img_file = InMemoryUploadedFile(
        buffer, None, s3Name, 'image/png', buffer.getbuffer().nbytes, None
    )

    # Subir a S3
    upload_to_s3(img_file, AWS_BUCKET_NAME, full_s3_path)
    infraestructure.save()  # Guardar cambios en la base de datos

    print(f"QR guardado en la base de datos con URL: {full_s3_path}")

    # Generar la URL 
    qr_url = generate_presigned_url(AWS_BUCKET_NAME, full_s3_path)
    print(f"Generando URL del QR en S3: {qr_url}")

    return JsonResponse({'status': 'success', 'qr_url': qr_url})


#funcion para descargar el qr
def descargar_qr_infraestructure(request):
    id_infraestructure = request.GET.get("itemId")
    print("este es el id de la infraestructura:", id_infraestructure)
    tipo_qr = request.GET.get("type")  

    infrastructure = InfrastructureItemDetail.objects.filter(id=id_infraestructure).first()
    if infrastructure:
        if tipo_qr == "info":
            if not infrastructure.qr_info_infrastructure:
                return JsonResponse({'error': 'QR no generado'}, status=404)

            url_infraestrucuture = infrastructure.qr_info_infrastructure  
        else:
            return JsonResponse({'error': 'Tipo de QR no válido'}, status=400)

        url_s3 = generate_presigned_url(AWS_BUCKET_NAME, str(url_infraestrucuture))
        return JsonResponse({'url_infraestructure': url_s3})
    else:
        return JsonResponse({'error': 'infraestructure no encontrado'}, status=404)


#funcion para eliminar el qr
def delete_qr_infraestructure(request, qr_type, itemId):
    infrastructure = get_object_or_404(InfrastructureItemDetail, id=itemId)
    url = ""
    if qr_type == 'info' and infrastructure.qr_info_infrastructure:
        url = str(infrastructure.qr_info_infrastructure)
        infrastructure.qr_info_infrastructure.delete()
    elif qr_type == 'access' and infrastructure.qr_access:
        url = str(infrastructure.qr_access)
        infrastructure.qr_access.delete()
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid QR type or QR does not exist'}, status=400)
    
    delete_s3_object(AWS_BUCKET_NAME, url)
    return JsonResponse({'status':'success'})


# Funcion para obtener los nombres de las ubicaciones
def get_items_locations(request):
    try:
        context = user_data(request)
        company_id = context["company"]["id"]

        if not company_id:
            return JsonResponse({'success': False, 'message': 'No se encontró la empresa asociada al usuario'}, status=400)

        ubicaciones = Items_locations.objects.filter(
            company_id=company_id
        ).values('id', 'name')  
        data = list(ubicaciones)
        return JsonResponse({'data': data}, safe=False)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


# Funcion para obtener los nombres de las empresas
def get_company_items(request):
    try:
        empresas = Company.objects.values('id', 'name')  
        data = list(empresas)
        return JsonResponse({'data': data}, safe=False)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


# Función para agregar una nueva ubicación
def add_item_location(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            if not name:
                return JsonResponse({'success': False, 'message': 'Los campos son requeridos.'}, status=400)
            #Obtener la empresa del usuario 
            context = user_data(request) 
            company_id = context["company"]["id"] 

            company = get_object_or_404(
                Company,
                id=company_id,
            )

            # Verificar que no exista una ubicación con el mismo nombre
            if Items_locations.objects.filter(name__iexact=name, company=company).exists():
                return JsonResponse({'success': False, 'message': 'Ya existe una ubicación con ese nombre para esta empresa.'}, status=400)

            # Crear la nueva ubicación
            new_location = Items_locations.objects.create(
                name=name,
                company=company,
                status=True
            )

            # Retornar la nueva ubicación para actualizar el select
            return JsonResponse({'success': True, 'message': 'Ubicación agregada exitosamente.', 'new_location': {
                'id': new_location.id,
                'name': new_location.name
            }})

        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Error interno del servidor.'}, status=500)
    return JsonResponse({'success': False, 'message': 'Método de solicitud no válido.'}, status=405)


def get_infrastructure_item_details(request):
    item_id = request.GET.get("id")
    data = []

    if item_id:
        registros = InfrastructureItemDetail.objects.filter(item_id=item_id).values(
            "id", 
            "identifier", 

            "assignment_type",

            "responsible__id",  
            "responsible__first_name",  
            "responsible__last_name",  

            "area_responsable__id",
            "area_responsable__name",

            "responsible_text",


            "assignment_date",
            "photo_infraestructure",
            "is_deactivated",
            "is_active",
            "location_item",
            "location_item__name",
        )
        for r in registros:

            nombre_usuario = (
                f"{r['responsible__first_name'] or ''} "
                f"{r['responsible__last_name'] or ''}"
            ).strip()

            # TIPO DE ASIGNACIÓN
            tipo = r["assignment_type"]

            if tipo == "usuario":
                responsable = nombre_usuario or "Sin asignar"

            elif tipo == "area":
                responsable = r["area_responsable__name"] or "Sin asignar"

            elif tipo == "comunitario":
                responsable = "Activo comunitario"

            else:
                responsable = "Sin asignar"
            # FOTOGRAGIA
            fotografia = None
            if r["photo_infraestructure"]:
                tUrl = generate_presigned_url( AWS_BUCKET_NAME, str(r["photo_infraestructure"]))
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

            
            # UBICACIÓN
            tiene_ubicacion = bool(r["location_item"])

            location_id = r["location_item"]
            location_name = r["location_item__name"] or "" if tiene_ubicacion else ""

            data.append({
                "id": r["id"],
                "identificador": r["identifier"],
                # Información de asignación
                "responsable": responsable,
                "assignment_type": tipo,

                "responsable_id": r["responsible__id"],
                "area_responsable_id": r["area_responsable__id"],
                "area_responsable": r["area_responsable__name"] or "",
                "responsible_text": r["responsible_text"] or "",

                "tiene_responsable": bool(
                    r["responsible__id"]
                    or r["area_responsable__id"]
                    or tipo == "comunitario"
                ),

                "fecha_asignacion": r["assignment_date"].strftime('%Y-%m-%d') if r["assignment_date"] else "",
              
                "fotografia": fotografia,
                "is_deactivated": r["is_deactivated"],
                "is_active": r["is_active"],

                "tiene_ubicacion": tiene_ubicacion,
                "location_item_id": location_id,
                "location_item": location_name,
            })

    return JsonResponse({"success": True, "data": data})


def obtner_usuarios(request):
    try:
        context = user_data(request)
        company_id = context["company"]["id"]

        if not company_id:
            return JsonResponse({'success': False, 'message': 'No se encontró la empresa asociada al usuario'}, status=400)

        tipo_user = context["role"]["name"].lower()

        if tipo_user in ['administrador', 'super usuario']:
            users = User.objects.filter(
                id__in=User_Access.objects.filter(company_id=company_id).values('user_id')
            ).distinct().values('id', 'first_name', 'last_name')
        else:
            users = User.objects.filter(id=request.user.id).values('id', 'first_name', 'last_name')

        # Construir la lista con nombre completo
        data = [{'id': u['id'], 'name': f"{u['first_name']} {u['last_name']}".strip()} for u in users]

        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)





@csrf_exempt
def asignar_responsable(request):

    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "Método no permitido."
        })

    detalle_id = request.POST.get("id")
    tipo = request.POST.get("tipo_responsable")

    responsable_id = request.POST.get("responsable")
    area_id = request.POST.get("area_responsable")

    try:
        detalle = InfrastructureItemDetail.objects.get(id=detalle_id)

        if tipo == "usuario":

            if not responsable_id:
                return JsonResponse({
                    "success": False,
                    "message": "Seleccione un usuario."
                })

            detalle.responsible_id = responsable_id
            detalle.area_responsable = None
            detalle.responsible_text = None

            tipo_guardado = "usuario"


        elif tipo == "area":

            if not area_id:
                return JsonResponse({
                    "success": False,
                    "message": "Seleccione un área."
                })

            detalle.responsible = None
            detalle.area_responsable_id = area_id
            detalle.responsible_text = None

            tipo_guardado = "area"


        elif tipo == "activo_comunitario":

            detalle.responsible = None
            detalle.area_responsable = None
            detalle.responsible_text = "Activo comunitario"
            tipo_guardado = "comunitario"

        else:
            return JsonResponse({
                "success": False,
                "message": "El tipo de asignación no es válido."
            })

        detalle.assignment_type = tipo_guardado
        detalle.assignment_date = timezone.now().date()

        detalle.save()

        return JsonResponse({
            "success": True,
            "message": "Asignación realizada correctamente."
        })

    except InfrastructureItemDetail.DoesNotExist:
        return JsonResponse({
            "success": False,
            "message": "No se encontró el registro."
        })

    except (ValueError, TypeError, IntegrityError):
        return JsonResponse({
            "success": False,
            "message": "El usuario o área seleccionados no son válidos."
        })
    
# Vista para obtener los  registros de identificadores
@login_required
def get_identifier(request):
    try:
        context = user_data(request)
        company_id = context["company"]["id"]  

        if not company_id:
            return JsonResponse({'success': False, 'message': 'No se encontró la empresa asociada al usuario'}, status=400)
    # Obtener los registros
        identifier = InfrastructureItemDetail.objects.filter(
            company_id=company_id, is_active=True
        ).values('id', 'identifier') 
        data = list(identifier)
        print("esta es la lista de identificadores de la empresa:", identifier)
        return JsonResponse({'data': data}, safe=False)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


# Funcion para obtener los nombres de los proveedores
@login_required
@csrf_exempt
def get_items_providers(request):
    try:
        context = user_data(request)
        company_id = context["company"]["id"]
        company_name = context["company"]["name"]

        if not company_id:
            return JsonResponse({'success': False, 'message': 'No se encontró la empresa asociada al usuario'}, status=400)
        
        provedores = Provider.objects.filter(company_id=company_id).distinct().values('id', 'name')  
        data = list(provedores)
        print("esta es lalista de proveedores:", data)
        return JsonResponse({'data': data}, safe=False)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


def get_maintenance_actions(request):
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    directorio_json = os.path.join(directorio_actual, '..', '..', 'static', 'assets', 'json', 'items-maintenance.json')

    try:
        with open(directorio_json, 'r') as file:
            json_data = json.load(file)

        opciones = []
        # Organizar los datos por tipo de mantenimiento
        for mantenimiento in json_data['data']:
            opciones.append({
                'id': mantenimiento['id'],
                'tipo': mantenimiento['tipo'],
                'items': mantenimiento['items']
            })

        return JsonResponse({'data': opciones}, safe=False)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)




@csrf_exempt
def add_new_maintenance_option(request):
    if request.method == 'POST':
        try:
            
            # Cargar datos del cuerpo del request
            data = json.loads(request.body)
            
            option_name = data.get('option_maintenance_name', '').strip()
            maintenance_type = data.get('maintenance_type', '').strip()

            if not option_name or not maintenance_type:
                return JsonResponse({'status': 'error', 'message': 'Faltan datos necesarios'}, status=400)

            # Definir la ruta del archivo JSON
            directorio_actual = os.path.dirname(os.path.abspath(__file__))
            directorio_json = os.path.join(directorio_actual, '..', '..', 'static', 'assets', 'json', 'items-maintenance.json')

            # Cargar el JSON desde el archivo
            with open(directorio_json, 'r') as file:
                json_data = json.load(file)
            # Función para agregar un nuevo ítem
            def agregar_item(json_data, tipo_mantenimiento, nueva_descripcion):
                for mantenimiento in json_data['data']:
                    if mantenimiento['tipo'].lower() == tipo_mantenimiento.lower():
                        if mantenimiento['items']: 
                            max_id = max([item['id'] for item in mantenimiento['items']])
                        else:
                            max_id = 0
                        nuevo_id = max_id + 1
                        nuevo_item = {
                            "id": nuevo_id,
                            "descripcion":  nueva_descripcion.upper()
                        }
                        mantenimiento['items'].append(nuevo_item)
                        return json_data
                return None

            # Llamar a la función para agregar el ítem
            data_actualizada = agregar_item(json_data, maintenance_type, option_name)

            if data_actualizada:
                # Guardar el JSON actualizado
                with open(directorio_json, 'w') as file:
                    json.dump(data_actualizada, file, indent=4)

                # Ejecutar python manage.py collectstatic
                try:
                    subprocess.run(['python', 'manage.py', 'collectstatic', '--noinput'], check=True)
                except subprocess.CalledProcessError as e:
                    return JsonResponse({'status': 'error', 'message': 'Error al ejecutar collectstatic'}, status=500)

                return JsonResponse({'status': 'success', 'message': 'Mantenimiento agregado correctamente'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Tipo de mantenimiento no encontrado'}, status=400)
            
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Error en el formato de JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Error interno: {str(e)}'}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'},status=405)


#tabla de mantenimiento
def get_table_item_maintenance(request):
    response = {"success": False}
    context = user_data(request)
    subModule_id = 25
    company_id = context["company"]["id"]
    
    access = get_module_user_permissions(context, subModule_id)["data"]["access"]

    datos = Infrastructure_maintenance.objects.select_related(
        "identifier__item", "provider"
    ).filter(
        identifier__item__company_id=company_id, is_active = True
    ).order_by("-id").values(
        "id",
        "identifier__identifier", 
        "identifier__item__name", 
        "type_maintenance",
        "date",
        "provider__name",
        "cost",
        "general_notes", 
        "status"
    )

    data_list = []
    for item in datos:
        row = dict(item)
        row["btn_action"] = ""
        
        row["btn_action"] += "<button type='button' name='view' class='btn btn-icon btn-sm btn-info-light' data-maintenance-action='view-maintenance' data-id='{0}'>" \
                             "<i class='fa-solid fa-eye'></i></button>\n".format(item["id"])

        if access.get("update"):
            row["btn_action"] += "<button type='button' name='update' class='btn btn-icon btn-sm btn-primary-light' data-maintenance-action='update-maintenance' data-id='{0}'>" \
                                 "<i class='fa-solid fa-pen'></i></button>\n".format(item["id"])
        if access.get("delete"):
            row["btn_action"] += "<button type='button' name='delete' class='btn btn-icon btn-sm btn-danger-light' data-maintenance-action='delete-maintenance' data-id='{0}'>" \
                                 "<i class='fa-solid fa-trash'></i></button>\n".format(item["id"])

        data_list.append(row)

    response["data"] = data_list
    response["status"] = "success"
    response["success"] = True
    return JsonResponse(response)



@csrf_exempt
def add_infrastructure_maintenance(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            maintenance_id = data.get('id')
            identifier_id = data.get('identifier_id')
            date = data.get('date')
            new_regiter = data.get('is_new_register')
            provider_id = data.get('provider_id')
            maintenance_type = data.get('type')
            cost = data.get('cost')
            general_notes = data.get('general_notes')
            actions = data.get('actions', [])

            # Validación básica
            if not identifier_id or not provider_id or not maintenance_type or not date or cost is None:
                return JsonResponse({'status': 'error', 'message': 'Faltan campos obligatorios.'}, status=400)

            identifier = get_object_or_404(InfrastructureItemDetail, id=identifier_id)
            provider = get_object_or_404(Provider, id=provider_id)

            maintenance = Infrastructure_maintenance.objects.create(
                identifier=identifier,
                provider=provider,
                type_maintenance=maintenance_type,
                date=date,
                cost=cost,
                general_notes=general_notes,
                actions = actions,
                status = new_regiter
            )
               
                   
            message = "Registro guardado correctamente."

            return JsonResponse({'status': 'success', 'message': message})

        except Exception as e:
            print(f"Error en mantenimiento: {e}")
            return JsonResponse({'status': 'error', 'message': 'Error interno del servidor.'}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido.'}, status=405)

def get_infrastructure_maintenance_detail(request):
    response = {"status": "error"}
    id = request.GET.get("id")

    try:
        obj = Infrastructure_maintenance.objects.get(id=id)

        # Procesar acciones
        acciones_str = ""
        if obj.actions:
            try:
                acciones_data = eval(obj.actions)
                if isinstance(acciones_data, dict):
                    acciones_list = list(acciones_data.keys())
                elif isinstance(acciones_data, list):
                    acciones_list = acciones_data
                else:
                    acciones_list = []
            except Exception:
                acciones_list = []
        else:
            acciones_list = []


        response["status"] = "success"
        print("estas son las acciones:", acciones_data)
        response["data"] = {
            "id": obj.id,
            "date": obj.date.strftime("%Y-%m-%d"),
            "type_maintenance": obj.type_maintenance,
            "cost": str(obj.cost),
            "general_notes": obj.general_notes,
            "identifier_id": obj.identifier_id,
            "provider_id": obj.provider_id,
            "actions": acciones_list
        }

    except Infrastructure_maintenance.DoesNotExist:
        response["message"] = "No se encontró el mantenimiento"

    return JsonResponse(response)


@csrf_exempt
def update_infraestructure_maintenance(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            maintenance_id = data.get('id')
            identifier_id = data.get('identifier_id')
            date = data.get('date')
            provider_id = data.get('provider_id')
            maintenance_type = data.get('type')
            cost = data.get('cost')
            general_notes = data.get('general_notes')
            actions = data.get('actions', [])

            print(actions)
            if not maintenance_id:
                return JsonResponse({'status': 'error', 'message': 'ID de mantenimiento requerido.'}, status=400)

            maintenance = get_object_or_404(Infrastructure_maintenance, id=maintenance_id)

            maintenance.identifier_id = identifier_id
            maintenance.provider_id = provider_id
            maintenance.type_maintenance = maintenance_type
            maintenance.date = date
            maintenance.cost = cost
            maintenance.general_notes = general_notes
            maintenance.actions = actions
            maintenance.save()

            return JsonResponse({'status': 'success', 'message': 'Mantenimiento actualizado correctamente.'})

        except Exception as e:
            print(f"Error en mantenimiento: {e}")
            return JsonResponse({'status': 'error', 'message': 'Error interno del servidor.'}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido.'}, status=405)

#funcion para eliminar el mantenimiento
@login_required
@csrf_exempt
def delete_maintenance_infraestructure(request):
    if request.method == 'POST':
        form = request.POST
        _id = form.get('id')

        if not _id:
            return JsonResponse({'success': False, 'message': 'No ID provided'})

        try:
            maintenance = Infrastructure_maintenance.objects.get(id=_id)
        except Infrastructure_maintenance.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'El mantenimiento no existe'})

        maintenance.is_active = False
        maintenance.save(update_fields=['is_active'])

        return JsonResponse({'success': True, 'message': 'Mantenimiento eliminado correctamente!'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})




@csrf_exempt 
def update_status_mantenance(request):
    if request.method == 'POST':
        # Obtener los datos enviados
        maintenance_id = request.POST.get('id')
        new_status = request.POST.get('status')

        try:
            # Obtener el mantenimiento
            maintenance = Infrastructure_maintenance.objects.get(id=maintenance_id)
            
            # Verificar si la fecha ya pasó y si el estado no es "Proceso" o "Finalizado"
            current_date = timezone.now().date()
            maintenance_date = maintenance.date
            if maintenance_date < current_date and maintenance.status not in ["Proceso", "Finalizado"]:
                new_status = "Retrasado"  # Si la fecha ya pasó, marcar como "Retrasado"
            
            # Actualizar el estado
            maintenance.status = new_status
            maintenance.save()

            # Responder con éxito
            return JsonResponse({'status': 'success', 'message': 'Estado actualizado correctamente.'})

        except Vehicle_Maintenance.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Mantenimiento no encontrado.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido.'})


def get_infrastructure_info_from_maintenance(request, maintenance_id):
    import ast

    try:
        maintenance = Infrastructure_maintenance.objects.select_related(
            'identifier__item'
        ).get(id=maintenance_id)

        detail = maintenance.identifier

        # Imagen de infraestructura
        image_url = None

        if detail.item.image:
            image_url = generate_presigned_url(
                AWS_BUCKET_NAME,
                str(detail.item.image)
            )

        detail_html = render_to_string(
            "infrastructure/cards/infraestructure_info.html",
            context={
                'detail': detail,
                'item': detail.item,
                'id': maintenance.id,
                'image': image_url
            }
        )

        # Acciones de mantenimiento
        action2 = []

        for key, value in ast.literal_eval(maintenance.actions).items():
            action2.append({
                "name": key,
                "status": value
            })

        # Comprobante
        comprobante_url = None

        if maintenance.comprobante:
            comprobante_url = generate_presigned_url(
                AWS_BUCKET_NAME,
                str(maintenance.comprobante)
            )

        maintenance_html = render_to_string(
            "infrastructure/cards/maintenance_infraestructure_info.html",
            context={
                'detail': maintenance,
                'item': detail.item,
                'actions': action2,
                'comprobante': comprobante_url
            }
        )

        return JsonResponse({
            'detail_html': detail_html,
            'maintenance_html': maintenance_html
        })

    except Infrastructure_maintenance.DoesNotExist:
        return JsonResponse(
            {'error': 'Mantenimiento no encontrado'},
            status=404
        )


def mostrar_informacion(request, maintenance_id):
    try:
        mantenimiento = Infrastructure_maintenance.objects.select_related(
            "identifier", "identifier__item", "identifier__responsible"
        ).get(id=maintenance_id)

        detalle = mantenimiento.identifier
        item = detalle.item

        image_url = None
        if item.image:
            image_url = generate_presigned_url(AWS_BUCKET_NAME, str(item.image))
        
        print("este es el id del mantenimiento:", mantenimiento.id)
        response_data = {
            #Id
            "maintenance_id": mantenimiento.id,
            "name": detalle.name,
            #Identificador
            "identifier": detalle.identifier,
            #Tipo de mantenimiento
            "type_maintenance" : mantenimiento.type_maintenance,
            #Fecha de mantenimiento
            "date_maintenance" : mantenimiento.date.strftime("%Y-%m-%d") if mantenimiento.date else "Sin fecha",
            #Comprobante
            "voucher" : "mantenimiento.comprobante",
            #Proveedor
            "provider" : mantenimiento.provider.name,
            "responsible": f"{detalle.responsible.first_name} {detalle.responsible.last_name}" if detalle.responsible else "Sin responsable",
            #Costo
            "cost" : mantenimiento.cost,
            #Notas generales
            "general_notes" : mantenimiento.general_notes,
            "assignment_date": detalle.assignment_date.strftime("%Y-%m-%d") if detalle.assignment_date else "Sin fecha",
            
            "image_url": image_url,
            "actions" : mantenimiento.actions
        }

        print(response_data)
        return JsonResponse({"success": True, "data": response_data})

    except ObjectDoesNotExist:
        return JsonResponse({"success": False, "error": "Mantenimiento no encontrado"})
    
def update_infraestructure_status_man(request):
    try:
        context = {}
        fd = request.POST.get
        obj = Infrastructure_maintenance.objects.get(pk = fd("id"))
        temporal = user_data(request)
        company_id = temporal["company"]["id"]
        if "comprobante" in request.FILES:
            file = request.FILES["comprobante"]
            folder_path = f'docs/{company_id}/infrastructure_maintenance/{fd("id")}/voucher/'
            file_name, extension = os.path.splitext(file.name)
            new_name = f'voucher_{fd("id")}{extension}'
            s3_path = folder_path + new_name
            
            print(AWS_SECRET_ACCESS_KEY)
            print(AWS_ACCESS_KEY_ID)
            print(AWS_BUCKET_NAME)
            
            upload_to_s3(file, AWS_BUCKET_NAME, s3_path)
            obj.comprobante = s3_path
        print(obj.comprobante)
        action = {}
        for item in json.loads(fd("actions"))["action"]:
            action[item["name"]] = item["value"]
        obj.status = "Finalizado"
        obj.actions = action
        obj.save()
        context["status"] = "success"
        context["message"] = "Mantenimiento Realizado"
        print(request.FILES)
        return JsonResponse(context, safe=False)
    except Exception as e:
        context["status"] = "error"
        context["message"] = e
        return JsonResponse(context, safe=False)


# vista de submodulo responsiva
@login_required
def infrastructure_responsiva_view(request):
    context = user_data(request)
    module_id = 4
    subModule_id = 26

    access = get_module_user_permissions(context, subModule_id)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]
    
    template = "infrastructure/responsiva_infrastructure.html" if context["access"]["read"] and check_user_access_to_module(request, module_id, subModule_id) else "error/access_denied.html"
    return render(request, template , context)

# tabla de datos de responsiva
@login_required
def get_infrastructure_responsiva(request):
    context = user_data(request)
    response = {
        "status": "error",
        "message": "Sin procesar",
        "data": []
    }

    dt = request.GET
    isList = dt.get("isList", False)
    subModule_id = 19

    datos = Infraestructure_Responsiva.objects.values(
        "id",
        "responsible_infraestructure_id",
        "responsible_infraestructure__first_name",
        "responsible_infraestructure__last_name",
        "area_responsable_id",
        "area_responsable__name",
        "items",
        "record",
        "responsibility_pdf",
        "created_at",
        "updated_at",
    )

    modified_data_list = []

    for data in datos:

        modified_data = data.copy()

        # Historial
        record_string = data.get("record") or "[]"

        try:
            record_data = json.loads(record_string)
        except json.JSONDecodeError:
            record_data = []

        # Convertir rutas del historial a URLs firmadas
        for record in record_data:
            file_path = record.get("file_path")

            if file_path:
                record["file_path"] = generate_presigned_url(
                    AWS_BUCKET_NAME,
                    file_path
                )

        modified_data["record"] = json.dumps(record_data)

        # PDF actual
        if data.get("responsibility_pdf"):
            modified_data["responsibility_pdf"] = generate_presigned_url(
                AWS_BUCKET_NAME,
                data["responsibility_pdf"]
            )
        else:
            modified_data["responsibility_pdf"] = None

        modified_data_list.append(modified_data)

    if isList:

        response["data"] = list(
            Infraestructure_Responsiva.objects.values(
                "id",
                "responsible_infraestructure_id",
                "responsible_infraestructure__first_name",
                "responsible_infraestructure__last_name",
            )
        )

    else:

        access = get_module_user_permissions(context, subModule_id)
        access = access["data"]["access"]

        for item in modified_data_list:

            item["btn_action"] = ""

            if access["update"]:
                item["btn_action"] += f"""
                    <button
                        class="btn btn-icon btn-sm btn-primary-light"
                        data-id="{item['id']}"
                        data-infrastructure-responsiva="update-item"
                        title="Editar">
                        <i class="fa-solid fa-pen"></i>
                    </button>
                """

            if access["delete"]:
                item["btn_action"] += f"""
                    <button
                        class="btn btn-icon btn-sm btn-danger-light"
                        data-id="{item['id']}"
                        data-infrastructure-responsiva="delete-item"
                        title="Eliminar">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                """

        response["data"] = modified_data_list

    response["status"] = "success"

    return JsonResponse(response)


# usuarios de la empresa
@login_required
def get_users_infrastructure_responsiva(request):
    context = user_data(request)
    company_id = context["company"]["id"]

    response = {
        "status": "success",
        "data": []
    }

    usuarios = User_Access.objects.filter(
        company_id=company_id,
        user__is_active=True
    ).select_related(
        "user"
    ).values(
        "user_id",
        "user__first_name",
        "user__last_name"
    ).distinct().order_by(
        "user__first_name",
        "user__last_name"
    )

    data = []

    for item in usuarios:
        data.append({
            "id": item["user_id"],
            "first_name": item["user__first_name"],
            "last_name": item["user__last_name"],
        })

    response["data"] = data

    return JsonResponse(response)

# generar pdf
@login_required
def infrastructure_responsiva_pdf_view(request):
    dt = request.GET
    context = user_data(request)

    context2 = {
        "title": "Carta Responsiva",
        "user": {
            "name": ""
        },
        "data": []
    }

    responsible_id = dt.get("user_id")

    if not responsible_id:
        responsible_id = context["user"]["id"]

    # ==========================
    # Datos del responsable
    # ==========================
    usuario = User.objects.filter(id=responsible_id).first()

    if usuario:
        context2["user"]["name"] = (
            f"{usuario.first_name} {usuario.last_name}"
        )

    # ==========================
    # Activos asignados
    # ==========================
    infraestructura = (
        InfrastructureItemDetail.objects
        .filter(
            company_id=context["company"]["id"],
            responsible_id=responsible_id,
            is_active = True
        )
        .select_related(
            "item",
            "item__category",
            "item__location"
        )
    )

    for activo in infraestructura:

        descripcion = ""

        # Categoría
        if activo.item.category:
            descripcion += f"{activo.item.category.name}: "

        # Nombre
        descripcion += activo.item.name

        # Descripción
        if activo.item.description:
            descripcion += f". {activo.item.description}"

        # Ubicación
        if activo.item.location:
            descripcion += f". Ubicación: {activo.item.location.name}"

        context2["data"].append({

            "amount": 1,

            "identifier": activo.identifier,

            "description": descripcion

        })

    return WeasyPDF(
        "pdf/infrastructure_responsiva_infrastructure.html",
        context2
    ).render()


# agregar responsiva de Infraestructure_Responsiva
def add_infrastructure_responsiva(request):
    context = user_data(request)
    response = {"status": "error", "message": "sin procesar" }
    dt = request.POST
    company_id = context["company"]["id"]

    try:
        responsible_infraestructure = dt.get("responsible_infraestructure")

        if responsible_infraestructure == None:
            response["message"] = "Sin Responsable"
            return JsonResponse(response)
        
        responsable = User_Access.objects.filter(user_id = responsible_infraestructure)

        if not responsable.exists():
            response["message"] = "El responsable no existe"
            return JsonResponse(response)

        responsable = responsable.values()[0]
        area_id = responsable["area_id"]

        registro = Infraestructure_Responsiva.objects.filter(
            responsible_infraestructure = responsible_infraestructure
            ).count()

        if registro >= 1:
            response["message"] = f"Ya existen {registro} regitro(s) de la responsibla del usuario asignado"
            return JsonResponse(response)


        with transaction.atomic():
            obj = Infraestructure_Responsiva(
                responsible_infraestructure_id=responsible_infraestructure,
                area_responsable_id=area_id
            )
            
            obj.save()
            id = obj.id

        if 'responsibility_pdf' in request.FILES and request.FILES['responsibility_pdf']:
            load_file = request.FILES.get('responsibility_pdf')
            folder_path = f"docs/{company_id}/infrastructure/responsiva/{id}/"

            file_name, extension = os.path.splitext(load_file.name)
            new_name = f"doc_1{extension}"
            s3Name = folder_path + new_name

            # Guardar archivo
            upload_to_s3(load_file, AWS_BUCKET_NAME, s3Name)

            # Guardar ruta en la tabla
            obj.responsibility_pdf = s3Name
            # obj.save()

            # Cargar y actualizar el historial existente
            try:
                historial = json.loads(obj.record)
            except (ValueError, TypeError):
                historial = []

            # Agregar el nuevo registro al historial
            count = len(historial) + 1
            historial.append({
                "id": count,
                "file_path": str(obj.responsibility_pdf),
                "date": datetime.now().isoformat()
            })

            # Convertir el historial actualizado a cadena JSON
            historial_str = json.dumps(historial)
            obj.record = historial_str
            obj.save()
            response["id"] = id
        response["status"] = "success"
        response["message"] = "Guardado"
    except ValidationError as e:
        response["status"] = "error"
        response["message"] = e.message_dict
    except Exception as e:
        response["status"] = "error"
        response["message"] = str(e)
    return JsonResponse(response)


# funcion para obtener un registro
@login_required
def get_infrastructure_responsiva_item(request):

    response = {
        "status": "error",
        "message": "Sin procesar"
    }

    id = request.GET.get("id")

    try:

        obj = Infraestructure_Responsiva.objects.values(
            "id",
            "responsible_infraestructure_id",
            "area_responsable_id",
            "responsibility_pdf"
        ).get(id=id)

        response["status"] = "success"
        response["data"] = obj

    except Infraestructure_Responsiva.DoesNotExist:
        response["message"] = "No existe el registro."

    return JsonResponse(response)


# Editar responsiva
@login_required
@csrf_exempt
def update_infrastructure_responsiva(request):
    context = user_data(request)
    response = {"status": "error", "message": "Sin procesar"}

    # obtener informacion
    if request.method == "GET":
        id = request.GET.get("id")

        try:

            obj = Infraestructure_Responsiva.objects.values(
                "id",
                "responsible_infraestructure_id",
                "area_responsable_id",
                "responsibility_pdf"
            ).get(id=id)

            return JsonResponse({
                "status": "success",
                "data": obj
            })

        except Infraestructure_Responsiva.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "No existe el registro."
            })

    # Actualizar informacion    
    dt = request.POST
    company_id = context["company"]["id"]

    try:

        id = dt.get("id")
        responsible_infraestructure = dt.get("responsible_infraestructure")

        if not id:
            response["message"] = "No se recibió el ID de la responsiva."
            return JsonResponse(response)

        if not responsible_infraestructure:
            response["message"] = "Debe seleccionar un responsable."
            return JsonResponse(response)

        responsable = User_Access.objects.filter(
            user_id=responsible_infraestructure
        )

        if not responsable.exists():
            response["message"] = "El responsable no existe."
            return JsonResponse(response)

        area_id = responsable.values("area_id").first()["area_id"]

        with transaction.atomic():

            obj = Infraestructure_Responsiva.objects.get(id=id)

            obj.responsible_infraestructure_id = responsible_infraestructure
            obj.area_responsable_id = area_id

            # Si se cargó una nueva responsiva
            if request.FILES.get("responsibility_pdf"):

                load_file = request.FILES["responsibility_pdf"]

                folder_path = (
                    f"docs/{company_id}/infrastructure/responsiva/{id}/"
                )

                try:
                    historial = json.loads(obj.record) if obj.record else []
                except Exception:
                    historial = []

                _, extension = os.path.splitext(load_file.name)

                new_name = f"doc_{len(historial)+1}{extension}"

                s3name = folder_path + new_name

                upload_to_s3(
                    load_file,
                    AWS_BUCKET_NAME,
                    s3name
                )

                obj.responsibility_pdf = s3name

                historial.append({
                    "id": len(historial) + 1,
                    "file_path": s3name,
                    "date": datetime.now().isoformat()
                })

                obj.record = json.dumps(historial)

            obj.save()

        response["status"] = "success"
        response["message"] = "Responsiva actualizada correctamente."
        response["id"] = obj.id

    except Infraestructure_Responsiva.DoesNotExist:

        response["message"] = (
            f"No existe la responsiva con ID {id}."
        )

    except ValidationError as e:

        response["message"] = e.message_dict

    except Exception as e:

        response["message"] = str(e)

    return JsonResponse(response)


# Eliminar responsiva
def delete_infrastructure_responsiva(request):
    response = {"success": False, "data": []}
    dt = request.POST
    id = dt.get("id", None)

    if id == None:
        response["error"] = {"message": "Proporcione un id valido"}
        response["status"] = "error"
        response["message"] = "Proporcione un id valido"
        return JsonResponse(response)
    try:
        obj = Infraestructure_Responsiva.objects.get(id = id)
    except Infraestructure_Responsiva.DoesNotExist:
        response["error"] = {"message": "El objeto no existe"}
        response["status"] = "error"
        response["message"] = "El objeto no existe"
        return JsonResponse(response)
    else:
        obj.delete()
    response["success"] = True
    response["status"] = "success"
    response["message"] = "Se ha borrado el registro"
    return JsonResponse(response)


# Guardar imagen individual de infraestructura
@login_required
@csrf_exempt
def save_photo_infrastructure(request):

    context = user_data(request)
    company_id = context["company"]["id"]

    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "Método no permitido."
        }, status=405)

    try:
        detalle_id = request.POST.get("detalle_id")
        image = request.FILES.get("photo")

        # Validar información
        if not detalle_id:
            return JsonResponse({
                "success": False,
                "message": "No se recibió el detalle de infraestructura."
            })

        detalle = InfrastructureItemDetail.objects.get(
            id=detalle_id,
            company_id=company_id
        )

        if not image:
            return JsonResponse({
                "success": False,
                "message": "No se recibió ninguna imagen."
            })

        # Ruta 
        folder_path = (
            f"docs/{company_id}/"
            f"infrastructure/{detalle_id}/"
            f"image/{detalle_id}/"
        )

        # Obtener extensión
        _, extension = os.path.splitext(image.name)

        # Nombre nuevo
        new_name = (
            f"infrastructure_image_{detalle_id}"
            f"{extension}"
        )

        s3Name = folder_path + new_name
        # Eliminar imagen anterior 
        if detalle.photo_infraestructure:
            delete_s3_object(
                AWS_BUCKET_NAME,
                str(detalle.photo_infraestructure)
            )

        # SUBIR NUEVA IMAGEN
        upload_to_s3(
            image,
            AWS_BUCKET_NAME,
            s3Name
        )
        # Guardar ruta 
        detalle.photo_infraestructure = s3Name

        detalle.save(
            update_fields=["photo_infraestructure"]
        )

        return JsonResponse({
            "success": True,
            "message": "Imagen guardada correctamente.",
            "photo": s3Name
        })

    except InfrastructureItemDetail.DoesNotExist:

        return JsonResponse({
            "success": False,
            "message": "No se encontró el detalle de infraestructura."
        })

    except Exception as e:

        return JsonResponse({
            "success": False,
            "message": f"Error al guardar la imagen: {str(e)}"
        })


@login_required
def modal_infrastructure_detail(request):
    detail_id = request.GET.get("id")

    if not detail_id:
        return JsonResponse({
            "success": False,
            "message": "No se recibió el identificador."
        })

    try:
        context = user_data(request)
        company_id = context["company"]["id"]
        detail = InfrastructureItemDetail.objects.get(
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

    except InfrastructureItemDetail.DoesNotExist:

        return JsonResponse({
            "success": False,
            "message": "El detalle no existe."
        }, status=404)



# dar de baja / habilitar un equipo
@login_required
def disable_infrastructure_detail(request):

    detail_id = request.POST.get("detail_id")
    print("este es el id a deshabilitar", detail_id)
    action = request.POST.get("action")

    if not detail_id:
        return JsonResponse({
            "success": False,
            "message": "No se recibió el ID del detalle."
        })

    try:
        context = user_data(request)
        company_id = context["company"]["id"]
        detail = InfrastructureItemDetail.objects.get(id=detail_id, company_id=company_id)

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
            item_id = detail.item_id

            # Evidencia 1
            if evidence1:

                folder_path = (
                    f"docs/{company_id}/"
                    f"infrastructure/{item_id}/"
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
                    f"infrastructure/{item_id}/"
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

            # Actualizar cantidad del registro principal
            cantidad_activa = InfrastructureItemDetail.objects.filter(
                item_id=detail.item_id,
                is_active=True
            ).count()

            Infrastructure_Item.objects.filter(
                id=detail.item_id,
                company_id=company_id
            ).update(
                quantity=cantidad_activa
            )

            return JsonResponse({
                "success": True,
                "message": (
                    "El activo "
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

            # Actualizar cantidad del registro principal
            cantidad_activa = InfrastructureItemDetail.objects.filter(
                item_id=detail.item_id,
                is_active=True
            ).count()

            Infrastructure_Item.objects.filter(
                id=detail.item_id,
                company_id=company_id
            ).update(
                quantity=cantidad_activa
            )

            return JsonResponse({ "success": True, "message": ("El equipo o herramienta " "ha sido habilitado correctamente.")})

        # ACCIÓN NO VÁLIDA
        else:

            return JsonResponse({"success": False, "message": "Acción no válida."})

    except InfrastructureItemDetail.DoesNotExist:

        return JsonResponse({
            "success": False,
            "message": "El equipo o herramienta no existe."
        }, status=404)

    except Exception as e:

        return JsonResponse({
            "success": False,
            "message": f"Error interno: {str(e)}"
        }, status=500)


# submodulo de activos eliminados
@login_required
def infrastructure_removed(request):
    context = user_data(request)
    module_id = 4
    subModule_id = 41
    request.session["last_module_id"] = module_id

    sidebar = get_sidebar(context, [1, module_id])
    access = get_module_user_permissions(context, subModule_id)
    for module in sidebar["data"]:
        for submodule in module.get("submodules", []):
            submodule["title"] = submodule["title"].strip() 
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]
    template = "infrastructure/infrastructure_removed.html" if context["access"]["read"] and check_user_access_to_module(request, module_id, subModule_id) else "error/access_denied.html"
    return render(request, template, context)




# Funcion para obtener los activos dados de baja
@csrf_exempt
def get_infrastructure_removed(request):

    response = {
        "status": "error",
        "message": "Sin procesar",
        "data": []
    }

    context = user_data(request)

    try:
        company_id = context["company"]["id"]

        bajas = list(
            InfrastructureItemDetail.objects
            .select_related(
                "item",
                "company",
                "user_modification",
            )
            .filter(
                company_id=company_id,
                is_deactivated=True,
            )
            .order_by("-id")
            .values(
                "id",
                "identifier",
                "name",
                "evidence1_image",
                "evidence2_image",
                "deactivation_reason",
                "deactivation_description",
                "deactivated_at",
                "user_modification__id",
                "user_modification__first_name",
                "user_modification__last_name",
                "user_modification__username",

                # Responsable
                "responsible__id",
                "responsible__first_name",
                "responsible__last_name",
                "responsible__username",
            )
        )

        # Obtener último responsable
        for item in bajas:

            if item["responsible__id"]:

                nombre = (
                    f"{item['responsible__first_name']} "
                    f"{item['responsible__last_name']}"
                ).strip()

                item["last_responsible"] = (
                    nombre
                    if nombre
                    else item["responsible__username"]
                )

            else:

                item["last_responsible"] = ""


        # Catálogo de motivos
        motivos = dict(
            InfrastructureItemDetail.DEACTIVATION_REASONS
        )

        for item in bajas:

            # ESTADO
            item["state"] = "BAJA"

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
                except Exception:
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
                except Exception:
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
                    item["deactivated_at"]
                    .strftime("%Y-%m-%d %H:%M:%S")
                )

                item["deactivated_at"] = (
                    item["deactivated_at"]
                    .strftime("%d/%m/%Y %H:%M")
                )

            else:

                item["deactivated_at_sort"] = ""
                item["deactivated_at"] = ""

            # NOMBRE DEL ACTIVO
            item["infrastructure__equipment_name"] = (
                item["name"] or ""
            )

        response["data"] = bajas
        response["status"] = "success"
        response["message"] = (
            "Activos de infraestructura dados de baja "
            "cargados correctamente"
        )

    except Exception as e:

        response["status"] = "error"
        response["message"] = str(e)

    return JsonResponse(response)


# Funcion para obtener los nombres de las areas
@login_required
@csrf_exempt
def get_item_areas(request):
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

# Funcion para obtener los nombres de los usuarios 
@login_required
@csrf_exempt
def get_responsible_users_item(request):
    try:
        context = user_data(request)
        company_id = context["company"]["id"]

        if not company_id:
            return JsonResponse({'success': False, 'message': 'No se encontró la empresa asociada al usuario'}, status=400)
        
        users = User.objects.filter(
            id__in=User_Access.objects.filter(company_id=company_id).values('user_id')
        ).distinct().values('id', 'username')  
        data = []
        for user in users: 
            data.append({
                'id': user['id'],
                'username': user['username'],
                'is_current_user': user['id'] == request.user.id
            })
        return JsonResponse({'data': data}, safe=False)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

# funciones para descargar xlsx
@require_GET
def get_items_categories(request):
    categorias = Infrastructure_Category.objects.filter(is_active=True).order_by("name").values("id", "name")
    return JsonResponse({"success": True, "data": list(categorias)})


def excel_safe_value(value):
    if isinstance(value, (datetime, time)) and value.tzinfo is not None:
        return value.replace(tzinfo=None)
    return value


def configurar_hoja_excel(sheet, encabezados, anchos):
    sheet.sheet_view.showGridLines = False
    sheet.freeze_panes = "A2"
    sheet.append(encabezados)
    for celda in sheet[1]:
        celda.font = Font(bold=True, color="FFFFFF")
        celda.fill = PatternFill("solid", fgColor="17365D")
        celda.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    sheet.row_dimensions[1].height = 32
    for columna, ancho in enumerate(anchos, 1):
        sheet.column_dimensions[get_column_letter(columna)].width = ancho


# Descargar excel
@require_GET
def download_items_xlsx(request):
    tipo = request.GET.get("type", "all")
    estado = request.GET.get("status", "all")
    category_ids = request.GET.getlist("category_ids")

    if tipo not in ("all", "category") or estado not in ("all", "active", "inactive"):
        return JsonResponse({"success": False, "message": "Los filtros seleccionados no son válidos."}, status=400)
    if tipo == "category" and (not category_ids or not all(value.isdigit() for value in category_ids)):
        return JsonResponse({"success": False, "message": "Selecciona categorías válidas."}, status=400)

    equipos = Infrastructure_Item.objects.select_related(
        "company",
        "category",
        "location"
    ).order_by(
        "category__name",
        "name",
        "id"
    )

    if tipo == "category":
        equipos = equipos.filter(category_id__in=category_ids)

    if estado == "active":
        equipos = equipos.filter(is_active=True)
    elif estado == "inactive":
        equipos = equipos.filter(is_active=False)

    workbook = Workbook()
    resumen = workbook.active
    resumen.title = "Resumen del catálogo"
    detalle_sheet = workbook.create_sheet("Inventario detallado")

    encabezados_resumen = [
        "ID Registro", "Empresa", "Categoría", "Activo",
        "Tipo de activo", "Marca","Cantidad registrada", "Costo unitario", "Descripción", "Área", "Responsable general", "Comentarios", "Cuenta con ficha técnica", "Cuenta con factura","Fotografía"
    ]
    anchos_resumen = [13, 22, 25, 32, 20, 20, 40, 22, 28, 25, 18, 16, 20, 22, 35]
    configurar_hoja_excel(resumen, encabezados_resumen, anchos_resumen)

    encabezados_detalle = [
        "ID catálogo", "Empresa", "Categoría", "Equipo / herramienta",
        "Tipo", "Marca", "Descripción del equipo", "Área",
        "Responsable general", "Cantidad registrada",
        "Costo unitario", "Estado del catálogo", "ID detalle",
        "Identificador", "Nombre del identificador", "Número de serie",
        "Estado del registro", "Estado operativo", "Responsable asignado",
        "Ubicación individual", "Fecha de asignación", "Fecha de activación",
        "Usuario de activación", "Usuario de modificación", "Motivo de baja",
        "Descripción de baja", "Fecha de baja"
    ]
    anchos_detalle = [
        13, 22, 25, 32, 20, 20, 35, 22, 28, 25, 18, 16, 20,
        13, 25, 28, 25, 20, 20, 28, 25, 20, 22, 28, 28, 20, 35, 22
    ]
    configurar_hoja_excel(detalle_sheet, encabezados_detalle, anchos_detalle)

    for equipo in equipos.iterator():
        categoria = equipo.category.name if equipo.category else ""
        empresa = str(equipo.company or "")
        ubicacion_general = (
            equipo.location.name
            if equipo.location else ""
        )

        costo = float(equipo.cost) if equipo.cost is not None else 0

        responsable_general = (
            equipo.item_responsible.get_full_name()
            if equipo.item_responsible else ""
        )

        area_general = (
            equipo.item_area.name
            if equipo.item_area else ""
        )

        datos_generales = [
            equipo.pk,
            empresa,
            categoria,
            equipo.is_active,
            equipo.item_type or "",
            equipo.item_brand or "",
            equipo.quantity if equipo.quantity is not None else 0,
            costo,
            equipo.description or "",
            area_general,
            responsable_general,
            equipo.comments or "",
            "Sí" if equipo.technical_sheet else "No",
            "Sí" if equipo.invoice else "No",
            "Sí" if equipo.image else "No",
        ]


        fila_resumen = datos_generales 

        resumen.append([excel_safe_value(v) for v in fila_resumen])

        detalles = Infrastructure_Item.objects.filter(
            details=equipo.pk
        ).select_related(
            "responsible", "equipment_location", "user_activation", "user_modification"
        ).order_by("id")

        if estado == "active":
            detalles = detalles.filter(is_active=True)
        elif estado == "inactive":
            detalles = detalles.filter(Q(is_active=False))

        if not detalles.exists():
            fila_detalle = datos_generales + [
                None, "", "", "", "", "", "", "", None, None, "", "", "", "", None
            ]
            detalle_sheet.append([excel_safe_value(v) for v in fila_detalle])
            continue

        for detalle in detalles.iterator():
            responsable = detalle.responsible.get_full_name() if detalle.responsible else ""
            usuario_activacion = detalle.user_activation.get_full_name() if detalle.user_activation else ""
            usuario_modificacion = detalle.user_modification.get_full_name() if detalle.user_modification else ""
            ubicacion_individual = detalle.equipment_location.location_name if detalle.equipment_location else ""

            fila_detalle = datos_generales + [
                detalle.pk, detalle.identifier or "", detalle.name or "",
                "Habilitado" if detalle.is_active and not detalle.is_deactivated else "Deshabilitado",
                detalle.get_state_display() if detalle.state else "",
                responsable, ubicacion_individual, detalle.assignment_date,
                detalle.modification_date, usuario_activacion, usuario_modificacion,
                detalle.deactivation_reason or "",
                detalle.deactivation_description or "",
                detalle.deactivated_at
            ]
            detalle_sheet.append([excel_safe_value(v) for v in fila_detalle])

    borde = Border(bottom=Side(style="thin", color="D9E2F3"))
    for sheet in (resumen, detalle_sheet):
        for fila_celdas in sheet.iter_rows(min_row=2):
            for celda in fila_celdas:
                celda.alignment = Alignment(vertical="top", wrap_text=True)
                celda.border = borde

    for fila_celdas in detalle_sheet.iter_rows(min_row=2):
        for columna in (22, 23, 28):
            celda = fila_celdas[columna - 1]
            if celda.value:
                celda.number_format = "dd/mm/yyyy" if columna == 22 else "dd/mm/yyyy hh:mm"

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="reporte_infraestructura.xlsx"'
    workbook.save(response)
    return response


@csrf_exempt
def asignar_location(request):
    if request.method == "POST":
        detalle_id = request.POST.get("id")
        location_id = request.POST.get("location")

        try:
            if not detalle_id or not location_id:
                return JsonResponse({
                    "success": False,
                    "message": "Faltan datos para asignar la ubicación."
                })

            detalle = InfrastructureItemDetail.objects.get(
                id=detalle_id
            )

            detalle.location_item_id = location_id
            detalle.save()

            return JsonResponse({
                "success": True,
                "message": "Ubicación asignada correctamente."
            })

        except InfrastructureItemDetail.DoesNotExist:
            return JsonResponse({
                "success": False,
                "message": "No se encontró el registro."
            })

        except Exception as e:
            print("Error al asignar ubicación:", str(e))

            return JsonResponse({
                "success": False,
                "message": "No se pudo asignar la ubicación."
            })

    return JsonResponse({
        "success": False,
        "message": "Método no permitido."
    })



# submodulo para verificación de activos
@login_required
def infrastructure_asset_verification(request):
    context = user_data(request)
    module_id = 4
    subModule_id = 43
    request.session["last_module_id"] = module_id

    sidebar = get_sidebar(context, [1, module_id])
    access = get_module_user_permissions(context, subModule_id)
    for module in sidebar["data"]:
        for submodule in module.get("submodules", []):
            submodule["title"] = submodule["title"].strip() 
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]
    template = "infrastructure/infrastructure_asset_verification.html" if context["access"]["read"] and check_user_access_to_module(request, module_id, subModule_id) else "error/access_denied.html"
    return render(request, template, context)


#Tabla activos 
# def get_infrastructure_items_verification(request):
#     response = {"success": False}
#     context = user_data(request)
#     dt = request.GET
#     subModule_id = 24
#     company_id = context["company"]["id"]
#     isList = dt.get("isList", False)
#     category_id = dt.get("category_id", 1)
#     category_name = dt.get("category_name", "Infraestructura de Seguridad")
#     responsible_id = dt.get("responsible_id")

#     datos = Infrastructure_Item.objects.filter(company_id = company_id, is_active = True ).values(
#         "id",
#         "company_id", 
#         "company__name",
#         "category_id", 
#         "category__name",

#         "name", 
#         "item_brand",
#         "description", 
#         "quantity",
#         "cost",

#         "is_active", 
#         "created_at",
#         "updated_at",
#     )

#     if isList:
#         datos = datos.filter(is_active = True).values("id", "category_id", "category__name", "name")
#         if category_id:
#             datos = datos.filter(category_id = category_id)
#     else:
#         access = get_module_user_permissions(context, subModule_id)
#         access = access["data"]["access"]
#         for item in datos:
#             item["row_id"] = item["id"] 

#             item["cantidad_encontrada"] = None
#             item["estado"] = "Pendiente"

#             if item["image"]:
#                 item["image"] = generate_presigned_url(
#                     bucket_name,
#                     item["image"]
#                 )
#             else:
#                 item["image"] = None

#             # Desglose
#             item["btn_identifiers"] = (
#                 f"<button type='button' "
#                 f"class='btn btn-icon btn-sm btn-success-light' "
#                 f"data-infrastructure-item='view-identifiers' "
#                 f"data-id='{item['id']}' "
#                 f"aria-label='Ver desglose'>"
#                 f"<i class='fa-solid fa-list'></i>"
#                 f"</button>"
#             )

#     response["data"] = list(datos)
#     response["status"] = "success"
#     return JsonResponse(response)

#Función para obtener los activos de las categorias seleccionadas
def get_infrastructure_audit_assets(request):
    try:
        context = user_data(request)
        company_id = context["company"]["id"]

        if not company_id:
            return JsonResponse({
                "status": "error",
                "message": "No se encontró la empresa asociada al usuario."
            }, status=400)

        # Obtener las categorías seleccionadas
        categories_ids = request.GET.getlist("categories")

        if not categories_ids:
            return JsonResponse({
                "status": "success",
                "data": []
            })

        # Consultar los activos de las categorías seleccionadas
        assets = Infrastructure_Item.objects.filter(
            company_id=company_id,
            category_id__in=categories_ids,
            is_active=True
        ).values(
            "id",
            "name",
            "quantity",
            "category__name"
        ).order_by("name")

        data = [
            {
                "id": asset["id"],
                "name": asset["name"],
                "quantity": asset["quantity"],
                "category": asset["category__name"]
            }
            for asset in assets
        ]

        return JsonResponse({
            "status": "success",
            "data": data
        })

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)

# Agregar auditoría
def add_infrastructure_audit(request):
    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "Método no permitido"
        }, status=405)

    try:
        context = user_data(request)
        company_id = context["company"]["id"]

        if not company_id:
            return JsonResponse({
                "status": "error",
                "message": "No se encontró la empresa asociada al usuario."
            }, status=400)

        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()
        start_date = request.POST.get("start_date") or None

        categories_ids = request.POST.getlist("audit_categories")

        if not name:
            return JsonResponse({
                "status": "warning",
                "message": "Ingrese el nombre de la auditoría."
            })

        if not start_date:
            return JsonResponse({
                "status": "warning",
                "message": "Seleccione la fecha de inicio."
            })

        start_date = parse_date(start_date)

        if not start_date:
            return JsonResponse({
                "status": "warning",
                "message": "La fecha de inicio no es válida."
            })

        if not categories_ids:
            return JsonResponse({
                "status": "warning",
                "message": "Seleccione al menos una categoría para la auditoría."
            })

        if InfrastructureAudit.objects.filter(
            name__iexact=name,
            company_id=company_id
        ).exists():
            return JsonResponse({
                "status": "warning",
                "message": "Ya existe una auditoría con ese nombre."
            })

        categories = Infrastructure_Category.objects.filter(
            id__in=categories_ids,
            empresa_id=company_id,
            is_active=True
        )

        if categories.count() != len(set(categories_ids)):
            return JsonResponse({
                "status": "warning",
                "message": "Una o varias categorías seleccionadas no pertenecen a la empresa."
            })

        with transaction.atomic():

            # Crear auditoría
            obj = InfrastructureAudit.objects.create(
                company_id=company_id,
                name=name,
                description=description,
                start_date=start_date,
                created_by=request.user
            )

            # Relacionar categorías seleccionadas
            obj.categories.set(categories)

            # Obtener activos de las categorías seleccionadas
            infrastructure_items = Infrastructure_Item.objects.filter(
                company_id=company_id,
                is_active=True,
                category_id__in=categories.values_list("id", flat=True)
            )

            # Crear los registros de activos correspondientes a la auditoría
            audit_items = [
                InfrastructureAuditItem(
                    audit=obj,
                    item=item,
                    registered_quantity=item.quantity
                )
                for item in infrastructure_items
            ]

            InfrastructureAuditItem.objects.bulk_create(audit_items)

        return JsonResponse({
            "status": "success",
            "id": obj.id,
            "message": "Auditoría registrada exitosamente."
        })

    except Exception as e:
        print("Error al guardar la auditoría:", str(e))

        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)



# Funcion para obtener los nombres de las categorias de una empresa
def get_categories_audit(request):
    try:
        context = user_data(request)
        company_id = context["company"]["id"]

        if not company_id:
            return JsonResponse({
                'success': False,
                'message': 'No se encontró la empresa asociada al usuario'
            }, status=400)

        categories = Infrastructure_Category.objects.filter(
            empresa_id=company_id, is_active=True
        ).values('id', 'name')

        return JsonResponse({
            'success': True,
            'data': list(categories)
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


def get_infrastructure_audit(request):
    response = {"success": False}

    try:
        context = user_data(request)
        subModule_id = 43
        company_id = context["company"]["id"]

        if not company_id:
            return JsonResponse({
                "success": False,
                "message": "No se encontró la empresa asociada al usuario."
            }, status=400)

        # Consultar auditorías de la empresa
        datos = InfrastructureAudit.objects.filter(
            company_id=company_id,
            is_active=True
        ).select_related(
            "company",
            "created_by"
        ).prefetch_related(
            "categories"
        ).order_by("-created_at")

        access = get_module_user_permissions(context, subModule_id)
        access = access["data"]["access"]

        data = []

        for item in datos:

            active_categories = item.categories.filter(is_active=True)

            categories_names = ", ".join(
                active_categories.values_list("name", flat=True)
            )

            categories_ids = list(
                active_categories.values_list("pk", flat=True)
            )

            categories_ids = [int(category_id) for category_id in categories_ids]

            total_assets = Infrastructure_Item.objects.filter(
                company_id=company_id,
                category_id__in=categories_ids,
                is_active=True
            ).aggregate(
                total=Sum("quantity")
            )["total"] or 0

            nombre_responsable = " ".join(
                filter(
                    None,
                    [
                        item.created_by.first_name if item.created_by else "",
                        item.created_by.last_name if item.created_by else ""
                    ]
                )
            )

            responsable = (
                nombre_responsable 
                or (item.created_by.username if item.created_by else "")
            )

            # Obtener activos registrados en esta auditoría
            audit_items = InfrastructureAuditItem.objects.filter(
                audit_id=item.id
            )

            total_audit_items = audit_items.count()

            # Obtener activos que ya fueron verificados
            verified_items = audit_items.filter(
                is_completed=True
            ).count()

            # Calcular porcentaje de avance
            progress = (
                round((verified_items / total_audit_items) * 100)
                if total_audit_items > 0 else 0
            )
            

            print("este es el responsable:", responsable)

            row = {
                "id": item.id,
                "row_id": item.id,
                "company_id": item.company_id,
                "company__name": item.company.name,

                "categories": categories_names,
                "categories_ids": categories_ids,

                "name": item.name,
                "total_assets": total_assets,
                "description": item.description or "",
                "start_date": item.start_date.strftime("%Y-%m-%d") if item.start_date else "",
                "end_date": item.end_date.strftime("%d-%m-%Y") if item.end_date else "Sin fecha",
                "status": item.status,
                "created_by": item.created_by_id,

                "responsible_audit": item.created_by_id,
                "responsible_audit": item.created_by_id,
                "responsible_name": responsable,

                "total_audit_items": total_audit_items,
                "verified_items": verified_items,
                "progress": progress,

                "btn_action": ""
            }
            print("esto contiene row:", row)

            # Botón actualizar
            if access["update"]:
                row["btn_action"] += (
                    "<button type='button' name='update' "
                    "class='btn btn-icon btn-sm btn-primary-light' "
                    "data-infrastructure-audit='update-audit' "
                    "data-id='{}' aria-label='Editar'>"
                    "<i class='fa-solid fa-pen'></i>"
                    "</button>\n"
                ).format(item.id)

            # Botón eliminar
            # if access["delete"]:
            #     row["btn_action"] += (
            #         "<button type='button' name='delete' "
            #         "class='btn btn-icon btn-sm btn-danger-light' "
            #         "data-infrastructure-audit='delete-audit' "
            #         "data-id='{}' aria-label='Eliminar'>"
            #         "<i class='fa-solid fa-trash'></i>"
            #         "</button>\n"
            #     ).format(item.id)

            data.append(row)

        response["data"] = data
        response["status"] = "success"
        response["success"] = True

        return JsonResponse(response)

    except Exception as e:
        print("Error al consultar las auditorías:", str(e))

        return JsonResponse({
            "success": False,
            "status": "error",
            "message": str(e)
        }, status=500)

# Editar auditoría
def update_infrastructure_audit(request):
    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "Método no permitido"
        }, status=405)

    try:
        context = user_data(request)
        company_id = context["company"]["id"]

        if not company_id:
            return JsonResponse({
                "status": "error",
                "message": "No se encontró la empresa asociada al usuario."
            }, status=400)

        audit_id = request.POST.get("id")

        if not audit_id:
            return JsonResponse({
                "status": "warning",
                "message": "No se especificó la auditoría que desea actualizar."
            })

        obj = InfrastructureAudit.objects.filter(
            id=audit_id,
            company_id=company_id,
            is_active=True
        ).first()

        if not obj:
            return JsonResponse({
                "status": "warning",
                "message": "La auditoría no existe o no pertenece a su empresa."
            })

        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()
        start_date = request.POST.get("start_date") or None
        end_date = request.POST.get("end_date") or None

        categories_ids = request.POST.getlist("audit_categories")

        if not name:
            return JsonResponse({
                "status": "warning",
                "message": "Ingrese el nombre de la auditoría."
            })

        if not start_date:
            return JsonResponse({
                "status": "warning",
                "message": "Seleccione la fecha de inicio."
            })

        start_date = parse_date(start_date)

        if not start_date:
            return JsonResponse({
                "status": "warning",
                "message": "La fecha de inicio no es válida."
            })

        if end_date:
            end_date = parse_date(end_date)

            if not end_date:
                return JsonResponse({
                    "status": "warning",
                    "message": "La fecha de finalización no es válida."
                })

            if end_date < start_date:
                return JsonResponse({
                    "status": "warning",
                    "message": "La fecha de finalización no puede ser anterior a la fecha de inicio."
                })

        if not categories_ids:
            return JsonResponse({
                "status": "warning",
                "message": "Seleccione al menos una categoría para la auditoría."
            })

        if InfrastructureAudit.objects.filter(
            name__iexact=name,
            company_id=company_id
        ).exclude(id=obj.id).exists():
            return JsonResponse({
                "status": "warning",
                "message": "Ya existe otra auditoría con ese nombre."
            })

        categories_ids = list(set(categories_ids))

        categories = Infrastructure_Category.objects.filter(
            id__in=categories_ids,
            empresa_id=company_id,
            is_active=True
        )

        if categories.count() != len(categories_ids):
            return JsonResponse({
                "status": "warning",
                "message": "Una o varias categorías seleccionadas no pertenecen a la empresa."
            })

        # Comprobar si existen sesiones
        tiene_sesiones = obj.sessions.exists()

        # No permitir cambiar categorías cuando ya existen sesiones
        if tiene_sesiones:
            categorias_actuales = set(
                obj.categories.values_list("id", flat=True)
            )

            categorias_nuevas = set(
                categories.values_list("id", flat=True)
            )

            if categorias_actuales != categorias_nuevas:
                return JsonResponse({
                    "status": "warning",
                    "message": (
                        "No es posible modificar las categorías porque "
                        "la auditoría ya tiene sesiones registradas."
                    )
                })

        with transaction.atomic():

            obj.name = name
            obj.description = description
            obj.start_date = start_date
            obj.end_date = end_date

            obj.save()

            obj.categories.set(categories)

            # Sincronizar activos solamente si no existen sesiones
            if not tiene_sesiones:

                assets = Infrastructure_Item.objects.filter(
                    company_id=company_id,
                    category_id__in=categories_ids,
                    is_active=True
                )

                asset_ids = assets.values_list("id", flat=True)

                # Eliminar activos que ya no corresponden a las categorías
                InfrastructureAuditItem.objects.filter(
                    audit=obj
                ).exclude(
                    item_id__in=asset_ids
                ).delete()

                # Identificar activos que ya están registrados
                existing_ids = InfrastructureAuditItem.objects.filter(
                    audit=obj
                ).values_list("item_id", flat=True)

                # Crear únicamente los activos nuevos
                nuevos_activos = [
                    InfrastructureAuditItem(
                        audit=obj,
                        item=item,
                        registered_quantity=item.quantity or 0
                    )
                    for item in assets.exclude(id__in=existing_ids)
                ]

                if nuevos_activos:
                    InfrastructureAuditItem.objects.bulk_create(
                        nuevos_activos
                    )

        return JsonResponse({
            "status": "success",
            "id": obj.id,
            "message": "Auditoría actualizada exitosamente."
        })

    except Exception as e:
        print("Error al actualizar la auditoría:", str(e))

        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)

def get_infrastructure_info_from_audit(request, audit_id):
    try:
        auditoria = InfrastructureAudit.objects.get(
            id=audit_id
        )

        info_html = render_to_string(
            "infrastructure/cards/audit_info.html",
            context={
                'audit': auditoria,
            },
            request=request
        )

        #tabla de activos
        audit_html = ""


        return JsonResponse({
            'info_html': info_html,
            'audit_html': audit_html,
        })

    except InfrastructureAudit.DoesNotExist:
        return JsonResponse({
            'error': 'Auditoría no encontrada'
        }, status=404)


# Crear sesión de auditoría
def add_infrastructure_audit_session(request):

    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "Método no permitido."
        }, status=405)

    try:
        context = user_data(request)
        company_id = context["company"]["id"]

        if not company_id:
            return JsonResponse({
                "success": False,
                "message": "No se encontró la empresa del usuario."
            }, status=400)

        audit_id = request.POST.get("audit_id")
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()
        responsible_id = request.POST.get("responsible_id") or None

        if not audit_id:
            return JsonResponse({
                "success": False,
                "message": "No se recibió la auditoría."
            }, status=400)

        if not name:
            return JsonResponse({
                "success": False,
                "message": "Ingrese el nombre de la sesión."
            }, status=400)

        # Verificar que la auditoría pertenezca a la empresa
        audit = InfrastructureAudit.objects.filter(
            id=audit_id,
            company_id=company_id,
            is_active=True
        ).first()

        if not audit:
            return JsonResponse({
                "success": False,
                "message": "No se encontró la auditoría."
            }, status=404)

        # No permitir crear sesiones en auditorías cerradas o canceladas
        if audit.status in ["CERRADA", "CANCELADA"]:
            return JsonResponse({
                "success": False,
                "message": "No se pueden crear sesiones en una auditoría cerrada o cancelada."
            }, status=400)

        # Validar responsable si fue seleccionado
        responsible = None

        if responsible_id:
            responsible = User.objects.filter(
                id=responsible_id
            ).first()

            if not responsible:
                return JsonResponse({
                    "success": False,
                    "message": "El responsable seleccionado no existe."
                }, status=400)

        with transaction.atomic():

            # Crear sesión
            session = InfrastructureAuditSession.objects.create(
                audit=audit,
                name=name,
                description=description,
                responsible=responsible,
                status="PENDIENTE"
            )

            # La auditoría pasa a estar en proceso
            if audit.status == "BORRADOR":
                audit.status = "EN_PROCESO"
                audit.save(update_fields=["status", "updated_at"])

        return JsonResponse({
            "success": True,
            "message": "Sesión creada correctamente.",
            "data": {
                "id": session.id,
                "name": session.name,
                "description": session.description or "",
                "status": session.status,
                "responsible": (
                    str(session.responsible)
                    if session.responsible else "Sin asignar"
                ),
                "created_at": session.created_at.strftime("%d/%m/%Y %H:%M")
            }
        })

    except Exception as e:
        print("Error al crear sesión de auditoría:", str(e))

        return JsonResponse({
            "success": False,
            "message": str(e)
        }, status=500)
    
# Consultar sesiones de una auditoría
def get_infrastructure_audit_sessions(request):

    try:
        context = user_data(request)
        company_id = context["company"]["id"]

        audit_id = request.GET.get("audit_id")

        if not audit_id:
            return JsonResponse({
                "success": False,
                "message": "No se recibió el ID de la auditoría.",
                "data": []
            }, status=400)

        audit = InfrastructureAudit.objects.filter(
            id=audit_id,
            company_id=company_id
        ).first()

        if not audit:
            return JsonResponse({
                "success": False,
                "message": "No se encontró la auditoría.",
                "data": []
            }, status=404)

        sessions = InfrastructureAuditSession.objects.filter(
            audit=audit
        ).select_related(
            "responsible"
        ).order_by("created_at")

        data = []

        for session in sessions:
            data.append({
                "id": session.id,
                "name": session.name,
                "description": session.description or "",
                "status": session.status,
                "responsible": (
                    str(session.responsible)
                    if session.responsible else "Sin asignar"
                ),
                "created_at": session.created_at.strftime(
                    "%d/%m/%Y %H:%M"
                )
            })

        return JsonResponse({
            "success": True,
            "data": data
        })

    except Exception as e:
        print("Error al consultar sesiones:", str(e))

        return JsonResponse({
            "success": False,
            "message": str(e),
            "data": []
        }, status=500)


@csrf_exempt
def add_infrastructure_audit_session(request):
    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "Método no permitido."
        }, status=405)

    try:
        context = user_data(request)
        company_id = context["company"]["id"]

        if not company_id:
            return JsonResponse({
                "success": False,
                "message": "No se encontró la empresa del usuario."
            }, status=400)

        audit_id = request.POST.get("audit_id")
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()
        responsible_id = request.POST.get("responsible_id") or None

        # Validaciones
        if not audit_id:
            return JsonResponse({
                "success": False,
                "message": "No se recibió el ID de la auditoría."
            }, status=400)

        if not name:
            return JsonResponse({
                "success": False,
                "message": "Ingrese el nombre de la sesión."
            }, status=400)

        # Verificar auditoría y empresa
        audit = InfrastructureAudit.objects.filter(
            id=audit_id,
            company_id=company_id,
            is_active=True
        ).first()

        if not audit:
            return JsonResponse({
                "success": False,
                "message": "No se encontró la auditoría."
            }, status=404)

        if audit.status in ["CERRADA", "CANCELADA"]:
            return JsonResponse({
                "success": False,
                "message": "No se pueden crear sesiones en una auditoría cerrada o cancelada."
            }, status=400)

        # Validar responsable
        responsible = None

        if responsible_id:
            responsible = User.objects.filter(
                id=responsible_id
            ).first()

            if not responsible:
                return JsonResponse({
                    "success": False,
                    "message": "El responsable seleccionado no existe."
                }, status=400)

        with transaction.atomic():

            session = InfrastructureAuditSession.objects.create(
                audit=audit,
                name=name,
                description=description,
                responsible=responsible,
                status="PENDIENTE"
            )

            # Cambiar estado de la auditoría
            if audit.status == "BORRADOR":
                audit.status = "EN_PROCESO"
                audit.save(update_fields=["status", "updated_at"])

        return JsonResponse({
            "success": True,
            "message": "Sesión creada correctamente.",
            "data": {
                "id": session.id,
                "name": session.name,
                "description": session.description or "",
                "status": session.status,
                "responsible": (
                    str(session.responsible)
                    if session.responsible else "Sin asignar"
                ),
                "created_at": session.created_at.strftime("%d/%m/%Y %H:%M")
            }
        })

    except Exception as e:
        print("Error al crear sesión de auditoría:", str(e))

        return JsonResponse({
            "success": False,
            "message": str(e)
        }, status=500)



# Tabla de activos correspondientes a una auditoría
# def get_infrastructure_items_audit(request):
#     try:
#         context = user_data(request)
#         company_id = context["company"]["id"]

#         audit_id = request.GET.get("audit_id")

#         if not audit_id:
#             return JsonResponse({
#                 "success": False,
#                 "message": "No se recibió el ID de la auditoría.",
#                 "data": []
#             }, status=400)

#         # Obtener la auditoría de la empresa
#         audit = InfrastructureAudit.objects.get(
#             id=audit_id,
#             company_id=company_id
#         )

#         # Obtener las categorías seleccionadas en la auditoría
#         category_ids = audit.categories.values_list("id", flat=True)

#         # Obtener los activos de esas categorías
#         datos = Infrastructure_Item.objects.filter(
#             company_id=company_id,
#             is_active=True,
#             category_id__in=category_ids
#         ).values(
#             "id",
#             "company_id",
#             "company__name",
#             "category_id",
#             "category__name",
#             "name",
#             "image",
#             "item_brand",
#             "description",
#             "quantity",
#             "cost",
#             "is_active",
#             "created_at",
#             "updated_at",
#         )

#         # Preparar información para DataTables
#         data = list(datos)

#         for item in data:

#             item["row_id"] = item["id"]
#             item["cantidad_encontrada"] = None
#             item["estado"] = "Pendiente"

#             if item["image"]:
#                 item["image"] = generate_presigned_url(
#                     bucket_name,
#                     item["image"]
#                 )

#             # Botón de desglose
#             item["btn_identifiers"] = (
#                 f"<button type='button' "
#                 f"class='btn btn-icon btn-sm btn-success-light' "
#                 f"data-infrastructure-item='view-identifiers' "
#                 f"data-id='{item['id']}' "
#                 f"aria-label='Ver desglose'>"
#                 f"<i class='fa-solid fa-list'></i>"
#                 f"</button>"
#             )

#         return JsonResponse({
#             "success": True,
#             "status": "success",
#             "data": data
#         })

#     except InfrastructureAudit.DoesNotExist:
#         return JsonResponse({
#             "success": False,
#             "message": "No se encontró la auditoría.",
#             "data": []
#         }, status=404)

#     except Exception as e:
#         return JsonResponse({
#             "success": False,
#             "message": str(e),
#             "data": []
#         }, status=500)

#obtner los activos de las categorias seleccionadas por auditorias para mostrar en sesion 
def get_infrastructure_audit_session_items(request):
    try:
        context = user_data(request)
        company_id = context["company"]["id"]

        session_id = request.GET.get("session_id")

        if not session_id:
            return JsonResponse({
                "success": False,
                "message": "No se recibió el ID de la sesión.",
                "data": []
            }, status=400)

        # Obtener sesión y validar que pertenezca a la empresa
        session = InfrastructureAuditSession.objects.select_related(
            "audit"
        ).filter(
            id=session_id,
            audit__company_id=company_id,
            audit__is_active=True
        ).first()

        if not session:
            return JsonResponse({
                "success": False,
                "message": "No se encontró la sesión o no pertenece a su empresa.",
                "data": []
            }, status=404)

        # Obtener los activos registrados en la auditoría
        audit_items = InfrastructureAuditItem.objects.filter(
            audit_id=session.audit_id
        ).select_related(
            "item",
            "item__category"
        ).order_by("item__name")

        # Obtener los detalles de esta sesión
        session_details = {
            detail.audit_item_id: detail
            for detail in InfrastructureAuditSessionDetail.objects.filter(
                session=session
            )
        }

      

        data = []

        for audit_item in audit_items:

            item = audit_item.item
            detail = session_details.get(audit_item.id)

            # Obtener URL de evidencia guardada en S3
            evidence_url = None
    
            if detail and detail.evidence:
                evidence_url = generate_presigned_url(
                    bucket_name,
                    detail.evidence.name
                )

            cantidad_encontrada = (
                detail.found_quantity if detail else None
            )

            diferencia = (
                audit_item.registered_quantity - cantidad_encontrada
                if detail else None
            )

            image_url = None

            if item.image:
                image_url = generate_presigned_url(
                    bucket_name,
                    item.image.name
                )

            # Botón de desglose
            btn_identifiers = (
                f"<button type='button' "
                f"class='btn btn-icon btn-sm btn-success-light' "
                f"data-infrastructure-item='view-identifiers' "
                f"data-id='{item.id}' "
                f"aria-label='Ver desglose'>"
                f"<i class='fa-solid fa-list'></i>"
                f"</button>"
            )

            data.append({
                "id": audit_item.id,
                "item_id": item.id,
                "category": item.category.name if item.category else "",
                "name": item.name,
                "image": image_url,
                "description": item.description or "",
                "item_brand": item.item_brand or "",
                "cost": item.cost or 0,
                "btn_identifiers": btn_identifiers,
                "registered_quantity": audit_item.registered_quantity,
                "found_quantity": cantidad_encontrada,
                "difference": diferencia,
                "observations": detail.observations if detail else "",
                "is_completed": audit_item.is_completed,
                "evidence": evidence_url,
            })

        return JsonResponse({
            "success": True,
            "status": "success",
            "session_id": session.id,
            "audit_id": session.audit_id,
            "data": data
        })

    except Exception as e:
        print("Error al obtener activos de la sesión:", str(e))

        return JsonResponse({
            "success": False,
            "message": str(e),
            "data": []
        }, status=500)


# Guardar verificación de un activo en una sesión de auditoría
@csrf_exempt
def save_infrastructure_audit_session_detail(request):

    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "Método no permitido."
        }, status=405)

    try:
        context = user_data(request)
        company_id = context["company"]["id"]

        if not company_id:
            return JsonResponse({
                "success": False,
                "message": "No se encontró la empresa del usuario."
            }, status=400)

        session_id = request.POST.get("session_id")
        audit_item_id = request.POST.get("audit_item_id")
        found_quantity = request.POST.get("found_quantity")
        observations = request.POST.get("observations", "").strip()
        evidence = request.FILES.get("evidence")

        if not session_id or not audit_item_id:
            return JsonResponse({
                "success": False,
                "message": "Falta el ID de la sesión o del activo."
            }, status=400)

        if found_quantity is None or found_quantity.strip() == "":
            return JsonResponse({
                "success": False,
                "message": "Ingrese la cantidad encontrada."
            }, status=400)

        try:
            found_quantity = int(found_quantity)

            if found_quantity < 0:
                raise ValueError

        except (ValueError, TypeError):
            return JsonResponse({
                "success": False,
                "message": "La cantidad encontrada debe ser un número entero mayor o igual a cero."
            }, status=400)

        # Validar sesión y empresa
        session = InfrastructureAuditSession.objects.filter(
            id=session_id,
            audit__company_id=company_id,
            audit__is_active=True
        ).first()

        if not session:
            return JsonResponse({
                "success": False,
                "message": "No se encontró la sesión de auditoría."
            }, status=404)

        if session.status in ["COMPLETADA", "CANCELADA"]:
            return JsonResponse({
                "success": False,
                "message": "No se pueden modificar los activos de una sesión completada o cancelada."
            }, status=400)

        # Validar que el activo pertenezca a la auditoría de la sesión
        audit_item = InfrastructureAuditItem.objects.filter(
            id=audit_item_id,
            audit_id=session.audit_id
        ).first()

        if not audit_item:
            return JsonResponse({
                "success": False,
                "message": "El activo no pertenece a esta auditoría."
            }, status=404)

        # Verificar si el activo ya fue auditado
        if audit_item.is_completed:
            return JsonResponse({
                "success": False,
                "message": "Este activo ya fue verificado y no puede auditarse nuevamente."
            }, status=400)
        
        with transaction.atomic():

            # Bloquear el activo mientras se realiza la verificación
            audit_item = InfrastructureAuditItem.objects.select_for_update().filter(
                id=audit_item_id,
                audit_id=session.audit_id
            ).first()

            if not audit_item:
                return JsonResponse({
                    "success": False,
                    "message": "El activo no pertenece a esta auditoría."
                }, status=404)

            # Verificar si el activo ya fue auditado
            if audit_item.is_completed:
                return JsonResponse({
                    "success": False,
                    "message": "Este activo ya fue verificado y no puede auditarse nuevamente."
                }, status=400)

            detail, created = InfrastructureAuditSessionDetail.objects.get_or_create(
                session=session,
                audit_item=audit_item,
                defaults={
                    "found_quantity": found_quantity,
                    "observations": observations,
                    "verified_by": request.user
                }

            )

            if not created:
                detail.found_quantity = found_quantity
                detail.observations = observations
                detail.verified_by = request.user

            # Guardar evidencia en S3 si existe
            if evidence:
                folder_path = (
                    f"docs/{company_id}/infrastructure_audits/"
                    f"{session.audit_id}/{session.id}/{audit_item.id}/"
                )

                file_name, extension = os.path.splitext(evidence.name)

                new_name = f"evidence_{audit_item.id}{extension}"

                s3_path = folder_path + new_name

                upload_to_s3(evidence, bucket_name, s3_path)

                detail.evidence = s3_path

            detail.save()


            # Marcar el activo como verificado
            audit_item.is_completed = True
            audit_item.completed_at = timezone.now()
            audit_item.save(update_fields=["is_completed", "completed_at"])

            # Marcar la sesión como iniciada
            if session.status == "PENDIENTE":
                session.status = "EN_PROCESO"
                session.save(update_fields=["status"])


        return JsonResponse({
            "success": True,
            "message": "La verificación del activo se guardó correctamente.",
            "detail_id": detail.id,
            "found_quantity": detail.found_quantity,
            "observations": detail.observations,
            "created": created
        })

    except Exception as e:
        print("Error al guardar la verificación del activo:", str(e))

        return JsonResponse({
            "success": False,
            "message": str(e)
        }, status=500)


# Finalizar auditoría y todas sus sesiones
@csrf_exempt
def finish_infrastructure_audit(request):

    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "Método no permitido."
        }, status=405)

    try:
        context = user_data(request)
        company_id = context["company"]["id"]

        audit_id = request.POST.get("audit_id")

        if not company_id:
            return JsonResponse({
                "success": False,
                "message": "No se encontró la empresa del usuario."
            }, status=400)

        if not audit_id:
            return JsonResponse({
                "success": False,
                "message": "No se recibió el ID de la auditoría."
            }, status=400)

        with transaction.atomic():

            # Bloquear auditoría
            audit = InfrastructureAudit.objects.select_for_update().filter(
                id=audit_id,
                company_id=company_id,
                is_active=True
            ).first()

            if not audit:
                return JsonResponse({
                    "success": False,
                    "message": "No se encontró la auditoría."
                }, status=404)

            if audit.status in ["CERRADA", "CANCELADA"]:
                return JsonResponse({
                    "success": False,
                    "message": "La auditoría ya está cerrada o cancelada."
                }, status=400)

            # Obtener y bloquear las sesiones
            sessions = list(
                InfrastructureAuditSession.objects.select_for_update().filter(
                    audit=audit
                )
            )

            if not sessions:
                return JsonResponse({
                    "success": False,
                    "message": "No puedes finalizar una auditoría sin sesiones."
                }, status=400)

            # Bloquear los activos de la auditoría
            audit_items = list(
                InfrastructureAuditItem.objects.select_for_update().filter(
                    audit=audit
                ).select_related("item")
            )

            if not audit_items:
                return JsonResponse({
                    "success": False,
                    "message": "La auditoría no tiene activos registrados."
                }, status=400)

            # Identificar activos pendientes
            pending_items = [
                audit_item.item.name
                for audit_item in audit_items
                if not audit_item.is_completed
            ]

            if pending_items:
                return JsonResponse({
                    "success": False,
                    "message": (
                        f"No se puede finalizar la auditoría. "
                        f"Hay {len(pending_items)} activos pendientes de verificar."
                    ),
                    "pending_items": pending_items
                }, status=400)

            # Fecha y hora de finalización
            now = timezone.now()

            # Finalizar todas las sesiones
            InfrastructureAuditSession.objects.filter(
                audit=audit
            ).update(
                status="COMPLETADA",
                end_date=now
            )

            # Finalizar auditoría general
            audit.status = "CERRADA"
            audit.end_date = timezone.localdate()
            audit.save(update_fields=["status", "end_date", "updated_at"])

        return JsonResponse({
            "success": True,
            "message": "La auditoría y todas sus sesiones se finalizaron correctamente.",
            "audit_id": audit.id,
            "status": audit.status,
            "sessions_completed": len(sessions),
            "end_date": str(audit.end_date)
        })

    except Exception as e:
        print("Error al finalizar auditoría:", str(e))

        return JsonResponse({
            "success": False,
            "message": str(e)
        }, status=500)


#Generar reporte 
def generate_infrastructure_audit_report(request, audit_id):

    try:
        context = user_data(request)
        company_id = context["company"]["id"]

        # Consultar únicamente auditorías de la empresa que estén cerradas
        audit = get_object_or_404(
            InfrastructureAudit.objects.select_related(
                "company",
                "created_by"
            ).prefetch_related("categories"),
            id=audit_id,
            company_id=company_id,
            is_active=True,
            status="CERRADA"
        )

        # Consultar activos registrados en la auditoría
        audit_items = InfrastructureAuditItem.objects.filter(
            audit_id=audit.id
        ).select_related(
            "item",
            "item__category"
        ).order_by(
            "item__category__name",
            "item__name"
        )

        # Consultar todos los detalles de verificación
        details = InfrastructureAuditSessionDetail.objects.filter(
            audit_item__audit_id=audit.id
        ).select_related(
            "session",
            "verified_by"
        )

        details_by_item = {
            detail.audit_item_id: detail
            for detail in details
        }

        # Preparar información de los activos
        report_items = []

        for audit_item in audit_items:

            detail = details_by_item.get(audit_item.id)

            found_quantity = (
                detail.found_quantity if detail else 0
            )

            difference = (
                audit_item.registered_quantity - found_quantity
                if detail else None
            )

            evidence_url = None

            if detail and detail.evidence:
                evidence_url = generate_presigned_url(
                    bucket_name,
                    detail.evidence.name
                )

            report_items.append({
                "name": audit_item.item.name,
                "category": audit_item.item.category.name,
                "registered_quantity": audit_item.registered_quantity,
                "found_quantity": found_quantity if detail else None,
                "difference": difference,
                "observations": detail.observations if detail else "",
                "verified_by": (
                    detail.verified_by.get_full_name()
                    or detail.verified_by.username
                    if detail and detail.verified_by
                    else "Sin información"
                ),
                "verified_at": detail.verified_at if detail else None,
                "evidence": evidence_url,
                "is_completed": audit_item.is_completed,
            })

        total_items = audit_items.count()
        verified_items = audit_items.filter(is_completed=True).count()
        pending_items = total_items - verified_items

        progress = (
            round((verified_items / total_items) * 100)
            if total_items else 0
        )

        # Consultar sesiones
        sessions = InfrastructureAuditSession.objects.filter(
            audit_id=audit.id
        ).select_related(
            "responsible"
        ).order_by("created_at")

        report_context = {
            "audit": audit,
            "report_items": report_items,
            "sessions": sessions,
            "total_items": total_items,
            "verified_items": verified_items,
            "pending_items": pending_items,
            "progress": progress,
            "categories": audit.categories.all(),
        }

        # Generar HTML del reporte
        html_string = render_to_string(
            "infrastructure/infrastructure/audit_report.html",
            report_context
        )
        
        # Convertir HTML a PDF
        pdf_file = HTML(
            string=html_string,
            base_url=request.build_absolute_uri("/")
        ).write_pdf()

        response = HttpResponse(
            pdf_file,
            content_type="application/pdf"
        )

        response["Content-Disposition"] = (
            f'inline; filename="auditoria_{audit.id}.pdf"'
        )

        return response

    except Exception as e:
        print("Error al generar reporte de auditoría:", str(e))

        return HttpResponse(
            f"No fue posible generar el reporte: {str(e)}",
            status=500
        )