from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('develop/', views.develop_view),

    # path("500/", views.error_500_view),

    path("get-notifications/", views.get_notifications),
    path('update_records/', views.update_or_create_records),
    path('prueba_datos/', views.prueba_datos, name = 'prueba_datos'),
    
    path('enviar-cotizacion/', views.enviar_cotizacion, name='enviar_cotizacion'),
    
    path('stripe/get-plan/', views.getPlan),
    path('webhooks/stripe/', views.stripWebHook, name='stripe-webhook'),
    path('stripe-cancel/', views.CancelView.as_view(), name='cancel'),
    path('stripe-success/', views.SuccessView.as_view(), name='success'),
    path('reset-password/', views.siaChangePassword, name="siaChangePassword")
]