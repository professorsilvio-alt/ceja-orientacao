"""URLs do app agenda"""
from django.urls import path
from . import views

urlpatterns = [
    # Presenças
    path('presencas/', views.view_listar_presencas, name='listar_presencas'),
    path('presencas/novo/', views.view_novo_registro, name='novo_registro_presenca'),
    path('presencas/<int:pk>/editar/', views.view_editar_registro, name='editar_registro_presenca'),
    path('presencas/<int:pk>/excluir/', views.view_excluir_registro, name='excluir_registro_presenca'),

    # Auditório
    path('auditorio/', views.view_agenda_auditorio, name='agenda_auditorio'),
    path('auditorio/novo/', views.view_nova_reserva, name='nova_reserva'),
    path('auditorio/<int:pk>/editar/', views.view_editar_reserva, name='editar_reserva'),
    path('auditorio/<int:pk>/excluir/', views.view_excluir_reserva, name='excluir_reserva'),
    path('auditorio/json/', views.view_reservas_json, name='reservas_json'),
]
