"""
App: funcionarios
Modelos de Funcionário Administrativo e Funcionário Terceirizado.
"""
from django.db import models
from django.utils import timezone
from dateutil.relativedelta import relativedelta
import re


CARGO_ADM_CHOICES = [
    ('ate', 'ATE — Agente de Trabalho em Educação'),
    ('assistente_secretaria', 'Assistente de Secretaria'),
    ('secretario', 'Secretário Escolar'),
    ('orientador', 'Orientador Educacional'),
    ('coordenador', 'Coordenador Pedagógico'),
    ('diretor_adjunto', 'Diretor Adjunto'),
    ('outro', 'Outro'),
]

ESTADO_CIVIL_CHOICES = [
    ('solteiro', 'Solteiro(a)'),
    ('casado', 'Casado(a)'),
    ('divorciado', 'Divorciado(a)'),
    ('viuvo', 'Viúvo(a)'),
    ('uniao_estavel', 'União Estável'),
]

SEXO_CHOICES = [
    ('M', 'Masculino'),
    ('F', 'Feminino'),
    ('outro', 'Outro / Prefiro não informar'),
]


class FuncionarioAdministrativo(models.Model):
    """Funcionário público administrativo da escola."""

    # ── Identificação ──────────────────────────────────────
    cpf = models.CharField(max_length=11, verbose_name='CPF')
    id_vinculo = models.CharField(max_length=30, blank=True, verbose_name='ID / Vínculo', help_text='Ex: 40260437/2')
    matricula = models.CharField(max_length=20, unique=True, verbose_name='Matrícula')
    matricula_acumulacao = models.CharField(max_length=20, blank=True, verbose_name='Matrícula acumulação')
    nome_completo = models.CharField(max_length=200, verbose_name='Nome completo')

    # ── Cargo e função ─────────────────────────────────────
    cargo = models.CharField(max_length=150, verbose_name='Cargo')
    disciplina_ingresso = models.CharField(max_length=150, blank=True, verbose_name='Disciplina de ingresso')
    funcao_atual = models.CharField(max_length=150, blank=True, verbose_name='Função Atual')
    funcao_ingresso = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Função de ingresso',
        help_text='Função original do concurso / admissão.'
    )
    tipo_funcao = models.CharField(max_length=100, blank=True, verbose_name='Tipo de Função')
    regime_contratacao = models.CharField(max_length=100, blank=True, verbose_name='Regime de Contratação')

    # ── Datas ──────────────────────────────────────────────
    data_admissao = models.DateField(null=True, blank=True, verbose_name='Data de Admissão')
    data_nomeacao = models.DateField(null=True, blank=True, verbose_name='Data de Nomeação')
    data_ci_movimentacao = models.DateField(null=True, blank=True, verbose_name='Data da CI de movimentação')
    data_ingresso_unidade = models.DateField(null=True, blank=True, verbose_name='Data de ingresso na unidade')

    # ── Carga Horária & Acumulação ─────────────────────────
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
        null=True, blank=True, verbose_name='Classificação',
        help_text='Ordem de chegada: 1 = funcionário com mais tempo na escola.'
    )

    # ── Contato ────────────────────────────────────────────
    email = models.EmailField(blank=True, verbose_name='E-mail Interno')
    email_google = models.EmailField(blank=True, verbose_name='E-mail Google')
    email_alternativo = models.EmailField(blank=True, verbose_name='E-mail Alternativo')
    telefone = models.CharField(max_length=50, blank=True, verbose_name='Telefone')
    celular = models.CharField(max_length=50, blank=True, verbose_name='Celular')
    foto = models.ImageField(upload_to='funcionarios/fotos/', blank=True, null=True, verbose_name='Foto')

    # ── Status ─────────────────────────────────────────────
    ativo = models.BooleanField(default=True, verbose_name='Ativo na escola')
    data_saida = models.DateField(null=True, blank=True, verbose_name='Data de saída')
    observacoes = models.TextField(blank=True, verbose_name='Observações')

    # ── Timestamps ─────────────────────────────────────────
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Funcionário Administrativo'
        verbose_name_plural = 'Funcionários Administrativos'
        ordering = ['classificacao', 'nome_completo']

    def __str__(self):
        return f'{self.nome_completo} — {self.get_cargo_display()}'

    @property
    def tempo_na_escola(self):
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
    def nome_curto(self):
        partes = self.nome_completo.split()
        return f'{partes[0]} {partes[-1]}' if len(partes) >= 2 else self.nome_completo

    def save(self, *args, **kwargs):
        self.cpf = re.sub(r'\D', '', self.cpf)
        super().save(*args, **kwargs)


