import json
import os
import tempfile
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .decoradores import diretor_required
from .models import DocumentoCerebro, FragmentoConhecimento, ConversaCerebro, MensagemCerebro
from .forms import DocumentoCerebroForm
from .extratores import processar_arquivo_documento, dividir_em_fragmentos
from .servicos_ia import gerar_resposta_beth, processar_audio_para_texto, obter_cliente_gemini


@diretor_required
def chat_view(request, conversa_id=None):
    """
    Interface principal do Chat com a Orientadora Virtual Beth.
    """
    conversas = ConversaCerebro.objects.filter(usuario=request.user).order_by('-atualizado_em')
    
    conversa_ativa = None
    if conversa_id:
        conversa_ativa = get_object_or_404(ConversaCerebro, id=conversa_id, usuario=request.user)
    elif conversas.exists():
        conversa_ativa = conversas.first()
    else:
        # Criar primeira conversa automaticamente
        conversa_ativa = ConversaCerebro.objects.create(
            usuario=request.user,
            titulo='Orientação Inicial'
        )
        
    mensagens = conversa_ativa.mensagens.all().order_by('criado_em') if conversa_ativa else []
    total_docs_vigentes = DocumentoCerebro.objects.filter(status='vigente').count()
    
    context = {
        'conversas': conversas,
        'conversa_ativa': conversa_ativa,
        'mensagens': mensagens,
        'total_docs_vigentes': total_docs_vigentes,
        'tem_gemini_key': bool(obter_cliente_gemini()),
    }
    return render(request, 'cerebro/chat.html', context)


@diretor_required
def nova_conversa(request):
    """Cria uma nova sessão de conversa vazia."""
    conversa = ConversaCerebro.objects.create(
        usuario=request.user,
        titulo='Nova Consulta'
    )
    return redirect('cerebro_chat_conversa', conversa_id=conversa.id)


@diretor_required
@require_POST
def enviar_mensagem_api(request):
    """
    Endpoint AJAX para envio de perguntas (texto ou áudio transcrito) para a Beth.
    """
    try:
        data = json.loads(request.body)
        conversa_id = data.get('conversa_id')
        conteudo = data.get('mensagem', '').strip()
        tipo_entrada = data.get('tipo_entrada', 'texto')

        if not conteudo:
            return JsonResponse({'sucesso': False, 'erro': 'A mensagem não pode estar vazia.'}, status=400)

        conversa = get_object_or_404(ConversaCerebro, id=conversa_id, usuario=request.user)

        # Atualizar título da conversa se for a primeira mensagem
        if conversa.mensagens.count() == 0:
            titulo_resumido = conteudo[:45] + ('...' if len(conteudo) > 45 else '')
            conversa.titulo = titulo_resumido
            conversa.save(update_fields=['titulo'])

        # Salvar mensagem do Diretor
        msg_usuario = MensagemCerebro.objects.create(
            conversa=conversa,
            remetente='usuario',
            conteudo=conteudo,
            tipo_entrada=tipo_entrada
        )

        # Obter resposta da IA Beth
        resultado_ia = gerar_resposta_beth(conteudo)
        resposta_beth = resultado_ia.get('resposta', '')
        fontes = resultado_ia.get('fontes', [])

        # Salvar resposta da Beth
        msg_beth = MensagemCerebro.objects.create(
            conversa=conversa,
            remetente='beth',
            conteudo=resposta_beth,
            fontes_consultadas=fontes
        )

        conversa.save(update_fields=['atualizado_em'])

        return JsonResponse({
            'sucesso': True,
            'resposta': resposta_beth,
            'fontes': fontes,
            'hora': msg_beth.criado_em.strftime('%H:%M'),
        })

    except Exception as e:
        return JsonResponse({'sucesso': False, 'erro': str(e)}, status=500)


@diretor_required
@require_POST
def transcrever_audio_api(request):
    """
    Recebe um arquivo de áudio gravado no microfone do navegador e transcreve.
    """
    if 'audio' not in request.FILES:
        return JsonResponse({'sucesso': False, 'erro': 'Nenhum arquivo de áudio enviado.'}, status=400)

    audio_file = request.FILES['audio']
    ext = os.path.splitext(audio_file.name)[1] or '.webm'
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_audio:
        for chunk in audio_file.chunks():
            temp_audio.write(chunk)
        temp_audio_path = temp_audio.name

    try:
        transcricao = processar_audio_para_texto(temp_audio_path)
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

        if not transcricao:
            return JsonResponse({'sucesso': False, 'erro': 'Não foi possível transcrever o áudio gravado.'})

        return JsonResponse({'sucesso': True, 'transcricao': transcricao})
    except Exception as e:
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        return JsonResponse({'sucesso': False, 'erro': str(e)}, status=500)


