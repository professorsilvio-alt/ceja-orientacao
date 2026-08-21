"""Views do app professores"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from usuarios.views import diretor_required, verificar_primeiro_acesso
from .models import Professor, HorarioProfessor
from .forms import ProfessorForm, HorarioProfessorForm


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
