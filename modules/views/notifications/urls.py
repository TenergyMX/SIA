from django.urls import path
from . import views

urlpatterns = [
    #TODO - - - - - - - - - - V I E W S - - - - - - - - - - 
    path("notifications/", views.notifications_views),
    #path("vehicles/reports/", views.vehicles_reports_view),
]