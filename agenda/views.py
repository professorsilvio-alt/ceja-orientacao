"""Views do app agenda"""
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db import transaction
from django.urls import reverse
from datetime import date, timedelta, time
from usuarios.views import (
    diretor_required, coordenador_ou_diretor_required,
    quadro_horarios_required, verificar_primeiro_acesso
)
from .models import RegistroPresenca, ReservaAuditorio, AgendaAtendimentoProfessor
from .forms import (
    RegistroPresencaForm, ReservaAuditorioForm,
    AgendamentoPublicoAuditorioForm, AgendaAtendimentoProfessorForm
)
from professores.models import Professor
from funcionarios.models import FuncionarioAdministrativo, FuncionarioTerceirizado


# ── PRESENÇA ────────────────────────────────────────────────

@diretor_required
def view_listar_presencas(request):
    """Listagem e filtros de registros de presença."""
    data_inicio = request.GET.get('data_inicio', (timezone.now().date() - timedelta(days=30)).isoformat())
    data_fim = request.GET.get('data_fim', timezone.now().date().isoformat())
    tipo = request.GET.get('tipo', '')
    nome = request.GET.get('nome', '').strip()

    registros = RegistroPresenca.objects.filter(
        data__gte=data_inicio,
        data__lte=data_fim,
    ).order_by('-data', 'nome_funcionario')

    if tipo:
        registros = registros.filter(tipo=tipo)

    if nome:
        registros = registros.filter(nome_funcionario__icontains=nome)

    return render(request, 'agenda/listar_presencas.html', {
        'registros': registros,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'tipo_filtro': tipo,
        'nome_filtro': nome,
        'hoje': timezone.now().date().isoformat(),
    })


@diretor_required
def view_novo_registro(request):
    """Registra uma nova ocorrência (falta/atraso/ausência)."""
    # Listas para o select dinâmico no template
    professores = Professor.objects.filter(ativo=True).order_by('nome_completo')
    administrativos = FuncionarioAdministrativo.objects.filter(ativo=True).order_by('nome_completo')
    terceirizados = FuncionarioTerceirizado.objects.filter(ativo=True).order_by('nome_completo')

    form = RegistroPresencaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        registro = form.save(commit=False)
        registro.registrado_por = request.user

        # Preenche o nome em cache
        func = registro.get_funcionario()
        if func:
            registro.nome_funcionario = func.nome_completo
        registro.save()
        registro.sincronizar_banco_horas()

        messages.success(request, f'Registro de {registro.get_tipo_display()} cadastrado com sucesso.')
        return redirect('listar_presencas')

    return render(request, 'agenda/form_presenca.html', {
        'form': form,
        'professores': professores,
        'administrativos': administrativos,
        'terceirizados': terceirizados,
        'titulo': 'Novo Registro de Presença',
    })


@diretor_required
def view_editar_registro(request, pk):
    registro = get_object_or_404(RegistroPresenca, pk=pk)
    professores = Professor.objects.filter(ativo=True).order_by('nome_completo')
    administrativos = FuncionarioAdministrativo.objects.filter(ativo=True).order_by('nome_completo')
    terceirizados = FuncionarioTerceirizado.objects.filter(ativo=True).order_by('nome_completo')

    form = RegistroPresencaForm(request.POST or None, instance=registro)
    if request.method == 'POST' and form.is_valid():
        reg = form.save(commit=False)
        func = reg.get_funcionario()
        if func:
            reg.nome_funcionario = func.nome_completo
        reg.save()
        reg.sincronizar_banco_horas()
        messages.success(request, 'Registro de presença e banco de horas atualizados com sucesso.')
        return redirect('listar_presencas')

    return render(request, 'agenda/form_presenca.html', {
        'form': form,
        'professores': professores,
        'administrativos': administrativos,
        'terceirizados': terceirizados,
        'titulo': f'Editar: {registro}',
        'registro': registro,
    })


