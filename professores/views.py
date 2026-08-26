"""Views do app professores"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from usuarios.views import diretor_required, verificar_primeiro_acesso
from .models import Professor, HorarioProfessor, ConfiguracaoEscola, DisciplinaOfertada, Disciplina, UnidadeEscolar
from .forms import ProfessorForm, HorarioProfessorForm, ConfiguracaoEscolaForm, UnidadeEscolarForm


@login_required
@verificar_primeiro_acesso
def view_listar_professores(request):
    professores = Professor.objects.filter(ativo=True).prefetch_related(
        'disciplinas_lecionadas', 'horarios'
    )
    return render(request, 'professores/listar.html', {
        'professores': professores,
        'total': professores.count(),
    })


@diretor_required
def view_criar_professor(request):
    form = ProfessorForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        professor = form.save()
        messages.success(request, f'Professor {professor.nome_completo} cadastrado com sucesso!')
        return redirect('detalhe_professor', pk=professor.pk)
    return render(request, 'professores/form.html', {
        'form': form, 'titulo': 'Novo Professor'
    })


@login_required
@verificar_primeiro_acesso
def view_detalhe_professor(request, pk):
    professor = get_object_or_404(Professor, pk=pk)
    horarios = professor.horarios.filter(
        ano_letivo=timezone.now().year
    ).order_by('dia_semana', 'hora_inicio')
    return render(request, 'professores/detalhe.html', {
        'professor': professor,
        'horarios': horarios,
    })


@diretor_required
def view_editar_professor(request, pk):
    professor = get_object_or_404(Professor, pk=pk)
    form = ProfessorForm(request.POST or None, request.FILES or None, instance=professor)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Dados do professor atualizados.')
        return redirect('detalhe_professor', pk=professor.pk)
    return render(request, 'professores/form.html', {
        'form': form,
        'titulo': f'Editar: {professor.nome_completo}',
        'professor': professor,
    })


@login_required
@verificar_primeiro_acesso
def view_horarios_professor(request, pk):
    """
    Permite ao professor informar sua disponibilidade de horário.
    Diretor pode ver e aprovar os horários de todos.
    """
    professor = get_object_or_404(Professor, pk=pk)
    ano = request.GET.get('ano', timezone.now().year)

    # Professores só podem ver/editar seus próprios horários
    if request.user.perfil == 'professor':
        if professor.cpf != request.user.cpf:
            messages.error(request, 'Você só pode editar seus próprios horários.')
            return redirect('dashboard')

    horarios = professor.horarios.filter(ano_letivo=ano).order_by('dia_semana', 'hora_inicio')
    form = HorarioProfessorForm(request.POST or None, initial={'ano_letivo': ano})

    if request.method == 'POST' and form.is_valid():
        horario = form.save(commit=False)
        horario.professor = professor
        horario.aprovado = False  # Requer aprovação do diretor
        horario.save()
        messages.success(request, 'Horário adicionado. Aguardando aprovação da direção.')
        return redirect('horarios_professor', pk=professor.pk)

    return render(request, 'professores/horarios.html', {
        'professor': professor,
        'horarios': horarios,
        'form': form,
        'ano': ano,
        'is_diretor': request.user.perfil == 'diretor' or request.user.is_superuser,
    })


@diretor_required
def view_aprovar_horario(request, horario_pk):
    horario = get_object_or_404(HorarioProfessor, pk=horario_pk)
    horario.aprovado = True
    horario.save(update_fields=['aprovado'])
    messages.success(request, f'Horário de {horario.professor.nome_curto} aprovado.')
    return redirect('horarios_professor', pk=horario.professor.pk)


@diretor_required
def view_remover_horario(request, horario_pk):
    horario = get_object_or_404(HorarioProfessor, pk=horario_pk)
    prof_pk = horario.professor.pk
    if request.method == 'POST':
        horario.delete()
        messages.success(request, 'Horário removido.')
    return redirect('horarios_professor', pk=prof_pk)


@diretor_required
def view_configuracao_escola(request):
    unidades = UnidadeEscolar.objects.filter(ativo=True).order_by('tipo', 'nome')
    sede_padrao = unidades.filter(tipo='sede').first() or unidades.first()

    if not sede_padrao:
        sede_padrao = UnidadeEscolar.objects.create(
            nome="CEJA Professora Rosa Soares - Sede",
            tipo="sede",
            codigo="SEDE"
        )
        unidades = UnidadeEscolar.objects.filter(ativo=True).order_by('tipo', 'nome')

    unidade_id = request.GET.get('unidade') or request.POST.get('unidade_id')
    if unidade_id:
        unidade_atual = get_object_or_404(UnidadeEscolar, pk=unidade_id)
    else:
        unidade_atual = sede_padrao

    if request.method == 'POST' and request.POST.get('action') == 'nova_unidade':
        unidade_form = UnidadeEscolarForm(request.POST)
        if unidade_form.is_valid():
            nueva_u = unidade_form.save()
            messages.success(request, f'Unidade Vinculada "{nueva_u.nome}" cadastrada com sucesso!')
            return redirect(f'/professores/configuracao/?unidade={nueva_u.pk}')
    else:
        unidade_form = UnidadeEscolarForm(initial={'tipo': 'vinculada'})

    ano_req = request.GET.get('ano') or timezone.now().year
    try:
        ano_req = int(ano_req)
    except ValueError:
        ano_req = timezone.now().year

    config, _ = ConfiguracaoEscola.objects.get_or_create(
        unidade=unidade_atual,
        ano_letivo=ano_req,
        defaults={
            'ativo': True,
            'duracao_hora_aula': 50,
            'horario_abertura': '08:50',
            'horario_fechamento': '20:30',
            'seg_abertura': '08:50', 'seg_fechamento': '20:30',
            'ter_abertura': '08:50', 'ter_fechamento': '20:30',
            'qua_abertura': '08:50', 'qua_fechamento': '20:30',
            'qui_abertura': '08:50', 'qui_fechamento': '20:30',
            'sex_abertura': '08:50', 'sex_fechamento': '17:00',
            'func_segunda': True,
            'func_terca': True,
            'func_quarta': True,
            'func_quinta': True,
            'func_sexta': True,
        }
    )

    disciplinas = Disciplina.objects.all().order_by('nome')
    for disc in disciplinas:
        DisciplinaOfertada.objects.get_or_create(
            configuracao=config,
            disciplina=disc,
            defaults={'horas_aula_semanais': 4, 'carga_horaria_total': 80, 'ativo': True}
        )

    form = ConfiguracaoEscolaForm(request.POST or None, instance=config)

    if request.method == 'POST' and (request.POST.get('action') == 'salvar_config' or not request.POST.get('action')):
        if form.is_valid():
            form.save()
            
            ofertas = DisciplinaOfertada.objects.filter(configuracao=config)
            for of in ofertas:
                ativo_key = f'disc_ativo_{of.pk}'
                ha_key = f'disc_ha_{of.pk}'
                ch_key = f'disc_ch_{of.pk}'
                
                of.ativo = ativo_key in request.POST
                if ha_key in request.POST:
                    try:
                        of.horas_aula_semanais = int(request.POST[ha_key])
                    except ValueError:
                        pass
                if ch_key in request.POST:
                    try:
                        of.carga_horaria_total = int(request.POST[ch_key])
                    except ValueError:
                        pass
                of.save()

            messages.success(request, f'Configurações de {unidade_atual.nome} ({config.ano_letivo}) salvas!')
            return redirect(f'/professores/configuracao/?unidade={unidade_atual.pk}&ano={config.ano_letivo}')

    ofertas = DisciplinaOfertada.objects.filter(configuracao=config).select_related('disciplina').order_by('disciplina__nome')
    anos_cadastrados = ConfiguracaoEscola.objects.filter(unidade=unidade_atual).values_list('ano_letivo', flat=True).order_by('-ano_letivo')

    return render(request, 'professores/configuracao_escola.html', {
        'form': form,
        'config': config,
        'ofertas': ofertas,
        'unidades': unidades,
        'unidade_atual': unidade_atual,
        'unidade_form': unidade_form,
        'anos_cadastrados': anos_cadastrados,
        'ano_selecionado': config.ano_letivo,
    })
