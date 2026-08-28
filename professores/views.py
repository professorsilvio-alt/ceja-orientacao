from datetime import time
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import models
from django.db.models import Q
from usuarios.views import diretor_required, verificar_primeiro_acesso
from .models import (
    Professor, HorarioProfessor, ConfiguracaoEscola, DisciplinaOfertada, 
    Disciplina, UnidadeEscolar, TurmaComponente, AlocacaoHorarioTurma, 
    recalcular_classificacao_professores
)
from .forms import (
    ProfessorForm, HorarioProfessorForm, ConfiguracaoEscolaForm, 
    UnidadeEscolarForm, TurmaComponenteForm
)


@login_required
@verificar_primeiro_acesso
def view_listar_professores(request):
    import re
    recalcular_classificacao_professores()

    status_filtro = request.GET.get('status', 'ativos')
    q = request.GET.get('q', '').strip()
    cpf_limpo = re.sub(r'\D', '', q)

    # Contadores
    total_ativos = Professor.objects.filter(ativo=True, situacao_matricula_1='ativo').count()
    total_inativos = Professor.objects.filter(
        models.Q(ativo=False) | ~models.Q(situacao_matricula_1='ativo')
    ).count()
    total_geral = Professor.objects.count()

    if status_filtro == 'inativos':
        professores = Professor.objects.filter(
            models.Q(ativo=False) | ~models.Q(situacao_matricula_1='ativo')
        ).order_by('nome_completo')
    elif status_filtro == 'todos':
        professores = Professor.objects.all().order_by('nome_completo')
    else:
        # Padrão: Apenas ativos na escola
        professores = Professor.objects.filter(
            ativo=True, situacao_matricula_1='ativo'
        ).order_by('classificacao')

    if q:
        query_filter = Q(nome_completo__icontains=q) | \
                       Q(matricula__icontains=q) | \
                       Q(matricula_acumulacao__icontains=q) | \
                       Q(id_vinculo__icontains=q) | \
                       Q(id_vinculo_acumulacao__icontains=q) | \
                       Q(cargo__icontains=q) | \
                       Q(disciplina_ingresso__icontains=q)
        if cpf_limpo:
            query_filter |= Q(cpf__icontains=cpf_limpo)
        professores = professores.filter(query_filter)

    return render(request, 'professores/listar.html', {
        'professores': professores,
        'status_filtro': status_filtro,
        'query': q,
        'total_ativos': total_ativos,
        'total_inativos': total_inativos,
        'total_geral': total_geral,
        'total': professores.count(),
    })


@diretor_required
def view_criar_professor(request):
    form = ProfessorForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        professor = form.save()
        recalcular_classificacao_professores()
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

    # Dados da Pasta Digital
    from django.contrib.contenttypes.models import ContentType
    from .models import DocumentoServidor, OcorrenciaFolgaServidor, AnotacaoServidor
    ct = ContentType.objects.get_for_model(Professor)

    documentos = DocumentoServidor.objects.filter(content_type=ct, object_id=professor.pk)
    folgas = OcorrenciaFolgaServidor.objects.filter(content_type=ct, object_id=professor.pk)
    anotacoes = AnotacaoServidor.objects.filter(content_type=ct, object_id=professor.pk)

    total_creditos = sum(f.dias for f in folgas if f.tipo == 'credito')
    total_usufruidos = sum(f.dias for f in folgas if f.tipo == 'usufruido')
    saldo_folgas = total_creditos - total_usufruidos

    return render(request, 'professores/detalhe.html', {
        'professor': professor,
        'horarios': horarios,
        'documentos': documentos,
        'folgas': folgas,
        'anotacoes': anotacoes,
        'saldo_folgas': saldo_folgas,
        'total_creditos': total_creditos,
        'total_usufruidos': total_usufruidos,
        'tipo_servidor': 'professor',
    })


# ── VIEWS DA PASTA DIGITAL DO SERVIDOR (DOCUMENTOS, FOLGAS, ANOTAÇÕES) ──────

