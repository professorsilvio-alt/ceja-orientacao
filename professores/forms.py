"""Formulários do app professores"""
from django import forms
from .models import Professor, HorarioProfessor
import re


def aplicar_estilo_campos(form_instance):
    """Aplica classes CSS form-control e form-select a todos os campos do formulário."""
    for field in form_instance.fields.values():
        if isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-select'
        elif not isinstance(field.widget, (forms.CheckboxInput, forms.CheckboxSelectMultiple)):
            existing = field.widget.attrs.get('class', '')
            if 'form-control' not in existing:
                field.widget.attrs['class'] = (existing + ' form-control').strip()


class ProfessorForm(forms.ModelForm):
    class Meta:
        model = Professor
        fields = [
            'cpf', 'id_vinculo', 'matricula', 'matricula_acumulacao', 'nome_completo',
            'cargo', 'disciplina_ingresso', 'disciplinas_lecionadas',
            'data_ci_movimentacao', 'data_ingresso_unidade', 'classificacao',
            'email', 'telefone', 'foto', 'ativo', 'observacoes',
        ]
        widgets = {
            'cpf': forms.TextInput(attrs={'placeholder': '00000000000', 'id': 'id_cpf_prof'}),
            'id_vinculo': forms.TextInput(attrs={'placeholder': 'Ex: 40645924/2', 'id': 'id_vinculo_prof'}),
            'matricula': forms.TextInput(attrs={'id': 'id_matricula'}),
            'matricula_acumulacao': forms.TextInput(attrs={'id': 'id_mat_acum'}),
            'nome_completo': forms.TextInput(attrs={'id': 'id_nome_prof'}),
            'data_ci_movimentacao': forms.DateInput(
                attrs={'type': 'date', 'id': 'id_data_ci'}, format='%Y-%m-%d'
            ),
            'data_ingresso_unidade': forms.DateInput(
                attrs={'type': 'date', 'id': 'id_data_ingresso'}, format='%Y-%m-%d'
            ),
            'classificacao': forms.NumberInput(attrs={'min': 1, 'id': 'id_classificacao'}),
            'email': forms.EmailInput(attrs={'id': 'id_email_prof'}),
            'telefone': forms.TextInput(attrs={'placeholder': '(21) 99999-9999', 'id': 'id_tel_prof'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'id': 'id_obs_prof'}),
            'disciplinas_lecionadas': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data_ci_movimentacao'].input_formats = ['%Y-%m-%d']
        self.fields['data_ingresso_unidade'].input_formats = ['%Y-%m-%d']
        aplicar_estilo_campos(self)

    def clean_cpf(self):
        cpf = re.sub(r'\D', '', self.cleaned_data['cpf'])
        if len(cpf) != 11:
            raise forms.ValidationError('CPF deve ter 11 dígitos.')
        return cpf


class HorarioProfessorForm(forms.ModelForm):
    class Meta:
        model = HorarioProfessor
        fields = ['ano_letivo', 'dia_semana', 'hora_inicio', 'hora_fim', 'local', 'local_descricao']
        widgets = {
            'hora_inicio': forms.TimeInput(attrs={'type': 'time', 'id': 'id_hora_inicio_h'}),
            'hora_fim': forms.TimeInput(attrs={'type': 'time', 'id': 'id_hora_fim_h'}),
            'ano_letivo': forms.NumberInput(attrs={'min': 2020, 'max': 2099, 'id': 'id_ano_letivo_h'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        aplicar_estilo_campos(self)

    def clean(self):
        cleaned = super().clean()
        inicio = cleaned.get('hora_inicio')
        fim = cleaned.get('hora_fim')
        if inicio and fim and inicio >= fim:
            raise forms.ValidationError('O horário de início deve ser anterior ao horário de fim.')
        return cleaned
