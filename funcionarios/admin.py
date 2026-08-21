"""Admin do app funcionarios"""
from django.contrib import admin
from .models import FuncionarioAdministrativo, FuncionarioTerceirizado


@admin.register(FuncionarioAdministrativo)
class FuncionarioAdmAdmin(admin.ModelAdmin):
    list_display = ['classificacao', 'nome_completo', 'cargo', 'funcao_ingresso', 'data_ingresso_unidade', 'tempo_na_escola', 'ativo']
    list_filter = ['cargo', 'ativo']
    search_fields = ['nome_completo', 'cpf', 'matricula']
    ordering = ['classificacao', 'nome_completo']
    readonly_fields = ['tempo_na_escola', 'criado_em', 'atualizado_em']


@admin.register(FuncionarioTerceirizado)
class FuncionarioTercAdmin(admin.ModelAdmin):
    list_display = ['nome_completo', 'cargo_funcao', 'empresa_contratante', 'data_admissao', 'ativo']
    list_filter = ['ativo', 'empresa_contratante']
    search_fields = ['nome_completo', 'cpf']
    readonly_fields = ['tempo_na_escola', 'idade', 'criado_em', 'atualizado_em']
