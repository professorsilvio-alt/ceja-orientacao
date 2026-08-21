"""
App: agenda
Modelos de:
  - RegistroPresenca: ausências, faltas e atrasos de professores/funcionários
  - ReservaAuditorio: agenda do auditório para oficinas, aulas e eventos
"""
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


TIPO_OCORRENCIA_CHOICES = [
    ('falta', 'Falta'),
    ('ausencia', 'Ausência justificada'),
    ('atraso', 'Atraso'),
    ('saida_antecipada', 'Saída antecipada'),
]

TIPO_FUNCIONARIO_CHOICES = [
    ('professor', 'Professor'),
    ('administrativo', 'Funcionário Administrativo'),
    ('terceirizado', 'Funcionário Terceirizado'),
]

TIPO_EVENTO_AUDITORIO_CHOICES = [
    ('oficina', 'Oficina'),
    ('aula', 'Aula'),
    ('evento', 'Evento / Palestra'),
    ('reuniao', 'Reunião'),
    ('outro', 'Outro'),
]

STATUS_RESERVA_CHOICES = [
    ('confirmada', 'Confirmada'),
    ('pendente', 'Pendente'),
    ('cancelada', 'Cancelada'),
    ('realizada', 'Realizada'),
]


class RegistroPresenca(models.Model):
    """
    Registro de ausências, faltas e atrasos de professores e funcionários.
    Cadastrado pela Direção.
    """

    # De qual tipo de funcionário
    tipo_funcionario = models.CharField(
        max_length=20, choices=TIPO_FUNCIONARIO_CHOICES, verbose_name='Tipo de funcionário'
    )

    # IDs dos modelos específicos (FK genérica manual para flexibilidade)
    professor_id = models.PositiveIntegerField(
        null=True, blank=True, verbose_name='Professor (ID)'
    )
    administrativo_id = models.PositiveIntegerField(
        null=True, blank=True, verbose_name='Funcionário Administrativo (ID)'
    )
    terceirizado_id = models.PositiveIntegerField(
        null=True, blank=True, verbose_name='Funcionário Terceirizado (ID)'
    )

    # Cache do nome (para facilitar exibição sem joins extras)
    nome_funcionario = models.CharField(
        max_length=200, verbose_name='Nome do funcionário',
        help_text='Preenchido automaticamente.'
    )

    # Dados da ocorrência
    data = models.DateField(verbose_name='Data da ocorrência')
    tipo = models.CharField(max_length=20, choices=TIPO_OCORRENCIA_CHOICES, verbose_name='Tipo')
    hora_chegada = models.TimeField(
        null=True, blank=True, verbose_name='Hora de chegada',
        help_text='Preencha apenas para atrasos.'
    )
    hora_saida = models.TimeField(
        null=True, blank=True, verbose_name='Hora de saída',
        help_text='Preencha apenas para saídas antecipadas.'
    )
    justificado = models.BooleanField(default=False, verbose_name='Justificado')
    motivo = models.CharField(max_length=200, blank=True, verbose_name='Motivo')
    observacoes = models.TextField(blank=True, verbose_name='Observações')

    # Quem registrou
    registrado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='registros_presenca', verbose_name='Registrado por'
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Registro de Presença'
        verbose_name_plural = 'Registros de Presença'
        ordering = ['-data', '-criado_em']

    def __str__(self):
        return f'{self.data} — {self.nome_funcionario} — {self.get_tipo_display()}'

    def get_funcionario(self):
        """Retorna o objeto do funcionário conforme o tipo."""
        if self.tipo_funcionario == 'professor' and self.professor_id:
            from professores.models import Professor
            try:
                return Professor.objects.get(pk=self.professor_id)
            except Professor.DoesNotExist:
                pass
        elif self.tipo_funcionario == 'administrativo' and self.administrativo_id:
            from funcionarios.models import FuncionarioAdministrativo
            try:
                return FuncionarioAdministrativo.objects.get(pk=self.administrativo_id)
            except FuncionarioAdministrativo.DoesNotExist:
                pass
        elif self.tipo_funcionario == 'terceirizado' and self.terceirizado_id:
            from funcionarios.models import FuncionarioTerceirizado
            try:
                return FuncionarioTerceirizado.objects.get(pk=self.terceirizado_id)
            except FuncionarioTerceirizado.DoesNotExist:
                pass
        return None

    @property
    def badge_color(self):
        cores = {
            'falta': 'danger',
            'ausencia': 'warning',
            'atraso': 'info',
            'saida_antecipada': 'secondary',
        }
        return cores.get(self.tipo, 'secondary')


class ReservaAuditorio(models.Model):
    """
    Reserva do auditório para oficinas, aulas e eventos.
    """

    titulo = models.CharField(max_length=200, verbose_name='Título do evento')
    tipo = models.CharField(
        max_length=20, choices=TIPO_EVENTO_AUDITORIO_CHOICES, verbose_name='Tipo'
    )
    descricao = models.TextField(blank=True, verbose_name='Descrição / Detalhes')

    data = models.DateField(verbose_name='Data')
    hora_inicio = models.TimeField(verbose_name='Horário de início')
    hora_fim = models.TimeField(verbose_name='Horário de término')

    responsavel = models.CharField(
        max_length=200, verbose_name='Responsável pelo evento',
        help_text='Nome do professor ou organizador.'
    )
    turma_publico = models.CharField(
        max_length=200, blank=True, verbose_name='Turma / Público alvo'
    )
    capacidade_prevista = models.PositiveIntegerField(
        null=True, blank=True, verbose_name='Capacidade prevista (nº de pessoas)'
    )

    status = models.CharField(
        max_length=20, choices=STATUS_RESERVA_CHOICES,
        default='confirmada', verbose_name='Status'
    )
    observacoes = models.TextField(blank=True, verbose_name='Observações')

    criado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='reservas_auditorio', verbose_name='Criado por'
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Reserva do Auditório'
        verbose_name_plural = 'Reservas do Auditório'
        ordering = ['data', 'hora_inicio']

    def __str__(self):
        return f'{self.data} {self.hora_inicio:%H:%M} — {self.titulo}'

    @property
    def badge_color(self):
        cores = {
            'oficina': 'primary',
            'aula': 'success',
            'evento': 'info',
            'reuniao': 'warning',
            'outro': 'secondary',
        }
        return cores.get(self.tipo, 'secondary')

    @property
    def duracao_minutos(self):
        from datetime import datetime, date
        inicio = datetime.combine(date.today(), self.hora_inicio)
        fim = datetime.combine(date.today(), self.hora_fim)
        return int((fim - inicio).total_seconds() / 60)
