"""URLs do app professores"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.view_listar_professores, name='listar_professores'),
    path('novo/', views.view_criar_professor, name='criar_professor'),
    path('<int:pk>/', views.view_detalhe_professor, name='detalhe_professor'),
    path('<int:pk>/editar/', views.view_editar_professor, name='editar_professor'),
    path('<int:pk>/horarios/', views.view_horarios_professor, name='horarios_professor'),
    path('horarios/<int:horario_pk>/aprovar/', views.view_aprovar_horario, name='aprovar_horario'),
    path('horarios/<int:horario_pk>/remover/', views.view_remover_horario, name='remover_horario'),
]