@diretor_required
def view_excluir_registro(request, pk):
    registro = get_object_or_404(RegistroPresenca, pk=pk)
    if request.method == 'POST':
        registro.delete()
        messages.success(request, 'Registro removido.')
    return redirect('listar_presencas')


# ── AUDITÓRIO ───────────────────────────────────────────────

@login_required
@verificar_primeiro_acesso
def view_agenda_auditorio(request):
    """Calendário visual do auditório."""
    hoje = timezone.now().date()
    mes = int(request.GET.get('mes', hoje.month))
    ano = int(request.GET.get('ano', hoje.year))

    # Primeiro e último dia do mês
    primeiro_dia = date(ano, mes, 1)
    if mes == 12:
        ultimo_dia = date(ano + 1, 1, 1) - timedelta(days=1)
    else:
        ultimo_dia = date(ano, mes + 1, 1) - timedelta(days=1)

    reservas = ReservaAuditorio.objects.filter(
        data__gte=primeiro_dia,
        data__lte=ultimo_dia,
    ).order_by('data', 'hora_inicio')

    # Próximas reservas (para o painel lateral)
    proximas = ReservaAuditorio.objects.filter(
        data__gte=hoje,
        status__in=['confirmada', 'pendente'],
    ).order_by('data', 'hora_inicio')[:10]

    # Mês anterior e próximo para navegação
    if mes == 1:
        mes_ant, ano_ant = 12, ano - 1
    else:
        mes_ant, ano_ant = mes - 1, ano
    if mes == 12:
        mes_prox, ano_prox = 1, ano + 1
    else:
        mes_prox, ano_prox = mes + 1, ano

    MESES_NOMES = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]

    import json
    reservas_data = []
    for r in reservas:
        reservas_data.append({
            'id': r.id,
            'titulo': r.titulo,
            'tipo': r.tipo,
            'data': r.data.isoformat(),
            'hora_inicio': r.hora_inicio.strftime('%H:%M'),
            'hora_fim': r.hora_fim.strftime('%H:%M'),
            'responsavel': r.responsavel,
            'status': r.status,
        })
    reservas_json = json.dumps(reservas_data)

    return render(request, 'agenda/auditorio.html', {
        'reservas': reservas,
        'reservas_json': reservas_json,
        'proximas': proximas,
        'mes': mes,
        'ano': ano,
        'nome_mes': MESES_NOMES[mes - 1],
        'hoje': hoje,
        'primeiro_dia': primeiro_dia,
        'ultimo_dia': ultimo_dia,
        'mes_ant': mes_ant, 'ano_ant': ano_ant,
        'mes_prox': mes_prox, 'ano_prox': ano_prox,
        'is_diretor': request.user.perfil in ['diretor', 'coordenador_pedagogico'] or request.user.is_superuser,
        'link_publico_url': request.build_absolute_uri(reverse('agenda_auditorio_publico')),
    })


@coordenador_ou_diretor_required
def view_nova_reserva(request):
    form = ReservaAuditorioForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        reserva = form.save(commit=False)
        reserva.criado_por = request.user
        reserva.save()
        messages.success(request, f'Reserva "{reserva.titulo}" cadastrada!')
        return redirect('agenda_auditorio')
    return render(request, 'agenda/form_reserva.html', {
        'form': form, 'titulo': 'Nova Reserva do Auditório'
    })


@coordenador_ou_diretor_required
def view_editar_reserva(request, pk):
    reserva = get_object_or_404(ReservaAuditorio, pk=pk)
    form = ReservaAuditorioForm(request.POST or None, instance=reserva)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Reserva atualizada.')
        return redirect('agenda_auditorio')
    return render(request, 'agenda/form_reserva.html', {
        'form': form,
        'titulo': f'Editar: {reserva.titulo}',
        'reserva': reserva,
    })


