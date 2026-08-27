"""
App: professores
Modelo completo do professor com cálculo automático de tempo na escola.
"""
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
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


class UnidadeEscolar(models.Model):
    """
    Unidades Escolares (Sede e Unidades Vinculadas / Filiais / Extensões).
    """
    TIPO_CHOICES = [
        ('sede', 'Sede Principal'),
        ('vinculada', 'Unidade Vinculada / Filial'),
    ]

    nome = models.CharField(max_length=150, verbose_name='Nome da Unidade')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='sede', verbose_name='Tipo de Unidade')
    codigo = models.CharField(max_length=30, blank=True, verbose_name='Código / Sigla')
    endereco = models.CharField(max_length=255, blank=True, verbose_name='Endereço Completo')
    telefone = models.CharField(max_length=30, blank=True, verbose_name='Telefone')
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Unidade Escolar'
        verbose_name_plural = 'Unidades Escolares'
        ordering = ['tipo', 'nome']

    def __str__(self):
        sufixo = " (Sede)" if self.tipo == 'sede' else " (Vinculada)"
        return f'{self.nome}{sufixo}'


class HorarioProfessor(models.Model):
    """
    Horário semanal do professor nesta escola.
    Professores informam sua disponibilidade anualmente.
    """
    professor = models.ForeignKey(
        Professor, on_delete=models.CASCADE,
        related_name='horarios', verbose_name='Professor'
    )
    unidade = models.ForeignKey(
        UnidadeEscolar, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='horarios_professores',
        verbose_name='Unidade / Filial'
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
        u_nome = f" — {self.unidade.nome}" if self.unidade else ""
        return f'{self.professor.nome_curto}{u_nome} — {self.get_dia_semana_display()} {self.hora_inicio.strftime("%H:%M")}-{self.hora_fim.strftime("%H:%M")}'


class ConfiguracaoEscola(models.Model):
    """Configuração Geral da Escola por Unidade Escolar e Ano Letivo."""

    unidade = models.ForeignKey(
        UnidadeEscolar, on_delete=models.CASCADE,
        related_name='configuracoes', verbose_name='Unidade Escolar',
        null=True, blank=True
    )
    ano_letivo = models.PositiveIntegerField(
        verbose_name='Ano Letivo',
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

    # Dias e Horários Específicos de Funcionamento (Segunda a Domingo)
    func_segunda = models.BooleanField(default=True, verbose_name='Segunda-feira')
    seg_abertura = models.TimeField(default='08:50', verbose_name='Abertura Segunda')
    seg_fechamento = models.TimeField(default='20:30', verbose_name='Fechamento Segunda')

    func_terca = models.BooleanField(default=True, verbose_name='Terça-feira')
    ter_abertura = models.TimeField(default='08:50', verbose_name='Abertura Terça')
    ter_fechamento = models.TimeField(default='20:30', verbose_name='Fechamento Terça')

    func_quarta = models.BooleanField(default=True, verbose_name='Quarta-feira')
    qua_abertura = models.TimeField(default='08:50', verbose_name='Abertura Quarta')
    qua_fechamento = models.TimeField(default='20:30', verbose_name='Fechamento Quarta')

    func_quinta = models.BooleanField(default=True, verbose_name='Quinta-feira')
    qui_abertura = models.TimeField(default='08:50', verbose_name='Abertura Quinta')
    qui_fechamento = models.TimeField(default='20:30', verbose_name='Fechamento Quinta')

    func_sexta = models.BooleanField(default=True, verbose_name='Sexta-feira')
    sex_abertura = models.TimeField(default='08:50', verbose_name='Abertura Sexta')
    sex_fechamento = models.TimeField(default='17:00', verbose_name='Fechamento Sexta')

    func_sabado = models.BooleanField(default=False, verbose_name='Sábado')
    sab_abertura = models.TimeField(default='08:00', verbose_name='Abertura Sábado')
    sab_fechamento = models.TimeField(default='12:00', verbose_name='Fechamento Sábado')

    func_domingo = models.BooleanField(default=False, verbose_name='Domingo')
    dom_abertura = models.TimeField(default='08:00', verbose_name='Abertura Domingo')
    dom_fechamento = models.TimeField(default='12:00', verbose_name='Fechamento Domingo')

    observacoes = models.TextField(blank=True, verbose_name='Observações do Ano Letivo')

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuração da Escola'
        verbose_name_plural = 'Configurações da Escola'
        ordering = ['-ano_letivo']
        unique_together = ['unidade', 'ano_letivo']

    def __str__(self):
        status = ' (Ativo)' if self.ativo else ''
        u_str = f" — {self.unidade.nome}" if self.unidade else ""
        return f'Ano Letivo {self.ano_letivo}{u_str}{status}'


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
        return self.get_local_display() if hasattr(self, 'get_local_display') else ''


class TurmaComponente(models.Model):
    """
    Turma ou Componente Curricular ofertado no Ano Letivo e Unidade Escolar.
    Ex: TURMA/TEMPOS: CEJAS-C1L-080 (8 tempos) ou CEJAS-E32-100 (10 tempos).
    """
    configuracao = models.ForeignKey(
        ConfiguracaoEscola, on_delete=models.CASCADE,
        related_name='turmas', verbose_name='Ano Letivo / Unidade'
    )
    codigo_turma = models.CharField(
        max_length=50, verbose_name='Código da Turma / Componente',
        help_text='Ex: CEJAS-C1L-080, CEJAS-E32-100'
    )
    disciplina_ofertada = models.ForeignKey(
        DisciplinaOfertada, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='turmas', verbose_name='Disciplina Ofertada Relacionada'
    )
    area = models.CharField(
        max_length=150, blank=True, verbose_name='Área do Conhecimento',
        help_text='Ex: Linguagens, Ciências da Natureza, Matemática, Ciências Humanas'
    )
    trilha_nucleo = models.CharField(
        max_length=200, blank=True, verbose_name='Trilha de Aprofundamento / Núcleo Integrador',
        help_text='Ex: TRILHA DE APROFUNDAMENTO, NÚCLEO INTEGRADOR, ELETIVA 3 CATÁLOGO 2'
    )
    disciplina_nome = models.CharField(
        max_length=200, verbose_name='Nome da Disciplina / Componente',
        help_text='Ex: COMPONENTE DE ÁREA 1 LINGUAGENS, CLUBE DA LEITURA'
    )
    tempos_requeridos = models.PositiveIntegerField(
        default=8, verbose_name='Carga Horária Exigida (em Tempos de 50 min)',
        help_text='Quantidade de tempos a alocar no quadro (ex: 8 ou 10)'
    )
    observacoes = models.TextField(blank=True, verbose_name='Observações')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Turma / Componente Curricular'
        verbose_name_plural = 'Turmas / Componentes Curriculares'
        ordering = ['codigo_turma', 'disciplina_nome']

    def __str__(self):
        return f'{self.codigo_turma} — {self.disciplina_nome} ({self.configuracao.ano_letivo})'

    @property
    def tempos_alocados(self):
        return self.alocacoes.filter(professor__isnull=False).count()

    @property
    def status_ok(self):
        return self.tempos_alocados == self.tempos_requeridos

    @property
    def status_display(self):
        alocados = self.tempos_alocados
        if alocados == self.tempos_requeridos:
            return 'OK'
        elif alocados > self.tempos_requeridos:
            return f'Excesso ({alocados}/{self.tempos_requeridos})'
        return f'Pendente ({alocados}/{self.tempos_requeridos})'

    @property
    def professores_alocados_nomes(self):
        alocacoes = self.alocacoes.filter(professor__isnull=False).select_related('professor')
        nomes = []
        for al in alocacoes:
            nome = al.rotulo_exibicao or al.professor.nome_curto
            if nome not in nomes:
                nomes.append(nome)
        return ', '.join(nomes) if nomes else 'Nenhum alocado'


class AlocacaoHorarioTurma(models.Model):
    """
    Alocação de um professor em um slot de tempo e dia da semana para uma Turma.
    """
    turma = models.ForeignKey(
        TurmaComponente, on_delete=models.CASCADE,
        related_name='alocacoes', verbose_name='Turma'
    )
    dia_semana = models.CharField(
        max_length=10, choices=DIA_SEMANA_CHOICES, verbose_name='Dia da Semana'
    )
    hora_inicio = models.TimeField(verbose_name='Horário de Início')
    hora_fim = models.TimeField(verbose_name='Horário de Fim')
    professor = models.ForeignKey(
        Professor, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='alocacoes_horario', verbose_name='Professor Alocado'
    )
    rotulo_exibicao = models.CharField(
        max_length=100, blank=True, verbose_name='Rótulo de Exibição',
        help_text='Nome customizado para exibição no quadro (ex: SANDRA, LUCIANA 1, DANIELA 2)'
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Alocação de Horário'
        verbose_name_plural = 'Alocações de Horários'
        ordering = ['dia_semana', 'hora_inicio']
        unique_together = ['turma', 'dia_semana', 'hora_inicio']

    def __str__(self):
        prof = self.rotulo_exibicao or (self.professor.nome_curto if self.professor else 'Vazio')
        return f'{self.turma.codigo_turma} — {self.get_dia_semana_display()} {self.hora_inicio.strftime("%H:%M")}: {prof}'


def recalcular_classificacao_professores():
    """
    Recalcula a classificação oficial dos professores ativos pela ordem da Data da C.I.
    Professores aposentados, em licença ou inativos têm a classificação zerada (None)
    e a numeração dos ativos se ajusta automaticamente.
    """
    from datetime import datetime
    import unicodedata

    def norm(text):
        if not text: return ''
        n = unicodedata.normalize('NFD', text)
        return ''.join(c for c in n if unicodedata.category(c) != 'Mn').lower().strip()

    # 1. Limpa a classificação de inativos / aposentados
    Professor.objects.filter(
        models.Q(ativo=False) | ~models.Q(situacao_matricula_1='ativo')
    ).update(classificacao=None)

    # 2. Busca ativos
    ativos = list(Professor.objects.filter(ativo=True, situacao_matricula_1='ativo'))

    def key_ordem(p):
        d = p.data_ci_movimentacao or p.data_ingresso_unidade or p.data_admissao
        return (d if d else datetime(2099, 1, 1).date(), norm(p.nome_completo))

    ativos.sort(key=key_ordem)

    for rank, p in enumerate(ativos, 1):
        if p.classificacao != rank:
            p.classificacao = rank
            p.save(update_fields=['classificacao'])


# ============================================================
# PASTA DIGITAL DO SERVIDOR (DOCUMENTOS, FOLGAS, ANOTAÇÕES)
# ============================================================

class DocumentoServidor(models.Model):
    """Documentos anexados à pasta digital do servidor (Atestados, CI, Licenças, etc)."""
    CATEGORIA_CHOICES = [
        ('atestado', 'Atestado Médico / Licença'),
        ('ausencia', 'Justificativa de Ausência'),
        ('folga', 'Comprovante de Folga / Compensação'),
        ('documento', 'Documento Pessoal / CI / Contrato'),
        ('outro', 'Outros Documentos'),
    ]

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    servidor = GenericForeignKey('content_type', 'object_id')

    titulo = models.CharField(max_length=200, verbose_name='Título / Descrição')
    categoria = models.CharField(max_length=30, choices=CATEGORIA_CHOICES, default='documento', verbose_name='Categoria')
    arquivo = models.FileField(upload_to='documentos_servidores/%Y/%m/', verbose_name='Arquivo')
    data_documento = models.DateField(default=timezone.now, verbose_name='Data do Documento / Ocorrência')
    observacoes = models.TextField(blank=True, verbose_name='Observações')
    criado_em = models.DateTimeField(auto_now_add=True)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'Documento do Servidor'
        verbose_name_plural = 'Documentos do Servidor'
        ordering = ['-data_documento', '-criado_em']

    def __str__(self):
        return f"{self.titulo} ({self.get_categoria_display()})"


class OcorrenciaFolgaServidor(models.Model):
    """Lançamento de direitos e uso de folgas/banco de horas do servidor."""
    TIPO_CHOICES = [
        ('credito', '➕ Crédito de Folga (Direito Adquirido)'),
        ('usufruido', '➖ Gozo de Folga (Folga Usufruída)'),
    ]

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    servidor = GenericForeignKey('content_type', 'object_id')

    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='credito', verbose_name='Tipo de Lançamento')
    dias = models.DecimalField(max_digits=5, decimal_places=1, default=1.0, verbose_name='Quantidade em Dias')
    motivo = models.CharField(max_length=250, verbose_name='Motivo / Origem', help_text='Ex: Trabalho na Eleição, Reunião Extra, Gozo de Folga')
    data_ocorrencia = models.DateField(default=timezone.now, verbose_name='Data da Ocorrência')
    observacoes = models.TextField(blank=True, verbose_name='Observações')
    criado_em = models.DateTimeField(auto_now_add=True)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'Ocorrência de Folga do Servidor'
        verbose_name_plural = 'Ocorrências de Folgas dos Servidores'
        ordering = ['-data_ocorrencia', '-criado_em']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.dias} dia(s) ({self.motivo})"


class AnotacaoServidor(models.Model):
    """Anotações e histórico de observações da pasta do servidor."""
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    servidor = GenericForeignKey('content_type', 'object_id')

    texto = models.TextField(verbose_name='Anotação / Observação')
    criado_em = models.DateTimeField(auto_now_add=True)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'Anotação do Servidor'
        verbose_name_plural = 'Anotações do Servidor'
        ordering = ['-criado_em']

    def __str__(self):
        return f"Anotação de {self.criado_em.strftime('%d/%m/%Y %H:%M')}"
