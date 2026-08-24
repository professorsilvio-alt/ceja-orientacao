"""Formulários do app agenda"""
from django import forms
from django.utils import timezone
from .models import RegistroPresenca, ReservaAuditorio


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


class RegistroPresencaForm(forms.ModelForm):
    class Meta:
        model = RegistroPresenca
        fields = [
            'tipo_funcionario', 'professor_id', 'administrativo_id', 'terceirizado_id',
            'data', 'tipo', 'hora_chegada', 'hora_saida',
            'justificado', 'motivo', 'observacoes',
        ]
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date', 'id': 'id_data_presenca'}, format='%Y-%m-%d'),
            'hora_chegada': forms.TimeInput(attrs={'type': 'time', 'id': 'id_hora_chegada'}),
            'hora_saida': forms.TimeInput(attrs={'type': 'time', 'id': 'id_hora_saida'}),
            'motivo': forms.TextInput(attrs={'id': 'id_motivo_presenca', 'placeholder': 'Motivo da ocorrência'}),
            'observacoes': forms.Textarea(attrs={'rows': 2, 'id': 'id_obs_presenca'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data'].initial = timezone.now().date()
        self.fields['data'].input_formats = ['%Y-%m-%d']
        self.fields['professor_id'].required = False
        self.fields['administrativo_id'].required = False
        self.fields['terceirizado_id'].required = False
        aplicar_estilo_campos(self)

    def clean(self):
        cleaned = super().clean()
        tipo = cleaned.get('tipo_funcionario')
        if tipo == 'professor' and not cleaned.get('professor_id'):
            raise forms.ValidationError('Selecione o professor.')
        if tipo == 'administrativo' and not cleaned.get('administrativo_id'):
            raise forms.ValidationError('Selecione o funcionário administrativo.')
        if tipo == 'terceirizado' and not cleaned.get('terceirizado_id'):
            raise forms.ValidationError('Selecione o funcionário terceirizado.')
        return cleaned


class ReservaAuditorioForm(forms.ModelForm):
    class Meta:
        model = ReservaAuditorio
        fields = [
            'titulo', 'tipo', 'descricao',
            'data', 'hora_inicio', 'hora_fim',
            'responsavel', 'turma_publico', 'capacidade_prevista',
            'status', 'observacoes',
        ]
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date', 'id': 'id_data_reserva'}, format='%Y-%m-%d'),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time', 'id': 'id_hora_inicio_r'}),
            'hora_fim': forms.TimeInput(attrs={'type': 'time', 'id': 'id_hora_fim_r'}),
            'titulo': forms.TextInput(attrs={'id': 'id_titulo_reserva', 'placeholder': 'Nome do evento / atividade'}),
            'responsavel': forms.TextInput(attrs={'id': 'id_responsavel', 'placeholder': 'Nome do responsável'}),
            'turma_publico': forms.TextInput(attrs={'id': 'id_turma', 'placeholder': 'Ex: Turma A, EJA Noturno...'}),
            'descricao': forms.Textarea(attrs={'rows': 3, 'id': 'id_descricao_reserva'}),
            'observacoes': forms.Textarea(attrs={'rows': 2, 'id': 'id_obs_reserva'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data'].initial = timezone.now().date()
        self.fields['data'].input_formats = ['%Y-%m-%d']
        aplicar_estilo_campos(self)

    def clean(self):
        cleaned = super().clean()
        data = cleaned.get('data')
        inicio = cleaned.get('hora_inicio')
        fim = cleaned.get('hora_fim')

        if inicio and fim and inicio >= fim:
            raise forms.ValidationError('O horário de início deve ser anterior ao horário de fim.')

        # Verifica conflito de horário no auditório
        if data and inicio and fim:
            conflito_qs = ReservaAuditorio.objects.filter(
                data=data,
                status__in=['confirmada', 'pendente'],
                hora_inicio__lt=fim,
                hora_fim__gt=inicio,
            )
            if self.instance.pk:
                conflito_qs = conflito_qs.exclude(pk=self.instance.pk)
            if conflito_qs.exists():
                conflito = conflito_qs.first()
                raise forms.ValidationError(
                    f'Conflito de horário! O auditório já está reservado para "{conflito.titulo}" '
                    f'das {conflito.hora_inicio:%H:%M} às {conflito.hora_fim:%H:%M}.'
                )
        return cleaned