@coordenador_ou_diretor_required
def view_excluir_reserva(request, pk):
    reserva = get_object_or_404(ReservaAuditorio, pk=pk)
    if request.method == 'POST':
        reserva.delete()
        messages.success(request, 'Reserva removida.')
    return redirect('agenda_auditorio')


def view_reservas_json(request):
    """Retorna reservas do mês como JSON para o calendário dinâmico."""
    mes = int(request.GET.get('mes', timezone.now().month))
    ano = int(request.GET.get('ano', timezone.now().year))
    primeiro_dia = date(ano, mes, 1)
    if mes == 12:
        ultimo_dia = date(ano + 1, 1, 1) - timedelta(days=1)
    else:
        ultimo_dia = date(ano, mes + 1, 1) - timedelta(days=1)

    reservas = ReservaAuditorio.objects.filter(
        data__gte=primeiro_dia, data__lte=ultimo_dia
    ).values('id', 'titulo', 'tipo', 'data', 'hora_inicio', 'hora_fim', 'responsavel', 'status')

    data = []
    for r in reservas:
        data.append({
            'id': r['id'],
            'titulo': r['titulo'],
            'tipo': r['tipo'],
            'data': r['data'].isoformat(),
            'hora_inicio': r['hora_inicio'].strftime('%H:%M'),
            'hora_fim': r['hora_fim'].strftime('%H:%M'),
            'responsavel': r['responsavel'],
            'status': r['status'],
        })
    return JsonResponse({'reservas': data})


def view_auditorio_publico(request):
    """
    Página pública para visualização e agendamento do auditório do CEJA.
    Não requer autenticação.
    Garante não-concomitância de horários e exibe ocupação em tempo real.
    """
    hoje = timezone.now().date()
    mes = int(request.GET.get('mes', hoje.month))
    ano = int(request.GET.get('ano', hoje.year))

    primeiro_dia = date(ano, mes, 1)
    if mes == 12:
        ultimo_dia = date(ano + 1, 1, 1) - timedelta(days=1)
    else:
        ultimo_dia = date(ano, mes + 1, 1) - timedelta(days=1)

    # Reservas ativas do mês
    reservas = ReservaAuditorio.objects.filter(
        data__gte=primeiro_dia,
        data__lte=ultimo_dia,
        status__in=['confirmada', 'pendente'],
    ).order_by('data', 'hora_inicio')

    # Próximas reservas a partir de hoje
    proximas = ReservaAuditorio.objects.filter(
        data__gte=hoje,
        status__in=['confirmada', 'pendente'],
    ).order_by('data', 'hora_inicio')[:15]

    # Navegação entre meses
    if mes == 1:
        mes_ant, ano_ant = 12, ano - 1
    else:
        mes_ant, ano_ant = mes - 1, ano

    if mes == 12:
        mes_prox, ano_prox = 1, ano + 1
    else:
        mes_prox, ano_prox = mes + 1, ano

    MESES_NOMES = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]

    reservas_data = []
    for r in reservas:
        reservas_data.append({
            'id': r.id,
            'titulo': r.titulo,
            'tipo': r.tipo,
            'tipo_display': r.get_tipo_display(),
            'data': r.data.isoformat(),
            'hora_inicio': r.hora_inicio.strftime('%H:%M'),
            'hora_fim': r.hora_fim.strftime('%H:%M'),
            'responsavel': r.responsavel,
            'turma_publico': r.turma_publico,
            'status': r.status,
            'badge_color': r.badge_color,
        })
    reservas_json = json.dumps(reservas_data)

    form = AgendamentoPublicoAuditorioForm(request.POST or None)
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('is_ajax') == '1'

    if request.method == 'POST':
        if form.is_valid():
            with transaction.atomic():
                data_agendada = form.cleaned_data['data']
                inicio = form.cleaned_data['hora_inicio']
                fim = form.cleaned_data['hora_fim']

                # Bloqueio concorrente (select_for_update)
                conflitos = ReservaAuditorio.objects.select_for_update().filter(
                    data=data_agendada,
                    status__in=['confirmada', 'pendente'],
                    hora_inicio__lt=fim,
                    hora_fim__gt=inicio,
                )
                if conflitos.exists():
                    c = conflitos.first()
                    erro_msg = (
                        f'Conflito! O auditório já está agendado em {data_agendada.strftime("%d/%m/%Y")} '
                        f'das {c.hora_inicio:%H:%M} às {c.hora_fim:%H:%M} para "{c.titulo}". '
                        f'Por favor, selecione outro horário.'
                    )
                    form.add_error(None, erro_msg)
                    if is_ajax:
                        return JsonResponse({'success': False, 'mensagem': erro_msg})
                else:
                    reserva = form.save()
                    if is_ajax:
                        return JsonResponse({
                            'success': True,
                            'mensagem': f'Agendamento confirmado com sucesso para "{reserva.titulo}"!',
                            'reserva': {
                                'id': reserva.id,
                                'titulo': reserva.titulo,
                                'data': reserva.data.strftime('%d/%m/%Y'),
                                'hora_inicio': reserva.hora_inicio.strftime('%H:%M'),
                                'hora_fim': reserva.hora_fim.strftime('%H:%M'),
                                'responsavel': reserva.responsavel,
                                'tipo_display': reserva.get_tipo_display(),
                            }
                        })
                    messages.success(
                        request,
                        f'Agendamento confirmado com sucesso! Auditório reservado para "{reserva.titulo}" '
                        f'no dia {reserva.data.strftime("%d/%m/%Y")} das {reserva.hora_inicio.strftime("%H:%M")} às {reserva.hora_fim.strftime("%H:%M")}.'
                    )
                    return redirect('agenda_auditorio_publico')
        else:
            if is_ajax:
                erros = []
                for campo, lista in form.errors.items():
                    for err in lista:
                        erros.append(err)
                return JsonResponse({'success': False, 'mensagem': " ".join(erros)})

    return render(request, 'agenda/publico_auditorio.html', {
        'form': form,
        'reservas': reservas,
        'reservas_json': reservas_json,
        'proximas': proximas,
        'mes': mes,
        'ano': ano,
        'nome_mes': MESES_NOMES[mes - 1],
        'hoje': hoje,
        'primeiro_dia': primeiro_dia,
        'ultimo_dia': ultimo_dia,
        'mes_ant': mes_ant, 'ano_ant': ano_ant,
        'mes_prox': mes_prox, 'ano_prox': ano_prox,
    })