class FuncionarioTerceirizado(models.Model):
    """Trabalhador CLT terceirizado que atua na escola."""

    # ── Dados Pessoais ─────────────────────────────────────
    nome_completo = models.CharField(max_length=200, verbose_name='Nome completo')
    cpf = models.CharField(max_length=11, unique=True, verbose_name='CPF')
    rg = models.CharField(max_length=20, verbose_name='RG')
    data_nascimento = models.DateField(verbose_name='Data de nascimento')
    sexo = models.CharField(max_length=10, choices=SEXO_CHOICES, blank=True, verbose_name='Sexo')
    estado_civil = models.CharField(
        max_length=20, choices=ESTADO_CIVIL_CHOICES, blank=True, verbose_name='Estado civil'
    )
    naturalidade = models.CharField(max_length=100, blank=True, verbose_name='Naturalidade')

    # ── Documentos trabalhistas ────────────────────────────
    pis_pasep = models.CharField(max_length=20, blank=True, verbose_name='PIS/PASEP')
    ctps_numero = models.CharField(max_length=20, blank=True, verbose_name='CTPS — Número')
    ctps_serie = models.CharField(max_length=10, blank=True, verbose_name='CTPS — Série')
    ctps_uf = models.CharField(max_length=2, blank=True, verbose_name='CTPS — UF')

    # ── Contrato ───────────────────────────────────────────
    empresa_contratante = models.CharField(max_length=200, verbose_name='Empresa contratante')
    cargo_funcao = models.CharField(max_length=100, verbose_name='Cargo / Função')
    salario = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Salário (R$)'
    )
    data_admissao = models.DateField(verbose_name='Data de admissão')
    data_demissao = models.DateField(null=True, blank=True, verbose_name='Data de demissão')
    ativo = models.BooleanField(default=True, verbose_name='Ativo')

    # ── Endereço ───────────────────────────────────────────
    cep = models.CharField(max_length=9, blank=True, verbose_name='CEP')
    logradouro = models.CharField(max_length=200, blank=True, verbose_name='Logradouro')
    numero = models.CharField(max_length=10, blank=True, verbose_name='Número')
    complemento = models.CharField(max_length=100, blank=True, verbose_name='Complemento')
    bairro = models.CharField(max_length=100, blank=True, verbose_name='Bairro')
    cidade = models.CharField(max_length=100, blank=True, verbose_name='Cidade')
    uf = models.CharField(max_length=2, blank=True, default='RJ', verbose_name='UF')

    # ── Contato ────────────────────────────────────────────
    email = models.EmailField(blank=True, verbose_name='E-mail')
    telefone = models.CharField(max_length=20, blank=True, verbose_name='Telefone')
    telefone_emergencia = models.CharField(max_length=20, blank=True, verbose_name='Telefone de emergência')

    # ── Outros ─────────────────────────────────────────────
    foto = models.ImageField(upload_to='terceirizados/fotos/', blank=True, null=True, verbose_name='Foto')
    observacoes = models.TextField(blank=True, verbose_name='Observações')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Funcionário Terceirizado'
        verbose_name_plural = 'Funcionários Terceirizados'
        ordering = ['nome_completo']

    def __str__(self):
        return f'{self.nome_completo} — {self.cargo_funcao} ({self.empresa_contratante})'

    @property
    def idade(self):
        if not self.data_nascimento:
            return None
        return relativedelta(timezone.now().date(), self.data_nascimento).years

    @property
    def tempo_na_escola(self):
        data_ref = self.data_admissao
        data_fim = self.data_demissao or timezone.now().date()
        if not data_ref:
            return 'Não informado'
        diff = relativedelta(data_fim, data_ref)
        partes = []
        if diff.years:
            partes.append(f'{diff.years} ano{"s" if diff.years > 1 else ""}')
        if diff.months:
            partes.append(f'{diff.months} mês' if diff.months == 1 else f'{diff.months} meses')
        return ' e '.join(partes) if partes else 'Menos de 1 mês'

    @property
    def nome_curto(self):
        partes = self.nome_completo.split()
        return f'{partes[0]} {partes[-1]}' if len(partes) >= 2 else self.nome_completo

    def save(self, *args, **kwargs):
        self.cpf = re.sub(r'\D', '', self.cpf)
        super().save(*args, **kwargs)
