
from django.urls import path
from . import views

urlpatterns = [
    # TODO ----- [ VIEWS ] -----
    path("companys/", views.companys_views),
    path("users/", views.users_views),
    path("providers/", views.providers_views),
    path("areas/", views.areas_views),

    path("user/profile/", views.users_profile_view),

    # TODO ----- [ REQUEST ] -----

    # TODO ----- [ Empresas ] -----
    path("add-company/", views.get_companys),
    path("get-companys/", views.get_companys),
    path("update-company/", views.get_companys),
    path("delete-company/", views.get_companys),

    # TODO ----- [ Usuarios ] -----
    path("add_user_with_access/", views.add_user_with_access),
    path("get_user_with_access/", views.get_user_with_access),
    path("get_users_with_access/", views.get_users_with_access),
    path("update_user_with_access/", views.update_user_with_access),
    path("delete_user_with_access/", views.update_user_with_access),
    path("get_userPermissions/", views.get_userPermissions),
    path("update_userPermissions/", views.update_userPermissions),

    # TODO ----- [ Proveedores ] -----
    path("add-provider/", views.add_provider),
    path("get-providers/", views.get_providers),
    path("update-provider/", views.update_provider),
    path("delete-provider/", views.delete_provider),

    # TODO ----- [ Areas ] -----
    path("add_area/", views.add_area),
    path("get_areas/", views.get_areas),
    path("update_area/", views.update_area),
]