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


from django.http import JsonResponse, Http404
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
    response = { "status": "error", "message": "Sin procesar" }
    context = user_data(request)
    dt = request.GET
    subModule_id = 23
    isList = dt.get("isList", False)
    company_id = context["company"]["id"]
    datos = Infrastructure_Category.objects.filter(empresa__id=company_id).distinct().values()

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

    company_id = context["company"]["id"]
    category_id = dt.get("category_id", None)
    is_active = dt.get("is_active", True)
    location_id = dt.get("item_location", None) 
    cantidad = dt.get("quantity",1)
    name = dt.get("name", "").strip()
    print("esta es la ubicación de la empresa:", location_id)
    if not category_id:
        response["status"] = "warning"
        response["message"] = "Ingrese una categoria valida"
        print("Advertencia: No se proporcionó category_id")
        return JsonResponse(response)

    if Infrastructure_Item.objects.filter(name__iexact=name, company_id=company_id).exists():
        response["status"] = "warning"
        response["message"] = "Ya existe un registro con ese nombre en la empresa"
        return JsonResponse(response)
    
    try:
        obj = Infrastructure_Item(
            company_id = company_id,
            category_id = category_id,
            name = dt.get("name"),
            quantity = dt.get("quantity"),
            cost = dt.get("cost"),
            description = dt.get("description"),
            is_active = is_active,
            start_date = dt.get("start_date"),
            location_id = location_id, 

        )
        obj.save()
        _id = obj.id
        print(f"Infrastructure_Item creado con ID: {_id}")

        # Guardar archivos en S3 si existen
        if 'technical_sheet' in request.FILES and request.FILES['technical_sheet']:
            load_file = request.FILES.get('technical_sheet')
            folder_path = f"docs/{company_id}/infrastructure_items/{_id}/technical_sheet/"
            file_name, extension = os.path.splitext(load_file.name)
            new_name = f"technical_sheet_{_id}{extension}"
            s3_path = folder_path + new_name

            print(f"Subiendo technical_sheet a: {s3_path}")
            upload_to_s3(load_file, bucket_name, s3_path)
            obj.technical_sheet = s3_path
            print("Technical sheet subida exitosamente.")

        if 'invoice' in request.FILES and request.FILES['invoice']:
            load_file = request.FILES.get('invoice')
            folder_path = f"docs/{company_id}/infrastructure_items/{_id}/invoice/"
            file_name, extension = os.path.splitext(load_file.name)
            new_name = f"invoice_{_id}{extension}"
            s3_path = folder_path + new_name

            print(f"Subiendo invoice a: {s3_path}")
            upload_to_s3(load_file, bucket_name, s3_path)
            obj.invoice = s3_path
            print("Invoice subida exitosamente.")

        if 'image' in request.FILES and request.FILES['image']:
            load_file = request.FILES.get('image')
            folder_path = f"docs/{company_id}/infrastructure_items/{_id}/image/"
            file_name, extension = os.path.splitext(load_file.name)
            new_name = f"image_{_id}{extension}"
            s3_path = folder_path + new_name

            print(f"Subiendo image a: {s3_path}")
            upload_to_s3(load_file, bucket_name, s3_path)
            obj.image = s3_path
            print("Image subida exitosamente.")

        obj.save()

        generate_identificador(_id,company_id, cantidad)
        print("Infrastructure_Item actualizado con rutas de archivos.")

        response["id"] = obj.id
        response["status"] = "success"
        response["message"] = "Registro guardado exitosamente"
    except Exception as e:
        print("Error al guardar el Infrastructure_Item:", str(e))
        response["status"] = "error"
        response["message"] = str(e)

    return JsonResponse(response)


