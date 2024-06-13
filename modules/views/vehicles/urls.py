from django.urls import path
from . import views

urlpatterns = [
    # TODO ---------- [ VIEWS ] ----------
    path("vehicles/", views.vehicles),
    path("vehicles/info/", views.vehicles),
    path("vehicles/info/<int:vehicle_id>/", views.vehicles_details),
    path("vehicles/tenencia/", views.module_vehicle_tenencia),
    path("vehicles/refrendo/", views.module_vehicle_refrendo),
    path("vehicles/verificacion/", views.module_vehicle_verificacion),
    path("vehicles/responsiva/", views.module_vehicle_responsiva),
    path("vehicles/insurance/", views.module_vehicle_insurance),
    path("vehicles/audit/", views.module_vehicle_audit),
    path("vehicles/maintenance/", views.module_vehicle_maintenance),
    path("vehicles/calendar/", views.vehicles_calendar_views),
    path("vehicles/fuel/", views.vehicles_fuel_views),

    # TODO ---------- [ REQUEST ] ----------

    # TODO ----- [ Vehiculos ] -----
    path("add_vehicle_info/", views.add_vehicle_info),
    path("get_vehicle_info/", views.get_vehicle_info),
    path("get_vehicles_info/", views.get_vehicles_info),
    path("update_vehicle_info/", views.update_vehicle_info),
    path("delete_vehicle_info/", views.delete_vehicle_info),

    # TODO ----- [ Tenencia ] -----
    path("add_vehicle_tenencia/", views.add_vehicle_tenencia),
    path("get_vehicle_tenencia/", views.get_vehicle_tenencia),
    path("get_vehicles_tenencia/", views.get_vehicles_tenencia),
    path("update_vehicle_tenencia/", views.update_vehicle_tenencia),
    path("delete_vehicle_tenencia/", views.delete_vehicle_tenencia),

    # TODO ----- [ Refrendo ] -----
    path("add_vehicle_refrendo/", views.add_vehicle_refrendo),
    path("get_vehicle_refrendo/", views.get_vehicle_refrendo),
    path("get_vehicles_refrendo/", views.get_vehicles_refrendo),
    path("update_vehicle_refrendo/", views.update_vehicle_refrendo),
    path("delete_vehicle_refrendo/", views.delete_vehicle_refrendo),

    # TODO ----- [ Verificacion ] -----
    path("add_vehicle_verificacion/", views.add_vehicle_verificacion),
    path("get_vehicle_verificacion/", views.get_vehicle_verificacion),
    path("get_vehicles_verificacion/", views.get_vehicles_verificacion),
    path("update_vehicle_verificacion/", views.update_vehicle_verificacion),

    # TODO ----- [ Responsiva ] -----
    path("add_vehicle_responsiva/", views.add_vehicle_responsiva),
    path("get_vehicle_responsiva/", views.get_vehicle_responsiva),
    path("get_vehicles_responsiva/", views.get_vehicles_responsiva),
    path("update_vehicle_responsiva/", views.update_vehicle_responsiva),
    path("delete_vehicle_responsiva/", views.delete_vehicle_responsiva),

    # TODO ----- [ Seguro / Polisa ] -----
    path("add_vehicle_insurance/", views.add_vehicle_insurance),
    path("get_vehicle_insurance/", views.get_vehicle_insurance),
    path("get_vehicles_insurance/", views.get_vehicle_insurance),
    path("update_vehicle_insurance/", views.update_vehicle_insurance),
    path("delete_vehicle_insurance/", views.delete_vehicle_insurance),

    # Todo --- [ Auditoria ] ---
    path("add_vehicle_audit/", views.add_vehicle_audit),
    path("get_vehicle_audit/", views.get_vehicle_audit),
    path("get_vehicles_audit/", views.get_vehicles_audit),
    path("update_vehicle_audit/", views.update_vehicle_audit),
    path("delete_vehicle_audit/", views.delete_vehicle_audit),

    # Todo --- [ Mantenimiento ] ---
    path("add_vehicle_maintenance/", views.add_vehicle_maintenance),
    path("get_vehicle_maintenance/", views.get_vehicle_maintenance),
    path("get_vehicles_maintenance/", views.get_vehicles_maintenance),
    path("update_vehicle_maintenance/", views.update_vehicle_maintenance),
    path("delete_vehicle_maintenance/", views.delete_vehicle_maintenance),

    path("get-vehicles-calendar/", views.get_vehicles_calendar),

    path("add-vehicle-fuel/", views.add_vehicle_fuel),
    path("get-vehicle-fuels/", views.get_vehicles_fuels),
    path("get-vehicle-fuels-charts/", views.get_vehicles_fuels_charts),
    path("update-vehicle-fuel/", views.update_vehicle_fuel),
    path("delete-vehicle-fuel/", views.delete_vehicle_fuel),
]
