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
    
    if context["access"]["read"]:
        template = "infrastructure/infrastructure-category.html"
    else:
        template = "error/access_denied.html"
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
    
    if context["access"]["read"]:
        template = "infrastructure/infrastructure-items.html"
    else:
        template = "error/access_denied.html"
    return render(request, template , context)

@login_required
def infrastructure_review_view(request):
    context = user_data(request)
    module_id = 4
    subModule_id = 24
    request.session["last_module_id"] = module_id

    access = get_module_user_permissions(context, subModule_id)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]
    
    if context["access"]["read"]:
        template = "infrastructure/review.html"
    else:
        template = "error/access_denied.html"
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
    category_id = dt.get("category_id", None)
    is_active = dt.get("is_active", True)

    if not category_id:
        response["status"] = "warning"
        response["message"] = "Ingrese una categoria valida"
        return JsonResponse(response)

    try:
        obj = Infrastructure_Item(
            company_id = company_id,
            category_id = category_id,
            name = dt.get("name"),
            quantity = dt.get("quantity"),
            description = dt.get("description"),
            is_active = is_active,
            time_unit = dt.get("time_unit"),
            start_date = dt.get("start_date"),
            time_quantity = dt.get("time_quantity")
        )
        obj.save()

        response["id"] = obj.id
        response["status"] = "success"
        response["message"] = "Registro guardado exitosamente"
    except Exception as e:
        response["status"] = "error"
        response["message"] = str(e)

    return JsonResponse(response)

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
        "name", "description", "quantity",
        "is_active", "start_date",
        "time_quantity", "time_unit",
        "created_at"
    )
    if isList:
        datos = datos.filter(is_active = True).values("id", "category_id", "category__name", "name")
        if category_id:
            datos = datos.filter(category_id = category_id)
    else:
        access = get_module_user_permissions(context, subModule_id)
        access = access["data"]["access"]
        for item in datos:
            item["btn_action"] = ""
            if access["update"]:
                item["btn_action"] += "<button type='button' name='update' class='btn btn-icon btn-sm btn-primary-light' data-infrastructure-item='update-item' aria-label='info'>" \
                    "<i class=\"fa-solid fa-pen\"></i>" \
                "</button>\n"
            if access["delete"]:
                item["btn_action"] += "<button type='button' name='delete' class='btn btn-icon btn-sm btn-danger-light' data-infrastructure-item='delete-item' aria-label='delete'>" \
                    "<i class='fa-solid fa-trash'></i>" \
                "</button>"

    response["data"] = list(datos)
    response["status"] = "success"
    return JsonResponse(response)

def update_infrastructure_item(request):
    response = {"status": "error", "message": "Sin procesar"}
    context = user_data(request)
    dt = request.POST
    company_id = context["company"]["id"]
    category_id = dt.get("category_id", None)
    is_active = dt.get("is_active", True)
    id = dt.get("id")

    if not category_id:
        response["status"] = "warning"
        response["message"] = "Ingrese una categoría válida"
        return JsonResponse(response)

    try:
        # Obtener el objeto de infraestructura existente
        obj = Infrastructure_Item.objects.get(id = id)
        
        # Actualizar los campos del objeto
        obj.category_id = category_id
        obj.name = dt.get("name")
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



def add_infrastructure_review(request):
    response = {"status": "error", "message": "Sin procesar"}
    context = user_data(request)
    dt = request.POST
    company_id = context["company"]["id"]
    category_id = dt.get("category_id", 1)
    item_id = dt.get("item_id", 1)
    reviewer_id = dt.get("reviewer_id")

    try:
        with transaction.atomic():
            obj = Infrastructure_Review(
                category_id = category_id,
                item_id = item_id,
                checked = dt.get("checked"),
                notes = dt.get("notes"),
                date = dt.get("date"),
                reviewer_id = reviewer_id
            )
            obj.save()
            id = obj.id

            if 'file' in request.FILES and request.FILES['file']:
                load_file = request.FILES['file']
                folder_path = f"docs/{company_id}/infrastructure/review/"
                fs = FileSystemStorage(location=settings.MEDIA_ROOT)

                file_name, extension = os.path.splitext(load_file.name)
                new_name = f"review_{id}{extension}"

                # Guardar archivo
                fs.save(folder_path + new_name, load_file)

                # Guardar ruta en la tabla
                obj.file = folder_path + new_name
                obj.save()

        response["id"] = obj.id
        response["status"] = "success"
        response["message"] = "Registro guardado exitosamente"
    except Exception as e:
        response["status"] = "error"
        response["message"] = str(e)

    return JsonResponse(response)

def get_infrastructure_reviews(request):
    response = {"status": "error", "message": "Sin procesar"}
    context = user_data(request)
    dt = request.GET
    subModule_id = 25
    company_id = context["company"]["id"]
    category = dt.get("category", None)
    item = dt.get("item", None)
    reviewer_id = dt.get("reviewer_id")

    datos = Infrastructure_Review.objects.filter(item__company_id = company_id).values(
        "id",
        "category_id", "category__name",
        "item_id", "item__name",
        "checked", "notes", "date",
        "reviewer_id", "reviewer__first_name", "reviewer__last_name",
        "file"
    )

    access = get_module_user_permissions(context, subModule_id)
    access = access["data"]["access"]
    for item in datos:
        item["btn_action"] = ""
        if access["update"]:
            item["btn_action"] += "<button type='button' name='update' class='btn btn-icon btn-sm btn-primary-light' data-infrastructure-review='update-item' aria-label='info'>" \
                "<i class=\"fa-solid fa-pen\"></i>" \
            "</button>\n"
        if access["delete"]:
            item["btn_action"] += "<button type='button' name='delete' class='btn btn-icon btn-sm btn-danger-light' data-infrastructure-review='delete-item' aria-label='delete'>" \
                "<i class='fa-solid fa-trash'></i>" \
            "</button>"

    response["data"] = list(datos)
    response["status"] = "success"
    response["message"] = "Datos cargados exitosamente"
    return JsonResponse(response)

