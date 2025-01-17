from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    # TODO ----- [ VIEWS ] -----
    #submodulos de servicios 
    path("category_services/", views.category_services),
    path("services/", views.services),
    path("dashboard_services/", views.dashboard_services),
    path("payments_history/", views.payments_history),

    #tablas
    path("get_table_category_service/", views.get_table_category_service),
    path("get_table_services/", views.get_table_services),
    
    #categorias 
    path("add_category/", views.add_category),
    path("edit_category_services/", views.edit_category_services),
    path("delete_category_services/", views.delete_category_services),

    #servicios
    path("get_services_categories/", views.get_services_categories),
    path("get_services_providers/", views.get_services_providers),
    path("edit_services/", views.edit_services),
    path("add_service/", views.add_service),
    path("delete_services/", views.delete_services),
    

    path("update_payments_status/", views.update_payment_status),

    #Historial de pagos 
    path('get_payment_history/<int:service_id>/', views.get_payment_history),
    path('upload-payment-proof/<int:payment_id>/', views.upload_payment_proof),

    path('get-proof-payment/<int:payment_id>/', views.get_proof_payment),
    # Función para actualizar los pagos
    path('update_payment_status_view/', views.update_payment_status_view),
    #contadores
    path('get_dashboard_data/', views.get_dashboard_data),
    #Gráfica
    path('get_dashboard_grafica/', views.get_dashboard_grafica),

    path('get_services_by_category/<int:category_id>/', views.get_services_by_category),
    path('get_services_by_provider/<int:provider_id>/', views.get_services_by_provider),

    path('get_services_by_date_range/', views.get_services_by_date_range),


    path('get_payment_history_notifications/<int:service_id>/', views.get_payment_history_notifications),


    #Gráfica de historial de pagos 
    path('get_services_categories_payments/', views.get_services_categories_payments),
    path('get_payment_history_grafic/', views.get_payment_history_grafic),

]

