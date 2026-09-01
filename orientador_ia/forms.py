from django import forms
from .models import DocumentoCerebro


class DocumentoCerebroForm(forms.ModelForm):
    """
    Formulário para cadastro e upload de documentos no Cérebro (Beth).
    """
    class Meta:
        model = DocumentoCerebro
        fields = [
            'titulo',
            'categoria',
            'numero_normativa',
            'ano_referencia',
            'arquivo',
            'conteudo_extraido',
            'status',
            'documento_substituido',
            'observacoes'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Regimento Escolar 2026, Portaria SEEDUC nº 45...'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select'
            }),
            'numero_normativa': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Portaria nº 123/2026, CI nº 08'
            }),
            'ano_referencia': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 2026'
            }),
            'arquivo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.docx,.doc,.xlsx,.xls,.csv,.txt,.mp3,.wav,.m4a,.ogg,.png,.jpg,.jpeg'
            }),
            'conteudo_extraido': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Se não tiver arquivo, digite ou cole aqui o texto da lei, resolução, nota ou instrução...'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'documento_substituido': forms.Select(attrs={
                'class': 'form-select'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Observações adicionais para a equipe de direção...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar documentos para substituição
        self.fields['documento_substituido'].queryset = DocumentoCerebro.objects.all().order_by('-criado_em')
        self.fields['documento_substituido'].empty_label = "-- Nenhum (Documento Novo / Independente) --"
        self.fields['conteudo_extraido'].required = False
        self.fields['arquivo'].required = False