def view_verificar_disponibilidade_json(request):
    """
    Verifica se uma faixa de horário no auditório está livre.
    Retorna JSON com status de disponibilidade e detalhes do conflito, se houver.
    """
    data_str = request.GET.get('data')
    inicio_str = request.GET.get('hora_inicio')
    fim_str = request.GET.get('hora_fim')

    if not (data_str and inicio_str and fim_str):
        return JsonResponse({'disponivel': True, 'mensagem': ''})

    try:
        data = date.fromisoformat(data_str)
        if data < timezone.now().date():
            return JsonResponse({
                'disponivel': False,
                'mensagem': 'A data não pode ser anterior a hoje.'
            })

        h_i, m_i = [int(x) for x in inicio_str.split(':')[:2]]
        h_f, m_f = [int(x) for x in fim_str.split(':')[:2]]
        inicio = time(h_i, m_i)
        fim = time(h_f, m_f)

        if inicio >= fim:
            return JsonResponse({
                'disponivel': False,
                'mensagem': 'O horário de início deve ser anterior ao de término.'
            })

        conflitos = ReservaAuditorio.objects.filter(
            data=data,
            status__in=['confirmada', 'pendente'],
            hora_inicio__lt=fim,
            hora_fim__gt=inicio,
        )

        if conflitos.exists():
            c = conflitos.first()
            return JsonResponse({
                'disponivel': False,
                'conflito': True,
                'mensagem': f'Ocupado: "{c.titulo}" ({c.hora_inicio.strftime("%H:%M")} às {c.hora_fim.strftime("%H:%M")}) — {c.responsavel}'
            })

        return JsonResponse({
            'disponivel': True,
            'conflito': False,
            'mensagem': 'Horário 100% disponível no auditório!'
        })
    except Exception as e:
        return JsonResponse({'disponivel': True, 'mensagem': ''})


