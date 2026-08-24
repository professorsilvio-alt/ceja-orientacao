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
    
    # ── Acumulação (2ª Matrícula / Cargo na escola) ────────
    id_vinculo_acumulacao = models.CharField(
        max_length=30, blank=True, verbose_name='ID / Vínculo (2ª Matrícula)'
    )
    matricula_acumulacao = models.CharField(
        max_length=20, blank=True, verbose_name='Matrícula acumulação',
        help_text='Preencha apenas se o professor acumula cargo.'
    )
    SITUACAO_CHOICES = [
        ('ativo', 'Ativo(a)'),
        ('aposentado', 'Aposentado(a)'),
        ('licenca', 'Em Licença'),
        ('saida', 'Inativo / Transferido(a)'),
    ]

    SITUACAO_MAT2_CHOICES = [
        ('n_a', 'Não Possui 2ª Matrícula'),
        ('ativo', 'Ativo(a)'),
        ('aposentado', 'Aposentado(a)'),
        ('licenca', 'Em Licença'),
        ('saida', 'Inativo / Transferido(a)'),
    ]

    situacao_matricula_1 = models.CharField(
        max_length=20, choices=SITUACAO_CHOICES, default='ativo',
        verbose_name='Situação da 1ª Matrícula'
    )
    situacao_matricula_2 = models.CharField(
        max_length=20, choices=SITUACAO_MAT2_CHOICES, default='n_a',
        verbose_name='Situação da 2ª Matrícula'
    )

    cargo_acumulacao = models.CharField(
        max_length=150, blank=True, verbose_name='Cargo (2ª Matrícula)'
    )
    disciplina_ingresso_acumulacao = models.CharField(
        max_length=150, blank=True, verbose_name='Disciplina de Ingresso (2ª Matrícula)'
    )
    funcao_acumulacao = models.CharField(
        max_length=150, blank=True, verbose_name='Função (2ª Matrícula)'
    )
    ch_total_acumulacao = models.PositiveIntegerField(
        null=True, blank=True, verbose_name='CH Total (2ª Matrícula)'
    )
    data_admissao_acumulacao = models.DateField(
        null=True, blank=True, verbose_name='Data Admissão (2ª Matrícula)'
    )
    nome_completo = models.CharField(max_length=200, verbose_name='Nome completo')

    # ── Cargo e disciplina ─────────────────────────────────
    cargo = models.CharField(max_length=150, verbose_name='Cargo')
    disciplina_ingresso = models.CharField(
        max_length=150, blank=True, verbose_name='Disciplina de ingresso'
    )
    funcao = models.CharField(max_length=150, blank=True, verbose_name='Função')
    tipo_funcao = models.CharField(max_length=100, blank=True, verbose_name='Tipo de Função')
    regime_contratacao = models.CharField(max_length=100, blank=True, verbose_name='Regime de Contratação')

    disciplinas_lecionadas = models.ManyToManyField(
        'Disciplina',
        blank=True,
        verbose_name='Disciplinas que leciona na escola',
        related_name='professores'
    )

    # ── Datas ──────────────────────────────────────────────
    data_admissao = models.DateField(null=True, blank=True, verbose_name='Data de Admissão')
    data_nomeacao = models.DateField(null=True, blank=True, verbose_name='Data de Nomeação')
    data_ci_movimentacao = models.DateField(
        null=True, blank=True, verbose_name='Data da CI de movimentação'
    )
    data_ingresso_unidade = models.DateField(
        null=True, blank=True, verbose_name='Data de ingresso na unidade'
    )

    # ── Carga Horária & Acumulação ─────────────────────────
    ch_planejamento = models.PositiveIntegerField(null=True, blank=True, verbose_name='CH Planejamento')
    ch_regencia = models.PositiveIntegerField(null=True, blank=True, verbose_name='CH Regência')
    ch_complementacao = models.PositiveIntegerField(null=True, blank=True, verbose_name='CH Complementação')
    ch_total = models.PositiveIntegerField(null=True, blank=True, verbose_name='CH Total')
    acumulacao = models.CharField(max_length=100, blank=True, verbose_name='Acumulação')

    # ── Dados Pessoais & Endereço ─────────────────────────
    data_nascimento = models.DateField(null=True, blank=True, verbose_name='Data de Nascimento')
    sexo = models.CharField(max_length=10, blank=True, verbose_name='Sexo')
    endereco = models.CharField(max_length=250, blank=True, verbose_name='Endereço')
    numero = models.CharField(max_length=20, blank=True, verbose_name='Número')
    complemento = models.CharField(max_length=100, blank=True, verbose_name='Complemento')
    bairro = models.CharField(max_length=100, blank=True, verbose_name='Bairro')
    municipio = models.CharField(max_length=100, blank=True, verbose_name='Município')

    # ── Classificação (ordem de chegada) ───────────────────
    classificacao = models.PositiveIntegerField(
        verbose_name='Classificação',
        help_text='Ordem de chegada: 1 = professor com mais tempo na escola.',
        null=True, blank=True
    )

    # ── Contato ────────────────────────────────────────────
    email = models.EmailField(blank=True, verbose_name='E-mail Interno')
    email_google = models.EmailField(blank=True, verbose_name='E-mail Google')
    email_alternativo = models.EmailField(blank=True, verbose_name='E-mail Alternativo')
    telefone = models.CharField(max_length=50, blank=True, verbose_name='Telefone')
    celular = models.CharField(max_length=50, blank=True, verbose_name='Celular')
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
        max_length=100, blank=True,
        verbose_name='Descrição do local',
        help_text='Ex: Sala 204, Auditório, etc.'
    )
    aprovado = models.BooleanField(
        default=False, verbose_name='Aprovado pela direção'
    )
    observacoes = models.TextField(blank=True, verbose_name='Observações')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Horário do Professor'
        verbose_name_plural = 'Horários dos Professores'
        ordering = ['ano_letivo', 'dia_semana', 'hora_inicio']

    def __str__(self):
        return f'{self.professor.nome_curto} — {self.get_dia_semana_display()} {self.hora_inicio.strftime("%H:%M")}-{self.hora_fim.strftime("%H:%M")}'


