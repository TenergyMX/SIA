from django.urls import path
from . import views

urlpatterns = [
    # ! Vistas
    path("", views.module_home),
    path("companys/", views.module_companys),
    path("users/", views.module_users),
    path("providers/", views.module_providers),

    path("module/vehicle/", views.module_vehicle),
    path("module/vehicle/info/", views.module_vehicle),                     # Encaso de no pasarle id
    path("module/vehicle/info/<int:vehicle_id>/", views.module_vehicle_info_id),    # Si le pasa el id
    path("module/vehicle/tenencia/", views.module_vehicle_tenencia),
    path("module/vehicle/refrendo/", views.module_vehicle_refrendo),
    path("module/vehicle/verificacion/", views.module_vehicle_verificacion),
    path("module/vehicle/responsiva/", views.module_vehicle_responsiva),
    path("module/vehicle/insurance/", views.module_vehicle_insurance), # Seguro
    path("module/vehicle/audit/", views.module_vehicle_audit), # Auditoria
    path("module/vehicle/maintenance/", views.module_vehicle_maintenance), # Mantenimiento

    # ! Global
    path("get_notifications/", views.get_notifications),

    # TODO ----- [ Empresas ] -----
    path("get_companys/", views.get_companys),


    # TODO ----- [ Usuarios ] -----
    path("add_user_with_access/", views.add_user_with_access),
    path("get_user_with_access/", views.get_user_with_access),
    path("get_users_with_access/", views.get_users_with_access),
    path("update_user_with_access/", views.update_user_with_access),
    path("delete_user_with_access/", views.update_user_with_access),
    path("get_userPermissions/", views.get_userPermissions),
    path("update_userPermissions/", views.update_userPermissions),

    # TODO ----- [ Proveedores ] -----
    path("add_provider/", views.add_provider),
    path("get_providers/", views.get_providers),
    path("update_provider/", views.update_provider),
    path("delete_provider/", views.delete_provider),

    # ! Modulo: vehiculo

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
]