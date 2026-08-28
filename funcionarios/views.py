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
    import re
    from django.db.models import Q
    q = request.GET.get('q', '').strip()
    cpf_limpo = re.sub(r'\D', '', q)

    funcionarios = FuncionarioAdministrativo.objects.filter(ativo=True)

    if q:
        query_filter = Q(nome_completo__icontains=q) | \
                       Q(matricula__icontains=q) | \
                       Q(matricula_acumulacao__icontains=q) | \
                       Q(id_vinculo__icontains=q) | \
                       Q(cargo__icontains=q) | \
                       Q(funcao_atual__icontains=q)
        if cpf_limpo:
            query_filter |= Q(cpf__icontains=cpf_limpo)
        funcionarios = funcionarios.filter(query_filter)

    return render(request, 'funcionarios/listar_adm.html', {
        'funcionarios': funcionarios,
        'query': q,
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

    from django.contrib.contenttypes.models import ContentType
    from professores.models import DocumentoServidor, OcorrenciaFolgaServidor, AnotacaoServidor
    ct = ContentType.objects.get_for_model(FuncionarioAdministrativo)

    documentos = DocumentoServidor.objects.filter(content_type=ct, object_id=func.pk)
    folgas = OcorrenciaFolgaServidor.objects.filter(content_type=ct, object_id=func.pk)
    anotacoes = AnotacaoServidor.objects.filter(content_type=ct, object_id=func.pk)

    total_creditos = sum(f.dias for f in folgas if f.tipo == 'credito')
    total_usufruidos = sum(f.dias for f in folgas if f.tipo == 'usufruido')
    saldo_folgas = total_creditos - total_usufruidos

    return render(request, 'funcionarios/detalhe_adm.html', {
        'funcionario': func,
        'documentos': documentos,
        'folgas': folgas,
        'anotacoes': anotacoes,
        'saldo_folgas': saldo_folgas,
        'total_creditos': total_creditos,
        'total_usufruidos': total_usufruidos,
        'tipo_servidor': 'adm',
    })


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
    import re
    from django.db.models import Q
    q = request.GET.get('q', '').strip()
    cpf_limpo = re.sub(r'\D', '', q)

    funcionarios = FuncionarioTerceirizado.objects.filter(ativo=True)

    if q:
        query_filter = Q(nome_completo__icontains=q) | \
                       Q(codigo_terceirizado__icontains=q) | \
                       Q(cargo_funcao__icontains=q) | \
                       Q(empresa_contratante__icontains=q) | \
                       Q(rg__icontains=q)
        if cpf_limpo:
            query_filter |= Q(cpf__icontains=cpf_limpo)
        funcionarios = funcionarios.filter(query_filter)

    return render(request, 'funcionarios/listar_terc.html', {
        'funcionarios': funcionarios,
        'query': q,
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

    from django.contrib.contenttypes.models import ContentType
    from professores.models import DocumentoServidor, OcorrenciaFolgaServidor, AnotacaoServidor
    ct = ContentType.objects.get_for_model(FuncionarioTerceirizado)

    documentos = DocumentoServidor.objects.filter(content_type=ct, object_id=func.pk)
    folgas = OcorrenciaFolgaServidor.objects.filter(content_type=ct, object_id=func.pk)
    anotacoes = AnotacaoServidor.objects.filter(content_type=ct, object_id=func.pk)

    total_creditos = sum(f.dias for f in folgas if f.tipo == 'credito')
    total_usufruidos = sum(f.dias for f in folgas if f.tipo == 'usufruido')
    saldo_folgas = total_creditos - total_usufruidos

    return render(request, 'funcionarios/detalhe_terc.html', {
        'funcionario': func,
        'documentos': documentos,
        'folgas': folgas,
        'anotacoes': anotacoes,
        'saldo_folgas': saldo_folgas,
        'total_creditos': total_creditos,
        'total_usufruidos': total_usufruidos,
        'tipo_servidor': 'terc',
    })


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


def _json_cors_response(data, status=200):
    response = JsonResponse(data, status=status)
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response["Access-Control-Allow-Headers"] = "*"
    return response


@csrf_exempt
def api_registrar_ponto(request):
    """API Endpoint para validação de PIN, foto da webcam e salvamento da batida de ponto."""
    if request.method == 'OPTIONS':
        return _json_cors_response({'success': True})

    if request.method != 'POST':
        return _json_cors_response({'success': False, 'error': 'Método não permitido.'}, status=405)

    funcionario_id = request.POST.get('funcionario_id')
    pin = request.POST.get('pin', '').strip()
    tipo = request.POST.get('tipo', '').strip()
    foto_base64 = request.POST.get('foto_base64', '').strip()

    if not pin or not tipo:
        return _json_cors_response({'success': False, 'error': 'Digite a sua senha (PIN) e selecione a opção de batida.'})

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
        return _json_cors_response({'success': False, 'error': 'Funcionário não encontrado ou PIN incorreto.'})

    if not func.senha_ponto or not func.verificar_senha_ponto(pin):
        return _json_cors_response({'success': False, 'error': 'Senha / PIN incorreto.'})

    tipos_validos = dict(RegistroPontoTerceirizado.TIPO_PONTO_CHOICES)
    if tipo not in tipos_validos:
        return _json_cors_response({'success': False, 'error': 'Tipo de batida de ponto inválido.'})

    # Bloqueia registros duplicados do mesmo tipo no mesmo dia para o funcionário
    hoje = timezone.now().date()
    registro_existente = RegistroPontoTerceirizado.objects.filter(
        funcionario=func,
        tipo=tipo,
        data_hora__date=hoje
    ).first()

    if registro_existente:
        horario_str = registro_existente.data_hora.strftime("%H:%M:%S")
        tipo_display = registro_existente.get_tipo_display()
        return _json_cors_response({
            'success': False,
            'error': f'Você já registrou {tipo_display} hoje às {horario_str}. Cada tipo de ponto só é permitido uma vez ao dia.'
        })

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

    return _json_cors_response({
        'success': True,
        'message': 'Ponto registrado com sucesso!',
        'funcionario': func.nome_completo,
        'tipo': registro.get_tipo_display(),
        'data_hora': timezone.localtime(registro.data_hora).strftime('%d/%m/%Y às %H:%M:%S'),
        'email_destinatario': func.email or 'Nenhum e-mail cadastrado'
    })


@csrf_exempt
def api_listar_terceirizados_totem(request):
    """API Endpoint para listar terceirizados ativos no Totem de autoatendimento."""
    if request.method == 'OPTIONS':
        return _json_cors_response({'success': True})

    terceirizados = FuncionarioTerceirizado.objects.filter(ativo=True).order_by('nome_completo')
    data = [{
        'id': f.pk,
        'nome': f.nome_completo,
        'cargo': f.cargo_funcao,
        'empresa': f.empresa_contratante,
        'tem_pin': bool(f.senha_ponto)
    } for f in terceirizados]
    return _json_cors_response({'success': True, 'terceirizados': data})


@csrf_exempt
def api_validar_pin(request):
    """
    API Endpoint para validação do PIN do funcionário no Totem.
    Identifica automaticamente o funcionário correspondente ao PIN digitado.
    """
    if request.method == 'OPTIONS':
        return _json_cors_response({'success': True})

    if request.method != 'POST':
        return _json_cors_response({'success': False, 'error': 'Método não permitido.'}, status=405)

    func_id = request.POST.get('funcionario_id')
    pin = request.POST.get('pin', '').strip()

    if not pin:
        return _json_cors_response({'success': False, 'error': 'Por favor, digite a sua senha de ponto (PIN).'})

    # Se um funcionário específico for informado
    if func_id:
        try:
            func = FuncionarioTerceirizado.objects.get(pk=func_id, ativo=True)
            if func.senha_ponto and func.verificar_senha_ponto(pin):
                return _json_cors_response({
                    'success': True,
                    'funcionario_id': func.pk,
                    'nome': func.nome_completo,
                    'cargo': func.cargo_funcao,
                    'empresa': func.empresa_contratante
                })
            else:
                return _json_cors_response({'success': False, 'error': 'PIN incorreto. Tente novamente.'})
        except FuncionarioTerceirizado.DoesNotExist:
            return _json_cors_response({'success': False, 'error': 'Funcionário não encontrado.'})

    # Busca automática pelo PIN entre todos os terceirizados ativos
    terceirizados = FuncionarioTerceirizado.objects.filter(ativo=True)
    funcionario_encontrado = None

    for func in terceirizados:
        if func.senha_ponto and func.verificar_senha_ponto(pin):
            funcionario_encontrado = func
            break

    if funcionario_encontrado:
        return _json_cors_response({
            'success': True,
            'funcionario_id': funcionario_encontrado.pk,
            'nome': funcionario_encontrado.nome_completo,
            'cargo': funcionario_encontrado.cargo_funcao,
            'empresa': funcionario_encontrado.empresa_contratante
        })

    return _json_cors_response({'success': False, 'error': 'PIN incorreto ou não cadastrado. Tente novamente.'})


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


import calendar
import datetime

@login_required
@verificar_primeiro_acesso
def view_folha_ponto_kratus(request, pk=None):
    """
    Gera a Folha Individual de Ponto padronizada (Modelo Kratus) em formato de impressão.
    Pode gerar para um único funcionário terceirizado (se pk informado) ou em lote.
    """
    hoje = timezone.now().date()
    try:
        mes = int(request.GET.get('mes', 8 if hoje.year == 2026 and hoje.month == 8 else hoje.month))
    except ValueError:
        mes = hoje.month

    try:
        ano = int(request.GET.get('ano', hoje.year))
    except ValueError:
        ano = hoje.year

    if pk:
        funcionarios = FuncionarioTerceirizado.objects.filter(pk=pk)
    else:
        func_id = request.GET.get('funcionario')
        if func_id:
            funcionarios = FuncionarioTerceirizado.objects.filter(pk=func_id)
        else:
            funcionarios = FuncionarioTerceirizado.objects.filter(ativo=True).order_by('codigo_terceirizado', 'nome_completo')

    _, num_dias = calendar.monthrange(ano, mes)
    dias_semana_str = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']

    folhas = []
    for func in funcionarios:
        dias_mes = []
        for dia in range(1, num_dias + 1):
            dt = datetime.date(ano, mes, dia)
            w = dt.weekday()
            is_sabado = (w == 5)
            is_domingo = (w == 6)

            # Buscar registros de ponto do dia
            regs = RegistroPontoTerceirizado.objects.filter(funcionario=func, data_hora__date=dt)
            ponto_map = {r.tipo: r.data_hora.strftime("%H:%M") for r in regs}

            dias_mes.append({
                'dia_str': f"{dia:02d}",
                'semana_str': dias_semana_str[w],
                'is_sabado': is_sabado,
                'is_domingo': is_domingo,
                'entrada': ponto_map.get('ENTRADA', ''),
                'almoco_saida': ponto_map.get('ALMOCO_SAIDA', ''),
                'almoco_retorno': ponto_map.get('ALMOCO_RETORNO', ''),
                'saida': ponto_map.get('SAIDA', ''),
            })

        folhas.append({
            'funcionario': func,
            'dias': dias_mes,
        })

    todos_terceirizados = FuncionarioTerceirizado.objects.filter(ativo=True).order_by('nome_completo')

    return render(request, 'funcionarios/folha_ponto_kratus.html', {
        'folhas': folhas,
        'mes': mes,
        'ano': ano,
        'periodo_str': f"{mes:02d}/{ano}",
        'pk_selecionado': pk or request.GET.get('funcionario', ''),
        'terceirizados': todos_terceirizados,
        'meses': [
            (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'), (4, 'Abril'),
            (5, 'Maio'), (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'),
            (9, 'Setembro'), (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro')
        ],
        'anos': range(hoje.year - 2, hoje.year + 3),
    })


@diretor_required
def view_editar_ponto_terceirizado(request, pk):
    """Permite ao diretor fazer ajustes manuais nos registros de ponto do terceirizado."""
    registro = get_object_or_404(RegistroPontoTerceirizado, pk=pk)
    if request.method == 'POST':
        data_hora_str = request.POST.get('data_hora')
        tipo = request.POST.get('tipo')
        observacao = request.POST.get('observacao', '').strip()

        if data_hora_str:
            from django.utils.dateparse import parse_datetime
            dt = parse_datetime(data_hora_str)
            if dt:
                if timezone.is_naive(dt):
                    dt = timezone.make_aware(dt)
                registro.data_hora = dt

        if tipo in dict(RegistroPontoTerceirizado.TIPO_PONTO_CHOICES):
            registro.tipo = tipo

        user_nome = getattr(request.user, 'nome_completo', None) or getattr(request.user, 'cpf', 'Direção')
        registro.observacao = observacao or f"Ajuste manual realizado por {user_nome}"
        registro.save()
        messages.success(request, f'Batida de ponto de {registro.funcionario.nome_curto} ajustada com sucesso!')

    return redirect(request.META.get('HTTP_REFERER', 'espelho_ponto'))


@diretor_required
def view_excluir_ponto_terceirizado(request, pk):
    """Permite ao diretor excluir uma batida de ponto duplicada ou incorreta."""
    registro = get_object_or_404(RegistroPontoTerceirizado, pk=pk)
    nome = registro.funcionario.nome_curto
    registro.delete()
    messages.success(request, f'Batida de ponto de {nome} excluída com sucesso.')
    return redirect(request.META.get('HTTP_REFERER', 'espelho_ponto'))


@diretor_required
def view_reenviar_email_ponto(request, pk):
    """Reenvia o e-mail de confirmação de batida de ponto para o funcionário."""
    registro = get_object_or_404(RegistroPontoTerceirizado, pk=pk)
    if not registro.funcionario.email:
        messages.error(request, f'O funcionário {registro.funcionario.nome_curto} não possui e-mail cadastrado.')
    else:
        sucesso = enviar_email_confirmacao_ponto(registro)
        if sucesso:
            messages.success(request, f'E-mail de confirmação reenviado para {registro.funcionario.email}.')
        else:
            messages.error(request, 'Falha ao enviar e-mail. Verifique se o e-mail está correto ou as configurações de SMTP.')

    return redirect(request.META.get('HTTP_REFERER', 'espelho_ponto'))

