"""Formulários do app professores"""
from django import forms
from .models import Professor, HorarioProfessor, ConfiguracaoEscola, UnidadeEscolar, TurmaComponente, AlocacaoHorarioTurma


class UnidadeEscolarForm(forms.ModelForm):
    class Meta:
        model = UnidadeEscolar
        fields = ['nome', 'tipo', 'codigo', 'endereco', 'telefone', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Ex: Unidade Vinculada Maricá / Extensão Itaipuaçu', 'id': 'id_nome_unidade'}),
            'tipo': forms.Select(attrs={'id': 'id_tipo_unidade'}),
            'codigo': forms.TextInput(attrs={'placeholder': 'Ex: EXT-01', 'id': 'id_codigo_unidade'}),
            'endereco': forms.TextInput(attrs={'placeholder': 'Rua, Número, Bairro', 'id': 'id_end_unidade'}),
            'telefone': forms.TextInput(attrs={'placeholder': '(21) 99999-9999', 'id': 'id_tel_unidade'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        aplicar_estilo_campos(self)


class ConfiguracaoEscolaForm(forms.ModelForm):
    class Meta:
        model = ConfiguracaoEscola
        fields = [
            'ano_letivo', 'ativo', 'duracao_hora_aula',
            'horario_abertura', 'horario_fechamento',
            'func_segunda', 'seg_abertura', 'seg_fechamento',
            'func_terca', 'ter_abertura', 'ter_fechamento',
            'func_quarta', 'qua_abertura', 'qua_fechamento',
            'func_quinta', 'qui_abertura', 'qui_fechamento',
            'func_sexta', 'sex_abertura', 'sex_fechamento',
            'func_sabado', 'sab_abertura', 'sab_fechamento',
            'func_domingo', 'dom_abertura', 'dom_fechamento',
            'observacoes',
        ]
        widgets = {
            'ano_letivo': forms.NumberInput(attrs={'min': 2020, 'max': 2099, 'id': 'id_ano_letivo_cfg'}),
            'duracao_hora_aula': forms.NumberInput(attrs={'min': 15, 'max': 120, 'id': 'id_duracao_ha'}),
            'horario_abertura': forms.TimeInput(attrs={'type': 'time', 'id': 'id_abertura'}),
            'horario_fechamento': forms.TimeInput(attrs={'type': 'time', 'id': 'id_fechamento'}),
            'seg_abertura': forms.TimeInput(attrs={'type': 'time'}),
            'seg_fechamento': forms.TimeInput(attrs={'type': 'time'}),
            'ter_abertura': forms.TimeInput(attrs={'type': 'time'}),
            'ter_fechamento': forms.TimeInput(attrs={'type': 'time'}),
            'qua_abertura': forms.TimeInput(attrs={'type': 'time'}),
            'qua_fechamento': forms.TimeInput(attrs={'type': 'time'}),
            'qui_abertura': forms.TimeInput(attrs={'type': 'time'}),
            'qui_fechamento': forms.TimeInput(attrs={'type': 'time'}),
            'sex_abertura': forms.TimeInput(attrs={'type': 'time'}),
            'sex_fechamento': forms.TimeInput(attrs={'type': 'time'}),
            'sab_abertura': forms.TimeInput(attrs={'type': 'time'}),
            'sab_fechamento': forms.TimeInput(attrs={'type': 'time'}),
            'dom_abertura': forms.TimeInput(attrs={'type': 'time'}),
            'dom_fechamento': forms.TimeInput(attrs={'type': 'time'}),
            'observacoes': forms.Textarea(attrs={'rows': 2, 'id': 'id_obs_cfg'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fname in ['seg_abertura', 'seg_fechamento', 'ter_abertura', 'ter_fechamento',
                      'qua_abertura', 'qua_fechamento', 'qui_abertura', 'qui_fechamento',
                      'sex_abertura', 'sex_fechamento', 'sab_abertura', 'sab_fechamento',
                      'dom_abertura', 'dom_fechamento']:
            if fname in self.fields:
                self.fields[fname].required = False
        aplicar_estilo_campos(self)
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
            'cpf', 'id_vinculo', 'matricula', 'situacao_matricula_1',
            'id_vinculo_acumulacao', 'matricula_acumulacao', 'situacao_matricula_2',
            'cargo_acumulacao', 'disciplina_ingresso_acumulacao', 'funcao_acumulacao', 'ch_total_acumulacao',
            'nome_completo', 'cargo', 'disciplina_ingresso', 'disciplinas_lecionadas',
            'data_admissao', 'data_ci_movimentacao', 'data_ingresso_unidade', 'classificacao',
            'email', 'telefone', 'celular', 'foto', 'ativo', 'observacoes',
        ]
        widgets = {
            'cpf': forms.TextInput(attrs={'placeholder': '00000000000', 'id': 'id_cpf_prof'}),
            'id_vinculo': forms.TextInput(attrs={'placeholder': 'Ex: 40645924/2', 'id': 'id_vinculo_prof'}),
            'matricula': forms.TextInput(attrs={'id': 'id_matricula'}),
            'situacao_matricula_1': forms.Select(attrs={'id': 'id_sit_mat1'}),
            'id_vinculo_acumulacao': forms.TextInput(attrs={'placeholder': 'Ex: 40645924/1', 'id': 'id_vinc_acum'}),
            'matricula_acumulacao': forms.TextInput(attrs={'id': 'id_mat_acum'}),
            'situacao_matricula_2': forms.Select(attrs={'id': 'id_sit_mat2'}),
            'cargo_acumulacao': forms.TextInput(attrs={'id': 'id_cargo_acum'}),
            'disciplina_ingresso_acumulacao': forms.TextInput(attrs={'id': 'id_disc_acum'}),
            'funcao_acumulacao': forms.TextInput(attrs={'id': 'id_func_acum'}),
            'ch_total_acumulacao': forms.NumberInput(attrs={'id': 'id_ch_acum'}),
            'nome_completo': forms.TextInput(attrs={'id': 'id_nome_prof'}),
            'cargo': forms.TextInput(attrs={'id': 'id_cargo'}),
            'disciplina_ingresso': forms.TextInput(attrs={'id': 'id_disc_ing'}),
            'data_admissao': forms.DateInput(attrs={'type': 'date', 'id': 'id_data_adm'}, format='%Y-%m-%d'),
            'data_ci_movimentacao': forms.DateInput(
                attrs={'type': 'date', 'id': 'id_data_ci'}, format='%Y-%m-%d'
            ),
            'data_ingresso_unidade': forms.DateInput(
                attrs={'type': 'date', 'id': 'id_data_ingresso'}, format='%Y-%m-%d'
            ),
            'classificacao': forms.NumberInput(attrs={'min': 1, 'id': 'id_classificacao'}),
            'email': forms.EmailInput(attrs={'id': 'id_email_prof'}),
            'telefone': forms.TextInput(attrs={'placeholder': '(21) 99999-9999', 'id': 'id_tel_prof'}),
            'celular': forms.TextInput(attrs={'placeholder': '(21) 99999-9999', 'id': 'id_cel_prof'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'id': 'id_obs_prof'}),
            'disciplinas_lecionadas': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data_admissao'].required = False
        self.fields['data_ci_movimentacao'].required = False
        self.fields['data_ingresso_unidade'].required = False
        self.fields['data_admissao'].input_formats = ['%Y-%m-%d']
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
        fields = ['unidade', 'ano_letivo', 'dia_semana', 'hora_inicio', 'hora_fim', 'local', 'local_descricao']
        widgets = {
            'unidade': forms.Select(attrs={'id': 'id_unidade_horario'}),
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


class TurmaComponenteForm(forms.ModelForm):
    class Meta:
        model = TurmaComponente
        fields = ['codigo_turma', 'area', 'trilha_nucleo', 'disciplina_nome', 'tempos_requeridos', 'observacoes']
        widgets = {
            'codigo_turma': forms.TextInput(attrs={'placeholder': 'Ex: CEJAS-C1L-080', 'id': 'id_codigo_turma'}),
            'area': forms.TextInput(attrs={'placeholder': 'Ex: Linguagens, Ciências da Natureza', 'id': 'id_area_turma'}),
            'trilha_nucleo': forms.TextInput(attrs={'placeholder': 'Ex: TRILHA DE APROFUNDAMENTO, NÚCLEO INTEGRADOR', 'id': 'id_trilha_turma'}),
            'disciplina_nome': forms.TextInput(attrs={'placeholder': 'Ex: COMPONENTE DE ÁREA 1 LINGUAGENS', 'id': 'id_disc_nome_turma'}),
            'tempos_requeridos': forms.NumberInput(attrs={'min': 1, 'max': 40, 'id': 'id_tempos_turma'}),
            'observacoes': forms.Textarea(attrs={'rows': 2, 'id': 'id_obs_turma'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        aplicar_estilo_campos(self)
