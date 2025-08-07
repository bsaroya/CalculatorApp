from django.urls import path
from . import views

urlpatterns = [
    path('', views.subnet_calculator, name='subnet_calculator'),
]