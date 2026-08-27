"""Views do app funcionarios"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
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
        messages.success(request, f'Dados de {func.nome_completo} atualizados com sucesso.')
        return redirect('detalhe_terceirizado', pk=func.pk)
    return render(request, 'funcionarios/form_terc.html', {
        'form': form, 'titulo': f'Editar: {func.nome_completo}'
    })


# ── Controle de Ponto (Terceirizados) ──────────────────────────
import base64
import uuid
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.utils import timezone
from .models import FuncionarioAdministrativo, FuncionarioTerceirizado, RegistroPontoTerceirizado
from .utils import enviar_email_confirmacao_ponto


def view_terminal_ponto(request):
    """Interface do Terminal para bater ponto (Totem / Computador da escola)."""
    terceirizados = FuncionarioTerceirizado.objects.filter(ativo=True).order_by('nome_completo')
    return render(request, 'funcionarios/bater_ponto.html', {
        'terceirizados': terceirizados,
        'agora': timezone.now(),
    })


@csrf_exempt
def api_registrar_ponto(request):
    """API Endpoint para validação de PIN, foto da webcam e salvamento da batida de ponto."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método não permitido.'}, status=405)

    funcionario_id = request.POST.get('funcionario_id')
    pin = request.POST.get('pin', '').strip()
    tipo = request.POST.get('tipo', '').strip()
    foto_base64 = request.POST.get('foto_base64', '').strip()

    if not pin or not tipo:
        return JsonResponse({'success': False, 'error': 'Digite a sua senha (PIN) e selecione a opção de batida.'})

    func = None
    if funcionario_id:
        try:
            func = FuncionarioTerceirizado.objects.get(pk=funcionario_id, ativo=True)
        except (FuncionarioTerceirizado.DoesNotExist, ValueError):
            func = None

    if not func:
        # Busca automática pelo PIN caso funcionario_id esteja ausente ou nulo
        terceirizados = FuncionarioTerceirizado.objects.filter(ativo=True)
        for f in terceirizados:
            if f.senha_ponto and f.verificar_senha_ponto(pin):
                func = f
                break

    if not func:
        return JsonResponse({'success': False, 'error': 'Funcionário não encontrado ou PIN incorreto.'})

    if not func.senha_ponto or not func.verificar_senha_ponto(pin):
        return JsonResponse({'success': False, 'error': 'Senha / PIN incorreto.'})

    tipos_validos = dict(RegistroPontoTerceirizado.TIPO_PONTO_CHOICES)
    if tipo not in tipos_validos:
        return JsonResponse({'success': False, 'error': 'Tipo de batida de ponto inválido.'})

    # Instancia o registro de ponto
    registro = RegistroPontoTerceirizado(
        funcionario=func,
        tipo=tipo,
        data_hora=timezone.now(),
        ip_origem=request.META.get('REMOTE_ADDR')
    )

    # Processa a foto enviada em base64 da webcam
    if foto_base64 and 'base64,' in foto_base64:
        try:
            format, imgstr = foto_base64.split(';base64,')
            ext = format.split('/')[-1] if '/' in format else 'jpg'
            filename = f"ponto_{func.pk}_{uuid.uuid4().hex[:8]}.{ext}"
            file_data = ContentFile(base64.b64decode(imgstr), name=filename)
            registro.foto = file_data
        except Exception as e:
            print(f"[Ponto API] Erro ao decodificar foto: {e}")

    registro.save()

    # Dispara o envio de e-mail assíncrono (sem travar a resposta se o envio falhar)
    try:
        enviar_email_confirmacao_ponto(registro)
    except Exception as e:
        print(f"[Ponto API] Aviso no envio de e-mail de confirmação: {e}")

    return JsonResponse({
        'success': True,
        'message': 'Ponto registrado com sucesso!',
        'funcionario': func.nome_completo,
        'tipo': registro.get_tipo_display(),
        'data_hora': registro.data_hora.strftime('%d/%m/%Y às %H:%M:%S'),
        'email_destinatario': func.email or 'Nenhum e-mail cadastrado'
    })