# ── AGENDA DE AUSÊNCIAS E REPOSIÇÕES DE AULAS (PROFESSORES / TOTEM) ──

def garantir_seed_atendimentos_iniciais():
    """
    Popula inicialmente a tabela de Ausências e Reposições com os eventos
    de Novembro/Dezembro de 2026 da agenda da escola caso esteja vazia.
    """
    try:
        if AgendaAtendimentoProfessor.objects.exists():
            return
        eventos_iniciais = [
            # Semana 1 de Novembro 2026
            ('ausencia', 'Prof. Vitor', 'Matemática', date(2026, 11, 3), time(18, 0), 'Não haverá atendimento com o Prof. Vitor (Matemática)'),
            ('ausencia', 'Prof. Fernando', 'Filosofia & Sociologia', date(2026, 11, 4), time(8, 50), 'Não haverá atendimento com o Prof. Fernando (Filosofia & Sociologia)'),
            ('ausencia', 'Prof. Rafael Maia', 'Filosofia & Sociologia', date(2026, 11, 4), time(13, 0), 'Não haverá atendimento com o Prof. Rafael Maia (Filosofia & Sociologia)'),
            ('ausencia', 'Prof. Fernando', 'Filosofia & Sociologia', date(2026, 11, 5), time(8, 50), 'Não haverá atendimento com o Prof. Fernando (Filosofia & Sociologia)'),
            ('ausencia', 'Prof. Vitor', 'Matemática', date(2026, 11, 6), time(8, 50), 'Não haverá atendimento com o Prof. Vitor (Matemática)'),
            ('ausencia', 'Prof. Elázaro', 'Biologia', date(2026, 11, 6), time(8, 50), 'Não haverá atendimento com o professor Elázaro (Biologia)'),
            # Semana 2 de Novembro 2026
            ('ausencia', 'Prof. Vitor', 'Matemática', date(2026, 11, 10), time(18, 0), 'Não haverá atendimento com o Prof. Vitor (Matemática)'),
            ('ausencia', 'Prof. Fernando', 'Filosofia & Sociologia', date(2026, 11, 11), time(8, 50), 'Não haverá atendimento com o Prof. Fernando (Filosofia & Sociologia)'),
            ('ausencia', 'Prof. Fernando', 'Filosofia & Sociologia', date(2026, 11, 12), time(8, 50), 'Não haverá atendimento com o Prof. Fernando (Filosofia & Sociologia)'),
            ('reposicao', 'Prof. Carlos Laurindo', 'História', date(2026, 11, 12), time(17, 10), 'Reposição de atendimento com o Prof. Carlos Laurindo (História)'),
            ('ausencia', 'Prof. Vitor', 'Matemática', date(2026, 11, 13), time(8, 50), 'Não haverá atendimento com o Prof. Vitor (Matemática)'),
            # Semana 3 de Novembro 2026
            ('ausencia', 'Prof. Fernando', 'Filosofia & Sociologia', date(2026, 11, 18), time(8, 50), 'Não haverá atendimento com o Prof. Fernando (Filosofia & Sociologia)'),
            ('ausencia', 'Prof. Mário', 'História', date(2026, 11, 18), time(13, 50), 'Não haverá atendimento com o professor Mário (História)'),
            ('ausencia', 'Prof. Fernando', 'Filosofia & Sociologia', date(2026, 11, 19), time(8, 50), 'Não haverá atendimento com o Prof. Fernando (Filosofia & Sociologia)'),
            ('ausencia', 'Prof. Carlos Laurindo', 'História', date(2026, 11, 19), time(12, 10), 'Não haverá atendimento com o Prof. Carlos Laurindo (História)'),
            # Semana 4 de Novembro 2026
            ('ausencia', 'Prof.ª Viviane', 'Química', date(2026, 11, 23), time(8, 50), 'Não haverá atendimento com a professora Viviane (Química)'),
            ('reposicao', 'Prof. Mário', 'História', date(2026, 11, 23), time(12, 10), 'Reposição de atendimento com o Prof. Mário (História)'),
            ('ausencia', 'Prof. Fernando', 'Filosofia & Sociologia', date(2026, 11, 25), time(8, 50), 'Não haverá atendimento com o Prof. Fernando (Filosofia & Sociologia)'),
            ('ausencia', 'Prof. Fernando', 'Filosofia & Sociologia', date(2026, 11, 26), time(8, 50), 'Não haverá atendimento com o Prof. Fernando (Filosofia & Sociologia)'),
            ('reposicao', 'Prof. Carlos Laurindo', 'História', date(2026, 11, 26), time(17, 10), 'Reposição de atendimento com o Prof. Carlos Laurindo (História)'),
            # Primeira semana de Dezembro 2026
            ('ausencia', 'Prof. Fernando', 'Filosofia & Sociologia', date(2026, 12, 2), time(8, 50), 'Não haverá atendimento com o Prof. Fernando (Filosofia & Sociologia)'),
            ('ausencia', 'Prof. Fernando', 'Filosofia & Sociologia', date(2026, 12, 3), time(8, 50), 'Não haverá atendimento com o Prof. Fernando (Filosofia & Sociologia)'),
        ]
        objs = [
            AgendaAtendimentoProfessor(
                tipo=tp,
                nome_professor=prof,
                disciplina=disc,
                data=dt,
                hora_inicio=hr,
                titulo=tit,
                visivel_totem=True
            )
            for tp, prof, disc, dt, hr, tit in eventos_iniciais
        ]
        AgendaAtendimentoProfessor.objects.bulk_create(objs)
    except Exception:
        pass


