from django.urls import path
from core.adapters.api.views import (
    products,
    products_bulk,
    product_detail,
    product_categories,
    product_category_detail,
    categories,
    category_detail,
)

urlpatterns = [
    path("products/", products),
    path("products/bulk/", products_bulk),
    path("products/<str:product_id>/", product_detail),
    path("products/<str:product_id>/categories/", product_categories),
    path(
        "products/<str:product_id>/categories/<str:category_id>/",
        product_category_detail,
    ),
    path("categories/", categories),
    path("categories/<str:category_id>/", category_detail),
]