@csrf_exempt
def api_listar_terceirizados_totem(request):
    """API Endpoint para listar terceirizados ativos no Totem de autoatendimento."""
    terceirizados = FuncionarioTerceirizado.objects.filter(ativo=True).order_by('nome_completo')
    data = [{
        'id': f.pk,
        'nome': f.nome_completo,
        'cargo': f.cargo_funcao,
        'empresa': f.empresa_contratante,
        'tem_pin': bool(f.senha_ponto)
    } for f in terceirizados]
    return JsonResponse({'success': True, 'terceirizados': data})


@csrf_exempt
def api_validar_pin(request):
    """
    API Endpoint para validação do PIN do funcionário no Totem.
    Identifica automaticamente o funcionário correspondente ao PIN digitado.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método não permitido.'}, status=405)

    func_id = request.POST.get('funcionario_id')
    pin = request.POST.get('pin', '').strip()

    if not pin:
        return JsonResponse({'success': False, 'error': 'Por favor, digite a sua senha de ponto (PIN).'})

    # Se um funcionário específico for informado
    if func_id:
        try:
            func = FuncionarioTerceirizado.objects.get(pk=func_id, ativo=True)
            if func.senha_ponto and func.verificar_senha_ponto(pin):
                return JsonResponse({
                    'success': True,
                    'funcionario_id': func.pk,
                    'nome': func.nome_completo,
                    'cargo': func.cargo_funcao,
                    'empresa': func.empresa_contratante
                })
            else:
                return JsonResponse({'success': False, 'error': 'PIN incorreto. Tente novamente.'})
        except FuncionarioTerceirizado.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Funcionário não encontrado.'})

    # Busca automática pelo PIN entre todos os terceirizados ativos
    terceirizados = FuncionarioTerceirizado.objects.filter(ativo=True)
    funcionario_encontrado = None

    for func in terceirizados:
        if func.senha_ponto and func.verificar_senha_ponto(pin):
            funcionario_encontrado = func
            break

    if funcionario_encontrado:
        return JsonResponse({
            'success': True,
            'funcionario_id': funcionario_encontrado.pk,
            'nome': funcionario_encontrado.nome_completo,
            'cargo': funcionario_encontrado.cargo_funcao,
            'empresa': funcionario_encontrado.empresa_contratante
        })

    return JsonResponse({'success': False, 'error': 'PIN incorreto ou não cadastrado. Tente novamente.'})


@login_required
@verificar_primeiro_acesso
def view_espelho_ponto(request):
    """Painel do RH para visualização do espelho de ponto dos terceirizados."""
    registros = RegistroPontoTerceirizado.objects.select_related('funcionario').all()
    terceirizados = FuncionarioTerceirizado.objects.filter(ativo=True)

    # Filtros
    funcionario_id = request.GET.get('funcionario')
    tipo = request.GET.get('tipo')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')

    if funcionario_id:
        registros = registros.filter(funcionario_id=funcionario_id)
    if tipo:
        registros = registros.filter(tipo=tipo)
    if data_inicio:
        registros = registros.filter(data_hora__date__gte=data_inicio)
    if data_fim:
        registros = registros.filter(data_hora__date__lte=data_fim)

    hoje = timezone.now().date()
    total_hoje = RegistroPontoTerceirizado.objects.filter(data_hora__date=hoje).count()

    return render(request, 'funcionarios/espelho_ponto.html', {
        'registros': registros[:200],  # Limita as 200 mais recentes
        'terceirizados': terceirizados,
        'total_hoje': total_hoje,
        'funcionario_selecionado': funcionario_id,
        'tipo_selecionado': tipo,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
    })


@diretor_required
def view_gerenciar_senhas_ponto(request):
    """Interface para o RH cadastrar ou redefinir senhas/PINs dos funcionários terceirizados."""
    if request.method == 'POST':
        func_id = request.POST.get('funcionario_id')
        nova_senha = request.POST.get('nova_senha', '').strip()

        if func_id and nova_senha:
            func = get_object_or_404(FuncionarioTerceirizado, pk=func_id)
            func.definir_senha_ponto(nova_senha)
            func.save()
            messages.success(request, f'Senha de ponto do funcionário {func.nome_completo} atualizada com sucesso.')
        else:
            messages.error(request, 'Informe o funcionário e a nova senha/PIN.')
        return redirect('gerenciar_senhas_ponto')

    terceirizados = FuncionarioTerceirizado.objects.filter(ativo=True).order_by('nome_completo')
    return render(request, 'funcionarios/gerenciar_senhas.html', {
        'terceirizados': terceirizados,
    })

