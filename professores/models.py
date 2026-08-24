"""
App: professores
Modelo completo do professor com cálculo automático de tempo na escola.
"""
from django.db import models
from django.utils import timezone
from dateutil.relativedelta import relativedelta


DISCIPLINAS_CHOICES = [
    ('portugues', 'Língua Portuguesa'),
    ('ingles', 'Língua Inglesa'),
    ('espanhol', 'Língua Espanhola'),
    ('artes', 'Artes / Educação Artística'),
    ('educacao_fisica', 'Educação Física'),
    ('biologia', 'Ciências / Biologia'),
    ('quimica', 'Química'),
    ('fisica', 'Física'),
    ('historia', 'História'),
    ('geografia', 'Geografia'),
    ('filosofia', 'Filosofia'),
    ('sociologia', 'Sociologia'),
    ('matematica', 'Matemática'),
    ('outro', 'Outro'),
]

CARGO_CHOICES = [
    ('professor_i', 'Professor I'),
    ('professor_ii', 'Professor II'),
    ('professor_adjunto_i', 'Professor Adjunto I'),
    ('professor_adjunto_ii', 'Professor Adjunto II'),
    ('outro', 'Outro'),
]

DIA_SEMANA_CHOICES = [
    ('segunda', 'Segunda-feira'),
    ('terca', 'Terça-feira'),
    ('quarta', 'Quarta-feira'),
    ('quinta', 'Quinta-feira'),
    ('sexta', 'Sexta-feira'),
    ('sabado', 'Sábado'),
]

LOCAL_CHOICES = [
    ('cabine_linguagens', 'Cabine de Linguagens'),
    ('cabine_matematica', 'Cabine de Matemática'),
    ('cabine_ciencias_natureza', 'Cabine de Ciências da Natureza'),
    ('cabine_ciencias_humanas', 'Cabine de Ciências Humanas'),
    ('auditorio', 'Auditório'),
    ('secretaria', 'Secretaria'),
    ('outro', 'Outro'),
]


class Professor(models.Model):
    """Dados completos do professor."""

    # ── Identificação ──────────────────────────────────────
    cpf = models.CharField(
        max_length=11, unique=True, verbose_name='CPF',
        help_text='Somente números.'
    )
    id_vinculo = models.CharField(
        max_length=30, blank=True, verbose_name='ID / Vínculo',
        help_text='Ex: 40645924/2'
    )
    matricula = models.CharField(max_length=20, unique=True, verbose_name='Matrícula')
    matricula_acumulacao = models.CharField(
        max_length=20, blank=True, verbose_name='Matrícula acumulação',
        help_text='Preencha apenas se o professor acumula cargo.'
    )
    nome_completo = models.CharField(max_length=200, verbose_name='Nome completo')

    # ── Cargo e disciplina ─────────────────────────────────
    cargo = models.CharField(max_length=30, choices=CARGO_CHOICES, verbose_name='Cargo')
    disciplina_ingresso = models.CharField(
        max_length=30, choices=DISCIPLINAS_CHOICES,
        verbose_name='Disciplina de ingresso',
        help_text='Disciplina do concurso público / admissão.'
    )
    disciplinas_lecionadas = models.ManyToManyField(
        'Disciplina',
        blank=True,
        verbose_name='Disciplinas que leciona na escola',
        related_name='professores'
    )

    # ── Movimentação para a escola ─────────────────────────
    data_ci_movimentacao = models.DateField(
        verbose_name='Data da CI de movimentação',
        help_text='Data do documento de movimentação para esta unidade escolar.'
    )
    data_ingresso_unidade = models.DateField(
        verbose_name='Data de ingresso na unidade',
        help_text='Data em que o professor começou a trabalhar nesta escola.'
    )

    # ── Classificação (ordem de chegada) ───────────────────
    classificacao = models.PositiveIntegerField(
        verbose_name='Classificação',
        help_text='Ordem de chegada: 1 = professor com mais tempo na escola.',
        null=True, blank=True
    )

    # ── Contato ────────────────────────────────────────────
    email = models.EmailField(blank=True, verbose_name='E-mail')
    telefone = models.CharField(max_length=20, blank=True, verbose_name='Telefone')
    foto = models.ImageField(
        upload_to='professores/fotos/', blank=True, null=True, verbose_name='Foto'
    )

    # ── Status ─────────────────────────────────────────────
    ativo = models.BooleanField(default=True, verbose_name='Ativo na escola')
    data_saida = models.DateField(null=True, blank=True, verbose_name='Data de saída')
    observacoes = models.TextField(blank=True, verbose_name='Observações')

    # ── Timestamps ─────────────────────────────────────────
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Professor'
        verbose_name_plural = 'Professores'
        ordering = ['classificacao', 'nome_completo']

    def __str__(self):
        return f'{self.nome_completo} — {self.get_disciplina_ingresso_display()}'

    @property
    def tempo_na_escola(self):
        """Retorna string com anos e meses desde o ingresso na unidade."""
        if not self.data_ingresso_unidade:
            return 'Não informado'
        hoje = timezone.now().date()
        diff = relativedelta(hoje, self.data_ingresso_unidade)
        partes = []
        if diff.years:
            partes.append(f'{diff.years} ano{"s" if diff.years > 1 else ""}')
        if diff.months:
            partes.append(f'{diff.months} mês' if diff.months == 1 else f'{diff.months} meses')
        return ' e '.join(partes) if partes else 'Menos de 1 mês'

    @property
    def tempo_na_escola_dias(self):
        """Retorna total de dias para fins de ordenação."""
        if not self.data_ingresso_unidade:
            return 0
        return (timezone.now().date() - self.data_ingresso_unidade).days

    @property
    def nome_curto(self):
        partes = self.nome_completo.split()
        if len(partes) >= 2:
            return f'{partes[0]} {partes[-1]}'
        return self.nome_completo


