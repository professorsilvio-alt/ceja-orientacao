"""Views do app agenda"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from datetime import date, timedelta
from usuarios.views import diretor_required, verificar_primeiro_acesso
from .models import RegistroPresenca, ReservaAuditorio
from .forms import RegistroPresencaForm, ReservaAuditorioForm
from professores.models import Professor
from funcionarios.models import FuncionarioAdministrativo, FuncionarioTerceirizado


# ── PRESENÇA ────────────────────────────────────────────────

@diretor_required
def view_listar_presencas(request):
    """Listagem e filtros de registros de presença."""
    data_inicio = request.GET.get('data_inicio', (timezone.now().date() - timedelta(days=30)).isoformat())
    data_fim = request.GET.get('data_fim', timezone.now().date().isoformat())
    tipo = request.GET.get('tipo', '')

    registros = RegistroPresenca.objects.filter(
        data__gte=data_inicio,
        data__lte=data_fim,
    ).order_by('-data', 'nome_funcionario')

    if tipo:
        registros = registros.filter(tipo=tipo)

    return render(request, 'agenda/listar_presencas.html', {
        'registros': registros,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'tipo_filtro': tipo,
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

        messages.success(request, f'Registro de {registro.get_tipo_display()} cadastrado.')
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
        messages.success(request, 'Registro atualizado.')
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

    return render(request, 'agenda/auditorio.html', {
        'reservas': reservas,
        'proximas': proximas,
        'mes': mes,
        'ano': ano,
        'nome_mes': MESES_NOMES[mes - 1],
        'hoje': hoje,
        'primeiro_dia': primeiro_dia,
        'ultimo_dia': ultimo_dia,
        'mes_ant': mes_ant, 'ano_ant': ano_ant,
        'mes_prox': mes_prox, 'ano_prox': ano_prox,
        'is_diretor': request.user.perfil == 'diretor' or request.user.is_superuser,
    })


@diretor_required
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


@diretor_required
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


@diretor_required
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
