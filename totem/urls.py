"""URLs da API do totem"""
from django.urls import path
from . import views

urlpatterns = [
    path('horarios/', views.view_horarios_totem, name='api_horarios_totem'),
    path('escola/', views.view_info_escola, name='api_info_escola'),
]
