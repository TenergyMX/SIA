from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('develop/', views.develop_view),

    # path("500/", views.error_500_view),

    path("get-notifications/", views.get_notifications),
    path('update_records/', views.update_or_create_records),
    
    path('enviar-cotizacion/', views.enviar_cotizacion, name='enviar_cotizacion'),
]