def generates_review(request):
    items = Infrastructure_Item.objects.all().exclude(is_active=False)

    for item in items:
        latest_review = Infrastructure_Review.objects.filter(
            item=item, 
            category=item.category, 
            item__company=item.company
        ).order_by('-id').first()

        has_passed, message, time_passed, period_type, current_date, fecha_save = calc_date(
            item.start_date, item.time_unit, item.time_quantity
        )

        if has_passed:
            exist_review = Infrastructure_Review.objects.filter(
                category_id=item.category_id, item_id=item.id, date=fecha_save
            )
            if not exist_review:
                obj = Infrastructure_Review(
                    category_id=item.category_id,
                    item_id=item.id,
                    checked="",
                    notes="",
                    date=fecha_save,
                    reviewer_id=""
                )
                obj.save()

    return JsonResponse({"message": "Review generation complete"}, safe=False)

def calc_date(start_date, period_type, period_quantity):
    try:
        # Convertir la fecha de inicio a una cadena si es un objeto de tipo date
        if isinstance(start_date, date):
            start_date = start_date.strftime('%Y-%m-%d')
        
        # Convertir la cadena de la fecha de inicio a un objeto datetime
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        
        # Obtener la fecha actual del servidor
        current_date = datetime.now().date()
        
        # Calcular la fecha objetivo basada en el tipo de período y la cantidad
        if period_type == 'day':
            target_date = start_date_obj + timedelta(days=int(period_quantity))
        elif period_type == 'month':
            target_date = start_date_obj + relativedelta(months=int(period_quantity))
        elif period_type == 'year':
            target_date = start_date_obj + relativedelta(years=int(period_quantity))
        else:
            return False, "Tipo de período inválido. Por favor use 'day', 'month', o 'year'.", None, None, None
        
        # Determinar si el período ha pasado
        has_passed = current_date >= target_date

        # Calcular el tiempo pasado
        if period_type == 'day':
            time_passed = (current_date - start_date_obj).days
        elif period_type == 'month':
            time_passed = relativedelta(current_date, start_date_obj).months + (relativedelta(current_date, start_date_obj).years * 12)
        elif period_type == 'year':
            time_passed = relativedelta(current_date, start_date_obj).years

        # Calcular la fecha guardada (fecha_save) basada en la fecha de inicio y el tiempo pasado
        if period_type == 'day':
            fecha_save = start_date_obj + timedelta(days=time_passed)
        elif period_type == 'month':
            fecha_save = start_date_obj + relativedelta(months=time_passed)
        elif period_type == 'year':
            fecha_save = start_date_obj + relativedelta(years=time_passed)

        if has_passed:
            return True, "La fecha objetivo se ha alcanzado o pasado.", time_passed, period_type, current_date, fecha_save
        else:
            return False, "La fecha objetivo aún no se ha alcanzado.", time_passed, period_type, current_date, fecha_save

    except ValueError:
        # Manejar el caso donde la fecha de inicio no está en el formato correcto
        return False, "Formato de fecha inválido. Por favor use 'YYYY-MM-DD'.", None, None, None
    except Exception as e:
        return False, str(e), None, None, None

def update_infrastructure_review(request):
    response = {"status": "error", "message": "Sin procesar"}
    context = user_data(request)
    user_id = context["user"]["id"]
    dt = request.POST
    company_id = context["company"]["id"]
    id = dt.get("id")

    try:
        # Obtener el objeto de infraestructura existente
        obj = Infrastructure_Review.objects.get(id = id)

        # Actualizar los campos del objeto
        obj.checked = dt.get("checked")
        obj.notes = dt.get("notes")
        reviewer = User.objects.get(id=dt.get("reviewer_id"))
        obj.reviewer = reviewer
        if 'file' in request.FILES and request.FILES['file']:
                load_file = request.FILES['file']
                folder_path = f"docs/{company_id}/infrastructure/review/"
                fs = FileSystemStorage(location=settings.MEDIA_ROOT)

                file_name, extension = os.path.splitext(load_file.name)
                new_name = f"review_{id}{extension}"

                # Guardar archivo
                fs.save(folder_path + new_name, load_file)

                # Guardar ruta en la tabla
                obj.file = folder_path + new_name
                obj.save()

        obj.save()

        response["id"] = obj.id
        response["status"] = "success"
        response["message"] = "Registro actualizado exitosamente"
    except Infrastructure_Review.DoesNotExist:
        response["success"] = False
        response["error"] = {"message": f"No existe ningún registro con ese id"}
        return JsonResponse(response)
    except Exception as e:
        response["status"] = "error"
        response["message"] = str(e)

    return JsonResponse(response)

def delete_infrastructure_review(request):
    response = {"status": "error", "message": "Sin procesar"}
    context = user_data(request)
    dt = request.POST
    id = dt.get("id")

    if id == None:
        response["error"] = {"message": "Proporcione un id valido"}
        response["message"] = "Proporcione un id valido"
        return JsonResponse(response)
    try:
        obj = Infrastructure_Review.objects.get(id = id)
    except Infrastructure_Review.DoesNotExist:
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