@quadro_horarios_required
@verificar_primeiro_acesso
def view_agenda_atendimentos(request):
    """
    Calendário visual de Ausências e Reposições de Aulas dos Professores.
    Acesso exclusivo para Direção, Coordenação Pedagógica e Orientação Educacional.
    """
    garantir_seed_atendimentos_iniciais()

    hoje = timezone.now().date()
    mes = int(request.GET.get('mes', hoje.month))
    ano = int(request.GET.get('ano', hoje.year))
    tipo_filtro = request.GET.get('tipo', '').strip()

    primeiro_dia = date(ano, mes, 1)
    if mes == 12:
        ultimo_dia = date(ano + 1, 1, 1) - timedelta(days=1)
    else:
        ultimo_dia = date(ano, mes + 1, 1) - timedelta(days=1)

    eventos_qs = AgendaAtendimentoProfessor.objects.filter(
        data__gte=primeiro_dia,
        data__lte=ultimo_dia,
    ).order_by('data', 'hora_inicio')

    if tipo_filtro:
        eventos_qs = eventos_qs.filter(tipo=tipo_filtro)

    proximos = AgendaAtendimentoProfessor.objects.filter(
        data__gte=hoje,
        visivel_totem=True,
    ).order_by('data', 'hora_inicio')[:24]

    if mes == 1:
        mes_ant, ano_ant = 12, ano - 1
    else:
        mes_ant, ano_ant = mes - 1, ano
    if mes == 12:
        mes_prox, ano_prox = 1, ano + 1
    else:
        mes_prox, ano_prox = mes + 1, ano

    MESES_NOMES = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]

    eventos_data = []
    for ev in eventos_qs:
        eventos_data.append({
            'id': ev.id,
            'tipo': ev.tipo,
            'tipo_display': ev.get_tipo_display(),
            'nome_professor': ev.nome_professor,
            'disciplina': ev.disciplina,
            'titulo': ev.titulo,
            'data': ev.data.isoformat(),
            'hora_inicio': ev.hora_inicio.strftime('%H:%M'),
            'hora_fim': ev.hora_fim.strftime('%H:%M') if ev.hora_fim else '',
            'observacoes': ev.observacoes,
            'visivel_totem': ev.visivel_totem,
        })

    total_ausencias = eventos_qs.filter(tipo='ausencia').count()
    total_reposicoes = eventos_qs.filter(tipo='reposicao').count()

    can_edit = (
        request.user.perfil in ['diretor', 'coordenador_pedagogico', 'orientador_educacional']
        or request.user.is_superuser
    )

    return render(request, 'agenda/atendimentos_professores.html', {
        'eventos': eventos_qs,
        'eventos_json': json.dumps(eventos_data),
        'proximos': proximos,
        'total_ausencias': total_ausencias,
        'total_reposicoes': total_reposicoes,
        'tipo_filtro': tipo_filtro,
        'mes': mes,
        'ano': ano,
        'nome_mes': MESES_NOMES[mes - 1],
        'hoje': hoje,
        'primeiro_dia': primeiro_dia,
        'ultimo_dia': ultimo_dia,
        'mes_ant': mes_ant, 'ano_ant': ano_ant,
        'mes_prox': mes_prox, 'ano_prox': ano_prox,
        'can_edit': can_edit,
    })


