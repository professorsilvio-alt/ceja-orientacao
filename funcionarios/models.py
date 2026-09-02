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
    cpf = models.CharField(max_length=11, unique=True, verbose_name='CPF')
    id_vinculo = models.CharField(max_length=30, blank=True, verbose_name='ID / Vínculo', help_text='Ex: 40260437/2')
    matricula = models.CharField(max_length=20, unique=True, verbose_name='Matrícula')

    # ── Acumulação (2ª Matrícula / Cargo na escola) ────────
    id_vinculo_acumulacao = models.CharField(max_length=30, blank=True, verbose_name='ID / Vínculo (2ª Matrícula)')
    matricula_acumulacao = models.CharField(max_length=20, blank=True, verbose_name='Matrícula acumulação')
    
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
    cargo_acumulacao = models.CharField(max_length=150, blank=True, verbose_name='Cargo (2ª Matrícula)')
    disciplina_ingresso_acumulacao = models.CharField(max_length=150, blank=True, verbose_name='Disciplina de Ingresso (2ª Matrícula)')
    funcao_acumulacao = models.CharField(max_length=150, blank=True, verbose_name='Função (2ª Matrícula)')
    ch_total_acumulacao = models.PositiveIntegerField(null=True, blank=True, verbose_name='CH Total (2ª Matrícula)')
    data_admissao_acumulacao = models.DateField(null=True, blank=True, verbose_name='Data Admissão (2ª Matrícula)')
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
        return f'{self.nome_completo} — {self.cargo}'

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

    # ── Contrato e Empresa Contratante ─────────────────────
    empresa_contratante = models.CharField(
        max_length=200, default='KRATUS TECNOLOGIA COMERCIO E SERVICOS LT', verbose_name='Empresa Contratante'
    )
    empresa_cnpj = models.CharField(
        max_length=20, default='33.780.199/0001-77', blank=True, verbose_name='CNPJ da Empresa'
    )
    empresa_endereco = models.CharField(
        max_length=250, default='ESTRADA DO GALEAO, 1285', blank=True, verbose_name='Endereço da Empresa'
    )
    empresa_bairro = models.CharField(
        max_length=100, default='JARDIM GUANABARA', blank=True, verbose_name='Bairro da Empresa'
    )
    empresa_cidade = models.CharField(
        max_length=100, default='RIO DE JANEIRO', blank=True, verbose_name='Cidade da Empresa'
    )
    empresa_uf = models.CharField(
        max_length=2, default='RJ', blank=True, verbose_name='UF da Empresa'
    )
    empresa_cep = models.CharField(
        max_length=10, default='21931-383', blank=True, verbose_name='CEP da Empresa'
    )

    # ── Dados para Folha de Ponto ──────────────────────────
    codigo_terceirizado = models.CharField(
        max_length=20, blank=True, verbose_name='Código / Matrícula na Empresa',
        help_text='Ex: 176, 26'
    )
    horario_trabalho = models.CharField(
        max_length=50, default='07:00 X 16:48', blank=True, verbose_name='Horário de Trabalho',
        help_text='Ex: 07:00 X 16:48'
    )
    departamento = models.CharField(
        max_length=100, default='CECIERJ', blank=True, verbose_name='Departamento (DPTO)'
    )
    centro_custo = models.CharField(
        max_length=150, default='CEJA-MESQUITA - PROF ROSA SOARES', blank=True, verbose_name='Centro de Custo (C. Custo)'
    )

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

    # ── Outros & Controle de Ponto ─────────────────────────
    senha_ponto = models.CharField(
        max_length=128, blank=True, verbose_name='Senha do Ponto',
        help_text='PIN ou Senha individual para bater o ponto'
    )
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

    def definir_senha_ponto(self, raw_pin):
        """Define e armazena a senha/PIN de ponto usando SHA-256 com salt (validação instantânea em 0.01ms)."""
        import hashlib
        import secrets
        pin_clean = str(raw_pin).strip()
        salt = secrets.token_hex(8)
        digest = hashlib.sha256(f"{salt}:{pin_clean}".encode('utf-8')).hexdigest()
        self.senha_ponto = f"sha256${salt}${digest}"

    def verificar_senha_ponto(self, raw_pin):
        """Verifica a senha/PIN de ponto do funcionário de forma instantânea."""
        import hashlib
        if not self.senha_ponto:
            return False
        pin_clean = str(raw_pin).strip()
        if self.senha_ponto.startswith('sha256$'):
            try:
                partes = self.senha_ponto.split('$')
                if len(partes) == 3:
                    salt, digest = partes[1], partes[2]
                    calc = hashlib.sha256(f"{salt}:{pin_clean}".encode('utf-8')).hexdigest()
                    return calc == digest
            except Exception:
                return False

        # Compatibilidade com hash legado PBKDF2
        from django.contrib.auth.hashers import check_password
        ok = check_password(pin_clean, self.senha_ponto)
        if ok:
            # Migra automaticamente para SHA-256 na primeira validação para respostas instantâneas
            self.definir_senha_ponto(pin_clean)
            self.save(update_fields=['senha_ponto'])
        return ok

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


class RegistroPontoTerceirizado(models.Model):
    """Registro de batida de ponto do funcionário terceirizado com foto e tipo."""

    TIPO_PONTO_CHOICES = [
        ('ENTRADA', 'Entrada (Chegando à escola)'),
        ('ALMOCO_SAIDA', 'Saída para Almoço'),
        ('ALMOCO_RETORNO', 'Retorno do Almoço'),
        ('SAIDA', 'Saída para Casa (Fim de expediente)'),
    ]

    funcionario = models.ForeignKey(
        FuncionarioTerceirizado,
        on_delete=models.CASCADE,
        related_name='registros_ponto',
        verbose_name='Funcionário'
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_PONTO_CHOICES,
        verbose_name='Tipo de Registro'
    )
    data_hora = models.DateTimeField(
        default=timezone.now,
        verbose_name='Data e Hora da Batida'
    )
    foto = models.ImageField(
        upload_to='terceirizados/ponto/',
        blank=True,
        null=True,
        verbose_name='Foto da Batida'
    )
    ip_origem = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name='IP de Origem'
    )
    observacao = models.TextField(
        blank=True,
        verbose_name='Observação / Justificativa'
    )
    email_enviado = models.BooleanField(
        default=False,
        verbose_name='Confirmação por E-mail Enviada'
    )

    class Meta:
        verbose_name = 'Registro de Ponto (Terceirizado)'
        verbose_name_plural = 'Registros de Ponto (Terceirizados)'
        ordering = ['-data_hora']

    def __str__(self):
        return f'{self.funcionario.nome_curto} - {self.get_tipo_display()} em {self.data_hora.strftime("%d/%m/%Y %H:%M:%S")}'

