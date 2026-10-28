"""Modelos do app totem"""
from django.db import models
from django.utils import timezone


class MensagemFaleConosco(models.Model):
    """
    Mensagens enviadas através da tela 'Fale Conosco' no Totem ou site público.
    Registra sugestões, reclamações, elogios e dúvidas.
    """
    TIPO_CHOICES = [
        ('sugestao', 'Sugestão 💡'),
        ('reclamacao', 'Reclamação ⚠️'),
        ('elogio', 'Elogio ⭐'),
        ('outro', 'Outro Assunto 💬'),
    ]

    tipo = models.CharField(
        max_length=30,
        choices=TIPO_CHOICES,
        default='sugestao',
        verbose_name='Tipo de Mensagem'
    )
    assunto = models.CharField(
        max_length=150,
        verbose_name='Assunto Principal'
    )
    mensagem = models.TextField(
        verbose_name='Mensagem / Relato'
    )
    nome = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Nome (Opcional)'
    )
    contato = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Contato / E-mail / WhatsApp (Opcional)'
    )
    ip_origem = models.CharField(
        max_length=45,
        blank=True,
        verbose_name='IP de Origem'
    )
    criado_em = models.DateTimeField(
        default=timezone.now,
        verbose_name='Data e Hora do Envio'
    )
    email_enviado = models.BooleanField(
        default=False,
        verbose_name='E-mail Enviado com Sucesso?'
    )
    erro_envio = models.TextField(
        blank=True,
        verbose_name='Detalhes do Erro no Envio'
    )
    lido = models.BooleanField(
        default=False,
        verbose_name='Lido pela Direção'
    )

    class Meta:
        verbose_name = 'Mensagem do Fale Conosco'
        verbose_name_plural = 'Mensagens do Fale Conosco'
        ordering = ['-criado_em']

    def __str__(self):
        return f'[{self.get_tipo_display()}] {self.assunto} ({self.criado_em.strftime("%d/%m/%Y %H:%M")})'