@quadro_horarios_required
@verificar_primeiro_acesso
def view_novo_atendimento_professor(request):
    """Cadastra uma ausência ou reposição de atendimento de professor (com opção de repetição semanal)."""
    professores = Professor.objects.filter(ativo=True).prefetch_related('disciplinas_lecionadas').order_by('nome_completo')
    form = AgendaAtendimentoProfessorForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        aviso = form.save(commit=False)
        aviso.criado_por = request.user
        aviso.save()

        repetir = form.cleaned_data.get('repetir_semanalmente')
        ate_data = form.cleaned_data.get('repetir_ate_data')
        criados_extras = 0

        if repetir:
            data_base = aviso.data
            if not ate_data:
                # Por padrão repete até o final do mês da data selecionada
                if data_base.month == 12:
                    ate_data = date(data_base.year + 1, 1, 1) - timedelta(days=1)
                else:
                    ate_data = date(data_base.year, data_base.month + 1, 1) - timedelta(days=1)

            proxima_data = data_base + timedelta(days=7)
            while proxima_data <= ate_data and criados_extras < 24:
                AgendaAtendimentoProfessor.objects.create(
                    tipo=aviso.tipo,
                    professor=aviso.professor,
                    nome_professor=aviso.nome_professor,
                    disciplina=aviso.disciplina,
                    data=proxima_data,
                    hora_inicio=aviso.hora_inicio,
                    hora_fim=aviso.hora_fim,
                    titulo=aviso.titulo,
                    observacoes=aviso.observacoes,
                    visivel_totem=aviso.visivel_totem,
                    criado_por=request.user,
                )
                criados_extras += 1
                proxima_data += timedelta(days=7)

        if criados_extras > 0:
            messages.success(
                request,
                f'Aviso "{aviso.titulo}" registrado com sucesso (+{criados_extras} repetições semanais criadas)!'
            )
        else:
            messages.success(request, f'Aviso "{aviso.titulo}" registrado com sucesso e já visível no Totem!')
        return redirect(f"{reverse('agenda_atendimentos')}?mes={aviso.data.month}&ano={aviso.data.year}")

    # Mapa de professores para autopreenchimento no JS
    profs_js = []
    for p in professores:
        discs = list(p.disciplinas_lecionadas.values_list('nome', flat=True))
        disc_str = ' & '.join(discs) if discs else (p.disciplina_ingresso or '')
        primeiro_nome = p.nome_completo.split()[0]
        prefixo = 'Prof.ª' if (p.sexo and p.sexo.upper().startswith('F')) else 'Prof.'
        profs_js.append({
            'id': p.id,
            'nome_completo': p.nome_completo,
            'nome_curto': f'{prefixo} {primeiro_nome}',
            'disciplina': disc_str,
        })

    return render(request, 'agenda/form_atendimento_professor.html', {
        'form': form,
        'professores': professores,
        'profs_json': json.dumps(profs_js),
        'titulo': 'Registrar Ausência ou Reposição de Aula',
    })


