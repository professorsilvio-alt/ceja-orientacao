"""Admin do app usuarios"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario
    list_display = ['cpf_formatado', 'nome_completo', 'perfil', 'email', 'is_active', 'primeiro_acesso']
    list_filter = ['perfil', 'is_active', 'primeiro_acesso']
    search_fields = ['cpf', 'nome_completo', 'email']
    ordering = ['nome_completo']

    fieldsets = (
        ('Identificação', {'fields': ('cpf', 'nome_completo', 'email', 'telefone', 'perfil')}),
        ('Acesso', {'fields': ('password', 'is_active', 'is_staff', 'primeiro_acesso')}),
        ('Grupos e Permissões', {'fields': ('groups', 'user_permissions'), 'classes': ('collapse',)}),
        ('Datas', {'fields': ('data_cadastro', 'ultimo_login_sistema'), 'classes': ('collapse',)}),
    )

    add_fieldsets = (
        ('Novo Usuário', {
            'classes': ('wide',),
            'fields': ('cpf', 'nome_completo', 'email', 'telefone', 'perfil', 'password1', 'password2'),
        }),
    )

    readonly_fields = ['data_cadastro', 'ultimo_login_sistema', 'cpf_formatado']
