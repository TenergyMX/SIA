from celery import shared_task


from datetime import datetime, timedelta
from modules.views.main.views import *

@shared_task(bind=True)
def my_task1(self):
    print("This task runs every 3 min")
    return "This task runs every 3 min."

@shared_task(bind=True)
def my_task2(self):
    probe()
    print("This task runs every 1 mins.")
    return "This task runs every 1 mins."

@shared_task(bind=True)
def notifications_task(self):

    response = {"success": False, "data": []}
    id_modules = [2, 5, 6]
    context = {}
    context["role"] = {
        "id": 1,  
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

        area = "sistemas" #sistemas o almacen, minisculas y mayusculas ¬¬
        rol = 1 #que sea superusuario
        company_id = empresa['id']
        user_id = 1

        for id_module in id_modules:
            create_notifications(id_module, user_id, company_id, area, rol, response, access)
            
    return "¡Éxito!"