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
from modules.utils import send_contact_email
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

    context = user_data(request)

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
    elif url_modulo == "users":
        id_module = 1
    elif url_modulo == "computer-equipment":
        id_module = 3  
    elif url_modulo == "infrastructure":
        id_module = 4
    elif url_modulo == "services":
        id_module = 5
    elif url_modulo == "equipment-and-tools":
        id_module = 6

    response_ = create_notifications(id_module, user_id, company_id, area,rol, response, access, request)

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
    
    empresas = Company.objects.all().values('id', 'name')  
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

    YOUR_DOMAIN = request.build_absolute_uri('/')[:-1]

    try:
        context = {}
        fd = request.POST.get

        if fd("accept_terms") != "on":
            return JsonResponse({
                "error": "Debes aceptar los términos y condiciones."
            })

        if User.objects.filter(email__iexact=fd("email")).exists():
            return JsonResponse({
                "error": "Ya existe una cuenta registrada con este correo."
            })

        if Company.objects.filter(
            name__iexact=fd("company")
        ).exists():
            return JsonResponse({
                "error": "La empresa ya se encuentra registrada."
            })
    

   
        qs_plan = StripeProducts.objects.filter(name__iexact = fd("plan"))
        if qs_plan.count() == 0:
            return JsonResponse({
                "error":"Plan no encontrado"
            }, safe=False)
        
        plan = qs_plan.first()
        context["id"] = plan.stripedID
        
        #YOUR_DOMAIN = "http://localhost" #para desarrollo
        # YOUR_DOMAIN = request.build_absolute_uri('/')[:-1]
        method = ['card']
        item = [{'price':plan.stripedID,'quantity':1}]
        
        prompts = verifiedPrompts(fd("company").lower(), fd("email"))
        if "error" in prompts:
            return JsonResponse(prompts, safe=False)
        
        serializer = URLSafeSerializer("ID_ENC_SECRET_KEY")

        success_url = "/stripe-success/"
        
        #if metadadato["accesos"] == "login_directo":
        #    success_url = "/login/"

        session = stripe.checkout.Session.create(
            payment_method_types = method,
            mode = "subscription",
            line_items=item,
            metadata={

                # Control
                "method": "Activar Licencia",

                # Empresa
                "company": fd("company"),

                # Usuario
                "name": fd("name"),
                "email": fd("email"),
                "phone": fd("phone"),
                "password": fd("password"),

                # Plan
                "plan_name": plan.name,
                "plan_description": plan.description,
                "plan_price" : plan.stripedID
            },
            success_url=f"{YOUR_DOMAIN}{success_url}",
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



# @csrf_exempt  # Webhooks no usan CSRF
# def stripWebHook(request):
#     payload = request.body
#     header = request.META.get('HTTP_STRIPE_SIGNATURE')
#     webSecret = settings.STRIPE_WEBHOOK_SECRET

#     # Verificar la firma del webhook
#     try:
#         evt = stripe.Webhook.construct_event(payload, header, webSecret)
#     except (ValueError, stripe.error.SignatureVerificationError):
#         return HttpResponse(status=400)
   
#     print("======================================================")
#     print(evt['type'])
#     print("======================================================")


#     if evt['type'] == "checkout.session.completed":
#         data = evt['data']['object']
#         print(data)
#         username = data['customer_details']['name']
#         email = data['customer_details']['email']

#         if data['metadata'].get('method') == 'Activar Licencia':
            
#             try:
#                 with transaction.atomic():
#                     #create company
#                     company = Company.objects.create(
#                         name=data['metadata'].get('company'),
#                         # address=data['metadata'].get('address'),
#                         # terminos y condiciones 
#                         accept_terms=True
#                     )

#                     #generate password
#                     password = passwordSecure()  # Asegúrate de tener esta función implementada

#                     #create user
#                     user = User.objects.create_user(
#                         username=f"admin_{company.name}",
#                         email=email,
#                         password=password
#                     )

#                     #create area
#                     areas = ["Sistemas", "Almacen", "Compras"]
#                     area_objs = []
#                     for area in areas:
#                         obj = Area.objects.create(
#                             company=company,
#                             name=area,
#                             code=area[:2].upper(),
#                             description=area
#                         )
#                         area_objs.append(obj)

#                     #get system area
#                     area_sistemas = next((a for a in area_objs if a.name.lower() == "sistemas"), None)

#                     #get administrator role
#                     rol_admin = Role.objects.filter(name__iexact="Administrador").first()

#                     #create access
#                     if rol_admin and area_sistemas:
#                         user_access = User_Access.objects.create(
#                             user=user,
#                             role=rol_admin,
#                             company=company,
#                             area=area_sistemas
#                         )
                        
#                     qs_modules = Module.objects.filter(name__in = ["Usuarios", "Vehículo"])
#                     for module in qs_modules:
#                         subModules = SubModule.objects.filter(module = module)
#                         for subModule in subModules:
#                             SubModule_Permission(
#                                 subModule = subModule,
#                                 user = user_access,
#                                 create = True,
#                                 read = True,
#                                 update = True,
#                                 delete = True
#                             ).save()
                            
#                         Plans(
#                             company = company,
#                             module = module,
#                             start_date_plan = datetime.now().date(),
#                             type_plan = data['metadata'].get('name'),
#                             status_payment_plan = True,
#                             time_quantity_plan = 1,
#                             time_unit_plan = 'month',
#                             end_date_plan = datetime.now().date() + timedelta(days=30),
#                             total = data['amount_total']
#                         ).save()
#                     Send_Informative_Stripe(email, f"admin_{company.name}", password, request)
#             except Exception as e:
#                 print(f"Error en webhook: {e}")
#                 return HttpResponse(status=500)
    

#     elif evt['type'] == 'checkout.subscription.created':
#         data = evt['data']['object']
#         print("checkout.subscription.created",data)
#         pass

#     elif evt['type'] == 'invoice.paid':
#         data = evt['data']['object']
#         print("invoice.paid",data)
#         pass

#     elif evt['type'] == 'customer.created':
#         data = evt['data']['object']
#         print("customer.created",data)
#         pass


#     elif evt['type'] == 'customer.subscription.created':
#         data = evt['data']['object']
#         print("customer.subscription.created",data)
#         pass

#     elif evt['type'] == 'payment_method.attached':
#         data = evt['data']['object']
#         print("payment_method.attached",data)
#         pass

#     elif evt['type'] == 'payment_intent.succeeded':
#         data = evt['data']['object']
#         print("payment_intent.succeeded",data)
#         pass

#     elif evt['type'] == 'customer.subscription.updated':
#         data = evt['data']['object']
#         print("customer.subscription.updated",data)
#         pass

#     return HttpResponse(status=200)


@csrf_exempt
def stripWebHook(request):

    payload = request.body
    signature = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            signature,
            settings.STRIPE_WEBHOOK_SECRET
        )

    except Exception as e:
        print(e)
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":

        session = event["data"]["object"]

        if session["metadata"].get("method") == "Activar Licencia":

            try:

                with transaction.atomic():

                    metadata = session["metadata"]

                    print("METADATA RECIBIDA")
                    print(metadata) 

                    company_name = metadata.get("company")
                    email = metadata.get("email")
                    password = metadata.get("password")
                    plan_name = metadata.get("plan_name")

                    # ----------------------
                    # EMPRESA
                    # ----------------------

                    company = Company.objects.create(
                        name=company_name,
                        accept_terms=True
                    )

                    # ----------------------
                    # USUARIO ADMIN
                    # ----------------------

                    username = f"admin_{company.id}"
                    full_name = metadata.get("name", "")

                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        first_name=full_name
                    )
                    
                    # ----------------------
                    # AREAS
                    # ----------------------

                    area_sistemas = Area.objects.create(
                        company=company,
                        name="Sistemas",
                        code="SI",
                        description="Sistemas"
                    )
                    
                    Area.objects.create(
                        company=company,
                        name="Almacen",
                        code="AL",
                        description="Almacen"
                    )

                    Area.objects.create(
                        company=company,
                        name="Compras",
                        code="CO",
                        description="Compras"
                    )

                    # ----------------------
                    # ROL ADMIN
                    # ----------------------

                    rol_admin = Role.objects.filter(
                        name__iexact="Administrador"
                    ).first()

                    if not rol_admin:
                        raise Exception(
                            "No existe el rol Administrador"
                        )

                    # ----------------------
                    # ACCESO
                    # ----------------------

                    user_access = User_Access.objects.create(
                        user=user,
                        role=rol_admin,
                        company=company,
                        area=area_sistemas
                    )

                    # ----------------------
                    # MODULOS
                    # ----------------------

                    modules = Module.objects.filter(
                        name__in=[
                            "Usuarios",
                            "Vehículo",
                            "Equipos de computo",
                            "Infraestructura",
                            "Servicios",
                            "Equipos y herramientas",
                            "Notificaciones"
                        ]
                    )

                    for m in modules:
                        print("MODULO ENCONTRADO:", m.id, "-", m.name)
                    

                    for m in Module.objects.all():
                        print(m.id, "-", m.name)

                    plan_header = PlanHeader()
                    plan_header.title = f"Licencia de uso: {company} de {user.first_name} {user.last_name}"
                    plan_header.stripeClient = session["customer"]
                    plan_header.StripeProductss = session["metadata"].get("plan_price")
                    plan_header.stripeSubcription = session["subscription"]
                    plan_header.company =company
                    plan_header.user = user 
                    plan_header.q_modules = 0
                    plan_header.save()
                    i = 0
                    
                    for module in modules:

                        submodules = SubModule.objects.filter(
                            module=module
                        )

                        for submodule in submodules:

                            SubModule_Permission.objects.create(
                                subModule=submodule,
                                user=user_access,
                                create=True,
                                read=True,
                                update=True,
                                delete=True
                            )

                        Plans.objects.create(
                            company=company,
                            module=module,
                            start_date_plan=datetime.now().date(),
                            type_plan=plan_name,
                            status_payment_plan=True,
                            time_quantity_plan=1,
                            time_unit_plan='month',
                            end_date_plan=datetime.now().date() + timedelta(days=30),
                            total=(session.get("amount_total", 0) / 100),
                            planHeader = plan_header
                        )
                        
                        i = i + 1
                        
                    plan_header.q_modules = i
                    plan_header.save()

                    Send_Informative_Stripe(
                        email,
                        username,
                        password,
                        request
                    )

            except Exception as e:
                import traceback

                print("ERROR WEBHOOK")
                print(str(e))
                traceback.print_exc()

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["showLabels"] = True
        return context

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


