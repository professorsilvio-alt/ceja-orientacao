"""
App: usuarios
Modelo de usuário customizado com CPF como chave primária e login.
"""
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
import re


def validar_cpf(cpf: str) -> str:
    """Remove pontuação e valida formato do CPF."""
    cpf = re.sub(r'\D', '', cpf)
    if len(cpf) != 11:
        raise ValueError('CPF deve ter 11 dígitos.')
    return cpf


class UsuarioManager(BaseUserManager):
    """Manager customizado para usuário com CPF."""

    def create_user(self, cpf, nome_completo, email, perfil, password=None, **extra_fields):
        if not cpf:
            raise ValueError('O CPF é obrigatório.')
        cpf = validar_cpf(cpf)
        email = self.normalize_email(email)
        user = self.model(
            cpf=cpf,
            nome_completo=nome_completo,
            email=email,
            perfil=perfil,
            **extra_fields
        )
        # Senha inicial = CPF (sem pontuação), obriga troca no primeiro acesso
        user.set_password(password or cpf)
        user.primeiro_acesso = True
        user.save(using=self._db)
        return user

    def create_superuser(self, cpf, nome_completo, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(cpf, nome_completo, email, 'diretor', password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    """
    Usuário do sistema CEJA.
    CPF é a chave primária e o identificador de login.
    """

    PERFIL_CHOICES = [
        ('diretor', 'Diretor'),
        ('professor', 'Professor'),
        ('administrativo', 'Funcionário Administrativo'),
        ('terceirizado', 'Funcionário Terceirizado'),
    ]

    # Chave primária = CPF (11 dígitos, sem pontuação)
    cpf = models.CharField(
        max_length=11,
        primary_key=True,
        verbose_name='CPF',
        help_text='Somente números, 11 dígitos.'
    )
    nome_completo = models.CharField(max_length=200, verbose_name='Nome completo')
    email = models.EmailField(unique=True, verbose_name='E-mail')
    telefone = models.CharField(max_length=20, blank=True, verbose_name='Telefone')
    perfil = models.CharField(max_length=20, choices=PERFIL_CHOICES, verbose_name='Perfil')

    # Controle de acesso
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    is_staff = models.BooleanField(default=False, verbose_name='Acesso ao Admin')
    primeiro_acesso = models.BooleanField(
        default=True,
        verbose_name='Primeiro acesso',
        help_text='Se verdadeiro, o usuário será obrigado a trocar a senha.'
    )

    # Timestamps
    data_cadastro = models.DateTimeField(default=timezone.now, verbose_name='Data de cadastro')
    ultimo_login_sistema = models.DateTimeField(null=True, blank=True, verbose_name='Último login')

    # Recuperação de senha
    token_recuperacao = models.CharField(max_length=100, blank=True, verbose_name='Token de recuperação')
    token_expiracao = models.DateTimeField(null=True, blank=True, verbose_name='Expiração do token')

    objects = UsuarioManager()

    USERNAME_FIELD = 'cpf'
    REQUIRED_FIELDS = ['nome_completo', 'email']

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['nome_completo']

    def __str__(self):
        return f'{self.nome_completo} ({self.get_perfil_display()})'

    @property
    def cpf_formatado(self):
        """Retorna CPF no formato XXX.XXX.XXX-XX"""
        c = self.cpf
        if len(c) == 11:
            return f'{c[:3]}.{c[3:6]}.{c[6:9]}-{c[9:]}'
        return c

    @property
    def primeiro_nome(self):
        return self.nome_completo.split()[0]

    def save(self, *args, **kwargs):
        self.cpf = re.sub(r'\D', '', self.cpf)
        super().save(*args, **kwargs)
