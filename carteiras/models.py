from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid
import secrets


class ConfiguracaoCarteira(models.Model):
    """
    Configurações do módulo de carteirinhas e chancela digital da Direção.
    Permite ao Diretor ativar/desativar a emissão pública e gerenciar parâmetros.
    """
    emissao_publica_ativa = models.BooleanField(
        default=True,
        verbose_name="Emissão Pública Ativa",
        help_text="Se desmarcado, a emissão pública para terceirizados fica temporariamente suspensa."
    )
    nome_diretor = models.CharField(
        max_length=200,
        default="Silvio da Silva Rosa Soares",
        verbose_name="Nome do Diretor"
    )
    cargo_diretor = models.CharField(
        max_length=150,
        default="Direção",
        verbose_name="Cargo / Titulação"
    )
    unidade_escolar = models.CharField(
        max_length=255,
        default="CEJA PROFESSORA ROSA SOARES",
        verbose_name="Nome da Unidade Escolar"
    )
    codigo_ua = models.CharField(
        max_length=100,
        default="U.A.: 11802310502 - Ensino Médio",
        verbose_name="Código U.A. / Modalidade"
    )
    caminho_assinatura_arquivo = models.CharField(
        max_length=500,
        default="media/seguro/assinatura_silvio.png",
        verbose_name="Caminho seguro da assinatura"
    )
    aviso_manutencao = models.CharField(
        max_length=255,
        blank=True,
        default="A emissão de carteirinhas está temporariamente pausada para manutenção.",
        verbose_name="Mensagem quando pausada"
    )
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuração de Carteirinhas"
        verbose_name_plural = "Configurações de Carteirinhas"

    def __str__(self):
        status = "Ativa" if self.emissao_publica_ativa else "Pausada"
        return f"Configuração Carteira CEJA ({status})"

    @classmethod
    def get_config(cls):
        try:
            obj = cls.objects.first()
            if not obj:
                obj = cls.objects.create(id=1)
            return obj
        except Exception:
            return cls(
                emissao_publica_ativa=True,
                nome_diretor="Silvio da Silva Rosa Soares",
                cargo_diretor="Direção",
                unidade_escolar="CEJA PROFESSORA ROSA SOARES",
                codigo_ua="U.A.: 11802310502 - Ensino Médio",
            )


def gerar_codigo_autenticidade():
    token = secrets.token_hex(3).upper()
    ano = timezone.now().year
    return f"CEJA-{ano}-{token[:3]}-{token[3:]}"


class CarteiraEstudanteEmitida(models.Model):
    """
    Registro imutável de cada carteirinha de estudante autenticada e emitida.
    Permite conferência por QR Code e auditoria completa da Direção.
    """
    codigo_autenticidade = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        default=gerar_codigo_autenticidade,
        verbose_name="Código de Autenticidade"
    )
    matricula = models.CharField(
        max_length=50,
        db_index=True,
        verbose_name="Matrícula do Aluno"
    )
    nome_aluno = models.CharField(
        max_length=255,
        verbose_name="Nome do Aluno"
    )
    curso = models.CharField(
        max_length=150,
        default="Ensino Médio",
        verbose_name="Curso / Segmento"
    )
    unidade = models.CharField(
        max_length=150,
        default="11802310502 - Ensino Médio",
        verbose_name="Unidade / U.A."
    )
    email_aluno = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="E-mail do Aluno"
    )
    data_nascimento = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Data de Nascimento"
    )
    data_validade = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Data de Validade"
    )
    filiacao = models.TextField(
        blank=True,
        verbose_name="Filiação"
    )
    foto_base64_ou_url = models.TextField(
        blank=True,
        verbose_name="Foto do Aluno (URL ou Base64)"
    )

    # Dados de Auditoria e Responsabilidade
    nome_operador = models.CharField(
        max_length=200,
        verbose_name="Operador / Funcionário que Autenticou",
        help_text="Nome da pessoa da secretaria/terceirizado que acionou a emissão"
    )
    ip_origem = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP de Origem"
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name="Navegador / Dispositivo"
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data e Hora de Emissão"
    )

    # Controle de Revogação
    ativo = models.BooleanField(
        default=True,
        verbose_name="Válida / Ativa",
        help_text="Se desmarcado, a validação via QR Code apontará carteira revogada/inválida."
    )
    motivo_cancelamento = models.TextField(
        blank=True,
        verbose_name="Motivo do Cancelamento / Revogação"
    )
    cancelado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Cancelado por"
    )
    cancelado_em = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Cancelado em"
    )

    class Meta:
        verbose_name = "Carteira de Estudante Emitida"
        verbose_name_plural = "Carteiras de Estudante Emitidas"
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.matricula} - {self.nome_aluno} ({self.codigo_autenticidade})"
