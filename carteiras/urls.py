from django.urls import path
from . import views

urlpatterns = [
    path('', views.pagina_publica_carteira, name='carteiras_publica'),
    path('emitir/', views.emitir_carteira_api, name='carteiras_emitir'),
    path('imprimir/<str:codigo>/', views.imprimir_carteira, name='carteiras_imprimir'),
    path('validar/<str:codigo>/', views.validar_carteira_publica, name='carteiras_validar'),
    path('auditoria/', views.painel_auditoria_diretor, name='carteiras_auditoria'),
    path('bookmarklet.js', views.bookmarklet_js, name='carteiras_bookmarklet_js'),
    path('sync/', views.sincronizar_servidor, name='carteiras_sync'),
]

