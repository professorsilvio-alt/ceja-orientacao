"""Formulários do app diario_bordo"""
from django import forms
from .models import OcorrenciaDiario


class OcorrenciaDiarioForm(forms.ModelForm):
    class Meta:
        model = OcorrenciaDiario
        fields = ['titulo', 'categoria', 'prioridade', 'texto', 'anexo']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título ou assunto resumido (opcional)...',
                'maxlength': '200',
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select',
            }),
            'prioridade': forms.Select(attrs={
                'class': 'form-select',
            }),
            'texto': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Descreva a ocorrência, fatos relevantes, providências adotadas ou recado para a equipe da Direção...',
                'required': True,
            }),
            'anexo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png,.webp,.txt',
            }),
        }
        labels = {
            'titulo': 'Título / Assunto (Opcional)',
            'categoria': 'Categoria',
            'prioridade': 'Prioridade do Recado',
            'texto': 'Relato da Ocorrência / Mensagem',
            'anexo': 'Anexo ou Foto (Opcional)',
        }

