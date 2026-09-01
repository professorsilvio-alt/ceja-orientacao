from django.urls import path
from . import views

urlpatterns = [
    # Chat com a Beth
    path('', views.chat_view, name='cerebro_chat'),
    path('conversa/<int:conversa_id>/', views.chat_view, name='cerebro_chat_conversa'),
    path('nova-conversa/', views.nova_conversa, name='cerebro_nova_conversa'),
    path('api/enviar-mensagem/', views.enviar_mensagem_api, name='cerebro_api_enviar_mensagem'),
    path('api/transcrever-audio/', views.transcrever_audio_api, name='cerebro_api_transcrever_audio'),

    # Acervo e Gestão de Documentos
    path('documentos/', views.listar_documentos, name='cerebro_documentos'),
    path('documentos/novo/', views.upload_documento, name='cerebro_upload_documento'),
    path('documentos/<int:doc_id>/', views.detalhe_documento, name='cerebro_detalhe_documento'),
    path('documentos/<int:doc_id>/excluir/', views.excluir_documento, name='cerebro_excluir_documento'),
    path('documentos/<int:doc_id>/reprocessar/', views.reprocessar_documento, name='cerebro_reprocessar_documento'),
]
