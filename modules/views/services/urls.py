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

    #Historial de pagos 
    path('get-payment-history/<int:service_id>/', views.get_payment_history),
    path('upload-payment-proof/<int:payment_id>/', views.upload_payment_proof),

    path('get-proof-payment/<int:payment_id>/', views.get_proof_payment),

    path('dashboard_data/', views.dashboard_data),

]

