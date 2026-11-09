from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
import json
import re

from .models import ConfiguracaoCarteira, CarteiraEstudanteEmitida, gerar_codigo_autenticidade
from .utils import (
    gerar_qrcode_base64,
    gerar_codigo_barras_svg,
    obter_assinatura_base64,
    obter_brasao_base64
)


def pagina_publica_carteira(request):
    """
    Página pública para os funcionários terceirizados e secretaria.
    Permite emissão da carteira com a chancela digital da Direção
    e disponibiliza o instalador do 'Botão Mágico' (Bookmarklet de 1 clique).
    """
    config = ConfiguracaoCarteira.get_config()
    
    # URL base para o Bookmarklet
    host = request.build_absolute_uri('/')[:-1]

    context = {
        'config': config,
        'host': host,
    }
    return render(request, 'carteiras/publica_emissao.html', context)


@csrf_exempt
def emitir_carteira_api(request):
    """
    API pública para registrar a emissão da carteirinha e gerar o código de autenticidade.
    Aceita requisições do formulário web ou do Bookmarklet de 1 clique no SCA CECIERJ.
    """
    config = ConfiguracaoCarteira.get_config()
    if not config.emissao_publica_ativa:
        return JsonResponse({
            'sucesso': False,
            'erro': config.aviso_manutencao or 'Emissões temporariamente suspensas pela Direção.'
        }, status=403)

    if request.method != 'POST':
        return JsonResponse({'sucesso': False, 'erro': 'Método não permitido.'}, status=405)

    try:
        if request.content_type and 'application/json' in request.content_type:
            data = json.loads(request.body.decode('utf-8'))
        else:
            data = request.POST.dict()

        matricula = data.get('matricula', '').strip()
        nome_aluno = data.get('nome_aluno', '').strip().upper()
        nome_operador = data.get('nome_operador', '').strip()

        if not matricula or not nome_aluno:
            return JsonResponse({
                'sucesso': False,
                'erro': 'Matrícula e Nome do Aluno são obrigatórios.'
            }, status=400)

        if not nome_operador:
            nome_operador = 'Secretaria / Terceirizado'

        # Obter IP de origem
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '')).split(',')[0].strip()
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        curso = data.get('curso', 'Ensino Médio').strip()
        unidade = data.get('unidade', '11802310502 - Ensino Médio').strip()
        email_aluno = data.get('email_aluno', '').strip()
        data_nascimento = data.get('data_nascimento', '').strip()
        data_validade = data.get('data_validade', '').strip()
        filiacao = data.get('filiacao', '').strip()
        foto_base64_ou_url = data.get('foto_base64_ou_url', '').strip()

        # Cria o registro no banco de dados
        carteira = CarteiraEstudanteEmitida.objects.create(
            codigo_autenticidade=gerar_codigo_autenticidade(),
            matricula=matricula,
            nome_aluno=nome_aluno,
            curso=curso,
            unidade=unidade,
            email_aluno=email_aluno,
            data_nascimento=data_nascimento,
            data_validade=data_validade,
            filiacao=filiacao,
            foto_base64_ou_url=foto_base64_ou_url,
            nome_operador=nome_operador,
            ip_origem=ip,
            user_agent=user_agent,
            criado_em=timezone.now(),
            ativo=True
        )

        return JsonResponse({
            'sucesso': True,
            'codigo': carteira.codigo_autenticidade,
            'redirect_url': f"/carteira/imprimir/{carteira.codigo_autenticidade}/?auto_print=1"
        })

    except Exception as e:
        return JsonResponse({'sucesso': False, 'erro': str(e)}, status=500)


def imprimir_carteira(request, codigo):
    """
    Renderiza a carteirinha de estudante nas dimensões exatas de 17 cm x 7 cm,
    com a assinatura oficial do Diretor Silvio sobre a linha da Direção
    e a aba oculta com QR Code e dados de autenticação.
    """
    carteira = get_object_or_404(CarteiraEstudanteEmitida, codigo_autenticidade=codigo)
    config = ConfiguracaoCarteira.get_config()

    # URL absoluta para validação do QR Code
    url_validacao = request.build_absolute_uri(f"/carteira/validar/{carteira.codigo_autenticidade}/")
    qr_b64 = gerar_qrcode_base64(url_validacao)
    barcode_svg = gerar_codigo_barras_svg(carteira.matricula)
    assinatura_b64 = obter_assinatura_base64()
    brasao_b64 = obter_brasao_base64()

    auto_print = request.GET.get('auto_print') == '1'

    context = {
        'carteira': carteira,
        'config': config,
        'url_validacao': url_validacao,
        'qr_b64': qr_b64,
        'barcode_svg': barcode_svg,
        'assinatura_b64': assinatura_b64,
        'brasao_b64': brasao_b64,
        'auto_print': auto_print,
    }
    return render(request, 'carteiras/imprimir_carteira.html', context)


def validar_carteira_publica(request, codigo):
    """
    Página pública de validação acessada via QR Code por fiscais, instituições ou alunos.
    Mostra o status de autenticidade emitido pela Direção.
    """
    carteira = CarteiraEstudanteEmitida.objects.filter(codigo_autenticidade=codigo).first()
    config = ConfiguracaoCarteira.get_config()

    context = {
        'carteira': carteira,
        'codigo_buscado': codigo,
        'config': config,
    }
    return render(request, 'carteiras/validar_publico.html', context)


