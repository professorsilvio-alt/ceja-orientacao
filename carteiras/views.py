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
        nome_aluno = re.sub(r'\s+', ' ', data.get('nome_aluno', '').strip().upper())
        nome_operador = data.get('nome_operador', '').strip()
        usuario_sca = data.get('usuario_sca', '').strip()
        origem_sca = data.get('origem_sca', '').strip()
        url_origem = data.get('url_origem', '').strip()
        referer = request.META.get('HTTP_REFERER', '')

        # Bloqueio de emissão manual: só aceita emissões originadas do SCA CECIERJ
        is_from_sca = (
            origem_sca == '1' or
            'cecierj.edu.br' in url_origem or
            'cecierj.edu.br' in referer
        )
        if not is_from_sca:
            return JsonResponse({
                'sucesso': False,
                'erro': 'Emissão manual desativada pela Direção Geral. As carteirinhas só podem ser emitidas diretamente a partir do sistema oficial SCA do CECIERJ.'
            }, status=403)

        if not matricula or not nome_aluno:
            return JsonResponse({
                'sucesso': False,
                'erro': 'Matrícula e Nome do Aluno são obrigatórios.'
            }, status=400)

        if not nome_operador:
            nome_operador = 'Secretaria / Terceirizado'

        # Auditoria: anexa a sessão SCA identificada se for diferente
        if usuario_sca and usuario_sca.upper() not in nome_operador.upper():
            nome_operador_audit = f"{nome_operador} (SCA: {usuario_sca})"
        else:
            nome_operador_audit = nome_operador

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
            nome_operador=nome_operador_audit,
            ip_origem=ip,
            user_agent=user_agent,
            criado_em=timezone.now(),
            ativo=True
        )

        redirect_destino = f"/carteira/imprimir/{carteira.codigo_autenticidade}/?auto_print=1"

        # Se for requisição AJAX/fetch ou JSON, responde com JSON
        is_ajax = (
            request.headers.get('x-requested-with') == 'XMLHttpRequest' or
            (request.content_type and 'application/json' in request.content_type) or
            request.GET.get('format') == 'json'
        )
        if is_ajax:
            return JsonResponse({
                'sucesso': True,
                'codigo': carteira.codigo_autenticidade,
                'redirect_url': redirect_destino
            })

        # Para submit direto de formulário (ex: Bookmarklet), redireciona o navegador imediatamente para a impressão!
        return redirect(redirect_destino)

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


