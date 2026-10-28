"""Views do Diário de Bordo da Direção Escolar"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from usuarios.views import diretor_required
from .models import OcorrenciaDiario, LeituraOcorrencia
from .forms import OcorrenciaDiarioForm


def get_client_ip(request):
    """Captura o IP real do cliente mesmo através de proxy ou load balancer."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


@diretor_required
def view_listar_diario(request):
    """
    Exibe a listagem das ocorrências do Diário de Bordo da Direção.
    Inclui KPIs de acompanhamento, checklist de confirmação de leitura e filtros.
    """
    filtro_status = request.GET.get('status', 'todos')
    filtro_prioridade = request.GET.get('prioridade', '')
    filtro_categoria = request.GET.get('categoria', '')
    busca = request.GET.get('q', '').strip()

    qs = OcorrenciaDiario.objects.filter(ativo=True).select_related('autor').prefetch_related('leituras__usuario')

    if busca:
        qs = qs.filter(
            Q(titulo__icontains=busca) |
            Q(texto__icontains=busca) |
            Q(autor__nome_completo__icontains=busca)
        )

    if filtro_prioridade:
        qs = qs.filter(prioridade=filtro_prioridade)

    if filtro_categoria:
        qs = qs.filter(categoria=filtro_categoria)

    if filtro_status == 'pendentes':
        qs = qs.exclude(autor=request.user).exclude(leituras__usuario=request.user)
    elif filtro_status == 'minhas':
        qs = qs.filter(autor=request.user)
    elif filtro_status == 'lidas':
        qs = qs.filter(Q(autor=request.user) | Q(leituras__usuario=request.user)).distinct()

    # Prepara lista com objetos e dados de leitura computados
    lista_ocorrencias = []
    for oc in qs:
        lista_ocorrencias.append({
            'obj': oc,
            'checklist': oc.get_checklist_leituras(),
            'estatisticas': oc.estatisticas_leituras,
            'ja_lido': oc.lida_por(request.user),
        })

    # KPIs gerais
    hoje = timezone.now().date()
    total_geral = OcorrenciaDiario.objects.filter(ativo=True).count()
    pendentes_usuario = OcorrenciaDiario.objects.filter(
        ativo=True
    ).exclude(autor=request.user).exclude(leituras__usuario=request.user).count()
    urgentes_ativas = OcorrenciaDiario.objects.filter(ativo=True, prioridade='urgente').count()
    ocorrencias_hoje = OcorrenciaDiario.objects.filter(ativo=True, criado_em__date=hoje).count()

    form_novo = OcorrenciaDiarioForm()

    contexto = {
        'ocorrencias': lista_ocorrencias,
        'total_geral': total_geral,
        'pendentes_usuario': pendentes_usuario,
        'urgentes_ativas': urgentes_ativas,
        'ocorrencias_hoje': ocorrencias_hoje,
        'filtro_status': filtro_status,
        'filtro_prioridade': filtro_prioridade,
        'filtro_categoria': filtro_categoria,
        'busca': busca,
        'form_novo': form_novo,
    }
    return render(request, 'diario_bordo/listar.html', contexto)


@diretor_required
def view_criar_ocorrencia(request):
    """Cria uma nova ocorrência no Diário de Bordo."""
    if request.method == 'POST':
        form = OcorrenciaDiarioForm(request.POST, request.FILES)
        if form.is_valid():
            ocorrencia = form.save(commit=False)
            ocorrencia.autor = request.user
            ocorrencia.save()

            # Registra a confirmação de leitura automática do próprio autor
            LeituraOcorrencia.objects.get_or_create(
                ocorrencia=ocorrencia,
                usuario=request.user,
                defaults={
                    'ip_origem': get_client_ip(request),
                    'observacao': 'Registrado pelo autor',
                    'lido_em': ocorrencia.criado_em,
                }
            )

            messages.success(request, 'Ocorrência registrada no Diário de Bordo com sucesso! Todos os diretores foram notificados.')
            return redirect('listar_diario')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = OcorrenciaDiarioForm()

    return render(request, 'diario_bordo/form.html', {
        'form': form,
        'titulo_pagina': 'Novo Registro no Diário de Bordo',
        'subtitulo_pagina': 'Registre recados, ocorrências e orientações para a equipe de direção',
    })


@diretor_required
def view_detalhe_ocorrencia(request, pk):
    """Exibe o detalhe completo da ocorrência com checklist de leitura de toda a direção."""
    ocorrencia = get_object_or_404(
        OcorrenciaDiario.objects.select_related('autor').prefetch_related('leituras__usuario'),
        pk=pk,
        ativo=True
    )
    checklist = ocorrencia.get_checklist_leituras()
    ja_lido = ocorrencia.lida_por(request.user)

    return render(request, 'diario_bordo/detalhe.html', {
        'ocorrencia': ocorrencia,
        'checklist': checklist,
        'ja_lido': ja_lido,
    })


