"""Rotas do app diario_bordo"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.view_listar_diario, name='listar_diario'),
    path('novo/', views.view_criar_ocorrencia, name='criar_ocorrencia'),
    path('<int:pk>/', views.view_detalhe_ocorrencia, name='detalhe_ocorrencia'),
    path('<int:pk>/editar/', views.view_editar_ocorrencia, name='editar_ocorrencia'),
    path('<int:pk>/excluir/', views.view_excluir_ocorrencia, name='excluir_ocorrencia'),
    path('<int:pk>/confirmar-leitura/', views.view_confirmar_leitura, name='confirmar_leitura_diario'),
    path('confirmar-todas/', views.view_confirmar_todas_leituras, name='confirmar_todas_leituras_diario'),
]

