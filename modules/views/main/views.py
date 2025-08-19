from django.urls import resolve
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F, Q, Value, Max, Sum, CharField, BooleanField
from django.http import JsonResponse
from core.settings import EMAIL_HOST_PASSWORD, EMAIL_HOST_USER, STRIPE_PUBLISHABLE_KEY
from django.apps import apps
from django.db import transaction
import json, os
from datetime import datetime, timedelta
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from django.views.generic import TemplateView
from django.contrib.auth.models import User

from uritools import uridecode
from modules.models import *
from users.models import *
from modules.utils import *
import requests
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash

from django.utils.timezone import now

# TODO -- EMAIL --
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import json


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
        domain = request.build_absolute_uri('/')[:-1]  # Obtiene el dominio dinámicamente
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
            <img src="{domain}/staticfiles/assets/images/brand-logos/CS_LOGO.png" alt="Logo">
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


def probe():
    print("imprimi desde el views de modules")



def get_notifications(request):
    response = {"success": False, "data": []}

    print("request")
    print(request)

    context = user_data(request)

    print("* ************** context **************")
    print(context)


    
    fecha_actual = datetime.now().date()
    current_year = datetime.today().year
    current_month = datetime.today().month
    roles_usuario = [1, 2, 3]

    company_id = context["company"]["id"]
    area = context["area"]["name"]
    rol = context["role"]["id"]
    user_id = context["user"]["id"]

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
    

    response_ = create_notifications(id_module, user_id, company_id, area,rol, response, access, request)
    print(response_)
    return JsonResponse(response)

def prueba_datos(request):

    response = {"success": False, "data": []}
    id_modules = [2, 5, 6]
    context = {}
    context["role"] = {
        "id": 1,  # por ejemplo
        "name": "Administrador",
        "level": 1
    }
    access = get_user_access(context)
    access = access["data"]
    
    empresas = Company.objects.all().values('id', 'name')  # esto retorna un queryset de diccionarios
    empresas_list = list(empresas)

    print(empresas_list)
    for empresa in empresas:

        print(" ")
        print(empresa['id'], empresa['name'])

        data_ = User_Access.objects.filter(company=empresa['id']).values()

        area = "sistemas" #sistemas o almacen, minisculas y mayusculas ¬¬
        rol = 1 #que sea superusuario
        company_id = empresa['id']
        user_id = 1

        for id_module in id_modules:
            create_notifications(id_module, user_id, company_id, area, rol, response, access)
            

    return JsonResponse(empresas_list, safe=False, status=200)




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