class Disciplina(models.Model):
    """Disciplinas disponíveis na escola."""
    nome = models.CharField(max_length=100, unique=True, verbose_name='Disciplina')
    area = models.CharField(max_length=100, blank=True, verbose_name='Área do conhecimento')
    cor = models.CharField(max_length=7, default='#1565C0', verbose_name='Cor (hex)')

    class Meta:
        verbose_name = 'Disciplina'
        verbose_name_plural = 'Disciplinas'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class HorarioProfessor(models.Model):
    """
    Horário semanal do professor nesta escola.
    Professores informam sua disponibilidade anualmente.
    """
    professor = models.ForeignKey(
        Professor, on_delete=models.CASCADE,
        related_name='horarios', verbose_name='Professor'
    )
    ano_letivo = models.PositiveIntegerField(verbose_name='Ano letivo')
    dia_semana = models.CharField(max_length=10, choices=DIA_SEMANA_CHOICES, verbose_name='Dia da semana')
    hora_inicio = models.TimeField(verbose_name='Início')
    hora_fim = models.TimeField(verbose_name='Fim')
    local = models.CharField(max_length=40, choices=LOCAL_CHOICES, verbose_name='Local')
    local_descricao = models.CharField(
        max_length=100, blank=True, verbose_name='Descrição do local',
        help_text='Complemento se "Outro" for selecionado.'
    )
    aprovado = models.BooleanField(
        default=False, verbose_name='Aprovado pela Direção',
        help_text='Diretor marca como aprovado após revisão.'
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Horário do Professor'
        verbose_name_plural = 'Horários dos Professores'
        ordering = ['dia_semana', 'hora_inicio']
        unique_together = ['professor', 'ano_letivo', 'dia_semana', 'hora_inicio']

    def __str__(self):
        return f'{self.professor.nome_curto} — {self.get_dia_semana_display()} {self.hora_inicio:%H:%M}–{self.hora_fim:%H:%M}'

    @property
    def local_display(self):
        if self.local == 'outro' and self.local_descricao:
            return self.local_descricao
        return self.get_local_display()
