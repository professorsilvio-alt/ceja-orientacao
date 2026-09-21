from django import forms
from django.db import models
from .models import ProcessoSEI, AndamentoProcesso
from professores.models import Professor
from funcionarios.models import FuncionarioAdministrativo


class ProcessoSEIForm(forms.ModelForm):
    professores_relacionados = forms.ModelMultipleChoiceField(
        queryset=Professor.objects.filter(ativo=True).order_by('nome_completo'),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Professores Relacionados"
    )
    administrativos_relacionados = forms.ModelMultipleChoiceField(
        queryset=FuncionarioAdministrativo.objects.filter(ativo=True).order_by('nome_completo'),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Funcionários Administrativos Relacionados"
    )

    class Meta:
        model = ProcessoSEI
        fields = [
            'numero_sei',
            'titulo',
            'tipo',
            'palavras_chave',
            'descricao',
            'interessado',
            'setor_atual',
            'status',
            'prioridade',
            'data_abertura',
            'link_sei',
            'professores_relacionados',
            'administrativos_relacionados',
        ]
        widgets = {
            'tipo': forms.Select(attrs={
                'class': 'form-select',
            }),
            'numero_sei': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: SEI-030029/000123/2026',
                'autocomplete': 'off',
                'required': True,
            }),
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Solicitação de Reparo no Telhado do CEJA',
                'required': True,
            }),
            'palavras_chave': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Infraestrutura, Telhado, Obras, Emergência',
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descreva detalhadamente do que se trata o processo, histórico inicial, objetivos e observações importantes...',
            }),
            'interessado': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Direção Geral / CEJA Profa Rosa Soares',
            }),
            'setor_atual': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: SEEDUC/SUBEST, DIESP, Regional Metropolitana I',
            }),
            'status': forms.Select(attrs={
                'class': 'form-select',
            }),
            'prioridade': forms.Select(attrs={
                'class': 'form-select',
            }),
            'data_abertura': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'link_sei': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://sei.rj.gov.br/... (opcional)',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Se estiver editando e houver servidores já vinculados (mesmo inativos), garantir que estejam no queryset
        if self.instance and self.instance.pk:
            p_ids = list(self.instance.professores_relacionados.values_list('pk', flat=True))
            if p_ids:
                self.fields['professores_relacionados'].queryset = Professor.objects.filter(
                    models.Q(ativo=True) | models.Q(pk__in=p_ids)
                ).distinct().order_by('nome_completo')

            a_ids = list(self.instance.administrativos_relacionados.values_list('pk', flat=True))
            if a_ids:
                self.fields['administrativos_relacionados'].queryset = FuncionarioAdministrativo.objects.filter(
                    models.Q(ativo=True) | models.Q(pk__in=a_ids)
                ).distinct().order_by('nome_completo')

    def clean_numero_sei(self):
        numero = self.cleaned_data.get('numero_sei', '').strip()
        return numero


class AndamentoProcessoForm(forms.ModelForm):
    class Meta:
        model = AndamentoProcesso
        fields = ['data', 'setor', 'descricao']
        widgets = {
            'data': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True,
            }),
            'setor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Encaminhado para DIESP / Resposta da SEEDUC',
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Detalhes do andamento, parecer, despacho ou providência tomada...',
                'required': True,
            }),
        }
