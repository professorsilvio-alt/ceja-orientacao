"""URLs do app professores"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.view_listar_professores, name='listar_professores'),
    path('configuracao/', views.view_configuracao_escola, name='configuracao_escola'),
    path('novo/', views.view_criar_professor, name='criar_professor'),
    path('<int:pk>/', views.view_detalhe_professor, name='detalhe_professor'),
    path('<int:pk>/editar/', views.view_editar_professor, name='editar_professor'),
    path('<int:pk>/horarios/', views.view_horarios_professor, name='horarios_professor'),
    path('horarios/<int:horario_pk>/aprovar/', views.view_aprovar_horario, name='aprovar_horario'),
    path('horarios/<int:horario_pk>/remover/', views.view_remover_horario, name='remover_horario'),

    # Módulo Quadro de Horários & Alocação
    path('horarios/quadro/', views.view_listar_quadro_horarios, name='quadro_horarios'),
    path('horarios/quadro/turma/<int:pk>/', views.view_grade_turma, name='grade_turma'),
    path('horarios/quadro/turma/<int:pk>/alocar/', views.view_salvar_alocacao_slot, name='salvar_alocacao_slot'),
    path('horarios/quadro/turma/<int:pk>/excluir/', views.view_excluir_turma, name='excluir_turma'),

    # Módulo Pasta Digital do Servidor (Documentos, Folgas, Anotações)
    path('pasta/<str:tipo_servidor>/<int:pk>/documentos/adicionar/', views.view_adicionar_documento_servidor, name='adicionar_documento_servidor'),
    path('pasta/documentos/<int:pk>/editar/', views.view_editar_documento_servidor, name='editar_documento_servidor'),
    path('pasta/documentos/<int:pk>/excluir/', views.view_excluir_documento_servidor, name='excluir_documento_servidor'),
    path('pasta/<str:tipo_servidor>/<int:pk>/folgas/adicionar/', views.view_adicionar_folga_servidor, name='adicionar_folga_servidor'),
    path('pasta/folgas/<int:pk>/editar/', views.view_editar_folga_servidor, name='editar_folga_servidor'),
    path('pasta/folgas/<int:pk>/excluir/', views.view_excluir_folga_servidor, name='excluir_folga_servidor'),
    path('pasta/<str:tipo_servidor>/<int:pk>/anotacoes/adicionar/', views.view_adicionar_anotacao_servidor, name='adicionar_anotacao_servidor'),
    path('pasta/anotacoes/<int:pk>/editar/', views.view_editar_anotacao_servidor, name='editar_anotacao_servidor'),
    path('pasta/anotacoes/<int:pk>/excluir/', views.view_excluir_anotacao_servidor, name='excluir_anotacao_servidor'),
]
