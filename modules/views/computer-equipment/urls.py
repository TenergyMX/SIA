from django.urls import path
from . import views

urlpatterns = [
    # Vistas
    path('computers-equipment/', views.computer_equipment_view),
    path('computers-equipment/info/<int:equipment_id>/', views.computer_system_details),
    path("computers-equipment/peripheral/", views.computer_peripherals),
    path("computers-equipment/software/", views.computer_software),
    path("computers-equipment/audit/", views.computer_equipment_audit_view),
    path("computers-equipment/maintenance/", views.computer_equipment_maintenance_view),
    path("computers-equipment/assigned/", views.assigned_computer_equipment_view),
    path("computers-equipment/responsiva/", views.computer_equipment_responsiva_view),
    path("computers-equipment/responsiva/pdf/", views.computer_equipment_responsiva_pdf_view),
    path("computers-equipment/deliverie/", views.computer_equipment_deliverie_view),
    path("computers-equipment/deliverie/pdf/", views.computer_equipment_deliverie_pdf_view),

    # Peticiones
    path("add-computer-system/", views.add_computer_system),
    path("get-computer-equipment/", views.get_computer_equipment),
    path("get-computers-equipment/", views.get_computers_equipment),
    path("update-computer-system/", views.update_computer_system),
    path("delete-computer-system/", views.delete_computer_system),

    path("add_computer_peripheral/", views.add_computer_peripherals),
    path("get_computer_peripherals/", views.get_computer_peripherals),
    path("update_computer_peripheral/", views.update_computer_peripheral),
    path("delete_computer_peripheral/", views.delete_computer_peripheral),

    path("add_software/", views.add_software),
    path("get_softwares/", views.get_softwares),
    path("update_software/", views.update_software),
    path("delete_softwares/", views.get_softwares),

    path("add_software_installation/", views.add_software_installation),
    path("get_software_installations/", views.get_software_installations),
    path("update_software_installation/", views.update_software_installation),
    path("delete_software_installation/", views.delete_software_installations),

    path("add-computer-equipment-audit/", views.add_computer_equipment_audit),
    path("get-computer-equipment-audits/", views.get_computer_equipment_audits),
    path("update-computer-equipment-audit/", views.update_computer_equipment_audit),
    path("delete-computer-equipment-audit/", views.delete_computer_equipment_audit),

    path("add-computer-equipment-maintenance/", views.add_computer_equipment_maintenance),
    path("get-computer-equipment-maintenances/", views.get_computer_equipment_maintenances),
    path("update-computer-equipment-maintenance/", views.update_computer_equipment_maintenance),
    path("delete-computer-equipment-maintenance/", views.delete_computer_equipment_maintenance),

    path("add-computer-equipment-responsiva/", views.add_computer_equipment_responsiva),
    path("get-computer-equipment-responsivas/", views.get_computer_equipment_responsiva),
    path("update-computer-equipment-responsiva/", views.update_computer_equipment_responsiva),
    path("delete-computer-equipment-responsiva/", views.delete_computer_equipment_responsiva),

    path("add-computer-equipment-deliverie/", views.add_computer_equipment_deliverie),
    path("get-computer-equipment-deliveries/", views.get_computer_equipment_deliveries),
    path("update-computer-equipment-deliverie/", views.update_computer_equipment_deliverie),
    path("delete-computer-equipment-deliverie/", views.delete_computer_equipment_deliverie),

    path("get_users_with_assigned_computer_equipment/", views.get_users_with_assigned_computer_equipment),
]