@login_required
def view_adicionar_documento_servidor(request, tipo_servidor, pk):
    """Adiciona documento (atestado, licença, CI) à pasta digital do servidor."""
    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        categoria = request.POST.get('categoria', 'documento')
        data_documento = request.POST.get('data_documento') or timezone.now().date()
        observacoes = request.POST.get('observacoes', '').strip()
        arquivo = request.FILES.get('arquivo')

        if not titulo or not arquivo:
            messages.error(request, 'Por favor, informe o título e selecione o arquivo.')
            return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

        if tipo_servidor == 'professor':
            model_cls = Professor
        elif tipo_servidor == 'adm':
            from funcionarios.models import FuncionarioAdministrativo
            model_cls = FuncionarioAdministrativo
        elif tipo_servidor == 'terc':
            from funcionarios.models import FuncionarioTerceirizado
            model_cls = FuncionarioTerceirizado
        else:
            messages.error(request, 'Tipo de servidor inválido.')
            return redirect('dashboard')

        from django.contrib.contenttypes.models import ContentType
        from .models import DocumentoServidor
        servidor = get_object_or_404(model_cls, pk=pk)
        ct = ContentType.objects.get_for_model(model_cls)

        DocumentoServidor.objects.create(
            content_type=ct,
            object_id=servidor.pk,
            titulo=titulo,
            categoria=categoria,
            arquivo=arquivo,
            data_documento=data_documento,
            observacoes=observacoes,
            criado_por=request.user
        )
        messages.success(request, f'Documento "{titulo}" anexado à pasta com sucesso!')
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))


@login_required
def view_excluir_documento_servidor(request, pk):
    from .models import DocumentoServidor
    doc = get_object_or_404(DocumentoServidor, pk=pk)
    titulo = doc.titulo
    doc.delete()
    messages.success(request, f'Documento "{titulo}" removido.')
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))


@login_required
def view_adicionar_folga_servidor(request, tipo_servidor, pk):
    """Lança crédito ou uso de folga/banco de horas na pasta do servidor."""
    if request.method == 'POST':
        tipo = request.POST.get('tipo', 'credito')
        dias = request.POST.get('dias', '1.0')
        motivo = request.POST.get('motivo', '').strip()
        data_ocorrencia = request.POST.get('data_ocorrencia') or timezone.now().date()
        observacoes = request.POST.get('observacoes', '').strip()

        if not motivo:
            messages.error(request, 'Por favor, informe o motivo/origem do lançamento de folga.')
            return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

        if tipo_servidor == 'professor':
            model_cls = Professor
        elif tipo_servidor == 'adm':
            from funcionarios.models import FuncionarioAdministrativo
            model_cls = FuncionarioAdministrativo
        elif tipo_servidor == 'terc':
            from funcionarios.models import FuncionarioTerceirizado
            model_cls = FuncionarioTerceirizado
        else:
            messages.error(request, 'Tipo de servidor inválido.')
            return redirect('dashboard')

        from django.contrib.contenttypes.models import ContentType
        from .models import OcorrenciaFolgaServidor
        servidor = get_object_or_404(model_cls, pk=pk)
        ct = ContentType.objects.get_for_model(model_cls)

        OcorrenciaFolgaServidor.objects.create(
            content_type=ct,
            object_id=servidor.pk,
            tipo=tipo,
            dias=dias,
            motivo=motivo,
            data_ocorrencia=data_ocorrencia,
            observacoes=observacoes,
            criado_por=request.user
        )
        messages.success(request, 'Lançamento de folga registrado com sucesso!')
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))


@login_required
def view_excluir_folga_servidor(request, pk):
    from .models import OcorrenciaFolgaServidor
    folga = get_object_or_404(OcorrenciaFolgaServidor, pk=pk)
    folga.delete()
    messages.success(request, 'Lançamento de folga removido.')
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))


@login_required
def view_adicionar_anotacao_servidor(request, tipo_servidor, pk):
    """Adiciona uma anotação ao histórico da pasta do servidor."""
    if request.method == 'POST':
        texto = request.POST.get('texto', '').strip()
        if not texto:
            messages.error(request, 'Digite o texto da anotação.')
            return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

        if tipo_servidor == 'professor':
            model_cls = Professor
        elif tipo_servidor == 'adm':
            from funcionarios.models import FuncionarioAdministrativo
            model_cls = FuncionarioAdministrativo
        elif tipo_servidor == 'terc':
            from funcionarios.models import FuncionarioTerceirizado
            model_cls = FuncionarioTerceirizado
        else:
            messages.error(request, 'Tipo de servidor inválido.')
            return redirect('dashboard')

        from django.contrib.contenttypes.models import ContentType
        from .models import AnotacaoServidor
        servidor = get_object_or_404(model_cls, pk=pk)
        ct = ContentType.objects.get_for_model(model_cls)

        AnotacaoServidor.objects.create(
            content_type=ct,
            object_id=servidor.pk,
            texto=texto,
            criado_por=request.user
        )
        messages.success(request, 'Anotação salva na pasta do servidor.')
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))


