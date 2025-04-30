from django.urls import path
from . import views

urlpatterns = [
    # TODO ----- [ VIEWS ] -----
    path("vehicles/reports/", views.vehicles_reports_view),
    path("vehicles/get-statistics/", views.vehicle_statistic),
]