@diretor_required
def view_confirmar_leitura(request, pk):
    """
    Confirmação de leitura e ciência pelo diretor logado.
    Aceita requisição convencional (POST) e AJAX (JSON).
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método inválido.'}, status=405)

    ocorrencia = get_object_or_404(OcorrenciaDiario, pk=pk, ativo=True)
    ip = get_client_ip(request)

    leitura, criada = LeituraOcorrencia.objects.get_or_create(
        ocorrencia=ocorrencia,
        usuario=request.user,
        defaults={
            'ip_origem': ip,
            'lido_em': timezone.now(),
            'observacao': 'Ciência confirmada',
        }
    )

    # Recalcula pendentes deste usuário
    pendentes_restantes = OcorrenciaDiario.objects.filter(
        ativo=True
    ).exclude(autor=request.user).exclude(leituras__usuario=request.user).count()

    is_ajax = (
        request.headers.get('x-requested-with') == 'XMLHttpRequest' or
        request.content_type == 'application/json' or
        request.GET.get('format') == 'json'
    )

    if is_ajax:
        return JsonResponse({
            'success': True,
            'message': 'Leitura e ciência confirmadas com sucesso!',
            'ocorrencia_id': ocorrencia.id,
            'data_confirmacao': leitura.lido_em.strftime('%d/%m/%Y às %H:%M'),
            'pendentes_restantes': pendentes_restantes,
        })

    messages.success(request, f'Você confirmou a leitura do registro: "{ocorrencia.assunto_exibicao}".')
    proxima_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'listar_diario'
    return redirect(proxima_url)


@diretor_required
def view_confirmar_todas_leituras(request):
    """Marca como lidas todas as ocorrências pendentes para o diretor logado."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método inválido.'}, status=405)

    pendentes = OcorrenciaDiario.objects.filter(
        ativo=True
    ).exclude(autor=request.user).exclude(leituras__usuario=request.user)

    ip = get_client_ip(request)
    agora = timezone.now()
    count = 0

    for oc in pendentes:
        LeituraOcorrencia.objects.get_or_create(
            ocorrencia=oc,
            usuario=request.user,
            defaults={
                'ip_origem': ip,
                'lido_em': agora,
                'observacao': 'Ciência em lote confirmada',
            }
        )
        count += 1

    is_ajax = (
        request.headers.get('x-requested-with') == 'XMLHttpRequest' or
        request.content_type == 'application/json' or
        request.GET.get('format') == 'json'
    )

    if is_ajax:
        return JsonResponse({
            'success': True,
            'message': f'Todas as {count} ocorrências pendentes foram confirmadas!',
            'confirmadas_count': count,
            'pendentes_restantes': 0,
        })

    messages.success(request, f'{count} ocorrência(s) pendente(s) confirmada(s) com sucesso!')
    proxima_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'listar_diario'
    return redirect(proxima_url)


@diretor_required
def view_editar_ocorrencia(request, pk):
    """Edição de ocorrência (apenas o autor ou superusuário)."""
    ocorrencia = get_object_or_404(OcorrenciaDiario, pk=pk, ativo=True)

    if ocorrencia.autor != request.user and not request.user.is_superuser:
        messages.error(request, 'Apenas o autor do registro ou o administrador pode editá-lo.')
        return redirect('detalhe_ocorrencia', pk=pk)

    if request.method == 'POST':
        form = OcorrenciaDiarioForm(request.POST, request.FILES, instance=ocorrencia)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ocorrência atualizada com sucesso.')
            return redirect('detalhe_ocorrencia', pk=pk)
    else:
        form = OcorrenciaDiarioForm(instance=ocorrencia)

    return render(request, 'diario_bordo/form.html', {
        'form': form,
        'ocorrencia': ocorrencia,
        'titulo_pagina': 'Editar Registro no Diário de Bordo',
        'subtitulo_pagina': f'Editando ocorrência #{ocorrencia.id}',
    })


@diretor_required
def view_excluir_ocorrencia(request, pk):
    """Exclusão/Arquivamento de ocorrência (apenas autor ou superusuário)."""
    if request.method != 'POST':
        messages.error(request, 'Operação não permitida.')
        return redirect('listar_diario')

    ocorrencia = get_object_or_404(OcorrenciaDiario, pk=pk)
    if ocorrencia.autor != request.user and not request.user.is_superuser:
        messages.error(request, 'Apenas o autor do registro ou o administrador pode excluí-lo.')
        return redirect('listar_diario')

    ocorrencia.ativo = False
    ocorrencia.save(update_fields=['ativo'])
    messages.success(request, 'Registro arquivado do Diário de Bordo com sucesso.')
    return redirect('listar_diario')