@login_required
def view_editar_documento_servidor(request, pk):
    """Edita os dados de um documento/atestado na pasta digital do servidor."""
    from .models import DocumentoServidor
    doc = get_object_or_404(DocumentoServidor, pk=pk)
    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        categoria = request.POST.get('categoria', doc.categoria)
        data_documento = request.POST.get('data_documento') or doc.data_documento
        observacoes = request.POST.get('observacoes', '').strip()
        arquivo = request.FILES.get('arquivo')

        if not titulo:
            messages.error(request, 'O título não pode ficar em branco.')
            return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

        doc.titulo = titulo
        doc.categoria = categoria
        doc.data_documento = data_documento
        doc.observacoes = observacoes
        if arquivo:
            doc.arquivo = arquivo
        doc.save()
        messages.success(request, f'Documento "{titulo}" atualizado com sucesso!')
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))


@login_required
def view_editar_folga_servidor(request, pk):
    """Edita os dados de um lançamento de folga/compensação."""
    from .models import OcorrenciaFolgaServidor
    folga = get_object_or_404(OcorrenciaFolgaServidor, pk=pk)
    if request.method == 'POST':
        tipo = request.POST.get('tipo', folga.tipo)
        dias = request.POST.get('dias', folga.dias)
        motivo = request.POST.get('motivo', '').strip() or folga.motivo
        data_ocorrencia = request.POST.get('data_ocorrencia') or folga.data_ocorrencia
        observacoes = request.POST.get('observacoes', '').strip()

        folga.tipo = tipo
        folga.dias = dias
        folga.motivo = motivo
        folga.data_ocorrencia = data_ocorrencia
        folga.observacoes = observacoes
        folga.save()
        messages.success(request, 'Lançamento de folga atualizado com sucesso!')
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))


@login_required
def view_editar_anotacao_servidor(request, pk):
    """Edita o texto de uma anotação na pasta do servidor."""
    from .models import AnotacaoServidor
    note = get_object_or_404(AnotacaoServidor, pk=pk)
    if request.method == 'POST':
        texto = request.POST.get('texto', '').strip()
        if not texto:
            messages.error(request, 'A anotação não pode ficar em branco.')
            return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

        note.texto = texto
        note.save()
        messages.success(request, 'Anotação atualizada com sucesso!')
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))


@login_required
def view_excluir_anotacao_servidor(request, pk):
    """Remove uma anotação da pasta do servidor."""
    from .models import AnotacaoServidor
    note = get_object_or_404(AnotacaoServidor, pk=pk)
    note.delete()
    messages.success(request, 'Anotação removida da pasta.')
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))


@diretor_required
def view_editar_professor(request, pk):
    professor = get_object_or_404(Professor, pk=pk)
    form = ProfessorForm(request.POST or None, request.FILES or None, instance=professor)
    if request.method == 'POST' and form.is_valid():
        form.save()
        recalcular_classificacao_professores()
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
            config = form.save(commit=False)
            config.unidade = unidade_atual
            config.save()
            
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

                # Sincroniza os tempos requeridos nas turmas atreladas a esta disciplina ofertada
                TurmaComponente.objects.filter(configuracao=config, disciplina_ofertada=of).update(tempos_requeridos=of.horas_aula_semanais)

            messages.success(request, f'Configurações de {unidade_atual.nome} ({config.ano_letivo}) salvas com sucesso!')
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


# ── Módulo de Quadro de Horários & Alocação ────────────────────────────────────

