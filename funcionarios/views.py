"""Views do app funcionarios"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from usuarios.views import diretor_required, verificar_primeiro_acesso
from .models import FuncionarioAdministrativo, FuncionarioTerceirizado
from .forms import FuncionarioAdmForm, FuncionarioTercForm


# ── Administrativos ────────────────────────────────────────

@login_required
@verificar_primeiro_acesso
def view_listar_administrativos(request):
    funcionarios = FuncionarioAdministrativo.objects.filter(ativo=True)
    return render(request, 'funcionarios/listar_adm.html', {
        'funcionarios': funcionarios,
        'tipo': 'Funcionários Administrativos',
    })


@diretor_required
def view_criar_administrativo(request):
    form = FuncionarioAdmForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        func = form.save()
        messages.success(request, f'{func.nome_completo} cadastrado com sucesso.')
        return redirect('detalhe_administrativo', pk=func.pk)
    return render(request, 'funcionarios/form_adm.html', {
        'form': form, 'titulo': 'Novo Funcionário Administrativo'
    })


@login_required
@verificar_primeiro_acesso
def view_detalhe_administrativo(request, pk):
    func = get_object_or_404(FuncionarioAdministrativo, pk=pk)
    return render(request, 'funcionarios/detalhe_adm.html', {'funcionario': func})


@diretor_required
def view_editar_administrativo(request, pk):
    func = get_object_or_404(FuncionarioAdministrativo, pk=pk)
    form = FuncionarioAdmForm(request.POST or None, request.FILES or None, instance=func)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Dados atualizados com sucesso.')
        return redirect('detalhe_administrativo', pk=func.pk)
    return render(request, 'funcionarios/form_adm.html', {
        'form': form, 'titulo': f'Editar: {func.nome_completo}'
    })


# ── Terceirizados ──────────────────────────────────────────

@login_required
@verificar_primeiro_acesso
def view_listar_terceirizados(request):
    funcionarios = FuncionarioTerceirizado.objects.filter(ativo=True)
    return render(request, 'funcionarios/listar_terc.html', {
        'funcionarios': funcionarios,
        'tipo': 'Funcionários Terceirizados',
    })


@diretor_required
def view_criar_terceirizado(request):
    form = FuncionarioTercForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        func = form.save()
        messages.success(request, f'{func.nome_completo} cadastrado com sucesso.')
        return redirect('detalhe_terceirizado', pk=func.pk)
    return render(request, 'funcionarios/form_terc.html', {
        'form': form, 'titulo': 'Novo Funcionário Terceirizado'
    })


@login_required
@verificar_primeiro_acesso
def view_detalhe_terceirizado(request, pk):
    func = get_object_or_404(FuncionarioTerceirizado, pk=pk)
    return render(request, 'funcionarios/detalhe_terc.html', {'funcionario': func})


@diretor_required
def view_editar_terceirizado(request, pk):
    func = get_object_or_404(FuncionarioTerceirizado, pk=pk)
    form = FuncionarioTercForm(request.POST or None, request.FILES or None, instance=func)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Dados atualizados com sucesso.')
        return redirect('detalhe_terceirizado', pk=func.pk)
    return render(request, 'funcionarios/form_terc.html', {
        'form': form, 'titulo': f'Editar: {func.nome_completo}'
    })
