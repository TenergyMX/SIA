from django.urls import path, include
from . import views

urlpatterns = [
    path('', include('modules.views.main.urls') ),
    path('', include("modules.views.authentication.urls")),
    path('', include('modules.views.users.urls') ),
    path('', include('modules.views.vehicles.urls') ),
    path('', include('modules.views.computer-equipment.urls') ),
    path('', include('modules.views.infrastructure.urls') ),
    path('', include('modules.views.equipment-and-tools.urls') ),
]