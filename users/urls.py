from django.urls import path
from . import views

urlpatterns = [
    path("user/login/", views.login_view, name="login"),
    path("user/logout/", views.logout_view),
    path("user/profile/", views.users_profile_view),
]