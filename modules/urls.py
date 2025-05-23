from django.urls import path, include
from . import views

urlpatterns = [
    # mandamos llamar las url de las demas carpetas
    path('', include('modules.views.main.urls')),
    path('', include("modules.views.authentication.urls")),
    path('', include('modules.views.users.urls')),
    path('', include('modules.views.vehicles.urls')),
    path('', include('modules.views.computer-equipment.urls')),
    path('', include('modules.views.infrastructure.urls')),
    path('', include('modules.views.equipment-and-tools.urls')),
    path('', include('modules.views.services.urls')),
    path('', include('modules.views.charts.urls')),
    path('', include('modules.views.notifications.urls')),
]

