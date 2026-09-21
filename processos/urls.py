"""Rotas do app processos."""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.view_listar_processos, name='listar_processos'),
    path('novo/', views.view_criar_processo, name='criar_processo'),
    path('<int:pk>/', views.view_detalhe_processo, name='detalhe_processo'),
    path('<int:pk>/editar/', views.view_editar_processo, name='editar_processo'),
    path('<int:pk>/excluir/', views.view_excluir_processo, name='excluir_processo'),
    path('<int:pk>/andamento/', views.view_adicionar_andamento, name='adicionar_andamento'),
]
