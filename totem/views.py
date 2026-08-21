"""
App: totem
API pública que alimenta o index.html com dados dinâmicos do banco.
Substituirá o arquivo estático dados_escola.js
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from professores.models import Professor, HorarioProfessor
from django.utils import timezone


def view_totem_publico(request):
    """Exibe o Totem de Autoatendimento público (index.html)."""
    return render(request, 'index.html')

# Mapeamento dia semana (slug → texto) para o totem
DIAS_PT = {
    'segunda': 'Segunda-feira',
    'terca': 'Terça-feira',
    'quarta': 'Quarta-feira',
    'quinta': 'Quinta-feira',
    'sexta': 'Sexta-feira',
    'sabado': 'Sábado',
}

LOCAL_PT = {
    'cabine_linguagens': 'Cabine de Linguagens',
    'cabine_matematica': 'Cabine de Matemática',
    'cabine_ciencias_natureza': 'Cabine de Ciências da Natureza',
    'cabine_ciencias_humanas': 'Cabine de Ciências Humanas',
    'auditorio': 'Auditório',
    'secretaria': 'Secretaria',
    'outro': 'Outro',
}


@cache_page(60 * 5)  # Cache de 5 minutos
def view_horarios_totem(request):
    """
    GET /api/totem/horarios/
    Retorna a lista de professores com horários aprovados para o ano atual.
    Formato compatível com o index.html existente.
    """
    ano = int(request.GET.get('ano', timezone.now().year))

    professores = Professor.objects.filter(
        ativo=True
    ).prefetch_related(
        'horarios', 'disciplinas_lecionadas'
    ).order_by('classificacao', 'nome_completo')

    resultado = []
    for prof in professores:
        horarios_aprovados = prof.horarios.filter(
            ano_letivo=ano, aprovado=True
        ).order_by('dia_semana', 'hora_inicio')

        if not horarios_aprovados.exists():
            continue

        disciplinas = list(prof.disciplinas_lecionadas.values_list('nome', flat=True))
        if not disciplinas:
            disciplinas = [prof.get_disciplina_ingresso_display()]

        horarios_lista = []
        for h in horarios_aprovados:
            horarios_lista.append({
                'dia': DIAS_PT.get(h.dia_semana, h.dia_semana),
                'inicio': h.hora_inicio.strftime('%H:%M'),
                'fim': h.hora_fim.strftime('%H:%M'),
                'local': LOCAL_PT.get(h.local, h.local_descricao or h.local),
            })

        resultado.append({
            'nome': prof.nome_completo,
            'foto': prof.foto.url if prof.foto else '',
            'disciplinas': disciplinas,
            'horarios': horarios_lista,
        })

    return JsonResponse({
        'ano': ano,
        'gerado_em': timezone.now().isoformat(),
        'horarioProfessores': resultado,
    })


def view_info_escola(request):
    """
    GET /api/totem/escola/
    Retorna informações gerais da escola (fixas por enquanto).
    """
    return JsonResponse({
        'nome': 'CEJA Professora Rosa Soares',
        'cidade': 'Mesquita - RJ',
        'telefone': '(21) 98161-2512',
        'horarioAtendimento': [
            {'dia': 'Segunda a Quinta', 'horario': '08:30 às 20:30'},
            {'dia': 'Sexta', 'horario': '08:30 às 17:10'},
            {'dia': 'Sábado', 'horario': 'Fechado'},
        ],
        'localAtendimento': 'Secretaria - 2º Andar (Prédio do CIEP Nelson Ramos)',
    })