#NUEVO LANDING PAGE
def new_home_view(request):
    context = {}

    if request.user.is_authenticated:
        context["user"] = request.user

    # HERO (descripcion general de la pagina)
    context["homeStats"] = [
        {
            "icon": "directions_car",
            "title": "Vehículos",
            "num": "24",
            "subtitle": "+3 este mes",
            "iconColor": "text-amber-500",
            "subtitleColor": "text-emerald-500",
        },
        {
            "icon": "computer",
            "title": "Equipos de cómputo",
            "num": "156",
            "subtitle": "Activos",
            "iconColor": "text-sky-500",
            "subtitleColor": "text-emerald-500",
        },
        {
            "icon": "build",
            "title": "Equipos y Herramientas",
            "num": "89",
            "subtitle": "En inventario",
            "iconColor": "text-emerald-500",
            "subtitleColor": "text-gray-400",
        },
        {
            "icon": "apartment",
            "title": "Infraestructura y Servicios",
            "num": "12",
            "subtitle": "Registrados",
            "iconColor": "text-sky-300",
            "subtitleColor": "text-gray-400",
        },
    ]

    # FEATURES
    context["homeFeatures"] = [
        "Sin instalación",
        "100% en la nube",
        "Soporte 24/7",
    ]

    # Módulos 

    # MÓDULO VEHÍCULOS
    context["vehiclesModule"] = {
        "id": "vehiculos",
        "number": "Módulo 01",
        "icon": "directions_car",
        "title": "Vehículos",
        "description": """
            Control total de tu flotilla vehicular. Desde el registro
            de unidades hasta el seguimiento de mantenimientos,
            todo en un solo lugar para optimizar la operación
            de tu empresa.
        """,
        "color": "emerald",

        # badges superiores
        "features": [
            {
                "icon": "local_gas_station",
                "text": "Control de combustible",
            },
            {
                "icon": "location_on",
                "text": "Asignación de unidades",
            },
            {
                "icon": "calendar_month",
                "text": "Calendario de servicios",
            },
            {
                "icon": "security",
                "text": "Historial de anomalías en vehículos",
            },
        ],

        # cards del lado derecho
        "cards": [
            {
                "icon": "directions_car",
                "title": "Registro de Vehículos",
                "description": """
                    Administra vehículos con información completa:
                    marca, modelo, placas y número de serie.
                """,
            },

            {
                "icon": "description",
                "title": "Gestión Documental",
                "description": """
                    Control de tarjetas de circulación, pólizas de seguro, verificaciones y todos los documentos legales.
                """,
            },

            {
                "icon": "qr_code_scanner",
                "title": "Entradas y Salidas con QR",
                "description": """
                    Sistema de control de acceso mediante códigos QR para registro automático de movimientos.
                """,
            },

            {
                "icon": "build",
                "title": "Mantenimientos",
                "description": """
                    Programa y da seguimiento a servicios, cambios de aceite, afinaciones y más.
                """,
            },

            {
                "icon": "badge",
                "title": "Gestión de Conductores",
                "description": """
                    Registro de conductores, vigencia de licencias, historial de multas y asignaciones.
                """,
            },

            {
                "icon": "notifications",
                "title": "Sistema de Notificaciones",
                "description": """
                    Alertas automáticas por vencimientos, mantenimientos pendientes y documentos por renovar.
                """,
            },
        ]
    }

    # MODULO EQUIPOS DE COMPUTO
    context["computoModule"] = {

        "id": "computo",

        "number": "Módulo 02",

        "title": "Cómputo",

        "icon": "computer",

        "description": """
            Administra toda tu infraestructura tecnológica
            de manera eficiente. Controla equipos, software,
            licencias y mantenimientos con trazabilidad completa.
        """,

        # SPECS DEL DASHBOARD IZQUIERDO
        "specs": [
            "Marca y modelo",
            "Número de serie",
            "Sistema operativo",
            "Software instalado",
            "Fecha de adquisición",
            "Garantía vigente",
            "Usuario asignado",
            "Ubicación física",
        ],

        # CARD FLOTANTE SUPERIOR
        "topCard": {
            "icon": "dns",
            "number": "20",
            "label": "Equipos máx."
        },

        # CARD FLOTANTE INFERIOR
        "bottomCard": {
            "icon": "description",
            "title": "Software",
            "subtitle": "Control de licencias"
        },

        # FEATURES DERECHA
        "features": [
            {
                "icon": "inventory_2",
                "title": "Inventario Completo",
                "description": """
                    Registro detallado de hasta 20 equipos:
                    computadoras, laptops, impresoras,
                    monitores y periféricos.
                """
            },

            {
                "icon": "badge",
                "title": "Responsivas Digitales",
                "description": """
                    Genera y gestiona cartas responsivas
                    para cada equipo asignado a colaboradores.
                """
            },

            {
                "icon": "build",
                "title": "Control de Mantenimientos",
                "description": """
                    Programa mantenimientos preventivos
                    y correctivos con historial completo de servicios.
                """
            },

            {
                "icon": "fact_check",
                "title": "Control de Software",
                "description": """
                    Verifica licencias instaladas y cumplimiento
                    de políticas de TI.
                """
            },

        ]
    }

    # MODULO HERRAMIENTAS
    context["toolsModule"] = {
        "id": "herramientas",
        "number": "Módulo 03",
        "title": "Herramientas",
        "icon": "build",
        "description": """
            Mantén el control total de tus herramientas
            y equipos de trabajo. Desde el inventario
            hasta los prestamos, optimiza el uso
            de tus recursos.
        """,
        # CATEGORÍAS
        "categories": [
            {
                "icon": "construction",
                "title": "Herramienta manual",
                "description": "Martillos, llaves, etc."
            },
            {
                "icon": "handyman",
                "title": "Herramienta eléctrica",
                "description": "Taladros, sierras, etc."
            },
            {
                "icon": "straighten",
                "title": "Medición",
                "description": "Calibradores, niveles, etc."
            },
            {
                "icon": "engineering",
                "title": "Especializada",
                "description": "Equipo técnico"
            },
        ],

        # FEATURES
        "features": [
            {
                "icon": "inventory_2",
                "title": "Inventario Detallado",
                "description": """
                    Registra herramientas
                    con especificaciones técnicas,
                    números de serie y ubicación.
                """
            },
            {
                "icon": "description",
                "title": "Fichas Técnicas",
                "description": """
                    Documentación completa de cada herramienta:
                    manuales, especificaciones
                    y condiciones de uso.
                """
            },
            {
                "icon": "monitoring",
                "title": "Control de Inventario",
                "description": """
                    Seguimiento en tiempo real de existencias,
                    préstamos y devoluciones
                    de herramientas.
                """
            },
            {
                "icon": "settings",
                "title": "Responsivas",
                "description": """
                    Gestiona el control y seguimiento 
                    de equipos y herramientas, 
                    registrando su estado de prestamo y devolución. 
                """
            },
        ],

        # STATS
        "stats": [
            {
                "number": "Escalable",
                "label": "Herramientas máx.",
                "color": "text-emerald-500"
            },
            {
                "number": "100%",
                "label": "Trazabilidad",
                "color": "text-blue-950"
            },
            {
                "number": "24/7",
                "label": "Acceso al sistema",
                "color": "text-blue-950"
            },
        ]
    }

    # MÓDULO SERVICIOS
    context["servicesModule"] = {
        "id": "servicios",
        "number": "Módulo 04",
        "icon": "credit_card",
        "title": "Servicios",
        "description": """
            Centraliza la gestión de todos los servicios contratados por tu empresa.
            Controla pagos, fechas de vencimiento y genera reportes para optimizar
            tus gastos operativos.
        """,
        "color": "sky",

        # TIPOS DE SERVICIOS
        "serviceTypes": [
            {
                "icon": "wifi",
                "text": "Internet",
                "bg": "bg-sky-500/10",
                "iconColor": "text-sky-500",
            },
            {
                "icon": "call",
                "text": "Telefonía",
                "bg": "bg-sky-200/30",
                "iconColor": "text-sky-300",
            },
            {
                "icon": "bolt",
                "text": "Electricidad",
                "bg": "bg-amber-400/10",
                "iconColor": "text-amber-500",
            },
            {
                "icon": "water_drop",
                "text": "Agua",
                "bg": "bg-sky-500/10",
                "iconColor": "text-sky-500",
            },
            {
                "icon": "shield",
                "text": "Seguros",
                "bg": "bg-emerald-500/10",
                "iconColor": "text-emerald-500",
            },
        ],

        # FEATURES
        "features": [
            {
                "icon": "description",
                "title": "Registro de Servicios",
                "description": """
                    Administra servicios contratados con toda la
                    información de proveedores y contratos.
                """,
            },
            {
                "icon": "credit_card",
                "title": "Gestión de Pagos",
                "description": """
                    Control de fechas de pago, montos, métodos de pago
                    y registro de comprobantes.
                """,
            },
            {
                "icon": "bar_chart",
                "title": "Reportes Detallados",
                "description": """
                    Análisis de gastos por servicio, tendencias y proyecciones
                    para mejor planificación.
                """,
            },
            {
                "icon": "notifications",
                "title": "Alertas de Vencimiento",
                "description": """
                    Notificaciones automáticas antes de fechas límite
                    de pago para evitar recargos.
                """,
            },
        ],

        # STATS CARD
        "statsCard": {
            "title": "Servicios incluidos",
            "value": "Servicios Personalizados",
            "subtitle": "Historial de pagos incluido",
            "icon": "trending_up",
        },
    }
    
    # MÓDULO INFRAESTRUCTURA
    context["infrastructureModule"] = {
        "id": "infraestructura",
        "number": "Módulo 05",
        "icon": "apartment",
        "title": "Infraestructura",
        "description": """
            Centraliza la administración de todos tus inmuebles e instalaciones.
            Desde oficinas hasta plantas industriales,
            mantén todo bajo control.
        """,
        "color": "amber",

        # TIPOS DE INMUEBLES
        "propertyTypes": [
            {
                "icon": "apartment",
                "title": "Oficinas",
                "description": "Espacios administrativos",
            },
            {
                "icon": "factory",
                "title": "Plantas",
                "description": "Instalaciones productivas",
            },
            {
                "icon": "store",
                "title": "Sucursales",
                "description": "Puntos de venta",
            },
            {
                "icon": "warehouse",
                "title": "Bodegas",
                "description": "Almacenamiento",
            },
        ],

        # FEATURES
        "features": [
            {
                "icon": "apartment",
                "title": "Registro de Inmuebles",
                "description": """
                    Administra inmuebles:
                    oficinas, bodegas, sucursales y plantas.
                """,
            },

            {
                "icon": "fingerprint",
                "title": "Identificadores Únicos",
                "description": """
                    Cada inmueble cuenta con un ID único
                    para facilitar seguimiento y gestión.
                """,
            },

            {
                "icon": "description",
                "title": "Fichas Técnicas",
                "description": """
                    Documentación completa:
                    planos, contratos, escrituras y especificaciones.
                """,
            },

            {
                "icon": "build",
                "title": "Mantenimientos",
                "description": """
                    Programa y registra mantenimientos
                    eléctricos, hidráulicos y preventivos.
                """,
            },
        ],

        # INFO CARD
        "propertyInfo": [
            "Dirección completa",
            "Fecha de adquisición",
            "Responsable asignado",
            "Contratos vigentes",
            "Historial de mantenimiento",
        ],

        # FOOTER CARD
        "statsCard": {
            "title": "Capacidad máxima",
            "subtitle": "Incluido en tu plan",
            "value": "Escalable",
            "icon": "location_on",
        },
    }

    # PLANES
    context["plans"] = [

        # BÁSICO
        {
            "label": "Plan",
            "name": "Básico",
            "price": "250",
            "stripe": "basic",
            "icon": "workspace_premium",
            "recommended": False,

            "headerBg": """
                bg-gradient-to-r
                from-amber-400
                to-orange-500
            """,

            "features": [
                "Módulo de Vehículos completo",
                "Registro de hasta 10 vehículos",
                "Gestión documental",
                "Entradas/salidas con QR",
                "Mantenimientos preventivos",
                "Control de conductores y licencias",
                "Notificaciones automáticas",
            ],

            "modules": [
                {
                    "icon": "computer",
                    "title": "Equipos de Cómputo",
                    "limit": "1 - 20 registros",
                },

                {
                    "icon": "build",
                    "title": "Equipos y Herramientas",
                    "limit": "1 - 20 registros",
                },

                {
                    "icon": "credit_card",
                    "title": "Servicios",
                    "limit": "1 - 5 registros",
                },

                {
                    "icon": "apartment",
                    "title": "Infraestructura",
                    "limit": "1 - 25 registros",
                },
            ]
        },

        # ESENCIAL
        {
            "label": "Más popular",
            "name": "Esencial",
            "price": "525",
            "stripe": "esential",
            "icon": "star",
            "recommended": True,

            "headerBg": """
                bg-gradient-to-r
                from-amber-500
                to-yellow-500
            """,

            "features": [
                "Todo incluido en Básico",
                "Incremento de registros",
                "Reportes gráficos",
                "Panel administrativo avanzado",
                "Mayor capacidad operativa",
                "Historial y trazabilidad completa",
            ],

            "modules": [
                {
                    "icon": "computer",
                    "title": "Equipos",
                    "limit": "20 - 50 registros",
                },

                {
                    "icon": "build",
                    "title": "Herramientas",
                    "limit": "20 - 50 registros",
                },

                {
                    "icon": "credit_card",
                    "title": "Servicios",
                    "limit": "5 - 10 registros",
                },

                {
                    "icon": "apartment",
                    "title": "Infraestructura",
                    "limit": "25 - 100 registros",
                },
            ]
        },

        # AVANZADO
        {
            "label": "Empresarial",
            "name": "Avanzado",
            "price": "850",
            "stripe": "advance",
            "icon": "rocket_launch",
            "recommended": False,

            "headerBg": """
                bg-gradient-to-r
                from-slate-800
                to-slate-950
            """,

            "features": [
                "Todo incluido en Esencial",
                "Control de gasolina",
                "Correos automáticos",
                "Mayor capacidad multiusuario",
                "Reportes avanzados",
                "Escalabilidad empresarial",
            ],

            "modules": [
                {
                    "icon": "computer",
                    "title": "Equipos",
                    "limit": "25 - 50 registros",
                },

                {
                    "icon": "build",
                    "title": "Herramientas",
                    "limit": "25 - 50 registros",
                },

                {
                    "icon": "credit_card",
                    "title": "Servicios",
                    "limit": "10 - 20 registros",
                },

                {
                    "icon": "apartment",
                    "title": "Infraestructura",
                    "limit": "100 - 150 registros",
                },
            ]
        },

        # PRO
        {
            "label": "Corporativo",
            "name": "Pro",
            "price": "1500",
            "stripe": "pro",
            "icon": "verified",
            "recommended": False,

            "headerBg": """
                bg-gradient-to-r
                from-indigo-600
                to-purple-700
            """,

            "features": [
                "Vehículos de 50 a 100 registros",
                "Equipos de 50 a 100 registros",
                "Herramientas de 100 a 200 registros",
                "Servicios sin límite",
                "Infraestructura sin límite",
                "Soporte prioritario",
            ],

            "modules": [
                {
                    "icon": "directions_car",
                    "title": "Vehículos",
                    "limit": "50 - 100",
                },

                {
                    "icon": "computer",
                    "title": "Equipos",
                    "limit": "50 - 100",
                },

                {
                    "icon": "build",
                    "title": "Herramientas",
                    "limit": "100 - 200",
                },

                {
                    "icon": "apartment",
                    "title": "Infraestructura",
                    "limit": "Sin límite",
                },
            ]
        },

        # ÉLITE
        {
            "label": "Premium",
            "name": "Élite",
            "price": "2500",
            "stripe": "elite",
            "icon": "diamond",
            "recommended": False,

            "headerBg": """
                bg-gradient-to-r
                from-pink-600
                to-rose-700
            """,

            "features": [
                "Vehículos de 100 a 250 registros",
                "Equipos de 200 a 350 registros",
                "Herramientas de 200 a 350 registros",
                "Servicios ilimitados",
                "Infraestructura ilimitada",
                "Atención personalizada",
            ],

            "modules": [
                {
                    "icon": "directions_car",
                    "title": "Vehículos",
                    "limit": "100 - 250",
                },

                {
                    "icon": "computer",
                    "title": "Equipos",
                    "limit": "200 - 350",
                },

                {
                    "icon": "build",
                    "title": "Herramientas",
                    "limit": "200 - 350",
                },

                {
                    "icon": "apartment",
                    "title": "Infraestructura",
                    "limit": "Sin límite",
                },
            ]
        },

    ]

    # CONTACTO
    context["contactModule"] = {
        "badge": "Contacto",

        "title": {
            "normal": "¿Listo para",
            "highlight": "transformar",
            "end": "tu gestión empresarial?"
        },

        "description": """
            Completa el formulario y un especialista te contactará
            para mostrarte cómo Capital System puede ayudarte
            a optimizar los procesos de tu empresa.
        """,

        # BENEFICIOS /
        "trustSignals": [
            {
                "icon": "shield",
                "title": "Datos Seguros",
                "description": "Encriptación de extremo a extremo",
                "bg": "bg-yellow-100",
                "iconColor": "text-yellow-500",
            },
            {
                "icon": "schedule",
                "title": "Respuesta Rápida",
                "description": "Te contactamos en menos de 24h",
                "bg": "bg-yellow-100",
                "iconColor": "text-yellow-500",
            },
            {
                "icon": "support_agent",
                "title": "Soporte Dedicado",
                "description": "Acompañamiento personalizado",
                "bg": "bg-yellow-100",
                "iconColor": "text-yellow-500",
            },
        ],

        # FORMULARIO
        "form": {
            "title": "Solicita una demostración",
            "fields": [
                {
                    "label": "Nombre completo",
                    "type": "text",
                    "name": "name",
                    "placeholder": "Juan Pérez",
                    "required": True,
                },
                {
                    "label": "Empresa",
                    "type": "text",
                    "name": "company",
                    "placeholder": "Tu empresa",
                    "required": True,
                },
                {
                    "label": "Correo electrónico",
                    "type": "email",
                    "name": "email",
                    "placeholder": "juan@empresa.com",
                    "required": True,
                },
                {
                    "label": "Teléfono",
                    "type": "tel",
                    "name": "phone",
                    "placeholder": "+52 55 1234 5678",
                    "required": True,
                },
            ],
            "textarea": {
                "label": "Mensaje",
                "name": "message",
                "rows": 5,
                "placeholder": """
                    Cuéntanos sobre tu empresa
                    y qué necesitas gestionar...
                """,
            },
            "button": {
                "text": "Enviar solicitud",
                "icon": "send",
            },
            "privacyText": """
                Al enviar aceptas nuestra política de privacidad.
                No compartimos tu información.
            """,
        },
        # MENSAJE DE ÉXITO
        "successMessage": {
            "title": "¡Mensaje enviado!",
            "description": """
                Gracias por tu interés.
                Te contactaremos pronto.
            """,
            "buttonText": "Enviar otro mensaje",
        }

    }

    # FOOTER
    context["footerModule"] = {

        # BRAND
        "brand": {
            "name": "Capital System",

            "description": """
                Plataforma integral de gestión empresarial.
                Optimiza tus procesos con tecnología de vanguardia.
            """,

            "logoLetter": "S",
        },

        # REDES SOCIALES
        "socials": [
            {
                "icon": "facebook",
                "url": "#",
                "hover": "hover:bg-blue-600",
            },
            {
                "icon": "alternate_email",
                "url": "#",
                "hover": "hover:bg-sky-500",
            },
            {
                "icon": "business",
                "url": "#",
                "hover": "hover:bg-blue-700",
            },
        ],

        # LINKS
        "sections": [
            {
                "title": "Producto",
                "links": [
                    {
                        "name": "Módulos",
                        "url": "#modulos",
                    },
                    {
                        "name": "Planes",
                        "url": "#planes",
                    },
                 
                ]
            },
            {
                "title": "Empresa",
                "links": [
                    {
                        "name": "Nosotros",
                        "url": "#",
                    },
                    {
                        "name": "Contacto",
                        "url": "#contacto",
                    },
                    {
                        "name": "Blog",
                        "url": "#",
                    },
                ]
            },
            {
                "title": "Legal",
                "links": [
                    {
                        "name": "Privacidad",
                        "url": "#",
                    },
                    {
                        "name": "Términos",
                        "url": "#",
                    },
                    {
                        "name": "Cookies",
                        "url": "#",
                    },
                ]
            },
        ],

        # BOTTOM
        "bottom": {
            "copyright": """
                © 2026 Capital System Solutions.
                Todos los derechos reservados.
            """,

            "madeWith": "Hecho en México",
        }
    }

    print("hello new index.html")

    if request.method == "POST":
        print("Formulario recibido")

        # fd = request.POST.get

        name = request.POST.get("name")
        company = request.POST.get("company")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        message = request.POST.get("message")

        print(name, company, email, phone)

        html_content = f"""
        <h2>Nueva solicitud desde el sitio web</h2>

        <p><strong>Nombre:</strong> {name}</p>
        <p><strong>Empresa:</strong> {company}</p>
        <p><strong>Correo:</strong> {email}</p>
        <p><strong>Teléfono:</strong> {phone}</p>

        <p><strong>Mensaje:</strong></p>
        <p>{message}</p>
        """

        send_contact_email(
            subject="Nuevo contacto desde la web",
            recipient=["sia@tenergy.com.mx"],
            html_content=html_content
        )
        print("Correo enviado")


        messages.success(
            request,
            "Tu mensaje ha sido enviado correctamente."
        )

        return redirect("/")
        
    return render(request, "home2/new_index.html", context)


