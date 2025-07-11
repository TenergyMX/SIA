from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from modules.models import Vehicle, Vehicle_Insurance, Vehicle_Refrendo, Vehicle_Responsive, Vehicle_Tenencia, Vehicle_Verificacion, Vehicle_fuel
from modules.utils import check_user_access_to_module, get_module_user_permissions, get_sidebar, user_data
from users.models import User_Access

from django.utils import timezone
from datetime import datetime, timedelta

@login_required
def vehicles_reports_view(request):
    context = user_data(request)
    module_id = 2
    subModule_id = 4
    request.session["last_module_id"] = module_id
    
    access = get_module_user_permissions(context, subModule_id)
    sidebar = get_sidebar(context, [1, module_id])
    
    context["access"] = access["data"]["access"]
    context["sidebar"] = sidebar["data"]
    #GET ALL LIST OF VEHICLES
    try:
        data = Vehicle.objects.order_by('name').values(
            "id", "is_active", "image_path", "name", "state",
            "company_id", "company__name", "plate", "model",
            "year", "serial_number", "brand", "color", "vehicle_type", "validity", "mileage",
            "insurance_company",
            "responsible_id", "responsible__first_name", "responsible__last_name",
            "owner_id", "owner__first_name",
            "transmission_type",
            "policy_number"
        )
        data = data.filter(company_id=context["company"]["id"])
        
        for vehicle in data:
            vehicle["area"] = User_Access.objects.filter(user__id = vehicle["owner_id"]).values("area__name").first()
        context["vehicles"] = list(data)
    except Exception as e:
        print(f"Error fetching vehicles info: {e}")
    template = "charts/dashboard.html" if context["access"]["read"] and check_user_access_to_module(request, module_id, subModule_id) else "error/access_denied.html"
        
    return render(request, template, context)

def vehicle_statistic(request):
    context = {}
    formdata = request.POST.get
    key = formdata("option")
    start_date = formdata("start_date")
    end_date = formdata("end_date")
    
    #genero el historico de fechas solicitadas para hacer el gráfico
    timelapse = generar_fechas(formdata("start_date"), formdata("end_date"))
    #genero una consulta de los vehiculos solicitados para la lectura
    vehicles = Vehicle.objects.filter(id__in = formdata("vehicles").split(","))

    context["series"] = []
    context["labels"] = []
    
    #Acceso a la linea temporal
    flag = ["kilometer-record", "in-out-travels", "refrendo", "tenencia"]
    for vehicle in vehicles:
        context["series"].append({"name":vehicle.name, "data":[]})
        #esta condicional es cuando la serie del gráfico debe ser un historico de fechas
        if key in flag:
            context["categories"] = timelapse["timelapse"]
            context["series"][-1]["data"] = [0] * len(timelapse["timelapse"])
        else:
            context["categories"] = []
            
        #TODO - - - - - - - - - - KILOMETER-RECORD - - - - - - - - - -
        if key == "kilometer-record":
            item_responsive = Vehicle_Responsive.objects.filter(vehicle = vehicle, start_date__date__gte = start_date, start_date__date__lte = end_date).order_by("start_date")
            for item in item_responsive:
                i = item.end_date.date() if item.end_date else item.start_date.date()
                if str(i) in context["categories"]:
                    pos = context["categories"].index(str(i))
                else:
                    i = i - timedelta(days=1)
                    pos = context["categories"].index(str(i))
                context["series"][-1]["data"][pos] += float(item.final_mileage) - float(item.initial_mileage) if float(item.final_mileage) - float(item.initial_mileage) > 0 else 0
        
        #TODO - - - - - - - - - - KILOMETER-PER-DAY-RECORD - - - - - - - - - -
        if key == "kilometer-record-per-day":
            item_per_day = Vehicle_Responsive.objects.filter(vehicle = vehicle, start_date__date = start_date, end_date__date = start_date).order_by("start_date")
            for item in item_per_day:
                context["series"][-1]["data"].append(float(item.final_mileage) - float(item.initial_mileage) if float(item.final_mileage) - float(item.initial_mileage) > 0 else 0)
        
        #TODO - - - - - - - - - - IN-OUT-TRAVELS - - - - - - - - - -
        if key == "in-out-travels":
            item_per_travels = Vehicle_Responsive.objects.filter(vehicle = vehicle, start_date__date__gte = start_date, end_date__date__lte = end_date).order_by("start_date")
            for item in item_per_travels:
                i = item.end_date.date() if item.end_date else item.start_date.date()
                if str(i) in context["categories"]:
                    pos = context["categories"].index(str(i))
                else:
                    i = i - timedelta(days=1)
                    pos = context["categories"].index(str(i))
                context["series"][-1]["data"][pos] += 1
                
        #TODO - - - - - - - - - - REFRENDO OR TENENCIA - - - - - - - - - -
        if key == "refrendo" or key == "tenencia":
            items = Vehicle_Refrendo.objects if key == "refrendo" else Vehicle_Tenencia.objects
            items = items.filter(vehiculo = vehicle, fecha_pago__gte = start_date, fecha_pago__lte = end_date).order_by("fecha_pago")
            for item in items:
                i = item.fecha_pago
                pos = context["categories"].index(str(i))
                context["series"][-1]["data"][pos] += item.monto
        
        #TODO - - - - - - - - - - FUEL - - - - - - - - - -
        if key == "fuel":
            items_voucher = Vehicle_fuel.objects.filter(vehicle = vehicle, date__gte = start_date, date__lte = end_date)
            fuel = 0
            for item in items_voucher:
                fuel += item.fuel
            context["series"][-1]["data"].append(float(fuel))
            context["categories"].append(vehicle.name)
        
        #insurance
        #TODO - - - - - - - - - - VERIFICATION - - - - - - - - - -
        if key == "verification":
            items_verification = Vehicle_Verificacion.objects.filter(vehiculo = vehicle)
            for item in items_verification:
                context["series"][-1]["data"].append(item.monto)
                
        if key == "insurance":
            items_insurance = Vehicle_Insurance.objects.filter(vehicle = vehicle, start_date__gte = start_date, start_date__lte = end_date)
            for item in items_insurance:
                print(item.cost)
                context["series"][-1]["data"].append(item.cost)
                
    context["key"] = key
    return JsonResponse(context, safe=False)

def generar_fechas(start_date: str, end_date: str) -> dict:
    formato = "%Y-%m-%d"
    inicio = datetime.strptime(start_date, formato)
    fin = datetime.strptime(end_date, formato)
    fechas = []
    actual = inicio
    while actual <= fin:
        fechas.append(actual.strftime(formato))
        actual += timedelta(days=1)
    return {
        'start_date': [start_date],
        'end_date': [end_date],
        'timelapse': fechas
    }
    