@diretor_required
def view_listar_quadro_horarios(request):
    """Painel principal do Quadro de Horários por Unidade e Ano Letivo."""
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

    ano_req = request.GET.get('ano') or timezone.now().year
    try:
        ano_req = int(ano_req)
    except ValueError:
        ano_req = timezone.now().year

    config, _ = ConfiguracaoEscola.objects.get_or_create(
        unidade=unidade_atual,
        ano_letivo=ano_req,
        defaults={'ativo': True, 'duracao_hora_aula': 50}
    )

    # Ação POST: Criar nova turma/componente
    if request.method == 'POST' and request.POST.get('action') == 'nova_turma':
        turma_form = TurmaComponenteForm(request.POST)
        if turma_form.is_valid():
            turma = turma_form.save(commit=False)
            turma.configuracao = config
            turma.save()
            messages.success(request, f'Turma/Componente "{turma.codigo_turma}" criada com sucesso!')
            return redirect(f'/professores/horarios/quadro/?unidade={unidade_atual.pk}&ano={config.ano_letivo}')
    # Ação POST: Gerar turmas automáticas a partir das disciplinas ofertadas
    elif request.method == 'POST' and request.POST.get('action') == 'gerar_automaticas':
        ofertas = DisciplinaOfertada.objects.filter(configuracao=config, ativo=True)
        criadas = 0
        for of in ofertas:
            cod_sugerido = f'CEJAS-{of.disciplina.nome[:3].upper()}'
            _, created = TurmaComponente.objects.get_or_create(
                configuracao=config,
                disciplina_ofertada=of,
                defaults={
                    'codigo_turma': cod_sugerido,
                    'area': of.disciplina.area or 'Geral',
                    'trilha_nucleo': 'COMPONENTE CURRICULAR',
                    'disciplina_nome': of.disciplina.nome,
                    'tempos_requeridos': of.horas_aula_semanais,
                }
            )
            if created:
                criadas += 1
        if criadas > 0:
            messages.success(request, f'{criadas} turma(s)/componente(s) gerada(s) com sucesso!')
        else:
            messages.info(request, 'Todas as disciplinas ofertadas já possuem turmas criadas.')
        return redirect(f'/professores/horarios/quadro/?unidade={unidade_atual.pk}&ano={config.ano_letivo}')
    else:
        turma_form = TurmaComponenteForm()

    turmas = TurmaComponente.objects.filter(configuracao=config).prefetch_related('alocacoes', 'alocacoes__professor')
    anos_cadastrados = ConfiguracaoEscola.objects.filter(unidade=unidade_atual).values_list('ano_letivo', flat=True).order_by('-ano_letivo')

    # Estatísticas
    total_turmas = turmas.count()
    turmas_ok = sum(1 for t in turmas if t.status_ok)
    turmas_pendentes = total_turmas - turmas_ok

    return render(request, 'professores/quadro_horarios_list.html', {
        'config': config,
        'unidades': unidades,
        'unidade_atual': unidade_atual,
        'anos_cadastrados': anos_cadastrados,
        'ano_selecionado': config.ano_letivo,
        'turmas': turmas,
        'turma_form': turma_form,
        'total_turmas': total_turmas,
        'turmas_ok': turmas_ok,
        'turmas_pendentes': turmas_pendentes,
    })


@diretor_required
def view_grade_turma(request, pk):
    """Tela interativa da Grade Horária de uma Turma/Componente."""
    turma = get_object_or_404(TurmaComponente, pk=pk)
    config = turma.configuracao
    unidade = config.unidade

    # Dias da semana configurados
    DIAS_MAP = [
        ('segunda', 'SEGUNDA', config.func_segunda, config.seg_abertura, config.seg_fechamento),
        ('terca', 'TERÇA', config.func_terca, config.ter_abertura, config.ter_fechamento),
        ('quarta', 'QUARTA', config.func_quarta, config.qua_abertura, config.qua_fechamento),
        ('quinta', 'QUINTA', config.func_quinta, config.qui_abertura, config.qui_fechamento),
        ('sexta', 'SEXTA', config.func_sexta, config.sex_abertura, config.sex_fechamento),
    ]
    if config.func_sabado:
        DIAS_MAP.append(('sabado', 'SÁBADO', True, config.sab_abertura, config.sab_fechamento))
    if config.func_domingo:
        DIAS_MAP.append(('domingo', 'DOMINGO', True, config.dom_abertura, config.dom_fechamento))

    # Intervalos padrão de 50 minutos
    SLOTS = [
        (time(8, 0), time(8, 50), "08:00 / 08:50"),
        (time(8, 50), time(9, 40), "08:50 / 09:40"),
        (time(9, 40), time(10, 30), "09:40 / 10:30"),
        (time(10, 30), time(11, 20), "10:30 / 11:20"),
        (time(11, 20), time(12, 10), "11:20 / 12:10"),
        (time(12, 10), time(13, 0), "12:10 / 13:00"),
        (time(13, 0), time(13, 50), "13:00 / 13:50"),
        (time(13, 50), time(14, 40), "13:50 / 14:40"),
        (time(14, 40), time(15, 30), "14:40 / 15:30"),
        (time(15, 30), time(16, 20), "15:30 / 16:20"),
        (time(16, 20), time(17, 10), "16:20 / 17:10"),
        (time(17, 10), time(18, 0), "17:10 / 18:00"),
        (time(18, 0), time(18, 50), "18:00 / 18:50"),
        (time(18, 50), time(19, 40), "18:50 / 19:40"),
        (time(19, 40), time(20, 30), "19:40 / 20:30"),
        (time(20, 30), time(21, 20), "20:30 / 21:20"),
    ]

    # Mapa de alocações existentes para esta turma
    aloca_qs = AlocacaoHorarioTurma.objects.filter(turma=turma).select_related('professor')
    alocs_dict = {}
    for al in aloca_qs:
        key = (al.dia_semana, al.hora_inicio.strftime("%H:%M"))
        alocs_dict[key] = al

    # Construção da matriz da grade
    grid = []
    for inicio, fim, label_horario in SLOTS:
        row_cells = []
        for dia_code, dia_nome, func_dia, abert, fech in DIAS_MAP:
            is_fechada = not func_dia or (inicio < abert or fim > fech)
            aloc = alocs_dict.get((dia_code, inicio.strftime("%H:%M")))

            row_cells.append({
                'dia_code': dia_code,
                'dia_nome': dia_nome,
                'hora_inicio': inicio.strftime("%H:%M"),
                'hora_fim': fim.strftime("%H:%M"),
                'is_fechada': is_fechada,
                'alocacao': aloc,
                'professor_nome': (aloc.rotulo_exibicao or (aloc.professor.nome_curto if aloc.professor else '')) if aloc else ''
            })
        grid.append({
            'label_horario': label_horario,
            'hora_inicio': inicio.strftime("%H:%M"),
            'hora_fim': fim.strftime("%H:%M"),
            'cells': row_cells
        })

    all_profs = Professor.objects.filter(ativo=True).order_by('nome_completo')
    disc_nome = (turma.disciplina_nome or '').lower()

    profs_da_disciplina = []
    outros_profs = []
    for p in all_profs:
        p_disc = (p.disciplina_ingresso or '').lower()
        if disc_nome and (disc_nome in p_disc or p_disc in disc_nome or any(w in disc_nome for w in p_disc.split() if len(w) > 3)):
            profs_da_disciplina.append(p)
        else:
            outros_profs.append(p)

    return render(request, 'professores/quadro_horarios_grade.html', {
        'turma': turma,
        'config': config,
        'unidade': unidade,
        'dias_map': DIAS_MAP,
        'grid': grid,
        'professores': all_profs,
        'profs_da_disciplina': profs_da_disciplina,
        'outros_profs': outros_profs,
    })


