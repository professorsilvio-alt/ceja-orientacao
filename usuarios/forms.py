"""Formulários de autenticação e gestão de usuários"""
from django import forms
from django.contrib.auth import get_user_model
import re

User = get_user_model()


class LoginForm(forms.Form):
    cpf = forms.CharField(
        label='CPF',
        max_length=14,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '000.000.000-00',
            'autocomplete': 'username',
            'id': 'id_cpf',
        })
    )
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••',
            'autocomplete': 'current-password',
            'id': 'id_password',
        })
    )

    def clean_cpf(self):
        cpf = re.sub(r'\D', '', self.cleaned_data['cpf'])
        if len(cpf) != 11:
            raise forms.ValidationError('CPF inválido. Digite os 11 dígitos.')
        return cpf


class TrocaSenhaForm(forms.Form):
    """Troca de senha — obrigatória no primeiro acesso."""
    nova_senha = forms.CharField(
        label='Nova senha',
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mínimo 8 caracteres',
            'id': 'id_nova_senha'
        })
    )
    confirmar_senha = forms.CharField(
        label='Confirmar nova senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Repita a senha',
            'id': 'id_confirmar_senha'
        })
    )

    def clean(self):
        cleaned = super().clean()
        nova = cleaned.get('nova_senha')
        confirmar = cleaned.get('confirmar_senha')
        if nova and confirmar and nova != confirmar:
            raise forms.ValidationError('As senhas não coincidem.')
        return cleaned


class RecuperarSenhaForm(forms.Form):
    """Solicita recuperação de senha por e-mail."""
    email = forms.EmailField(
        label='E-mail cadastrado',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'seu@email.com',
            'id': 'id_email'
        })
    )


class RedefinirSenhaForm(forms.Form):
    """Redefine senha a partir do token enviado por e-mail."""
    nova_senha = forms.CharField(
        label='Nova senha',
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mínimo 8 caracteres',
            'id': 'id_nova_senha'
        })
    )
    confirmar_senha = forms.CharField(
        label='Confirmar nova senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Repita a senha',
            'id': 'id_confirmar_senha'
        })
    )

    def clean(self):
        cleaned = super().clean()
        nova = cleaned.get('nova_senha')
        confirmar = cleaned.get('confirmar_senha')
        if nova and confirmar and nova != confirmar:
            raise forms.ValidationError('As senhas não coincidem.')
        return cleaned


class UsuarioForm(forms.ModelForm):
    """Formulário para criar/editar usuários (uso do Diretor)."""

    class Meta:
        model = User
        fields = ['cpf', 'id_vinculo', 'matricula', 'nome_completo', 'email', 'telefone', 'perfil', 'is_active']
        widgets = {
            'cpf': forms.TextInput(attrs={'placeholder': '00000000000', 'id': 'id_cpf_usuario'}),
            'id_vinculo': forms.TextInput(attrs={'placeholder': 'Ex: 40645924/2', 'id': 'id_vinculo_usuario'}),
            'matricula': forms.TextInput(attrs={'placeholder': 'Ex: 2427227', 'id': 'id_matricula_usuario'}),
            'nome_completo': forms.TextInput(attrs={'id': 'id_nome_completo'}),
            'email': forms.EmailInput(attrs={'id': 'id_email_usuario'}),
            'telefone': forms.TextInput(attrs={'placeholder': '(21) 99999-9999', 'id': 'id_telefone'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
                if 'class' not in field.widget.attrs:
                    field.widget.attrs['class'] = 'form-select'
            elif not isinstance(field.widget, (forms.CheckboxInput, forms.CheckboxSelectMultiple)):
                existing = field.widget.attrs.get('class', '')
                if 'form-control' not in existing:
                    field.widget.attrs['class'] = (existing + ' form-control').strip()

    def clean_cpf(self):
        cpf = re.sub(r'\D', '', self.cleaned_data['cpf'])
        if len(cpf) != 11:
            raise forms.ValidationError('CPF deve ter 11 dígitos.')
        return cpf
