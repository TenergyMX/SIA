from django.urls import path
from . import views

urlpatterns = [
    path("user/login/", views.login_view, name="login"),
    path("user/logout/", views.logout_view, name="login"),

    # Restablecer constraseña
    path("password-recovery/request-username/", views.password_recovery_request_username_view),
    path("password-recovery/verify-token/", views.password_recovery_verify_token_view),
    path("password_recovery/reset-password/", views.password_recovery_reset_password_view),
]