from django.contrib import admin
from .models import MensagemFaleConosco


@admin.register(MensagemFaleConosco)
class MensagemFaleConoscoAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo', 'assunto', 'nome', 'criado_em', 'email_enviado', 'lido')
    list_filter = ('tipo', 'email_enviado', 'lido', 'criado_em')
    search_fields = ('assunto', 'mensagem', 'nome', 'contato', 'ip_origem')
    readonly_fields = ('criado_em', 'ip_origem', 'email_enviado', 'erro_envio')
    list_editable = ('lido',)
