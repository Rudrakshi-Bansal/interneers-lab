from django.urls import path
from .views import greet_user_view

urlpatterns = [
    path("greet/", greet_user_view),
]
