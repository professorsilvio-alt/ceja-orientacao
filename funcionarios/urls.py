"""URLs do app funcionarios"""
from django.urls import path
from . import views

urlpatterns = [
    # Administrativos
    path('administrativos/', views.view_listar_administrativos, name='listar_administrativos'),
    path('administrativos/novo/', views.view_criar_administrativo, name='criar_administrativo'),
    path('administrativos/<int:pk>/', views.view_detalhe_administrativo, name='detalhe_administrativo'),
    path('administrativos/<int:pk>/editar/', views.view_editar_administrativo, name='editar_administrativo'),

    # Terceirizados
    path('terceirizados/', views.view_listar_terceirizados, name='listar_terceirizados'),
    path('terceirizados/novo/', views.view_criar_terceirizado, name='criar_terceirizado'),
    path('terceirizados/<int:pk>/', views.view_detalhe_terceirizado, name='detalhe_terceirizado'),
    path('terceirizados/<int:pk>/editar/', views.view_editar_terceirizado, name='editar_terceirizado'),

    # Controle de Ponto (RH Terceirizados)
    path('ponto/', views.view_terminal_ponto, name='terminal_ponto'),
    path('ponto/api/terceirizados/', views.api_listar_terceirizados_totem, name='api_listar_terceirizados_totem'),
    path('ponto/api/validar_pin/', views.api_validar_pin, name='api_validar_pin'),
    path('ponto/api/registrar/', views.api_registrar_ponto, name='api_registrar_ponto'),
    path('ponto/espelho/', views.view_espelho_ponto, name='espelho_ponto'),
    path('ponto/<int:pk>/editar/', views.view_editar_ponto_terceirizado, name='editar_ponto_terceirizado'),
    path('ponto/<int:pk>/excluir/', views.view_excluir_ponto_terceirizado, name='excluir_ponto_terceirizado'),
    path('ponto/senhas/', views.view_gerenciar_senhas_ponto, name='gerenciar_senhas_ponto'),
    path('terceirizados/folha-ponto/', views.view_folha_ponto_kratus, name='folha_ponto_kratus'),
    path('terceirizados/<int:pk>/folha-ponto/', views.view_folha_ponto_kratus, name='folha_ponto_terceirizado'),
]

