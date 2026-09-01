from django.db import models
from django.conf import settings
from django.utils import timezone


class DocumentoCerebro(models.Model):
    """
    Documento ou registro de conhecimento do CEJA armazenado no Cérebro (Beth).
    """
    CATEGORIA_CHOICES = [
        ('legislacao', '📜 Legislação & Resoluções'),
        ('regimento', '🏛️ Regimento Escolar & Normas'),
        ('pedagogico', '📚 Pedagógico & Avaliação'),
        ('gestao', '💼 Gestão & Administrativo'),
        ('horarios', '⏰ Horários & Funcionamento'),
        ('matricula', '🎓 Matrícula & Documentação de Alunos'),
        ('geral', '📋 Geral & Informações Diversas'),
    ]

    TIPO_CHOICES = [
        ('pdf', 'PDF (.pdf)'),
        ('docx', 'Word (.docx)'),
        ('xlsx', 'Planilha Excel / CSV (.xlsx, .xls, .csv)'),
        ('audio', 'Gravação de Áudio (.mp3, .wav, .m4a, .ogg)'),
        ('imagem', 'Imagem / Print de Tela (.png, .jpg, .jpeg)'),
        ('texto', 'Nota de Texto / Legislação Direta'),
    ]

    STATUS_CHOICES = [
        ('vigente', '✅ Vigente / Ativo'),
        ('substituido', '🔄 Substituído / Revogado'),
        ('arquivado', '📦 Arquivado'),
    ]

    titulo = models.CharField(max_length=255, verbose_name='Título / Nome do Documento')
    categoria = models.CharField(max_length=30, choices=CATEGORIA_CHOICES, default='geral', verbose_name='Categoria')
    tipo_arquivo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='texto', verbose_name='Tipo de Conteúdo')
    
    arquivo = models.FileField(upload_to='cerebro/documentos/%Y/%m/', blank=True, null=True, verbose_name='Arquivo')
    conteudo_extraido = models.TextField(blank=True, verbose_name='Texto Extraído / Conteúdo')
    
    numero_normativa = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Nº da Normativa / Portaria / Resolução',
        help_text='Exemplo: Portaria SEEDUC nº 123/2026, Resolução CEJA nº 04'
    )
    ano_referencia = models.IntegerField(null=True, blank=True, verbose_name='Ano de Referência')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='vigente', verbose_name='Status')
    
    documento_substituido = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='substituidores',
        verbose_name='Documento que este atualiza/substitui',
        help_text='Se este documento revoga ou substitui outro documento anterior, selecione-o aqui.'
    )
    
    observacoes = models.TextField(blank=True, verbose_name='Observações da Direção')
    
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documentos_cerebro_criados',
        verbose_name='Cadastrado por'
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Última Atualização')

    class Meta:
        verbose_name = 'Documento do Cérebro'
        verbose_name_plural = 'Documentos do Cérebro'
        ordering = ['-criado_em']

    def __str__(self):
        return f'{self.titulo} ({self.get_status_display()})'

    def save(self, *args, **kwargs):
        # Se um documento novo substitui um anterior, atualiza automaticamente o anterior para 'substituido'
        is_novo = self.pk is None
        super().save(*args, **kwargs)
        if self.documento_substituido and self.status == 'vigente':
            doc_antigo = self.documento_substituido
            if doc_antigo.status != 'substituido':
                doc_antigo.status = 'substituido'
                doc_antigo.save(update_fields=['status'])


class FragmentoConhecimento(models.Model):
    """
    Trechos/chunks do texto processado para rápida indexação e busca contextual RAG.
    """
    documento = models.ForeignKey(DocumentoCerebro, on_delete=models.CASCADE, related_name='fragmentos')
    texto = models.TextField()
    indice_ordem = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Fragmento de Conhecimento'
        verbose_name_plural = 'Fragmentos de Conhecimento'
        ordering = ['documento', 'indice_ordem']

    def __str__(self):
        return f'Fragmento {self.indice_ordem} de {self.documento.titulo}'


class ConversaCerebro(models.Model):
    """
    Sessão de conversa de um diretor com a Beth (Cérebro do CEJA).
    """
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversas_cerebro',
        verbose_name='Diretor'
    )
    titulo = models.CharField(max_length=255, default='Nova Consulta', verbose_name='Título da Conversa')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Iniciada em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Última Interação')

    class Meta:
        verbose_name = 'Conversa com a Beth'
        verbose_name_plural = 'Conversas com a Beth'
        ordering = ['-atualizado_em']

    def __str__(self):
        return f'{self.titulo} - {self.usuario.primeiro_nome}'


class MensagemCerebro(models.Model):
    """
    Mensagem individual dentro de uma conversa com a Beth.
    """
    REMETENTE_CHOICES = [
        ('usuario', 'Diretor(a)'),
        ('beth', 'Beth (Orientadora Virtual)'),
    ]

    TIPO_ENTRADA_CHOICES = [
        ('texto', 'Texto'),
        ('audio', 'Voz / Áudio'),
    ]

    conversa = models.ForeignKey(ConversaCerebro, on_delete=models.CASCADE, related_name='mensagens')
    remetente = models.CharField(max_length=20, choices=REMETENTE_CHOICES)
    conteudo = models.TextField(verbose_name='Conteúdo da Mensagem')
    tipo_entrada = models.CharField(max_length=20, choices=TIPO_ENTRADA_CHOICES, default='texto')
    fontes_consultadas = models.JSONField(blank=True, null=True, default=list, verbose_name='Fontes Consultadas')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Mensagem'
        verbose_name_plural = 'Mensagens'
        ordering = ['criado_em']

    def __str__(self):
        return f'{self.get_remetente_display()}: {self.conteudo[:40]}...'
