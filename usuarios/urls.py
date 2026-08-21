"""URLs do app usuarios"""
from django.urls import path
from . import views

urlpatterns = [
    # Autenticação
    path('login/', views.view_login, name='login'),
    path('logout/', views.view_logout, name='logout'),
    path('trocar-senha/', views.view_trocar_senha, name='trocar_senha'),
    path('recuperar-senha/', views.view_recuperar_senha, name='recuperar_senha'),
    path('redefinir-senha/<str:token>/', views.view_redefinir_senha, name='redefinir_senha'),

    # Dashboard
    path('', views.view_dashboard, name='home'),
    path('dashboard/', views.view_dashboard, name='dashboard'),

    # CRUD Usuários (somente Diretor)
    path('usuarios/', views.view_listar_usuarios, name='listar_usuarios'),
    path('usuarios/novo/', views.view_criar_usuario, name='criar_usuario'),
    path('usuarios/<str:cpf>/editar/', views.view_editar_usuario, name='editar_usuario'),
    path('usuarios/<str:cpf>/resetar-senha/', views.view_resetar_senha_usuario, name='resetar_senha_usuario'),
]
