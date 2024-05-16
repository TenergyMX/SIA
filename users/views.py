from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import JsonResponse
from users.models import *
from modules.utils import * # Esto es un helpers


# Create your views here.
def login_view(request):
    context = {'success': False}
    context["redirect"] = request.GET['next'] if request.GET.get('next', None) else "/"
    context["next"] = request.GET['next'] if request.GET.get('next', None) else "/"

    if request.method == 'POST':
        dt = request.POST
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        context["next"] = dt.get("next", "/")

        user = authenticate(request, username=username, password=password)
        if user is not None:
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
                session_data.update({
                    'access': {'id': access.id},
                    'role': {
                        'id': access.role_id,
                        'name': access.role.name,
                        'level': access.role.level,
                    },
                    'company': {
                        'id': access.company.id,
                        'name': access.company.name,
                    }
                })
            # Actualizar la sesión con los datos recopilados
            request.session.update(session_data)
            context["success"] = True
            return JsonResponse(context)
        else:
            return JsonResponse(context)
    # Respuesta
    return render(request, 'authentication/sing-in-cover.html', context)

def logout_view(request):
    request.session.flush()
    return redirect('/')

def users_profile_view(request):
    context = user_data(request)

    sidebar = get_sidebar(context, [1])
    context["sidebar"] = sidebar["data"]

    return render(request, 'profile.html', context)