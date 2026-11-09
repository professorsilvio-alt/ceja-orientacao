from django.contrib import admin
from .models import ConfiguracaoCarteira, CarteiraEstudanteEmitida


@admin.register(ConfiguracaoCarteira)
class ConfiguracaoCarteiraAdmin(admin.ModelAdmin):
    list_display = ('nome_diretor', 'cargo_diretor', 'emissao_publica_ativa', 'atualizado_em')


@admin.register(CarteiraEstudanteEmitida)
class CarteiraEstudanteEmitidaAdmin(admin.ModelAdmin):
    list_display = ('codigo_autenticidade', 'matricula', 'nome_aluno', 'nome_operador', 'criado_em', 'ativo')
    list_filter = ('ativo', 'criado_em', 'curso')
    search_fields = ('matricula', 'nome_aluno', 'codigo_autenticidade', 'nome_operador')
    readonly_fields = ('codigo_autenticidade', 'criado_em', 'ip_origem', 'user_agent')