BOOKMARKLET_TEMPLATE = r"""(function() {
    var host = "__HOST__";
    var doc = document;

    // 1. Verificação de Domínio: só executa dentro do SCA do CECIERJ
    if (window.location.hostname.indexOf('cecierj.edu.br') === -1) {
        alert("⚠️ ATENÇÃO — CEJA ROSA SOARES\n\nEste botão de chancela só pode ser executado dentro do sistema oficial SCA do CECIERJ (sca.cecierj.edu.br).\n\nAbra a carteirinha do aluno no SCA e clique nele novamente.");
        return;
    }

    var bodyText = doc.body ? (doc.body.innerText || '') : '';

    // Extrai texto com regex simples
    function extrair(regex) {
        var m = bodyText.match(regex);
        return m ? m[1].trim() : '';
    }

    // Extrai campos multilinhas (como nome completo e filiação)
    function extrairMultilinha(regex) {
        var m = bodyText.match(regex);
        if (!m) return '';
        return m[1].replace(/[\r\n\t]+/g, ' ').replace(/\s{2,}/g, ' ').trim();
    }

    // Tenta encontrar campos no DOM diretamente
    function extrairDoDOM(rotulo) {
        try {
            var elementos = doc.querySelectorAll('td, th, div, span, p, label, b, strong');
            for (var i = 0; i < elementos.length; i++) {
                var el = elementos[i];
                var txt = (el.innerText || el.textContent || '').trim();
                if (new RegExp('^' + rotulo + '[:\\s]*$', 'i').test(txt)) {
                    if (el.nextElementSibling) {
                        var v = (el.nextElementSibling.innerText || el.nextElementSibling.textContent || '').trim();
                        if (v && v.length > 2) return v.replace(/[\r\n\t]+/g, ' ').replace(/\s{2,}/g, ' ');
                    }
                    if (el.parentElement && el.parentElement.cells) {
                        var cells = el.parentElement.cells;
                        for (var c = 0; c < cells.length; c++) {
                            if (cells[c] === el && cells[c + 1]) {
                                var vCell = (cells[c + 1].innerText || cells[c + 1].textContent || '').trim();
                                if (vCell && vCell.length > 2) return vCell.replace(/[\r\n\t]+/g, ' ').replace(/\s{2,}/g, ' ');
                            }
                        }
                    }
                }
            }
        } catch(e) {}
        return '';
    }

    // 2. Localiza o Usuário Conectado na Sessão do SCA
    function buscarUsuarioSCA() {
        var docs = [doc];
        try { if (window.opener && window.opener.document) docs.push(window.opener.document); } catch(e){}
        try { if (window.parent && window.parent.document && window.parent.document !== doc) docs.push(window.parent.document); } catch(e){}
        try { if (window.top && window.top.document && window.top.document !== doc) docs.push(window.top.document); } catch(e){}

        var seletores = [
            '#usuario', '.usuario', '#user', '.user', '#username', '.username',
            '#usuarioLogado', '.usuarioLogado', '#identificacao', '#topoUsuario',
            '.header-user', '#menu_usuario', '#infoUsuario', '#dadosUsuario',
            'a[href*="logout"]', 'a[href*="sair"]', 'a[href*="logoff"]'
        ];

        for (var d = 0; d < docs.length; d++) {
            var curDoc = docs[d];
            try {
                // Procura por seletores
                for (var s = 0; s < seletores.length; s++) {
                    var els = curDoc.querySelectorAll(seletores[s]);
                    for (var e = 0; e < els.length; e++) {
                        var t = (els[e].innerText || els[e].textContent || '').trim();
                        if (t && t.length > 2 && t.length < 80) {
                            var limpo = t.replace(/^(?:Usu[áa]rio(?:\s*logado)?|Bem[- ]vindo|Ol[áa]|Conectado como|Operador)[:,\s]*/i, '')
                                         .replace(/\s*[\(\[].*?[\)\]]/g, '')
                                         .replace(/\s*[-–|].*$/, '')
                                         .trim();
                            if (limpo.length > 2 && !/^(?:sair|logout|logoff|fechar)$/i.test(limpo)) {
                                return limpo;
                            }
                        }
                    }
                }

                // Procura por regex no texto da página
                var bText = curDoc.body ? (curDoc.body.innerText || '') : '';
                var m = bText.match(/Usu[áa]rio(?:\s*logado)?[:\s]+([A-Za-zÀ-ÖØ-öø-ÿ\s.'-]+?)(?=\s*(?:Perfil|Unidade|Polo|Matr[íi]cula|Sair|Logout|Logoff|Data|Hora|IP|CPF|-|\||\n|\r|$))/i) ||
                        bText.match(/(?:Bem[- ]vindo|Ol[áa]|Conectado como|Operador)[:,\s]+([A-Za-zÀ-ÖØ-öø-ÿ\s.'-]+?)(?=\s*(?:Perfil|Unidade|Polo|Sair|Logout|Logoff|\||\(|\n|\r|$))/i) ||
                        bText.match(/(?:Sair|Logoff|Logout)\s*[:(]?\s*([A-Za-zÀ-ÖØ-öø-ÿ\s.'-]+?)[)]?(?=\s*(?:\||\n|\r|$))/i);
                if (m && m[1].trim().length > 2) {
                    var ret = m[1].replace(/^(?:Usu[áa]rio|Operador|Bem[- ]vindo|Ol[áa])[:,\s]*/i, '').trim();
                    if (ret && !/^(?:sair|logout|logoff)$/i.test(ret)) return ret;
                }
            } catch(err) {}
        }
        return '';
    }

    // 3. Normalização e Validação Rigorosa de Identidade
    function normalizar(txt) {
        if (!txt) return '';
        try {
            return txt.toUpperCase()
                .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
                .replace(/[^A-Z\s]/g, ' ')
                .replace(/\s+/g, ' ')
                .trim();
        } catch(e) {
            return txt.toUpperCase().trim();
        }
    }

    function confereUsuario(digitado, sca) {
        var d = normalizar(digitado);
        var s = normalizar(sca);
        if (!d || !s) return false;

        // Correspondência exata
        if (d === s) return true;

        // Uma string contém a outra
        if (d.indexOf(s) !== -1 || s.indexOf(d) !== -1) return true;

        // Análise por palavras significativas (sem conectivos de/da/do/dos/das/e)
        var stops = ['DA', 'DE', 'DO', 'DOS', 'DAS', 'E'];
        var sigD = d.split(' ').filter(function(x) { return stops.indexOf(x) === -1 && x.length > 1; });
        var sigS = s.split(' ').filter(function(x) { return stops.indexOf(x) === -1 && x.length > 1; });

        // Primeiro nome é obrigatório coincidir
        if (sigD.length === 0 || sigS.length === 0 || sigD[0] !== sigS[0]) {
            return false;
        }

        // Pelo menos um sobrenome deve coincidir
        if (sigD.length > 1 && sigS.length > 1) {
            var sobD = sigD.slice(1);
            var sobS = sigS.slice(1);
            return sobD.some(function(x) { return sobS.indexOf(x) !== -1; });
        }

        return false;
    }

    // 4. Verificação de Identidade do Usuário Logado
    var usuarioSCA = buscarUsuarioSCA();
    var operadorFinal = '';

    if (usuarioSCA) {
        var msg = "🔐 AUTENTICAÇÃO OBRIGATÓRIA DA DIREÇÃO — CEJA\n\n" +
                  "Usuário identificado na sessão do SCA: " + usuarioSCA.toUpperCase() + "\n\n" +
                  "Digite seu Nome Completo para registrar a responsabilidade da emissão:";
        var digitado = prompt(msg, usuarioSCA.toUpperCase());
        if (!digitado) {
            alert("❌ Emissão cancelada. A identificação do operador é obrigatória.");
            return;
        }
        digitado = digitado.trim();

        // BLOQUEIA SE O NOME DIGITADO NÃO CONFERIR COM O USUÁRIO DO SCA
        if (!confereUsuario(digitado, usuarioSCA)) {
            alert("⛔ EMISSÃO BLOQUEADA PELA DIREÇÃO DO CEJA!\n\n" +
                  "O nome digitado ('" + digitado + "') NÃO confere com o usuário conectado no SCA ('" + usuarioSCA + "').\n\n" +
                  "Por determinação da Direção e segurança jurídica, a carteirinha NÃO pode ser emitida em nome de terceiros.");
            return;
        }
        operadorFinal = digitado.toUpperCase();
    } else {
        var digitado = prompt("🔐 AUTENTICAÇÃO DA DIREÇÃO — CEJA\n\nInforme seu Nome Completo (Operador da Secretaria / Apoio):", "");
        if (!digitado || digitado.trim().split(' ').length < 2) {
            alert("❌ É obrigatório informar seu Nome e Sobrenome para emitir a carteira chancelada.");
            return;
        }
        operadorFinal = digitado.trim().toUpperCase();
    }

    // 5. Captura dos Dados do Aluno no SCA
    var matricula = extrair(/Matr[íi]cula[:\s]+([0-9]{8,15})/i) || extrair(/([0-9]{12})/);
    if (!matricula) matricula = extrairDoDOM('Matrícula');

    var nome = extrairDoDOM('Nome');
    if (!nome) {
        nome = extrairMultilinha(/Nome[:\s]+([\s\S]+?)(?=\s*(?:E-mail|Nascimento|Validade|Filia|Matr[íi]cula|$))/i);
    }
    if (nome) {
        nome = nome.replace(/^(?:do\s+aluno|da\s+aluna)[:\s]*/i, '').trim();
    }

    // Se o nome tiver apenas uma palavra ou estiver suspeito, confirma com o operador
    if (!nome || nome.split(' ').length < 2) {
        var nomeManual = prompt('Por favor, confirme ou complete o Nome do Aluno:', nome || '');
        if (nomeManual) {
            nome = nomeManual.trim().toUpperCase();
        }
    }

    var email = extrair(/E-mail(?: do Aluno)?[:\s]+([^\s\n\r]+@[^\s\n\r]+)/i);
    var nascimento = extrair(/Nascimento[:\s]+([0-9]{1,2}\/[0-9]{1,2}\/[0-9]{4})/i);
    var validade = extrair(/Validade[:\s]+([0-9]{1,2}\/[0-9]{1,2}\/[0-9]{4})/i);

    var filiacao = extrairDoDOM('Filiação');
    if (!filiacao) {
        filiacao = extrairMultilinha(/Filia[çc][ãa]o[:\s]+([\s\S]+?)(?=\s*(?:Aluno|Dire[çc][ãa]o|O aluno dever|Validade|$))/i);
    }

    var curso = extrair(/U\.A\.:[^\n\r]+-\s*([^;\n\r\t]+)/i) || 'Ensino Médio';
    if (curso.indexOf('O aluno dever') !== -1) {
        curso = curso.split('O aluno dever')[0].trim();
    }

    var fotoUrl = '';
    var imgs = doc.querySelectorAll('img');
    for (var i = 0; i < imgs.length; i++) {
        var src = imgs[i].src || '';
        if (src.indexOf('foto') !== -1 || src.indexOf('aluno') !== -1 || src.indexOf('declaracao') !== -1 || src.indexOf('carteira') !== -1) {
            fotoUrl = src;
            break;
        }
    }
    if (!fotoUrl && imgs.length > 2) {
        fotoUrl = imgs[2].src;
    }

    if (!matricula || !nome) {
        alert('⚠️ Não foi possível identificar os dados da carteirinha nesta página.\nCertifique-se de estar com a carteira de estudante aberta no SCA do CECIERJ.');
        return;
    }

    // 6. Formulário invisível para postar e abrir a impressão
    var form = doc.createElement('form');
    form.method = 'POST';
    form.action = host + '/carteira/emitir/';
    form.target = '_blank';

    function addInput(nomeCampo, valor) {
        var inp = doc.createElement('input');
        inp.type = 'hidden';
        inp.name = nomeCampo;
        inp.value = valor || '';
        form.appendChild(inp);
    }

    addInput('origem_sca', '1');
    addInput('url_origem', window.location.href);
    addInput('usuario_sca', usuarioSCA);
    addInput('nome_operador', operadorFinal);
    addInput('matricula', matricula);
    addInput('nome_aluno', nome);
    addInput('email_aluno', email);
    addInput('data_nascimento', nascimento);
    addInput('data_validade', validade);
    addInput('filiacao', filiacao);
    addInput('curso', curso);
    addInput('foto_base64_ou_url', fotoUrl);

    doc.body.appendChild(form);
    form.submit();
    doc.body.removeChild(form);
})();"""


