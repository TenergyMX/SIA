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
    # path("vehicles_placas/", views.vehicles_placas),
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
    path("save_commitment_date/", views.save_commitment_date),
    path("vehicles/save_correction_evidence/", views.save_correction_evidence),

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

    path("add-vehicle-fuel/", views.add_vehicle_fuel, name="add_vehicle_fuel"),

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

    #placas
    path('get_vehicles/', views.get_vehicles),
    # path('table_placa_vehicles/', views.table_placa_vehicles),
    path('add_placa/', views.add_placa),
    path('update_status_placa/', views.update_status_placa),
    path('delete_placa/', views.delete_placa),
    path('edit_placa/', views.edit_placa),
    path('table_placa_vehicle/', views.table_placa_vehicle),
    path('get_vehicles_placa/', views.get_vehicles_placa),

    # Cartas de factura
    path('table_letter_factura_vehicle/', views.table_letter_factura_vehicle),
    path('get_vehicles_letter_factura/', views.get_vehicles_letter_factura),
    path('add_letter_factura/', views.add_letter_factura),
    path('edit_letter_factura/', views.edit_letter_factura),
    path('delete_letter_factura/', views.delete_letter_factura),

    path("vehicles/fuel-form/", views.qr_vehicle_fuel_form),

    # Facturas de Vehículos
    path('table_factura_vehicle/', views.table_factura_vehicle),
    path('add_factura/', views.add_factura),
    path('edit_factura/', views.edit_factura),
    path('delete_factura/', views.delete_factura),

    #tarjeta de vehiculos
    path('get_vehicles_card/', views.get_vehicles_card),
    path('add_card/', views.add_card),
    path('table_card_vehicle/', views.table_card_vehicle),
    path('edit_card/', views.edit_card),
    path("delete_card/", views.delete_card),
    
    # contrato
    path('table_contract_vehicle/', views.table_contract_vehicle),
    path('get_vehicles_contract/', views.get_vehicles_contract),
    path('add_contract/', views.add_contract),
    path('edit_contract/', views.edit_contract),
    path('delete_contract/', views.delete_contract),
    path('upload_letter_finiquito/', views.upload_letter_finiquito),
    path('cancel_contract_vehicle/', views.cancel_contract_vehicle),

    # Hologramas
    path('get_vehicles_hologram/', views.get_vehicles_hologram),
    path('table_hologram_vehicle/', views.table_hologram_vehicle),
    path('add_hologram/', views.add_hologram),
    path('edit_hologram/', views.edit_hologram),
    path('delete_hologram/', views.delete_hologram),

    # Carnet de servicios
    path('get_vehicles_carnet/', views.get_vehicles_carnet),
    path('table_carnet_vehicle/', views.table_carnet_vehicle),
    path('add_carnet/', views.add_carnet),
    path('edit_carnet/', views.edit_carnet),
    path('delete_carnet/', views.delete_carnet),

    # desactivar un vehiculo
    path("deactivate_vehicle/", views.deactivate_vehicle),

    # #codigo qr combustible
    # path('generate_qr_fuel/<str:qr_type>/<int:vehicle_id>/', views.generate_qr_fuel),
    # path('check_qr_fuel/<int:vehicle_id>/', views.check_qr_fuel),
    # path('descargar_qr_fuel/', views.descargar_qr_fuel),
    # # path('delete_qr_computer/<str:qr_type>/<int:computerSystemId>/', views.delete_qr_computer),

]