"""Formulários do app funcionarios"""
from django import forms
from .models import FuncionarioAdministrativo, FuncionarioTerceirizado
import re


class FuncionarioAdmForm(forms.ModelForm):
    class Meta:
        model = FuncionarioAdministrativo
        fields = [
            'cpf', 'matricula', 'matricula_acumulacao', 'nome_completo',
            'cargo', 'funcao_ingresso',
            'data_ci_movimentacao', 'data_ingresso_unidade', 'classificacao',
            'email', 'telefone', 'foto', 'ativo', 'observacoes',
        ]
        widgets = {
            'cpf': forms.TextInput(attrs={'placeholder': '00000000000', 'id': 'id_cpf_adm'}),
            'data_ci_movimentacao': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'data_ingresso_unidade': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data_ci_movimentacao'].input_formats = ['%Y-%m-%d']
        self.fields['data_ingresso_unidade'].input_formats = ['%Y-%m-%d']

    def clean_cpf(self):
        cpf = re.sub(r'\D', '', self.cleaned_data['cpf'])
        if len(cpf) != 11:
            raise forms.ValidationError('CPF deve ter 11 dígitos.')
        return cpf


class FuncionarioTercForm(forms.ModelForm):
    class Meta:
        model = FuncionarioTerceirizado
        fields = [
            'nome_completo', 'cpf', 'rg', 'data_nascimento', 'sexo', 'estado_civil', 'naturalidade',
            'pis_pasep', 'ctps_numero', 'ctps_serie', 'ctps_uf',
            'empresa_contratante', 'cargo_funcao', 'salario',
            'data_admissao', 'data_demissao', 'ativo',
            'cep', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'uf',
            'email', 'telefone', 'telefone_emergencia',
            'foto', 'observacoes',
        ]
        widgets = {
            'cpf': forms.TextInput(attrs={'placeholder': '00000000000', 'id': 'id_cpf_terc'}),
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'data_admissao': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'data_demissao': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
            'salario': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in ['data_nascimento', 'data_admissao', 'data_demissao']:
            self.fields[f].input_formats = ['%Y-%m-%d']

    def clean_cpf(self):
        cpf = re.sub(r'\D', '', self.cleaned_data['cpf'])
        if len(cpf) != 11:
            raise forms.ValidationError('CPF deve ter 11 dígitos.')
        return cpf
