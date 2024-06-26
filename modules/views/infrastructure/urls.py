from django.urls import path
from . import views

urlpatterns = [
    # Vistas
    path("infrastructure/", views.infrastructure_item_view),
    path("infrastructure/category/", views.infrastructure_category_view),
    path("infrastructure/review/", views.infrastructure_review_view),

    # Peticiones
    path("get-infrastructure-categorys/", views.get_infrastructure_categorys),
    path("add-infrastructure-category/", views.add_infrastructure_category),
    path("update-infrastructure-category/", views.update_infrastructure_category),
    path("delete-infrastructure-category/", views.delete_infrastructure_category),

    path("add-infrastructure-item/", views.add_infrastructure_item),
    path("get-infrastructure-items/", views.get_infrastructure_items),
    path("update-infrastructure-item/", views.update_infrastructure_item),
    path("delete-infrastructure-item/", views.delete_infrastructure_item),

    path("add-infrastructure-review/", views.add_infrastructure_review),
    path("get-infrastructure-reviews/", views.get_infrastructure_reviews),
    path("update-infrastructure-review/", views.update_infrastructure_review),
    path("delete-infrastructure-review/", views.delete_infrastructure_review),

    path("generates_review/", views.generates_review),
]