@login_required
def painel_auditoria_diretor(request):
    """
    Painel restrito para o Diretor acompanhar todas as carteirinhas emitidas
    pelos terceirizados, com filtros, histórico e controle geral (Ligar/Pausar).
    """
    if getattr(request.user, 'perfil', '') != 'diretor' and not request.user.is_superuser:
        messages.error(request, 'Acesso restrito à Direção do CEJA.')
        return redirect('dashboard')

    config = ConfiguracaoCarteira.get_config()

    # Toggle de status
    if request.method == 'POST' and 'toggle_emissao' in request.POST:
        config.emissao_publica_ativa = not config.emissao_publica_ativa
        config.save()
        status_txt = "ATIVADA" if config.emissao_publica_ativa else "PAUSADA"
        messages.success(request, f"Emissão pública de carteirinhas {status_txt} com sucesso!")
        return redirect('carteiras_auditoria')

    # Revogar carteira
    if request.method == 'POST' and 'revogar_codigo' in request.POST:
        cod = request.POST.get('revogar_codigo')
        motivo = request.POST.get('motivo_cancelamento', 'Revogado pela Direção')
        item = CarteiraEstudanteEmitida.objects.filter(codigo_autenticidade=cod).first()
        if item:
            item.ativo = False
            item.motivo_cancelamento = motivo
            item.cancelado_por = request.user
            item.cancelado_em = timezone.now()
            item.save()
            messages.warning(request, f"Carteira {cod} revogada!")
        return redirect('carteiras_auditoria')

    q = request.GET.get('q', '').strip()
    itens = CarteiraEstudanteEmitida.objects.all()
    if q:
        itens = itens.filter(matricula__icontains=q) | itens.filter(nome_aluno__icontains=q) | itens.filter(codigo_autenticidade__icontains=q)

    context = {
        'config': config,
        'itens': itens[:100],
        'total_emitidas': CarteiraEstudanteEmitida.objects.count(),
        'total_ativas': CarteiraEstudanteEmitida.objects.filter(ativo=True).count(),
        'q': q,
    }
    return render(request, 'carteiras/auditoria_diretor.html', context)


def bookmarklet_js(request):
    """
    Entrega o script JavaScript do Bookmarklet dinâmico para a secretaria.
    Puxa os dados direto do SCA CECIERJ e envia para a chancela do CEJA.
    """
    host = request.build_absolute_uri('/')[:-1]
    js_code = f"""(function(){{
    var host = "{host}";
    
    // Verifica se está na página de carteirinha do CECIERJ ou similar
    var doc = document;
    var bodyText = doc.body.innerText || '';
    
    // Captura dados do aluno na tela do SCA
    function extrair(regex) {{
        var m = bodyText.match(regex);
        return m ? m[1].trim() : '';
    }}
    
    var matricula = extrair(/Matr[íi]cula[:\\s]+([0-9]+)/i);
    var nome = extrair(/Nome[:\\s]+([^\\n\\r]+)/i);
    var email = extrair(/E-mail do Aluno[:\\s]+([^\\n\\r]+)/i);
    var nascimento = extrair(/Nascimento[:\\s]+([0-9\\/]+)/i);
    var validade = extrair(/Validade[:\\s]+([0-9\\/]+)/i);
    var filiacao = extrair(/Filia[çc][ãa]o[:\\s]+([^\\n\\r]+)/i);
    var curso = extrair(/U\\.A\\.:[^\\n\\r]+-\\s*([^\\n\\r]+)/i) || 'Ensino Médio';
    
    // Captura foto do aluno
    var fotoUrl = '';
    var imgs = doc.querySelectorAll('img');
    for (var i = 0; i < imgs.length; i++) {{
        var src = imgs[i].src || '';
        if (src.indexOf('foto') !== -1 || src.indexOf('aluno') !== -1 || src.indexOf('declaracao') !== -1) {{
            fotoUrl = src;
            break;
        }}
    }}
    if (!fotoUrl && imgs.length > 2) {{
        fotoUrl = imgs[2].src; // geralmente a foto do aluno
    }}

    // Nome do operador (salvo no navegador para não precisar digitar sempre)
    var operador = localStorage.getItem('ceja_operador_carteira') || '';
    if (!operador) {{
        operador = prompt('Informe seu Nome (Operador da Secretaria / Terceirizado):', '');
        if (operador) {{
            localStorage.setItem('ceja_operador_carteira', operador);
        }}
    }}
    if (!operador) {{
        operador = 'Secretaria / Apoio';
    }}

    if (!matricula || !nome) {{
        alert('⚠️ Não foi possível identificar os dados da carteirinha nesta página.\\nCertifique-se de estar com a carteira de estudante aberta no SCA do CECIERJ.');
        return;
    }}

    // Cria formulário invisível para postar e abrir a impressão
    var form = doc.createElement('form');
    form.method = 'POST';
    form.action = host + '/carteira/emitir/';
    form.target = '_blank';

    function addInput(nomeCampo, valor) {{
        var inp = doc.createElement('input');
        inp.type = 'hidden';
        inp.name = nomeCampo;
        inp.value = valor || '';
        form.appendChild(inp);
    }}

    addInput('matricula', matricula);
    addInput('nome_aluno', nome);
    addInput('email_aluno', email);
    addInput('data_nascimento', nascimento);
    addInput('data_validade', validade);
    addInput('filiacao', filiacao);
    addInput('curso', curso);
    addInput('foto_base64_ou_url', fotoUrl);
    addInput('nome_operador', operador);

    doc.body.appendChild(form);
    form.submit();
    doc.body.removeChild(form);
}})();"""
    return HttpResponse(js_code, content_type='application/javascript; charset=utf-8')
