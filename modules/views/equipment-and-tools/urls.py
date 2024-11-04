from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    #vistas
    path("equipments_and_tools/", views.equipments_and_tools),
    path("equipments_tools/", views.equipments_tools),
    path("responsiva/", views.responsiva),

    #peticiones para las tablas
    path("get_equipments_tools_categorys/", views.get_equipments_tools_categorys),
    path("get_equipments_tools/", views.get_equipments_tools),
    path("get_responsiva/", views.get_responsiva),

    #urls de categorias 
    path("add_equipment_category/", views.add_equipment_category), 
    path("edit_category/", views.edit_category),
    path("delete_category/", views.delete_category),

    #urls de equipos y herramientas 
    path("add_equipment_tools/", views.add_equipment_tools),
    path("edit_equipments_tools/", views.edit_equipments_tools),
    path("delete_equipment_tool/", views.delete_equipment_tool),

    #urls de responsivas 
    path("add_responsiva/", views.add_responsiva),
    path("status_responsiva/", views.status_responsiva),
    path("edit_date_responsiva/", views.edit_date_responsiva),

    #funciones para llaves foraneas
    path("get_equipment_categories/", views.get_equipment_categories),
    path("get_responsible_users/", views.get_responsible_users),
    path("get_equipment_areas/", views.get_equipment_areas),
    path("get_responsible_user/", views.get_responsible_user),
    path("get_locations/", views.get_locations),
    path("get_company/", views.get_company),

    path("get_server_date/", views.get_server_date),

    #funcion para el historial de los equipos
    path("get-equipment-history/", views.get_equipment_history),

    #funcion para agregar una nueva ubicación
    path("add_location/", views.add_location),
    #función para validar las fechas en el estado del equipo: 
    path("validar_fecha/", views.validar_fecha),
    #funcion para aprovar las responsivas
    path("approve_responsiva/", views.approve_responsiva),
    path("cancel_responsiva/", views.cancel_responsiva),

    #url para generar el pdf de la responsiva
    path("render_to_pdf/", views.render_to_pdf),
    path("generate_pdf/<int:responsiva_id>/", views.generate_pdf, name='generate_pdf'),

    #path("get_doc/", views.get_doc)
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)