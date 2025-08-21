from django.urls import path
from . import views

urlpatterns = [
    # TODO ----- [ VIEWS ] -----
    path("companys/", views.companys_views),
    path("users/", views.users_views),
    path("providers/", views.providers_views),
    path("areas/", views.areas_views),

    path("plans/", views.plans_views),

    path("user/profile/", views.users_profile_view),

    # TODO ----- [ REQUEST ] -----

    # TODO ----- [ Empresas ] -----
    path("add_company/", views.add_company),
    path("get_companys/", views.get_companys),
    path("edit_company/", views.edit_company),
    path("delete_company/", views.delete_company),

    # TODO ----- [ Usuarios ] -----
    path("add_user_with_access/", views.add_user_with_access),
    path("get_user_with_access/", views.get_user_with_access),
    path("get_users_with_access/", views.get_users_with_access),
    path("update_user_with_access/", views.update_user_with_access),
    path("delete_user_with_access/", views.delete_user_with_access),
    path("get_userPermissions/", views.get_userPermissions),
    path("update_userPermissions/", views.update_userPermissions),
    path("deactivate_user/", views.deactivate_user),

    # TODO ----- [ Proveedores ] -----
    path("add-provider/", views.add_provider),
    path("get-providers/", views.get_providers),
    path("update-provider/", views.update_provider),
    path("delete-provider/", views.delete_provider),

    # TODO ----- [ Areas ] -----
    path("add_area/", views.add_area),
    path("get_areas/", views.get_areas),
    path("update_area/", views.update_area),
    path("delete_area/", views.delete_area),
    #------[Planes]--------
    path("get_table_plans/", views.get_table_plans),
    path("get_company_plan/", views.get_company_plan),
    path("get_modules_plan/", views.get_modules_plan),
    path("add_plan/", views.add_plan),
    path("delete_plans/", views.delete_plans),
    path("edit_plans/", views.edit_plans),

    
]