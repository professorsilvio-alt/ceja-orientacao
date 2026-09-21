"""Views do aplicativo de Acompanhamento de Processos SEI."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from functools import wraps

from usuarios.views import verificar_primeiro_acesso
from .models import ProcessoSEI, AndamentoProcesso
from .forms import ProcessoSEIForm, AndamentoProcessoForm


def gestao_processos_required(view_func):
    """
    Permite acesso a usuários autorizados (Diretor, Administrativo ou Superusuário).
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.perfil not in ['diretor', 'administrativo'] and not request.user.is_superuser:
            messages.error(request, 'Acesso restrito à Direção e Administração da Escola.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@verificar_primeiro_acesso
@gestao_processos_required
def view_listar_processos(request):
    """
    Listagem de processos SEI com busca multifacetada:
    - Palavras / termos (busca geral e por tag específica)
    - Tipo / Categoria do processo
    - Status / Situação
    - Prioridade
    - Setor de tramitação
    - Período de abertura (datas início e fim)
    - Ordenação customizada
    """
    q = request.GET.get('q', '').strip()
    tipo_filtro = request.GET.get('tipo', '').strip()
    status_filtro = request.GET.get('status', 'todos').strip()
    prioridade_filtro = request.GET.get('prioridade', '').strip()
    tag_filtro = request.GET.get('tag', '').strip()
    setor_filtro = request.GET.get('setor', '').strip()
    data_inicio = request.GET.get('data_inicio', '').strip()
    data_fim = request.GET.get('data_fim', '').strip()
    ordenacao = request.GET.get('ordem', '-data_abertura').strip()

    base_qs = ProcessoSEI.objects.all()

    # Contadores gerais (base não filtrada)
    total_geral = base_qs.count()
    total_em_andamento = base_qs.filter(status='em_andamento').count()
    total_aguardando = base_qs.filter(status='aguardando_resposta').count()
    total_sob_analise = base_qs.filter(status='sob_analise').count()
    total_concluidos = base_qs.filter(status='concluido').count()
    total_urgentes = base_qs.filter(prioridade='urgente').exclude(status='concluido').count()

    queryset = base_qs

    # 1. Filtro por Tipo / Categoria
    if tipo_filtro and tipo_filtro != 'todos':
        queryset = queryset.filter(tipo=tipo_filtro)

    # 2. Filtro por Status
    if status_filtro and status_filtro != 'todos':
        queryset = queryset.filter(status=status_filtro)

    # 3. Filtro por Prioridade
    if prioridade_filtro and prioridade_filtro != 'todos':
        queryset = queryset.filter(prioridade=prioridade_filtro)

    # 4. Filtro por Tag / Palavra-chave específica
    if tag_filtro:
        queryset = queryset.filter(palavras_chave__icontains=tag_filtro)

    # 5. Filtro por Setor
    if setor_filtro:
        queryset = queryset.filter(setor_atual__icontains=setor_filtro)

    # 6. Filtro por Período de Abertura
    if data_inicio:
        queryset = queryset.filter(data_abertura__gte=data_inicio)
    if data_fim:
        queryset = queryset.filter(data_abertura__lte=data_fim)

    # 7. Busca Textual Ampla
    if q:
        queryset = queryset.filter(
            Q(numero_sei__icontains=q) |
            Q(titulo__icontains=q) |
            Q(palavras_chave__icontains=q) |
            Q(descricao__icontains=q) |
            Q(interessado__icontains=q) |
            Q(setor_atual__icontains=q)
        )

    # 8. Ordenação
    ordenacoes_validas = {
        '-data_abertura': '-data_abertura',
        'data_abertura': 'data_abertura',
        'titulo': 'titulo',
        '-atualizado_em': '-atualizado_em',
        'prioridade': 'prioridade',
    }
    campo_ordem = ordenacoes_validas.get(ordenacao, '-data_abertura')
    queryset = queryset.order_by(campo_ordem, '-id')

    # Extrair lista de setores cadastrados e nuvem de palavras-chave para sugestões
    setores_cadastrados = base_qs.exclude(setor_atual='').values_list('setor_atual', flat=True).distinct().order_by('setor_atual')
    
    # Coletar tags mais utilizadas
    todas_tags = []
    for proc in base_qs.only('palavras_chave'):
        todas_tags.extend(proc.palavras_chave_lista)
    
    # Contagem rápida das tags mais frequentes
    from collections import Counter
    tags_contadas = [tag for tag, _ in Counter(todas_tags).most_common(12)]

    tem_filtros_ativos = bool(
        q or (tipo_filtro and tipo_filtro != 'todos') or 
        (status_filtro and status_filtro != 'todos') or 
        (prioridade_filtro and prioridade_filtro != 'todos') or 
        tag_filtro or setor_filtro or data_inicio or data_fim
    )

    context = {
        'processos': queryset,
        'q': q,
        'tipo_filtro': tipo_filtro,
        'status_filtro': status_filtro,
        'prioridade_filtro': prioridade_filtro,
        'tag_filtro': tag_filtro,
        'setor_filtro': setor_filtro,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'ordenacao': ordenacao,
        'tem_filtros_ativos': tem_filtros_ativos,
        'total_filtrados': queryset.count(),
        'tipos_choices': ProcessoSEI.TIPO_CHOICES,
        'status_choices': ProcessoSEI.STATUS_CHOICES,
        'prioridade_choices': ProcessoSEI.PRIORIDADE_CHOICES,
        'setores_cadastrados': setores_cadastrados,
        'tags_populares': tags_contadas,
        'total_geral': total_geral,
        'total_em_andamento': total_em_andamento,
        'total_aguardando': total_aguardando,
        'total_sob_analise': total_sob_analise,
        'total_concluidos': total_concluidos,
        'total_urgentes': total_urgentes,
    }
    return render(request, 'processos/listar_processos.html', context)



@login_required
@verificar_primeiro_acesso
@gestao_processos_required
def view_criar_processo(request):
    """Cadastro de um novo processo SEI."""
    if request.method == 'POST':
        form = ProcessoSEIForm(request.POST)
        if form.is_valid():
            processo = form.save(commit=False)
            processo.criado_por = request.user
            processo.save()
            messages.success(request, f'Processo {processo.numero_sei} cadastrado com sucesso!')
            return redirect('detalhe_processo', pk=processo.pk)
    else:
        form = ProcessoSEIForm()

    return render(request, 'processos/form_processo.html', {
        'form': form,
        'titulo_pagina': 'Novo Processo SEI',
        'acao': 'Cadastrar'
    })


@login_required
@verificar_primeiro_acesso
@gestao_processos_required
def view_detalhe_processo(request, pk):
    """Visualização dos detalhes do processo SEI e histórico de andamentos."""
    processo = get_object_or_404(ProcessoSEI, pk=pk)
    andamentos = processo.andamentos.all()
    form_andamento = AndamentoProcessoForm()

    return render(request, 'processos/detalhe_processo.html', {
        'processo': processo,
        'andamentos': andamentos,
        'form_andamento': form_andamento,
    })


@login_required
@verificar_primeiro_acesso
@gestao_processos_required
def view_editar_processo(request, pk):
    """Edição dos dados de um processo SEI."""
    processo = get_object_or_404(ProcessoSEI, pk=pk)

    if request.method == 'POST':
        form = ProcessoSEIForm(request.POST, instance=processo)
        if form.is_valid():
            processo = form.save()
            messages.success(request, f'Processo {processo.numero_sei} atualizado com sucesso!')
            return redirect('detalhe_processo', pk=processo.pk)
    else:
        form = ProcessoSEIForm(instance=processo)

    return render(request, 'processos/form_processo.html', {
        'form': form,
        'processo': processo,
        'titulo_pagina': f'Editar Processo {processo.numero_sei}',
        'acao': 'Salvar Alterações'
    })


@login_required
@verificar_primeiro_acesso
@gestao_processos_required
def view_adicionar_andamento(request, pk):
    """Adiciona uma movimentação/despacho ao histórico do processo."""
    processo = get_object_or_404(ProcessoSEI, pk=pk)

    if request.method == 'POST':
        form = AndamentoProcessoForm(request.POST)
        if form.is_valid():
            andamento = form.save(commit=False)
            andamento.processo = processo
            andamento.registrado_por = request.user
            andamento.save()

            # Se informou novo setor no andamento, atualiza opcionalmente o setor_atual do processo
            novo_setor = form.cleaned_data.get('setor')
            if novo_setor and novo_setor.strip():
                processo.setor_atual = novo_setor.strip()
                processo.save(update_fields=['setor_atual', 'atualizado_em'])

            messages.success(request, 'Andamento registrado com sucesso!')
        else:
            messages.error(request, 'Erro ao registrar andamento. Verifique os campos.')

    return redirect('detalhe_processo', pk=processo.pk)


@login_required
@verificar_primeiro_acesso
@gestao_processos_required
def view_excluir_processo(request, pk):
    """Exclusão de processo SEI com confirmação."""
    processo = get_object_or_404(ProcessoSEI, pk=pk)

    if request.method == 'POST':
        numero = processo.numero_sei
        processo.delete()
        messages.success(request, f'Processo {numero} excluído com sucesso.')
        return redirect('listar_processos')

    return render(request, 'processos/confirmar_exclusao.html', {'processo': processo})