@diretor_required
def listar_documentos(request):
    """
    Acervo da Base de Conhecimento do Cérebro.
    """
    status_filtro = request.GET.get('status', 'todos')
    categoria_filtro = request.GET.get('categoria', '')
    busca = request.GET.get('q', '').strip()

    documentos = DocumentoCerebro.objects.all().select_related('documento_substituido', 'criado_por')

    if status_filtro and status_filtro != 'todos':
        documentos = documentos.filter(status=status_filtro)
    if categoria_filtro:
        documentos = documentos.filter(categoria=categoria_filtro)
    if busca:
        documentos = documentos.filter(titulo__icontains=busca) | documentos.filter(numero_normativa__icontains=busca)

    total_vigentes = DocumentoCerebro.objects.filter(status='vigente').count()
    total_substituidos = DocumentoCerebro.objects.filter(status='substituido').count()

    context = {
        'documentos': documentos,
        'status_filtro': status_filtro,
        'categoria_filtro': categoria_filtro,
        'busca': busca,
        'total_vigentes': total_vigentes,
        'total_substituidos': total_substituidos,
        'total_geral': DocumentoCerebro.objects.count(),
        'categorias': DocumentoCerebro.CATEGORIA_CHOICES,
    }
    return render(request, 'cerebro/documentos.html', context)


@diretor_required
def upload_documento(request):
    """
    Upload de arquivos ou cadastro de notas diretas para alimentar o cérebro.
    """
    if request.method == 'POST':
        form = DocumentoCerebroForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.criado_por = request.user
            doc.save()

            # Extração de texto automática
            texto_extraido = processar_arquivo_documento(doc)
            if texto_extraido and not doc.conteudo_extraido:
                doc.conteudo_extraido = texto_extraido
                doc.save(update_fields=['conteudo_extraido', 'tipo_arquivo'])

            # Se for áudio, tentar transcrição imediata
            if doc.tipo_arquivo == 'audio' and doc.arquivo:
                try:
                    transcricao = processar_audio_para_texto(doc.arquivo.path)
                    if transcricao:
                        doc.conteudo_extraido = transcricao
                        doc.save(update_fields=['conteudo_extraido'])
                except Exception as e:
                    print(f"Erro ao processar áudio: {e}")

            # Criar fragmentos para RAG
            FragmentoConhecimento.objects.filter(documento=doc).delete()
            chunks = dividir_em_fragmentos(doc.conteudo_extraido)
            for idx, chunk in enumerate(chunks):
                FragmentoConhecimento.objects.create(
                    documento=doc,
                    texto=chunk,
                    indice_ordem=idx
                )

            # Notificação de substituição automática
            if doc.documento_substituido:
                messages.success(
                    request,
                    f'Documento "{doc.titulo}" cadastrado com sucesso! A norma anterior "{doc.documento_substituido.titulo}" foi automaticamente marcada como Substituída/Revogada.'
                )
            else:
                messages.success(request, f'Documento "{doc.titulo}" adicionado à base de conhecimento da Beth!')

            return redirect('cerebro_documentos')
    else:
        form = DocumentoCerebroForm()

    return render(request, 'cerebro/upload.html', {'form': form})


@diretor_required
def detalhe_documento(request, doc_id):
    """
    Visualização e edição rápida do documento e seu conteúdo extraído.
    """
    doc = get_object_or_404(DocumentoCerebro, id=doc_id)
    if request.method == 'POST':
        form = DocumentoCerebroForm(request.POST, request.FILES, instance=doc)
        if form.is_valid():
            form.save()
            messages.success(request, 'Documento atualizado com sucesso!')
            return redirect('cerebro_documentos')
    else:
        form = DocumentoCerebroForm(instance=doc)

    return render(request, 'cerebro/detalhe_documento.html', {'doc': doc, 'form': form})


@diretor_required
def excluir_documento(request, doc_id):
    """Exclui um documento da base do Cérebro."""
    doc = get_object_or_404(DocumentoCerebro, id=doc_id)
    titulo = doc.titulo
    doc.delete()
    messages.success(request, f'Documento "{titulo}" removido do Cérebro.')
    return redirect('cerebro_documentos')


@diretor_required
def reprocessar_documento(request, doc_id):
    """Reprocessa a extração e fragmentação de um documento existente."""
    doc = get_object_or_404(DocumentoCerebro, id=doc_id)
    texto = processar_arquivo_documento(doc)
    doc.conteudo_extraido = texto
    doc.save(update_fields=['conteudo_extraido', 'tipo_arquivo'])

    FragmentoConhecimento.objects.filter(documento=doc).delete()
    chunks = dividir_em_fragmentos(texto)
    for idx, chunk in enumerate(chunks):
        FragmentoConhecimento.objects.create(
            documento=doc,
            texto=chunk,
            indice_ordem=idx
        )

    messages.success(request, f'Documento "{doc.titulo}" reprocessado com sucesso ({len(chunks)} fragmentos gerados).')
    return redirect('cerebro_documentos')
