from django.urls import path
from . import views

urlpatterns = [
    # Vistas
    path("infrastructure/", views.infrastructure_item_view),
    path("infrastructure/category/", views.infrastructure_category_view),
    path("infrastructure/maintenance/", views.infrastructure_maintenance_view),

    # Peticiones
    path("get-infrastructure-categorys/", views.get_infrastructure_categorys),
    path("add-infrastructure-category/", views.add_infrastructure_category),
    path("update-infrastructure-category/", views.update_infrastructure_category),
    path("delete-infrastructure-category/", views.delete_infrastructure_category),

    path("add-infrastructure-item/", views.add_infrastructure_item),
    path("get-infrastructure-items/", views.get_infrastructure_items),
    path("update-infrastructure-item/", views.update_infrastructure_item),
    path("delete-infrastructure-item/", views.delete_infrastructure_item),

    # path("add-infrastructure-review/", views.add_infrastructure_review),
    # path("get-infrastructure-reviews/", views.get_infrastructure_reviews),
    # path("update-infrastructure-review/", views.update_infrastructure_review),
    # path("delete-infrastructure-review/", views.delete_infrastructure_review),

    # path("generates_review/", views.generates_review),

    #codigo qr
    path('generate_qr_infraestructure/<str:qr_type>/<int:itemId>/', views.generate_qr_infraestructure),
    path('check_qr_infraestructure/<int:itemId>/', views.check_qr_infraestructure),
    path('descargar_qr_infraestructure/', views.descargar_qr_infraestructure),
    path('delete_qr_infraestructure/<str:qr_type>/<int:itemId>/', views.delete_qr_infraestructure),

    path('get_items_locations/', views.get_items_locations),
    path('get_company_items/', views.get_company_items),
    path('add_item_location/', views.add_item_location),	
    path('get_infrastructure_item_details/', views.get_infrastructure_item_details),
    path('obtener_usuarios/', views.obtner_usuarios),
    path('asignar_responsable/', views.asignar_responsable),


    path('get_identifier/', views.get_identifier),
    path('get_items_providers/', views.get_items_providers),
    path('get_maintenance_actions/', views.get_maintenance_actions),
    path('add_new_maintenance_option/', views.add_new_maintenance_option),

    path('get_table_item_maintenance/', views.get_table_item_maintenance),
    path('add_infrastructure_maintenance/', views.add_infrastructure_maintenance),
    path("get_infrastructure_maintenance_detail/", views.get_infrastructure_maintenance_detail),

    path("delete_maintenance_infraestructure/", views.delete_maintenance_infraestructure),
    # path('get_infraestructure_details/<int:id>/', views.get_infraestructure_details),
    path('update_infrastructure_maintenance/', views.update_infraestructure_maintenance),

    path('update_status_mantenance/', views.update_status_mantenance),


    path('ajax/infra-info-by-maintenance/<int:maintenance_id>/', views.get_infrastructure_info_from_maintenance),
    path('mostrar_informacion/<int:maintenance_id>/', views.mostrar_informacion),
    path('mostrar_informacion_mantenimiento/<int:maintenance_id>/', views.mostrar_informacion_mantenimiento),







]