from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import JsonResponse
from users.models import *


from modules.utils import *
from helpers.enviar_correo import *

# Login
def login_view(request):
    context = {'success': False}
    context["redirect"] = request.GET.get('next', "/")
    context["next"] = context["redirect"]

    if request.method == 'POST':
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')

        # Buscar el usuario por nombre de usuario o correo electrónico
        user = None

        if '@' in username_or_email:
            print("Sesion con correo electrónico")
            user = authenticate(request, email=username_or_email, password=password)
        else:
            print("Sesion con username")
            user = authenticate(request, username=username_or_email, password=password)
        
        if user is not None:
            # Iniciar sesión
            login(request, user)

            # Inicializar datos de sesión con valores predeterminados
            session_data = {
                'access': {'id': None},
                'role': {'id': None, 'name': None, 'level': None},
                'company': {'id': None, 'name': None},
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                }
            }

            # Obtener el acceso del usuario (si existe)
            access = User_Access.objects.filter(user_id=user.id).first()

            # Si hay acceso, actualizar los datos correspondientes
            if access:
                session_data['access']['id'] = access.id
                session_data['role']['id'] = access.role_id
                session_data['role']['name'] = access.role.name
                session_data['role']['level'] = access.role.level
                session_data['company']['id'] = access.company.id
                session_data['company']['name'] = access.company.name
                messages.success(request, 'Credenciales cargadas', extra_tags='persist')
            else:
                messages.warning(request, 'Su usuario con cuenta con credenciales de acceso', extra_tags='persist')

            # Actualizar la sesión con los datos recopilados
            request.session.update(session_data)
            # Finalizar proceso
            messages.success(request, 'Logeado exitosamente.', extra_tags='persist')
            return redirect(context["next"])
        if user is not None:
            login(request, user)
        else:
            messages.error(request, 'El usuario o la contraseña son incorrectos')    
    return render(request, 'authentication/sing-in-cover.html', context)

def logout_view(request):
    request.session.flush()
    return redirect('/')


# Paso 1
def password_recovery_request_username_view(request):
    context = {}

    if request.method == 'POST':
        dt = request.POST
        username = dt.get('username', '').strip()

        # Verifica si el usuario existe
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, 'El usuario no existe')
            return render(request, 'authentication/request-username.html', context)
        
        current_site = get_current_site(request)
        domain = current_site.domain
        protocol = 'https' if request.is_secure() else 'http'
        base_url = f'{protocol}://{domain}'
        
        datos={
            'username': username,
            'base_url': base_url
        }

        envio = enviar_correo(
            subject='Recuperación de contraseña',
            to_emails=[user.email],
            template='verification-token.html',
            datos = datos
        )
        request.session['user_id'] = user.id
        request.session['username'] = username
        # Redirecciona después de enviar el correo
        return redirect('/password-recovery/verify-token/')
    return render(request, 'authentication/request-username.html', context)
    
# Paso 2
def password_recovery_verify_token_view(request):
    context = {}

    if request.method == 'POST':
        dt = request.POST
        token_parts = dt.getlist('token[]')
        token = ''.join(token_parts).strip()

        if token == "1234":
            return redirect('/password_recovery/reset-password/')
            pass
        else:
            messages.error(request, 'El token no coincide.')

    return render(request, 'authentication/two-step-verification-basic.html', context)

# paso 3
def password_recovery_reset_password_view(request):
    context = {}
    print("ID:", request.session['user_id'])
    print("Username:", request.session["username"])

    if request.method == 'POST':
        dt = request.POST

        new_password = dt.get('password')
        confirm_password = dt.get('confirmpassword')

        if new_password != confirm_password:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'authentication/reset-password-basic.html', context)
        
        try:
            user_id = request.session['user_id']
            user = User.objects.get(id=user_id)
            user.password = make_password(new_password)
            user.save()

            messages.success(request, 'Tu contraseña ha sido restablecida exitosamente.', extra_tags='persist')
            return redirect('login')
        except KeyError:
            messages.error(request, 'No se ha podido verificar el usuario.')
            return redirect('password_recovery_request_username')
        except User.DoesNotExist:
            messages.error(request, 'El usuario no existe.')
            return redirect('password_recovery_request_username')
        
    return render(request, 'authentication/reset-password-basic.html', context)