def enviar_cotizacion(request):
    body_response = {
        "technology" : "Acceso a la plataforma de Equipos de cómputo",
        "data" : "Acceso a la plataforma de Infraestructura",
        "transports" : "Acceso a la plataforma de Vehículos",
        "assets-and-tools" : "Acceso a la plataforma de Equipos y herramientas",
        "services" : "Acceso a la plataforma de Servicios",
        "sm" : "Gestión para 10 trabajadores",
        "md" : "Gestión para 29 trabajadores",
        "lg" : "Gestión ilimitada",
        "minimum" : "Solo 1000 recursos administrables",
        "medio" : "Solo 5000 recursos administrables",
        "unlimited" : "recursos ilimitados administrables",        
        "local" : "Administración para un local",
        "store" : "Administración para una Sucursal",
        "corporation" : "Administración para un Corporativo",
        "storage" : "Administración para un Almacén",
        "multinational" : "Administración para una empresa"
    }

    form = request.POST
    details = form.get("details") if form.get("details") != "" else "Sin información adicional"
    body = form.get("options_quotations")[:-1].split(",")
    
    html_quotation = ""
    for item in body:
        print(item)
        html_quotation += f'<p>{body_response[item]}</p>'
    
    print(html_quotation)
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
                    font-weight: 500;
                }}
                strong {{
                    color: #000000;
                }}
            </style>
        </head>
        <body>
            <div class="container">
            <img src="https://sia-tenergy.com/staticfiles/assets/images/brand-logos/CS_LOGO.png" alt="Logo">
            <h2>Nuevo mensaje de {form.get("name", "Nombre no proporcionado")}</h2>
            <p><strong>Empresa:</strong> {form.get("company", "Empresa no especificada")}</p>
            <p><strong>Correo:</strong> {form.get("email", "sin correo")}</p>
            <p><strong>Detalles de cotización:</strong></p>
            {html_quotation}
            <p><strong>Información adicional:</strong></p>
            <p>{details}</p>
            </div>
        </body>
    </html>"""


    #Crear el email
    email = EmailMultiAlternatives(asunto, text_content, from_email, recipient_list)
    email.attach_alternative(html_content, "text/html")
    email.send()
    return JsonResponse({'mensaje': 'Cotización enviada correctamente'})

@csrf_exempt
def getPlan(request):
    try:
        context = {}
        fd = request.POST.get
        qs_plan = StripeProducts.objects.filter(name__iexact = fd("plan"))
        if qs_plan.count() == 0:
            return JsonResponse({
                "error":"Plan no encontrado"
            }, safe=False)
        
        plan = qs_plan.first()
        context["plan"] = fd("plan")
        context["id"] = plan.stripedID
        
        #YOUR_DOMAIN = "http://localhost" #para desarrollo
        YOUR_DOMAIN = request.build_absolute_uri('/')[:-1]
        if plan.description == "subscription":
            method = ['card']
            item = [{'price':plan.stripedID,'quantity':1}]
        else:
            pass
        
        prompts = verifiedPrompts(fd("company").lower(), fd("email"))
        if "error" in prompts:
            return JsonResponse(prompts, safe=False)
        
        serializer = URLSafeSerializer("ID_ENC_SECRET_KEY")
        session = stripe.checkout.Session.create(
            payment_method_types = method,
            mode = plan.description,
            line_items=item,
            metadata={
                'product_data':plan.description,
                'company':fd("company"),
                'email_address':fd("email"),
                'address': fd("address"),
                'name' : plan.name
            },
            success_url=f"{YOUR_DOMAIN}/stripe-success/",
            cancel_url=f"{YOUR_DOMAIN}/stripe-cancel/",
            subscription_data={},
        )
        context["id"] = session.id
        context["STP_ID"] = settings.STRIPE_PUBLISHABLE_KEY
    except Exception as e:
        return JsonResponse({
            "error":e
        }, safe=False)
        
    return JsonResponse(context, safe=False)


@csrf_exempt  # Webhooks no usan CSRF
def stripWebHook(request):
    payload = request.body
    header = request.META.get('HTTP_STRIPE_SIGNATURE')
    webSecret = settings.STRIPE_WEBHOOK_SECRET

    # Verificar la firma del webhook
    try:
        evt = stripe.Webhook.construct_event(payload, header, webSecret)
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if evt['type'] == "checkout.session.completed":
        data = evt['data']['object']
        print(data)
        username = data['customer_details']['name']
        email = data['customer_details']['email']

        if data['metadata'].get('product_data') == 'subscription':
            try:
                with transaction.atomic():
                    #create company
                    company = Company.objects.create(
                        name=data['metadata'].get('company'),
                        address=data['metadata'].get('address')
                    )

                    #generate password
                    password = passwordSecure()  # Asegúrate de tener esta función implementada

                    #create user
                    user = User.objects.create_user(
                        username=f"admin_{company.name}",
                        email=email,
                        password=password
                    )

                    #create area
                    areas = ["Sistemas", "Almacen", "Compras"]
                    area_objs = []
                    for area in areas:
                        obj = Area.objects.create(
                            company=company,
                            name=area,
                            code=area[:2].upper(),
                            description=area
                        )
                        area_objs.append(obj)

                    #get system area
                    area_sistemas = next((a for a in area_objs if a.name.lower() == "sistemas"), None)

                    #get administrator role
                    rol_admin = Role.objects.filter(name__iexact="Administrador").first()

                    #create access
                    if rol_admin and area_sistemas:
                        user_access = User_Access.objects.create(
                            user=user,
                            role=rol_admin,
                            company=company,
                            area=area_sistemas
                        )
                        
                    qs_modules = Module.objects.filter(name__in = ["Usuarios", "Vehículo"])
                    for module in qs_modules:
                        subModules = SubModule.objects.filter(module = module)
                        for subModule in subModules:
                            SubModule_Permission(
                                subModule = subModule,
                                user = user_access,
                                create = True,
                                read = True,
                                update = True,
                                delete = True
                            ).save()
                            
                        Plans(
                            company = company,
                            module = module,
                            start_date_plan = datetime.now().date(),
                            type_plan = data['metadata'].get('name'),
                            status_payment_plan = True,
                            time_quantity_plan = 1,
                            time_unit_plan = 'month',
                            end_date_plan = datetime.now().date() + timedelta(days=30),
                            total = data['amount_total']
                        ).save()
                    Send_Informative_Stripe(email, f"admin_{company.name}", password, request)
            except Exception as e:
                print(f"Error en webhook: {e}")
                return HttpResponse(status=500)
    return HttpResponse(status=200)

def verifiedPrompts(company, email):
    context = {}

    #Email Validation
    validator = EmailValidator()
    try:
        validator(email)
    except ValidationError:
        context["error"] = "El correo electrónico no es válido"
        return context

    #Verified if company exists
    if Company.objects.filter(name__iexact=company).exists():
        context["error"] = "Esta empresa ya fue registrada en la plataforma"
        return context

    #Verified if email exists
    if User.objects.filter(email__iexact=email).exists():
        context["error"] = "Este correo electrónico ya está en uso"
        return context

    context["success"] = True
    return context

class SuccessView(TemplateView):
    template_name = "home/stripe-success.html"

class CancelView(TemplateView):
    template_name = "home/stripe-cancel.html"

def passwordSecure(longitud=12):
    import random
    import string   
    if longitud < 3:
        raise ValueError("La longitud mínima recomendada es 3")

    # Caracteres permitidos
    mayusculas = string.ascii_uppercase
    minusculas = string.ascii_lowercase
    numeros = string.digits

    # Aseguramos al menos una mayúscula y un número
    obligatorios = [
        random.choice(mayusculas),
        random.choice(numeros)
    ]

    # El resto se completa con cualquier carácter permitido
    restantes = random.choices(mayusculas + minusculas + numeros, k=longitud - len(obligatorios))

    # Mezclamos todos para que no estén siempre al inicio
    caracteres = obligatorios + restantes
    random.shuffle(caracteres)

    return ''.join(caracteres)

@login_required
def siaChangePassword(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        user = request.user

        if not user.check_password(old_password):
            messages.error(request, 'La contraseña actual es incorrecta.')
        elif new_password1 != new_password2:
            messages.error(request, 'Las nuevas contraseñas no coinciden.')
        elif len(new_password1) < 8:
            messages.error(request, 'La nueva contraseña debe tener al menos 8 caracteres.')
        else:
            user.set_password(new_password1)
            user.save()
            update_session_auth_hash(request, user)  # Mantiene la sesión iniciada
            messages.success(request, 'Tu contraseña ha sido actualizada correctamente.')
            return redirect('/reset-password/')

    return render(request, 'home/reset-password.html')