def generate_identificador(item_id, company_id, cantidad):
    try:
        item = Infrastructure_Item.objects.get(id=item_id)
        company = Company.objects.get(id=company_id)

        base_name = item.name.replace(' ', '').upper()[:3]
        company_code = company.name.replace(' ', '').upper()[:3]
        prefix = f"{company_code}-{base_name}-"

        print(f"Generando identificadores para {cantidad} items de '{item.name}'")

        # Buscar el último número usado con ese prefijo
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

        for i in range(1, int(cantidad) + 1):
            number = last_number + i
            identifier = f"{prefix}{str(number).zfill(4)}"

            InfrastructureItemDetail.objects.create(
                item=item,
                company=company,
                name=item.name,
                identifier=identifier
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

    datos = Infrastructure_Item.objects.filter(company_id = company_id).values(
        "id",
        "company_id", "company__name",
        "category_id", "category__name",
        "name", "description", "quantity","cost",
        "is_active", "start_date","technical_sheet",
        "invoice", "image",
        "location_id", "location__name",

    )
    if isList:
        datos = datos.filter(is_active = True).values("id", "category_id", "category__name", "name")
        if category_id:
            datos = datos.filter(category_id = category_id)
    else:
        access = get_module_user_permissions(context, subModule_id)
        access = access["data"]["access"]
        for item in datos:

            if item["technical_sheet"]:
                item["technical_sheet"] = generate_presigned_url(bucket_name, item["technical_sheet"])  
            else:
                item["technical_sheet"] = None
            if item["invoice"]:
                item["invoice"] = generate_presigned_url(bucket_name, item["invoice"])
            
            item["btn_action"] = ""            

            item["row_id"] = item["id"] 
            
            if access["update"]:
                item["btn_action"] += "<button type='button' name='update' class='btn btn-icon btn-sm btn-primary-light' data-infrastructure-item='update-item' aria-label='info'>" \
                    "<i class=\"fa-solid fa-pen\"></i>" \
                "</button>\n"
            if access["delete"]:
                item["btn_action"] += "<button type='button' name='delete' class='btn btn-icon btn-sm btn-danger-light' data-infrastructure-item='delete-item' aria-label='delete'>" \
                    "<i class='fa-solid fa-trash'></i>" \
                "</button>\n"
            
            
            item["btn_action"] += f"<button type='button' name='identifiers' class='btn btn-icon btn-sm btn-success-light' data-infrastructure-item='view-identifiers' data-id='{item['id']}' aria-label='identifiers'>" \
                    "<i class=\"fa-solid fa-list\"></i>"\
                "</button>\n"
            
            if item["image"]:
                img_url = generate_presigned_url(bucket_name, item["image"])
                item["btn_action"] += f"<a href='{img_url}' target='_blank' class='btn btn-icon btn-sm btn-info-light' aria-label='view-image'>" \
                    "<i class='fa-solid fa-image'></i>" \
                    "</a>\n"




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
            old_quantity = obj.quantity  # Cantidad anterior

            # Actualizar campos
            obj.category_id = category_id
            obj.name = dt.get("name")
            obj.quantity = int(dt.get("quantity"))
            obj.description = dt.get("description")
            obj.is_active = is_active
            obj.start_date = dt.get("start_date")
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

            new_name = obj.name
            new_quantity = obj.quantity

            # Manejo de detalles
            current_details = InfrastructureItemDetail.objects.filter(item=obj)
            current_count = current_details.count()

            if new_quantity < current_count:
                # Eliminar excedente
                to_delete = current_details.order_by('-id')[:current_count - new_quantity]
                to_delete.delete()

            elif new_quantity > current_count:
                # Agregar los que faltan
                base_name = new_name.replace(" ", "").upper()[:3]
                company_code = str(company_id).zfill(3)
                prefix = f"{company_code}-{base_name}-"

                existing_identifiers = (
                    InfrastructureItemDetail.objects
                    .filter(identifier__startswith=prefix)
                    .values_list("identifier", flat=True)
                )

                existing_numbers = []
                for ident in existing_identifiers:
                    try:
                        num = int(ident.split("-")[-1])
                        existing_numbers.append(num)
                    except ValueError:
                        pass

                next_number = max(existing_numbers, default=0) + 1

                for i in range(new_quantity - current_count):
                    identifier = f"{prefix}{str(next_number + i).zfill(4)}"
                    InfrastructureItemDetail.objects.create(
                        item=obj,
                        company_id=company_id,
                        name=new_name,
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
    id = dt.get("id")

    if id == None:
        response["error"] = {"message": "Proporcione un id valido"}
        response["message"] = "Proporcione un id valido"
        return JsonResponse(response)
    try:
        obj = Infrastructure_Item.objects.get(id = id)
    except Infrastructure_Item.DoesNotExist:
        response["error"] = {"message": "El objeto no existe"}
        response["message"] = "El objeto no existe"
        return JsonResponse(response)
    else:
        obj.delete()
    response["success"] = True
    response["status"] = "success"
    response["message"] = "Eliminado correctamente"
    return JsonResponse(response)


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
    response = {"status": "error", "message": "Sin procesar"}
    context = user_data(request)
    dt = request.POST
    id = dt.get("id")

    if id == None:
        response["error"] = {"message": "Proporcione un id valido"}
        response["message"] = "Proporcione un id valido"
        return JsonResponse(response)
    try:
        obj = Infrastructure_Category.objects.get(id = id)
    except Infrastructure_Category.DoesNotExist:
        response["error"] = {"message": "El objeto no existe"}
        response["message"] = "El objeto no existe"
        return JsonResponse(response)
    else:
        obj.delete()
    response["success"] = True
    response["status"] = "success"
    response["message"] = "Eliminado correctamente"
    return JsonResponse(response)



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
            company_id = request.POST.get('company')

            print(f"Nombre de ubicación: {name}, ID de empresa: {company_id}")

            if not name or not company_id:
                return JsonResponse({'success': False, 'message': 'Los campos son requeridos.'}, status=400)

            # Verificar que no exista una ubicación con el mismo nombre
            if Items_locations.objects.filter(name__iexact=name).exists():
                print('Ya existe una ubicación con ese nombre para esta empresa.') 
                return JsonResponse({'success': False, 'message': 'Ya existe una ubicación con ese nombre para esta empresa.'}, status=400)

            company = get_object_or_404(Company, id=company_id)

            # Crear la nueva ubicación
            new_location = Items_locations.objects.create(
                name=name,
                company=company,
            )

            # Retornar la nueva ubicación para actualizar el select
            return JsonResponse({'success': True, 'message': 'Ubicación agregada exitosamente.', 'new_location': {
                'id': new_location.id,
                'name': new_location.name
            }})

        except Exception as e:
            print(f"Error al agregar ubicación: {str(e)}")
            return JsonResponse({'success': False, 'message': 'Error interno del servidor.'}, status=500)

    return JsonResponse({'success': False, 'message': 'Método de solicitud no válido.'}, status=405)





def get_infrastructure_item_details(request):
    item_id = request.GET.get("id")
    data = []

    if item_id:
        registros = InfrastructureItemDetail.objects.filter(item_id=item_id).values(
            "id", 
            "identifier", 
            "responsible__id",  
            "responsible__first_name",  
            "responsible__last_name",  
            "assignment_date"
        )
        for r in registros:
            tiene_responsable = r["responsible__first_name"] and r["responsible__last_name"]
            responsable = f"{r['responsible__first_name']} {r['responsible__last_name']}".strip() if tiene_responsable else ""

            # Botón QR solo si tiene responsable
            btn_qr = ""
            if tiene_responsable:
                btn_qr = f"""
                    <button type='button' name='qr_code' class='btn btn-icon btn-sm btn-info-light generate-qr' 
                            data-infrastructure-item='qr_code' data-id='{r['id']}' aria-label='qr_code'>
                        <i class="fa-solid fa-qrcode"></i>
                    </button>
                """

            data.append({
                "id": r["id"],
                "identificador": r["identifier"],
                "responsable": responsable if responsable else "Sin asignar",
                "fecha_asignacion": r["assignment_date"].strftime('%Y-%m-%d') if r["assignment_date"] else "",
                "responsable_id": r["responsible__id"] if tiene_responsable else None,
                "tiene_responsable": bool(tiene_responsable), 
                "btn_qr": btn_qr
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
    if request.method == "POST":
        detalle_id = request.POST.get("id")
        responsable_id = request.POST.get("responsable")

        try:
            detalle = InfrastructureItemDetail.objects.get(id=detalle_id)
            detalle.responsible_id = responsable_id
            detalle.assignment_date = timezone.now().date()
            detalle.save()
            return JsonResponse({
                "success": True,
                "message": "Responsable asignado correctamente."
            })
        except InfrastructureItemDetail.DoesNotExist:
            return JsonResponse({
                "success": False,
                "message": "No se encontró el registro."
            })
    return JsonResponse({
        "success": False,
        "message": "Método no permitido."
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
            company_id=company_id
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
        identifier__item__company_id=company_id
    ).values(
        "id",
        "identifier__identifier", 
        "identifier__item__name", 
        "type_maintenance",
        "date",
        "provider__name",
        "cost",
        "general_notes"
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
        except Services.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Service not found'})

        maintenance.delete()

        return JsonResponse({'success': True, 'message': 'Servicio eliminado correctamente!'})

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
        maintenance = Infrastructure_maintenance.objects.select_related('identifier__item').get(id=maintenance_id)
        detail = maintenance.identifier
        image_url = None
        
        if detail.item.image:
            image_url = generate_presigned_url(AWS_BUCKET_NAME, str(detail.item.image))
        detail_html = render_to_string("infrastructure/cards/infraestructure_info.html", context = {
            'detail': detail,
            'item': detail.item,
            'id': maintenance.id,
            'image' : image_url
        })
        
        action2 = []
        for key, value in ast.literal_eval(maintenance.actions).items():
            action2.append({ "name":key, "status" : value})
            
        image_url = None
        if maintenance.comprobante:
            image_url = generate_presigned_url(AWS_BUCKET_NAME, str(maintenance.comprobante))
        maintenance_html = render_to_string("infrastructure/cards/maintenance_infraestructure_info.html", context = {
            'detail': maintenance,
            'item': detail.item,
            'actions' : action2,
            'image': image_url
        })
        
        return JsonResponse({
            'detail_html': detail_html,
            'maintenance_html': maintenance_html
        })
    except Infrastructure_maintenance.DoesNotExist:
        return JsonResponse({'error': 'Mantenimiento no encontrado'}, status=404)




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