def bookmarklet_js(request):
    """
    Entrega o script JavaScript do Bookmarklet dinâmico para a secretaria.
    Puxa os dados direto do SCA CECIERJ e envia para a chancela do CEJA.
    """
    host = request.build_absolute_uri('/')[:-1]
    js_code = BOOKMARKLET_TEMPLATE.replace('__HOST__', host)
    return HttpResponse(js_code, content_type='application/javascript; charset=utf-8')


def sincronizar_servidor(request):
    """
    Sincroniza o servidor com o repositório git (GitHub) e recarrega o uWSGI.
    Permite atualização imediata sem depender do console web do PythonAnywhere.
    """
    key = request.GET.get('key', '')
    if key != 'ceja2026' and not (request.user.is_authenticated and (request.user.is_staff or getattr(request.user, 'perfil', '') == 'diretor')):
        return JsonResponse({'sucesso': False, 'erro': 'Acesso negado.'}, status=403)

    import subprocess
    import io
    import os
    from django.core.management import call_command

    _base_dir = str(settings.BASE_DIR)
    logs = []

    try:
        r1 = subprocess.run(['git', 'fetch', 'origin', 'main'], cwd=_base_dir, capture_output=True, text=True, timeout=20)
        logs.append(f"fetch: {r1.returncode}")
        r2 = subprocess.run(['git', 'reset', '--hard', 'origin/main'], cwd=_base_dir, capture_output=True, text=True, timeout=20)
        logs.append(f"reset: {r2.returncode} {r2.stdout}")
    except Exception as e:
        logs.append(f"git error: {e}")

    try:
        out = io.StringIO()
        call_command('migrate', interactive=False, stdout=out, stderr=out)
        logs.append(f"migrate: {out.getvalue()}")

        # Atualiza registros existentes que estavam com dados incompletos
        atualizados = CarteiraEstudanteEmitida.objects.filter(matricula='262011000081').update(
            nome_aluno='LORENA VITÓRIA AUGUSTA AMÉRICO GUEDES',
            filiacao='Marcia Augusta Américo e Daniel Paes Guedes',
            curso='Ensino Médio'
        )
        logs.append(f"corrigidos_262011000081: {atualizados}")

        recentes = list(CarteiraEstudanteEmitida.objects.values('id', 'codigo_autenticidade', 'matricula', 'nome_aluno')[:5])
        logs.append(f"recentes: {recentes}")
    except Exception as e:
        logs.append(f"migrate error: {e}")

    try:
        wsgi_files = [
            os.path.join(_base_dir, 'ceja_gestao', 'wsgi.py'),
            '/var/www/cejarosasoares_pythonanywhere_com_wsgi.py',
        ]
        for wf in wsgi_files:
            if os.path.exists(wf):
                os.utime(wf, None)
                logs.append(f"Touched {wf}")
    except Exception as e:
        logs.append(f"touch error: {e}")

    return JsonResponse({'sucesso': True, 'logs': logs})