@diretor_required
def view_salvar_alocacao_slot(request, pk):
    """Salva ou remove a alocação de um professor em um slot da grade."""
    turma = get_object_or_404(TurmaComponente, pk=pk)
    if request.method == 'POST':
        dia_semana = request.POST.get('dia_semana')
        hora_inicio_str = request.POST.get('hora_inicio')
        hora_fim_str = request.POST.get('hora_fim')
        professor_id = request.POST.get('professor_id')
        rotulo_exibicao = request.POST.get('rotulo_exibicao', '').strip()

        if not dia_semana or not hora_inicio_str:
            return JsonResponse({'success': False, 'error': 'Parâmetros inválidos.'}, status=400)

        if not professor_id or professor_id == 'limpar':
            AlocacaoHorarioTurma.objects.filter(
                turma=turma, dia_semana=dia_semana, hora_inicio=hora_inicio_str
            ).delete()
            msg = 'Horário liberado.'
        else:
            prof = get_object_or_404(Professor, pk=professor_id)
            rotulo = rotulo_exibicao or prof.nome_curto.upper()

            aloc, _ = AlocacaoHorarioTurma.objects.update_or_create(
                turma=turma,
                dia_semana=dia_semana,
                hora_inicio=hora_inicio_str,
                defaults={
                    'hora_fim': hora_fim_str or hora_inicio_str,
                    'professor': prof,
                    'rotulo_exibicao': rotulo
                }
            )
            msg = f'Professor {rotulo} alocado no horário!'

        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('format') == 'json':
            return JsonResponse({
                'success': True,
                'message': msg,
                'tempos_alocados': turma.tempos_alocados,
                'tempos_requeridos': turma.tempos_requeridos,
                'status_display': turma.status_display,
                'status_ok': turma.status_ok,
                'professores_nomes': turma.professores_alocados_nomes,
            })

        messages.success(request, msg)
        return redirect('grade_turma', pk=turma.pk)

    return redirect('grade_turma', pk=turma.pk)


@diretor_required
def view_excluir_turma(request, pk):
    """Exclui uma Turma/Componente e suas alocações."""
    turma = get_object_or_404(TurmaComponente, pk=pk)
    unidade_pk = turma.configuracao.unidade.pk if turma.configuracao.unidade else ''
    ano = turma.configuracao.ano_letivo
    cod = turma.codigo_turma

    if request.method == 'POST':
        turma.delete()
        messages.success(request, f'Turma/Componente "{cod}" removida com sucesso.')

    return redirect(f'/professores/horarios/quadro/?unidade={unidade_pk}&ano={ano}')
