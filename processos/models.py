from django.db import models
from django.conf import settings
from django.utils import timezone


class ProcessoSEI(models.Model):
    """
    Representa um Processo Administrativo SEI da escola CEJA Professora Rosa Soares.
    Permite registrar o número do processo, palavras-chave, assunto,
    descrição detalhada, data de registro/abertura e status de tramitação.
    """

    STATUS_CHOICES = [
        ('em_andamento', 'Em Andamento'),
        ('aguardando_resposta', 'Aguardando Resposta / Parecer'),
        ('sob_analise', 'Sob Análise'),
        ('concluido', 'Concluído / Deferido'),
        ('arquivado', 'Arquivado'),
        ('indeferido', 'Indeferido'),
    ]

    TIPO_CHOICES = [
        ('pessoal_rh', 'Pessoal & RH (Lotação, Licenças, GLPI, Aposentadoria)'),
        ('infraestrutura', 'Infraestrutura & Obras (Reforma, Reparos, Manutenção)'),
        ('pedagogico', 'Pedagógico & Alunos (Censo, Certificação, Projetos)'),
        ('financeiro_compras', 'Financeiro & Compras (PDDE, Prestação de Contas, Verbas)'),
        ('merenda_alimentacao', 'Alimentação & Merenda Escolar'),
        ('tecnologia_ti', 'Tecnologia & Informática (Computadores, Redes, TI)'),
        ('administrativo_geral', 'Administrativo Geral & Expediente'),
        ('outros', 'Outros'),
    ]

    PRIORIDADE_CHOICES = [
        ('normal', 'Normal'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]

    tipo = models.CharField(
        max_length=40,
        choices=TIPO_CHOICES,
        default='administrativo_geral',
        verbose_name="Tipo / Categoria do Processo",
        help_text="Área de classificação para organização e filtros rápidos"
    )

    numero_sei = models.CharField(
        max_length=80,
        unique=True,
        verbose_name="Número do Processo SEI",
        help_text="Ex: SEI-030029/000123/2026"
    )
    titulo = models.CharField(
        max_length=255,
        verbose_name="Assunto / Resumo do Processo",
        help_text="Identificação rápida do assunto principal"
    )
    palavras_chave = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Palavras-chave",
        help_text="Termos de busca rápida (ex: Reforma, Lotação, Prestação de Contas, GLPI, Merenda)"
    )
    descricao = models.TextField(
        blank=True,
        verbose_name="Descrição / Observações",
        help_text="Explicação clara do processo para leitura e compreensão imediata"
    )
    interessado = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Interessado / Requerente",
        help_text="Nome do servidor, setor ou requerente"
    )
    setor_atual = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Setor / Unidade Atual",
        help_text="Onde o processo está tramitando (ex: SEEDUC/DGE, DIESP, Regional Metropolitana I, etc.)"
    )
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='em_andamento',
        verbose_name="Status / Situação"
    )
    prioridade = models.CharField(
        max_length=20,
        choices=PRIORIDADE_CHOICES,
        default='normal',
        verbose_name="Prioridade"
    )
    data_abertura = models.DateField(
        default=timezone.now,
        verbose_name="Data de Abertura / Registro"
    )
    link_sei = models.URLField(
        blank=True,
        verbose_name="Link de Acesso Direto no SEI",
        help_text="Link opcional para abrir diretamente o processo no sistema SEI"
    )
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processos_criados",
        verbose_name="Cadastrado por"
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro no Sistema")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")

    class Meta:
        verbose_name = "Processo SEI"
        verbose_name_plural = "Processos SEI"
        ordering = ['-data_abertura', '-atualizado_em']

    def __str__(self):
        return f"{self.numero_sei} - {self.titulo}"

    @property
    def palavras_chave_lista(self):
        """Retorna uma lista limpa das palavras-chave separadas por vírgula ou ponto-e-vírgula."""
        if not self.palavras_chave:
            return []
        raw = self.palavras_chave.replace(';', ',')
        return [tag.strip() for tag in raw.split(',') if tag.strip()]


class AndamentoProcesso(models.Model):
    """
    Histórico de movimentações, anotações e despachos de acompanhamento de um processo SEI.
    """
    processo = models.ForeignKey(
        ProcessoSEI,
        on_delete=models.CASCADE,
        related_name="andamentos",
        verbose_name="Processo"
    )
    data = models.DateField(
        default=timezone.now,
        verbose_name="Data do Andamento"
    )
    descricao = models.TextField(
        verbose_name="Despacho / Anotação de Acompanhamento"
    )
    setor = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Setor / Local Envolvido"
    )
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Registrado por"
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Andamento do Processo"
        verbose_name_plural = "Andamentos do Processo"
        ordering = ['-data', '-criado_em']

    def __str__(self):
        return f"Andamento de {self.data} - {self.processo.numero_sei}"