class ConfiguracaoEscola(models.Model):
    """Configuração Geral da Escola por Ano Letivo."""

    ano_letivo = models.PositiveIntegerField(
        unique=True, verbose_name='Ano Letivo',
        help_text='Ex: 2026'
    )
    ativo = models.BooleanField(
        default=True, verbose_name='Ano Letivo Atual / Ativo'
    )
    duracao_hora_aula = models.PositiveIntegerField(
        default=50, verbose_name='Duração da Hora/Aula (Minutos)',
        help_text='Padrão: 50 minutos'
    )
    horario_abertura = models.TimeField(
        default='07:00', verbose_name='Horário de Abertura'
    )
    horario_fechamento = models.TimeField(
        default='22:00', verbose_name='Horário de Fechamento'
    )

    # Dias de Funcionamento (Segunda a Domingo)
    func_segunda = models.BooleanField(default=True, verbose_name='Segunda-feira')
    func_terca = models.BooleanField(default=True, verbose_name='Terça-feira')
    func_quarta = models.BooleanField(default=True, verbose_name='Quarta-feira')
    func_quinta = models.BooleanField(default=True, verbose_name='Quinta-feira')
    func_sexta = models.BooleanField(default=True, verbose_name='Sexta-feira')
    func_sabado = models.BooleanField(default=False, verbose_name='Sábado')
    func_domingo = models.BooleanField(default=False, verbose_name='Domingo')

    observacoes = models.TextField(blank=True, verbose_name='Observações do Ano Letivo')

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuração da Escola'
        verbose_name_plural = 'Configurações da Escola'
        ordering = ['-ano_letivo']

    def __str__(self):
        status = ' (Ativo)' if self.ativo else ''
        return f'Ano Letivo {self.ano_letivo}{status}'


class DisciplinaOfertada(models.Model):
    """Disciplinas ofertadas e carga horária (horas/aula) por Ano Letivo."""

    configuracao = models.ForeignKey(
        ConfiguracaoEscola, on_delete=models.CASCADE,
        related_name='disciplinas_ofertadas', verbose_name='Ano Letivo'
    )
    disciplina = models.ForeignKey(
        Disciplina, on_delete=models.CASCADE,
        related_name='ofertas', verbose_name='Disciplina'
    )
    horas_aula_semanais = models.PositiveIntegerField(
        default=4, verbose_name='Horas/Aula Semanais (50 min cada)'
    )
    carga_horaria_total = models.PositiveIntegerField(
        default=80, verbose_name='Carga Horária Total (Horas)'
    )
    ativo = models.BooleanField(default=True, verbose_name='Ofertada no Ano')

    class Meta:
        verbose_name = 'Disciplina Ofertada'
        verbose_name_plural = 'Disciplinas Ofertadas'
        unique_together = ['configuracao', 'disciplina']

    def __str__(self):
        return f'{self.disciplina.nome} — {self.configuracao.ano_letivo} ({self.horas_aula_semanais} h/a)'

    @property
    def local_display(self):
        if self.local == 'outro' and self.local_descricao:
            return self.local_descricao
