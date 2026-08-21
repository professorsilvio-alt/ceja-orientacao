"""Admin do app professores"""
from django.contrib import admin
from .models import Professor, Disciplina, HorarioProfessor


class HorarioInline(admin.TabularInline):
    model = HorarioProfessor
    extra = 0
    fields = ['ano_letivo', 'dia_semana', 'hora_inicio', 'hora_fim', 'local', 'aprovado']


@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = [
        'classificacao', 'nome_completo', 'cargo',
        'disciplina_ingresso', 'data_ingresso_unidade', 'tempo_na_escola', 'ativo'
    ]
    list_filter = ['cargo', 'disciplina_ingresso', 'ativo']
    search_fields = ['nome_completo', 'cpf', 'matricula']
    ordering = ['classificacao', 'nome_completo']
    readonly_fields = ['tempo_na_escola', 'criado_em', 'atualizado_em']
    inlines = [HorarioInline]

    fieldsets = (
        ('Identificação', {
            'fields': ('cpf', 'matricula', 'matricula_acumulacao', 'nome_completo', 'foto')
        }),
        ('Cargo e Disciplinas', {
            'fields': ('cargo', 'disciplina_ingresso', 'disciplinas_lecionadas')
        }),
        ('Movimentação e Classificação', {
            'fields': (
                'classificacao', 'data_ci_movimentacao',
                'data_ingresso_unidade', 'tempo_na_escola'
            )
        }),
        ('Contato', {'fields': ('email', 'telefone')}),
        ('Status', {'fields': ('ativo', 'data_saida', 'observacoes')}),
    )


@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'area', 'cor']
    search_fields = ['nome', 'area']


@admin.register(HorarioProfessor)
class HorarioProfessorAdmin(admin.ModelAdmin):
    list_display = ['professor', 'ano_letivo', 'dia_semana', 'hora_inicio', 'hora_fim', 'local', 'aprovado']
    list_filter = ['ano_letivo', 'dia_semana', 'aprovado']
    search_fields = ['professor__nome_completo']
    list_editable = ['aprovado']
