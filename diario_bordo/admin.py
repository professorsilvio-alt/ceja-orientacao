"""Configuração do Django Admin para o app diario_bordo"""
from django.contrib import admin
from .models import OcorrenciaDiario, LeituraOcorrencia


class LeituraOcorrenciaInline(admin.TabularInline):
    model = LeituraOcorrencia
    extra = 0
    readonly_fields = ('usuario', 'lido_em', 'ip_origem', 'observacao')
    can_delete = False


@admin.register(OcorrenciaDiario)
class OcorrenciaDiarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'assunto_exibicao', 'autor', 'prioridade', 'categoria', 'criado_em', 'ativo')
    list_filter = ('prioridade', 'categoria', 'ativo', 'criado_em')
    search_fields = ('titulo', 'texto', 'autor__nome_completo')
    readonly_fields = ('criado_em', 'atualizado_em')
    inlines = [LeituraOcorrenciaInline]


@admin.register(LeituraOcorrencia)
class LeituraOcorrenciaAdmin(admin.ModelAdmin):
    list_display = ('id', 'ocorrencia', 'usuario', 'lido_em', 'ip_origem')
    list_filter = ('lido_em',)
    search_fields = ('ocorrencia__titulo', 'usuario__nome_completo', 'ip_origem')
    readonly_fields = ('lido_em',)
