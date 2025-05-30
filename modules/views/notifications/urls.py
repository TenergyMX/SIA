from django.urls import path
from . import views

urlpatterns = [
    #TODO - - - - - - - - - - V I E W S - - - - - - - - - - 
    path("notifications/", views.notifications_views),
    path("notifications/mci-read-moduls/", views.notificationRead_modules),
    
    #TODO - - - - - - - - - - C R U D  - - - - - - - - - - 
    path("notifications/create-notification/", views.create_notification),
    path("notifications/get-notification-system/", views.read_notification),
    path("notifications/delete-notification/", views.delete_notification),
]