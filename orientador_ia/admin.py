from django.contrib import admin
from .models import DocumentoCerebro, FragmentoConhecimento, ConversaCerebro, MensagemCerebro


@admin.register(DocumentoCerebro)
class DocumentoCerebroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'tipo_arquivo', 'numero_normativa', 'status', 'documento_substituido', 'criado_em')
    list_filter = ('status', 'categoria', 'tipo_arquivo', 'criado_em')
    search_fields = ('titulo', 'numero_normativa', 'conteudo_extraido')
    ordering = ('-criado_em',)


@admin.register(FragmentoConhecimento)
class FragmentoConhecimentoAdmin(admin.ModelAdmin):
    list_display = ('documento', 'indice_ordem', 'trecho_resumo')
    search_fields = ('texto', 'documento__titulo')

    def trecho_resumo(self, obj):
        return obj.texto[:80] + '...'
    trecho_resumo.short_description = 'Trecho'


class MensagemInline(admin.TabularInline):
    model = MensagemCerebro
    extra = 0
    readonly_fields = ('remetente', 'conteudo', 'tipo_entrada', 'fontes_consultadas', 'criado_em')


@admin.register(ConversaCerebro)
class ConversaCerebroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'usuario', 'criado_em', 'atualizado_em')
    list_filter = ('criado_em', 'usuario')
    search_fields = ('titulo', 'usuario__nome_completo')
    inlines = [MensagemInline]
