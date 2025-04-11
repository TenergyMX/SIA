from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings


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
    path("delete_vehicle_verificacion/", views.delete_vehicle_verificacion),


    # TODO ----- [ Responsiva ] -----
    path("add_vehicle_responsiva/", views.add_vehicle_responsiva),
    path("get_vehicle_responsiva/", views.get_vehicle_responsiva),
    path("get_vehicles_responsiva/", views.get_vehicles_responsiva),
    path("update_vehicle_responsiva/", views.update_vehicle_responsiva),
    path("delete_vehicle_responsiva/", views.delete_vehicle_responsiva),

    # TODO ----- [ Seguro / Polisa ] -----
    path("add_vehicle_insurance/", views.add_vehicle_insurance),
    path("get_vehicle_insurance/", views.get_vehicle_insurance),
    path("get_vehicles_insurance/", views.get_vehicles_insurance),
    path("update_vehicle_insurance/", views.update_vehicle_insurance),
    path("delete_vehicle_insurance/", views.delete_vehicle_insurance),

    # Todo --- [ Auditoria ] ---
    path("add_vehicle_audit/", views.add_vehicle_audit),
    path("get_vehicle_audit/", views.get_vehicle_audit),
    path("get_vehicles_audit/", views.get_vehicles_audit),
    path("update_vehicle_audit/", views.update_vehicle_audit),
    path("delete_vehicle_audit/", views.delete_vehicle_audit),
    path("upd_audit_checks/", views.upd_audit_checks),
    path("evaluate_audit/", views.evaluate_audit),

    # Todo --- [ Mantenimiento ] ---
    path("add_vehicle_maintenance/", views.add_vehicle_maintenance),
    path("get_vehicle_maintenance/", views.get_vehicle_maintenance),
    path("get_vehicles_maintenance/", views.get_vehicles_maintenance),
    path("update_vehicle_maintenance/", views.update_vehicle_maintenance),
    path("delete_vehicle_maintenance/", views.delete_vehicle_maintenance),
    path("add_vehicle_kilometer/", views.add_vehicle_kilometer),
    path("delete_vehicle_kilometer/", views.delete_vehicle_kilometer),
    path("update_vehicle_kilometer/", views.update_vehicle_kilometer),
    path("get_vehicle_maintenance_kilometer/", views.get_vehicle_maintenance_kilometer),
    path('update_status_man/', views.update_status_man, name='update_status_man'),  # URL para actualizar el estado


    path("get-vehicles-calendar/", views.get_vehicles_calendar),

    path("add-vehicle-fuel/", views.add_vehicle_fuel),
    path("get-vehicle-fuels/", views.get_vehicles_fuels),
    path("get-vehicle-fuels-charts/", views.get_vehicles_fuels_charts),
    path("update-vehicle-fuel/", views.update_vehicle_fuel),
    path("delete-vehicle-fuel/", views.delete_vehicle_fuel),
    path("add_maintenance_option/", views.add_vehicle_maintenance),
    path("add_option/", views.add_option),
    path("obtener_opciones/", views.obtener_opciones),


    path('generate_qr/<str:qr_type>/<int:vehicle_id>/', views.generate_qr, name='generate_qr'),
    path('delete_qr/<str:qr_type>/<int:vehicle_id>/', views.delete_qr, name='delete_qr'),
    path('descargar_qr/', views.descargar_qr),

    path("vehicles/responsiva/<str:qr>/<int:vehicle_id>", views.module_vehicle_responsiva),
    path("validar_vehicle_en_sa/", views.validar_vehicle_en_sa),
    path("verificar_mantenimiento/", views.verificar_mantenimiento),

    #conductores
    path("driver_vehicles/", views.driver_vehicles),
    path("get_table_vehicles_driver/", views.get_table_vehicles_driver),
    path("get_users/", views.get_users),
    path("add_driver/", views.add_driver),
    path("delete_driver/", views.delete_driver),
    path("get_drivers/", views.get_drivers),
    path("edit_driver/", views.edit_driver),

    #información
    path("drivers/info/<int:driver_id>/", views.drivers_details),
    path("drivers/info/<int:driver_id>/details/", views.get_driver_details),

    #licencias
    path("get_table_licence/", views.get_table_licence),
    path("add_licence/", views.add_licence),
    path("edit_licence/", views.edit_licence),
    path("delete_licence/", views.delete_licence),

    #multas
    path("get_vehicles/", views.get_vehicles),
    path("get_table_multas/", views.get_table_multas),
    path("add_multa/", views.add_multa),
    path("edit_multa/", views.edit_multa),
    path("delete_multa/", views.delete_multa),

    path("add_check/", views.add_check),
    path("obtener_checks_empresa/", views.obtener_checks_empresa),
    path('get_checks_by_audit/<int:audit_id>/', views.get_checks_by_audit),
    
    path('get_user_vehicles/', views.get_user_vehicles),
    path('get_user_vehicles_for_edit/', views.get_user_vehicles_for_edit),
]