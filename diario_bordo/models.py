"""
App: diario_bordo
Modelos para o Diário de Bordo da Direção Escolar.
Permite registro de ocorrências diárias e comunicação interna com confirmação de leitura por checklist.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models import Q


class OcorrenciaDiario(models.Model):
    """
    Registro individual de ocorrência ou comunicado no Diário de Bordo da Direção.
    Captura automaticamente autor (usuário diretor logado), data e hora.
    """

    PRIORIDADE_CHOICES = [
        ('normal', 'Normal / Rotina'),
        ('importante', 'Importante'),
        ('urgente', 'Urgente / Imediato'),
    ]

    CATEGORIA_CHOICES = [
        ('geral', 'Geral / Rotina'),
        ('pedagogico', 'Pedagógico'),
        ('alunos', 'Alunos & Responsáveis'),
        ('funcionarios', 'Professores & Funcionários'),
        ('manutencao', 'Infraestrutura & Manutenção'),
        ('seguranca', 'Segurança & Portaria'),
        ('outros', 'Outros Assuntos'),
    ]

    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ocorrencias_diario',
        verbose_name='Autor da Ocorrência'
    )
    titulo = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Título / Assunto (opcional)',
        help_text='Ex: Contato com responsável do aluno João, Manutenção na bomba d\'água...'
    )
    texto = models.TextField(
        verbose_name='Relato / Ocorrência / Recado',
        help_text='Descreva os fatos ocorridos, providências adotadas ou recado para a equipe de direção.'
    )
    prioridade = models.CharField(
        max_length=20,
        choices=PRIORIDADE_CHOICES,
        default='normal',
        verbose_name='Prioridade'
    )
    categoria = models.CharField(
        max_length=40,
        choices=CATEGORIA_CHOICES,
        default='geral',
        verbose_name='Categoria'
    )
    anexo = models.FileField(
        upload_to='diario_bordo/%Y/%m/',
        null=True,
        blank=True,
        verbose_name='Anexo (opcional)',
        help_text='Documento, foto ou comprovante relacionado à ocorrência.'
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name='Ativo',
        help_text='Desmarque para arquivar ou desativar o registro sem apagá-lo.'
    )
    criado_em = models.DateTimeField(
        default=timezone.now,
        verbose_name='Data e Hora do Registro'
    )
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Atualização'
    )

    class Meta:
        verbose_name = 'Ocorrência do Diário de Bordo'
        verbose_name_plural = 'Ocorrências do Diário de Bordo'
        ordering = ['-criado_em']

    def __str__(self):
        assunto = self.titulo.strip() if self.titulo else (self.texto[:40] + '...')
        return f'[{self.get_prioridade_display()}] {assunto} ({self.criado_em.strftime("%d/%m/%Y %H:%M")})'

    @property
    def assunto_exibicao(self):
        if self.titulo and self.titulo.strip():
            return self.titulo.strip()
        limpo = ' '.join(self.texto.split())
        return limpo[:65] + ('...' if len(limpo) > 65 else '')

    @property
    def badge_prioridade_badge(self):
        if self.prioridade == 'urgente':
            return 'badge bg-danger text-white'
        elif self.prioridade == 'importante':
            return 'badge bg-warning text-dark'
        return 'badge bg-info-subtle text-info border border-info'

    @property
    def badge_prioridade_cor(self):
        if self.prioridade == 'urgente':
            return '#ef4444'
        elif self.prioridade == 'importante':
            return '#eab308'
        return '#38bdf8'

    def lida_por(self, usuario):
        """Retorna True se o usuário é o próprio autor ou se já registrou leitura."""
        if not usuario or not usuario.is_authenticated:
            return False
        if self.autor_id == usuario.pk:
            return True
        return self.leituras.filter(usuario=usuario).exists()

    def data_leitura_usuario(self, usuario):
        """Retorna o timestamp da leitura do usuário ou criação se for o autor."""
        if not usuario or not usuario.is_authenticated:
            return None
        if self.autor_id == usuario.pk:
            return self.criado_em
        leitura = self.leituras.filter(usuario=usuario).first()
        return leitura.lido_em if leitura else None

    def get_checklist_leituras(self):
        """
        Retorna a lista estruturada de confirmações de leitura para toda a equipe da direção escolar.
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()
        diretores = User.objects.filter(
            Q(perfil='diretor') | Q(is_superuser=True),
            is_active=True
        ).distinct().order_by('nome_completo')

        leituras_dict = {l.usuario_id: l for l in self.leituras.all()}

        checklist = []
        for d in diretores:
            is_autor = (d.pk == self.autor_id)
            leitura = leituras_dict.get(d.pk)
            lido = is_autor or (leitura is not None)
            data_confirmacao = self.criado_em if is_autor else (leitura.lido_em if leitura else None)
            checklist.append({
                'usuario': d,
                'is_autor': is_autor,
                'lido': lido,
                'data_confirmacao': data_confirmacao,
            })
        return checklist

    @property
    def estatisticas_leituras(self):
        """Calcula totais e percentual de leitura da direção."""
        checklist = self.get_checklist_leituras()
        total_esperado = len(checklist)
        total_lidos = sum(1 for item in checklist if item['lido'])
        percentual = int((total_lidos / total_esperado * 100)) if total_esperado > 0 else 100
        return {
            'total_esperado': total_esperado,
            'total_lidos': total_lidos,
            'total_pendentes': total_esperado - total_lidos,
            'percentual': percentual,
            'concluido': total_lidos >= total_esperado,
        }


class LeituraOcorrencia(models.Model):
    """
    Confirmação de leitura e ciência de uma ocorrência do Diário de Bordo por um usuário diretor.
    """
    ocorrencia = models.ForeignKey(
        OcorrenciaDiario,
        on_delete=models.CASCADE,
        related_name='leituras',
        verbose_name='Ocorrência'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='leituras_diario_bordo',
        verbose_name='Usuário Leitor'
    )
    lido_em = models.DateTimeField(
        default=timezone.now,
        verbose_name='Data e Hora da Confirmação'
    )
    ip_origem = models.CharField(
        max_length=45,
        blank=True,
        verbose_name='Endereço IP'
    )
    observacao = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Observação do Leitor'
    )

    class Meta:
        verbose_name = 'Confirmação de Leitura'
        verbose_name_plural = 'Confirmações de Leitura'
        unique_together = ('ocorrencia', 'usuario')
        ordering = ['-lido_em']

    def __str__(self):
        return f'{self.usuario.primeiro_nome} leu Ocorrência #{self.ocorrencia_id} em {self.lido_em.strftime("%d/%m/%Y %H:%M")}'
