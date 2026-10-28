"""URLs da API do totem"""
from django.urls import path
from . import views

urlpatterns = [
    path('horarios/', views.view_horarios_totem, name='api_horarios_totem'),
    path('auditorio/', views.view_auditorio_totem, name='api_auditorio_totem'),
    path('escola/', views.view_info_escola, name='api_info_escola'),
    path('feedback/', views.api_enviar_feedback, name='api_enviar_feedback'),
    path('feedback/listar/', views.api_listar_feedbacks, name='api_listar_feedbacks'),
]