@quadro_horarios_required
@verificar_primeiro_acesso
def view_editar_atendimento_professor(request, pk):
    aviso = get_object_or_404(AgendaAtendimentoProfessor, pk=pk)
    professores = Professor.objects.filter(ativo=True).prefetch_related('disciplinas_lecionadas').order_by('nome_completo')
    form = AgendaAtendimentoProfessorForm(request.POST or None, instance=aviso)

    if request.method == 'POST' and form.is_valid():
        aviso_salvo = form.save()
        messages.success(request, 'Registro atualizado com sucesso!')
        return redirect(f"{reverse('agenda_atendimentos')}?mes={aviso_salvo.data.month}&ano={aviso_salvo.data.year}")

    profs_js = []
    for p in professores:
        discs = list(p.disciplinas_lecionadas.values_list('nome', flat=True))
        disc_str = ' & '.join(discs) if discs else (p.disciplina_ingresso or '')
        primeiro_nome = p.nome_completo.split()[0]
        prefixo = 'Prof.ª' if (p.sexo and p.sexo.upper().startswith('F')) else 'Prof.'
        profs_js.append({
            'id': p.id,
            'nome_completo': p.nome_completo,
            'nome_curto': f'{prefixo} {primeiro_nome}',
            'disciplina': disc_str,
        })

    return render(request, 'agenda/form_atendimento_professor.html', {
        'form': form,
        'professores': professores,
        'profs_json': json.dumps(profs_js),
        'titulo': f'Editar: {aviso.titulo}',
        'aviso': aviso,
    })


@quadro_horarios_required
@verificar_primeiro_acesso
def view_excluir_atendimento_professor(request, pk):
    aviso = get_object_or_404(AgendaAtendimentoProfessor, pk=pk)
    mes, ano = aviso.data.month, aviso.data.year
    if request.method == 'POST':
        aviso.delete()
        messages.success(request, 'Aviso removido da agenda e do Totem.')
    return redirect(f"{reverse('agenda_atendimentos')}?mes={mes}&ano={ano}")


def view_atendimentos_json(request):
    """Retorna os avisos de ausência e reposição do mês em JSON."""
    garantir_seed_atendimentos_iniciais()
    mes = int(request.GET.get('mes', timezone.now().month))
    ano = int(request.GET.get('ano', timezone.now().year))
    primeiro_dia = date(ano, mes, 1)
    if mes == 12:
        ultimo_dia = date(ano + 1, 1, 1) - timedelta(days=1)
    else:
        ultimo_dia = date(ano, mes + 1, 1) - timedelta(days=1)

    qs = AgendaAtendimentoProfessor.objects.filter(
        data__gte=primeiro_dia,
        data__lte=ultimo_dia,
        visivel_totem=True
    ).order_by('data', 'hora_inicio')

    data = []
    for ev in qs:
        data.append({
            'id': ev.id,
            'tipo': ev.tipo,
            'tipo_display': ev.get_tipo_display(),
            'nome_professor': ev.nome_professor,
            'disciplina': ev.disciplina,
            'titulo': ev.titulo,
            'data': ev.data.isoformat(),
            'hora_inicio': ev.hora_inicio.strftime('%H:%M'),
            'hora_fim': ev.hora_fim.strftime('%H:%M') if ev.hora_fim else '',
            'observacoes': ev.observacoes,
        })
    return JsonResponse({'eventos': data})


