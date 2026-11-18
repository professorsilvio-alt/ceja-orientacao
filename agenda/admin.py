"""Admin do app agenda"""
from django.contrib import admin
from .models import RegistroPresenca, ReservaAuditorio, AgendaAtendimentoProfessor


@admin.register(RegistroPresenca)
class RegistroPresencaAdmin(admin.ModelAdmin):
    list_display = ['data', 'nome_funcionario', 'tipo_funcionario', 'tipo', 'justificado', 'registrado_por']
    list_filter = ['tipo', 'tipo_funcionario', 'justificado', 'data']
    search_fields = ['nome_funcionario']
    date_hierarchy = 'data'
    readonly_fields = ['criado_em', 'registrado_por']


@admin.register(ReservaAuditorio)
class ReservaAuditorioAdmin(admin.ModelAdmin):
    list_display = ['data', 'hora_inicio', 'hora_fim', 'titulo', 'tipo', 'responsavel', 'status']
    list_filter = ['tipo', 'status', 'data']
    search_fields = ['titulo', 'responsavel']
    date_hierarchy = 'data'
    readonly_fields = ['criado_em', 'atualizado_em', 'criado_por']


@admin.register(AgendaAtendimentoProfessor)
class AgendaAtendimentoProfessorAdmin(admin.ModelAdmin):
    list_display = ['data', 'hora_inicio', 'tipo', 'nome_professor', 'disciplina', 'titulo', 'visivel_totem']
    list_filter = ['tipo', 'visivel_totem', 'data', 'disciplina']
    search_fields = ['nome_professor', 'disciplina', 'titulo']
    date_hierarchy = 'data'
    readonly_fields = ['criado_em', 'atualizado_em', 'criado_por']
