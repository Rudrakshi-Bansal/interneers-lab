from django.urls import path
from core.adapters.api.views import products, product_detail

urlpatterns = [
    path("products/", products),
    path("products/<str:product_id>/", product_detail),
]
