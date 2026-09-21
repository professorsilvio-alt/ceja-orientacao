from django.contrib import admin
from .models import ProcessoSEI, AndamentoProcesso


class AndamentoProcessoInline(admin.TabularInline):
    model = AndamentoProcesso
    extra = 1
    fields = ('data', 'setor', 'descricao', 'registrado_por')


@admin.register(ProcessoSEI)
class ProcessoSEIAdmin(admin.ModelAdmin):
    list_display = ('numero_sei', 'titulo', 'status', 'prioridade', 'data_abertura', 'setor_atual', 'atualizado_em')
    list_filter = ('status', 'prioridade', 'data_abertura')
    search_fields = ('numero_sei', 'titulo', 'palavras_chave', 'descricao', 'interessado')
    inlines = [AndamentoProcessoInline]
    date_hierarchy = 'data_abertura'


@admin.register(AndamentoProcesso)
class AndamentoProcessoAdmin(admin.ModelAdmin):
    list_display = ('processo', 'data', 'setor', 'registrado_por', 'criado_em')
    list_filter = ('data', 'setor')
    search_fields = ('processo__numero_sei', 'descricao', 'setor')
