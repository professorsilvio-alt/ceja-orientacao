import os
import re
import json
from django.conf import settings
from .models import DocumentoCerebro, FragmentoConhecimento

import sys

GENAI_AVAILABLE = False
GENAI_IMPORT_ERROR = ""
genai = None
types = None

def tentar_importar_genai():
    global GENAI_AVAILABLE, GENAI_IMPORT_ERROR, genai, types
    if GENAI_AVAILABLE and genai is not None:
        return True

    # Injeta apenas o diretório de pacotes da versão EXATA do Python em execução
    caminho_user = os.path.expanduser(f"~/.local/lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages")
    if os.path.exists(caminho_user) and caminho_user not in sys.path:
        sys.path.insert(0, caminho_user)

    try:
        from google import genai as g_genai
        from google.genai import types as g_types
        genai = g_genai
        types = g_types
        GENAI_AVAILABLE = True
        GENAI_IMPORT_ERROR = ""
        return True
    except Exception as e:
        GENAI_AVAILABLE = False
        GENAI_IMPORT_ERROR = str(e)
        return False

# Tentativa inicial
tentar_importar_genai()


def obter_cliente_gemini(retornar_erro=False):
    """
    Retorna o cliente Google GenAI ou (cliente, erro_msg) com diagnóstico preciso.
    Compatível com ambiente local e PythonAnywhere.
    """
    from pathlib import Path

    if not tentar_importar_genai():
        py_ver = f"{sys.version_info.major}.{sys.version_info.minor}"
        msg = f"A biblioteca 'google-genai' não pôde ser carregada no Python {py_ver} ({GENAI_IMPORT_ERROR})."
        return (None, msg) if retornar_erro else None

    # Configuração de proxy para conexões de saída em contas gratuitas do PythonAnywhere
    base_url = getattr(settings, 'BASE_URL', '') or os.getenv('BASE_URL', '')
    if 'pythonanywhere' in base_url.lower() or 'PYTHONANYWHERE_DOMAIN' in os.environ:
        os.environ.setdefault('http_proxy', 'http://proxy.server:3128')
        os.environ.setdefault('https_proxy', 'http://proxy.server:3128')

    api_key = getattr(settings, 'GEMINI_API_KEY', None) or os.getenv('GEMINI_API_KEY', '')
    if not api_key:
        try:
            from dotenv import load_dotenv
            base_dir = getattr(settings, 'BASE_DIR', None)
            if base_dir:
                load_dotenv(base_dir / '.env')
            else:
                load_dotenv()
            api_key = os.getenv('GEMINI_API_KEY', '')
        except Exception:
            pass

    # Leitura direta do arquivo .env como garantia caso dotenv não tenha populado os.environ
    if not api_key:
        caminhos_tentativas = []
        base_dir = getattr(settings, 'BASE_DIR', None)
        if base_dir:
            caminhos_tentativas.append(Path(base_dir) / '.env')
        caminhos_tentativas.append(Path.cwd() / '.env')
        caminhos_tentativas.append(Path(__file__).resolve().parent.parent / '.env')
        caminhos_tentativas.append(Path('/home/cejarosasoares/ceja-orientacao/.env'))

        for p in caminhos_tentativas:
            try:
                if p.exists():
                    with open(p, 'r', encoding='utf-8') as f:
                        for line in f:
                            linha = line.strip()
                            if linha.startswith('GEMINI_API_KEY='):
                                chave = linha.split('=', 1)[1].strip().strip('"\'')
                                if chave:
                                    api_key = chave
                                    break
                    if api_key:
                        break
            except Exception:
                pass

    if not api_key:
        msg = "Chave GEMINI_API_KEY não localizada no arquivo .env do servidor."
        return (None, msg) if retornar_erro else None

    try:
        client = genai.Client(api_key=api_key)
        return (client, None) if retornar_erro else client
    except Exception as e:
        msg = f"Falha ao inicializar o cliente Gemini: {str(e)[:120]}"
        print(f"[Aviso Gemini Client]: {msg}")
        return (None, msg) if retornar_erro else None


def buscar_contexto_relevante(pergunta: str, max_fragmentos: int = 8) -> tuple[str, list[dict]]:
    """
    Busca os documentos e fragmentos mais relevantes na base do Cérebro.
    Dá prioridade absoluta a documentos com status 'vigente'.
    """
    termos = [t.lower() for t in re.findall(r'\w+', pergunta) if len(t) > 2]
    
    # Documentos vigentes
    docs_vigentes = DocumentoCerebro.objects.filter(status='vigente')
    
    score_por_doc = []
    for doc in docs_vigentes:
        score = 0
        conteudo_lower = (doc.conteudo_extraido or "").lower()
        titulo_lower = doc.titulo.lower()
        num_lower = (doc.numero_normativa or "").lower()
        
        for t in termos:
            if t in titulo_lower or t in num_lower:
                score += 5
            score += conteudo_lower.count(t)
            
        if score > 0 or not termos:
            score_por_doc.append((score, doc))
            
    # Ordenar por maior relevância
    score_por_doc.sort(key=lambda x: x[0], reverse=True)
    
    contextos = []
    fontes = []
    
    docs_selecionados = [doc for _, doc in score_por_doc[:5]]
    if not docs_selecionados and docs_vigentes.exists():
        # Fallback: incluir os documentos vigentes mais recentes se a base for concisa
        docs_selecionados = list(docs_vigentes[:5])

    for doc in docs_selecionados:
        substitui_info = ""
        if doc.documento_substituido:
            substitui_info = f" (Atualiza/substitui: {doc.documento_substituido.titulo})"
            
        norma_info = f" [Norma/Portaria: {doc.numero_normativa}]" if doc.numero_normativa else ""
        cabecalho = f"--- DOCUMENTO VIGENTE: {doc.titulo}{norma_info}{substitui_info} (Categoria: {doc.get_categoria_display()}) ---"
        
        # Limitar o tamanho do trecho por documento para caber com clareza no prompt
        texto = doc.conteudo_extraido[:3500] if doc.conteudo_extraido else "(Sem texto extraído)"
        contextos.append(f"{cabecalho}\n{texto}\n")
        
        fontes.append({
            'id': doc.id,
            'titulo': doc.titulo,
            'categoria': doc.get_categoria_display(),
            'normativa': doc.numero_normativa or '',
            'tipo': doc.get_tipo_arquivo_display(),
            'status': doc.get_status_display()
        })

    # Verificar se há documentos revogados relevantes para alertar se necessário
    docs_revogados = DocumentoCerebro.objects.filter(status='substituido')
    revogados_avisos = []
    
    # 1. Avisos diretos para os documentos que foram substituídos pelos documentos selecionados
    for doc in docs_selecionados:
        if doc.documento_substituido:
            sub = doc.documento_substituido
            revogados_avisos.append(
                f"- ATENÇÃO: O documento '{sub.titulo}' ({sub.numero_normativa or 'S/N'}) FOI REVOGADO/SUBSTITUÍDO pelo documento vigente '{doc.titulo}'."
            )
            
    # 2. Avisos para outros documentos revogados que coincidam com a busca
    for r in docs_revogados:
        conteudo_r = (r.conteudo_extraido or "").lower()
        titulo_r = r.titulo.lower()
        num_r = (r.numero_normativa or "").lower()
        for t in termos:
            if t in titulo_r or (num_r and t in num_r) or t in conteudo_r:
                revogados_avisos.append(
                    f"- ATENÇÃO: O documento '{r.titulo}' ({r.numero_normativa or 'S/N'}) FOI REVOGADO/SUBSTITUÍDO por uma norma mais recente."
                )
                break
                
    contexto_str = "\n\n".join(contextos)
    if revogados_avisos:
        # Manter avisos únicos
        lista_unica = list(dict.fromkeys(revogados_avisos))
        contexto_str += "\n\n--- REGISTRO DE NORMAS REVOGADAS / SUBSTITUÍDAS ---\n" + "\n".join(lista_unica)
        
    return contexto_str, fontes


def carregar_horarios_dados_escola():
    """Lê e processa a lista de horários dos professores a partir do dados_escola.js."""
    from pathlib import Path
    base_dir = getattr(settings, 'BASE_DIR', None)
    caminhos = []
    if base_dir:
        caminhos.append(Path(base_dir) / 'dados_escola.js')
    caminhos.append(Path('dados_escola.js'))
    caminhos.append(Path.cwd() / 'dados_escola.js')
    caminhos.append(Path(__file__).resolve().parent.parent / 'dados_escola.js')
    caminhos.append(Path('/home/cejarosasoares/ceja-orientacao/dados_escola.js'))

    for p in caminhos:
        try:
            if p.exists():
                txt = p.read_text(encoding='utf-8')
                m = re.search(r"//\s*HORARIOS_SYNC_START[\s\S]*?horarioProfessores\s*:\s*(\[[\s\S]*?\])\s*,\s*//\s*HORARIOS_SYNC_END", txt)
                if not m:
                    m = re.search(r"horarioProfessores\s*:\s*(\[[\s\S]*?\n\s*\])\s*,", txt)
                if m:
                    raw = m.group(1)
                    clean = re.sub(r"//.*", "", raw)
                    for key in ['nome', 'foto', 'disciplinas', 'horarios', 'dia', 'inicio', 'fim', 'local']:
                        clean = re.sub(rf'\b{key}\s*:', f'"{key}":', clean)
                    clean = re.sub(r',\s*([\]}])', r'\1', clean)
                    return json.loads(clean)
        except Exception as e:
            print(f"[Aviso carregar dados_escola.js]: {e}")
    return []


def buscar_dados_sistema(pergunta: str) -> tuple[str, list[dict]]:
    """
    Consulta os dados operacionais em tempo real do CEJA:
    - Quadro de horários dos professores e cabines de atendimento
    - Cadastro de professores (matrícula, disciplina, situação, tempo de escola)
    - Registros de Presença (faltas, atrasos, saídas antecipadas, ausências justificadas)
    - Funcionários administrativos e terceirizados
    - Reservas do auditório
    """
    from django.utils import timezone
    from django.db.models import Q
    from pathlib import Path

    pergunta_lower = pergunta.lower()
    termos = [t for t in re.findall(r'\w+', pergunta_lower) if len(t) > 2]
    blocos = []
    fontes = []

    # 1. Professores e Horários de Atendimento
    try:
        from professores.models import Professor, HorarioProfessor
        horarios_js = carregar_horarios_dados_escola()
        professores_mencionados = []

        nomes_prof_js = {}
        for p in horarios_js:
            nome_p = p.get('nome', '').lower()
            nome_sem_prefixo = re.sub(r'^prof(a|\.ª|\.|ª)?\s*', '', nome_p).strip()
            partes_nome = [w for w in nome_sem_prefixo.split() if len(w) > 2]
            nomes_prof_js[nome_p] = partes_nome

        algum_prof_citado = False
        for nome_p, partes in nomes_prof_js.items():
            if any(re.search(rf'\b{re.escape(parte)}\b', pergunta_lower) for parte in partes):
                algum_prof_citado = True
                break

        for p in horarios_js:
            nome_p = p.get('nome', '').lower()
            partes = nomes_prof_js.get(nome_p, [])
            nome_citado = any(re.search(rf'\b{re.escape(parte)}\b', pergunta_lower) for parte in partes)

            if algum_prof_citado:
                if nome_citado:
                    professores_mencionados.append(p)
            else:
                discs_p = [d.lower() for d in p.get('disciplinas', [])]
                disciplina_citada = any(
                    (d in pergunta_lower or any(re.search(rf'\b{re.escape(w)}\b', pergunta_lower) for w in re.findall(r'\w+', d) if len(w) > 3))
                    for d in discs_p
                )
                dias_p = [h.get('dia', '').lower() for h in p.get('horarios', [])]
                dias_perguntados = [dia for dia in ['segunda', 'terça', 'terca', 'quarta', 'quinta', 'sexta'] if dia in pergunta_lower]
                dia_citado = any(any(dp.startswith(dia[:3]) for dp in dias_p) for dia in dias_perguntados)

                geral = any(g in pergunta_lower for g in ['todos os professores', 'quadro de horários', 'escala completa', 'quem atende', 'grade de horários'])
                if disciplina_citada or (dia_citado and any(k in pergunta_lower for k in ['quem', 'prof', 'horario', 'cabine'])) or geral:
                    professores_mencionados.append(p)

        # Cadastro no banco Django
        professores_bd = Professor.objects.filter(ativo=True)
        if algum_prof_citado:
            q_obj = Q()
            for p in professores_mencionados:
                for parte in nomes_prof_js.get(p.get('nome', '').lower(), []):
                    q_obj |= Q(nome_completo__icontains=parte)
            professores_bd = professores_bd.filter(q_obj)
        else:
            professores_bd = Professor.objects.none()

        if professores_mencionados or professores_bd.exists():
            texto_profs = ["--- SISTEMA: QUADRO DE PROFESSORES E HORÁRIOS DE ATENDIMENTO ---"]
            for p in professores_mencionados:
                h_lista = []
                for h in p.get('horarios', []):
                    h_lista.append(f"{h.get('dia')}: {h.get('inicio')} às {h.get('fim')} ({h.get('local')})")
                horarios_str = " | ".join(h_lista) if h_lista else "Nenhum horário cadastrado"
                texto_profs.append(f"• {p.get('nome')} | Disciplina(s): {', '.join(p.get('disciplinas', []))} | Horários no Totem: {horarios_str}")

            for p in professores_bd[:5]:
                texto_profs.append(
                    f"• Cadastro Funcional: {p.nome_completo} | Matrícula: {p.matricula} | Cargo: {p.cargo} | "
                    f"Disciplina: {p.disciplina_ingresso} | Carga Horária: {p.ch_total or 'N/I'}h | "
                    f"Situação: {p.get_situacao_matricula_1_display()} | Tempo na escola: {p.tempo_na_escola}"
                )
            blocos.append("\n".join(texto_profs))
            fontes.append({'id': 'sistema_professores', 'titulo': 'Quadro de Horários e Cadastro Docente', 'categoria': 'Sistema / Horários'})
    except Exception as e:
        print(f"[Aviso buscar professores]: {e}")

    # 2. Registros de Presença (Faltas, Atrasos, Ausências Justificadas)
    try:
        from agenda.models import RegistroPresenca
        presencas = RegistroPresenca.objects.all()
        deve_incluir_presenca = False

        if termos:
            q_pres = Q()
            for t in termos:
                q_pres |= Q(nome_funcionario__icontains=t) | Q(motivo__icontains=t)
            presencas_filtradas = presencas.filter(q_pres)
            if presencas_filtradas.exists():
                presencas = presencas_filtradas
                deve_incluir_presenca = True
            elif any(palavra in pergunta_lower for palavra in ['falta', 'faltas', 'atraso', 'atrasos', 'presenca', 'presença', 'ausencia', 'ausência', 'frequencia', 'frequência', 'assiduidade']):
                deve_incluir_presenca = True
                presencas = presencas[:12]
        
        if deve_incluir_presenca or any(palavra in pergunta_lower for palavra in ['falta', 'faltas', 'atraso', 'atrasos', 'assiduidade']):
            texto_pres = ["--- SISTEMA: REGISTROS DE PRESENÇA, FALTAS E ATRASOS ---"]
            if presencas.exists():
                for reg in presencas[:15]:
                    horario_info = f" (Horário: {reg.hora_chegada or reg.hora_saida})" if (reg.hora_chegada or reg.hora_saida) else ""
                    just_info = "Justificado" if reg.justificado else "Não justificado"
                    motivo_info = f" - Motivo: {reg.motivo}" if reg.motivo else ""
                    obs_info = f" [Obs: {reg.observacoes}]" if reg.observacoes else ""
                    texto_pres.append(
                        f"• {reg.data.strftime('%d/%m/%Y')} — {reg.nome_funcionario} ({reg.get_tipo_funcionario_display()}): "
                        f"{reg.get_tipo_display()}{horario_info} | {just_info}{motivo_info}{obs_info}"
                    )
            else:
                texto_pres.append("• Nenhum registro de falta, ausência ou atraso foi encontrado no sistema para os critérios consultados.")
            blocos.append("\n".join(texto_pres))
            fontes.append({'id': 'sistema_presenca', 'titulo': 'Módulo de Registro de Frequência e Presença', 'categoria': 'Sistema / Frequência'})
    except Exception as e:
        print(f"[Aviso buscar presenças]: {e}")

    # 3. Funcionários Administrativos e Terceirizados
    try:
        from funcionarios.models import FuncionarioAdministrativo, FuncionarioTerceirizado
        if any(palavra in pergunta_lower for palavra in ['administrativo', 'secretaria', 'direcao', 'direção', 'terceirizado', 'limpeza', 'porteiro', 'vigilante', 'ate', 'coordenador', 'orientador']):
            texto_func = ["--- SISTEMA: EQUIPE ADMINISTRATIVA E TERCEIRIZADA ---"]
            for a in FuncionarioAdministrativo.objects.all()[:8]:
                texto_func.append(f"• Adm: {a.nome_completo} | Cargo: {a.cargo} | Função: {a.funcao_atual or a.cargo} | Situação: {a.get_situacao_matricula_1_display()}")
            for tr in FuncionarioTerceirizado.objects.all()[:8]:
                texto_func.append(f"• Terceirizado: {tr.nome_completo} | Função: {tr.cargo_funcao} | Empresa: {tr.empresa_contratante}")
            blocos.append("\n".join(texto_func))
            fontes.append({'id': 'sistema_funcionarios', 'titulo': 'Quadro de Funcionários Administrativos e Terceirizados', 'categoria': 'Sistema / Pessoal'})
    except Exception as e:
        print(f"[Aviso buscar funcionários]: {e}")

    # 4. Reservas de Auditório
    try:
        from agenda.models import ReservaAuditorio
        if any(palavra in pergunta_lower for palavra in ['auditorio', 'auditório', 'evento', 'oficina', 'palestra', 'reuniao', 'reunião']):
            texto_aud = ["--- SISTEMA: AGENDA DO AUDITÓRIO ---"]
            reservas = ReservaAuditorio.objects.filter(data__gte=timezone.now().date()).order_by('data', 'hora_inicio')[:10]
            if reservas.exists():
                for r in reservas:
                    texto_aud.append(f"• {r.data.strftime('%d/%m/%Y')} {r.hora_inicio.strftime('%H:%M')}-{r.hora_fim.strftime('%H:%M')}: {r.titulo} ({r.get_tipo_display()}) - Resp: {r.responsavel} | Status: {r.get_status_display()}")
            else:
                texto_aud.append("• Não há reservas futuras cadastradas para o auditório no momento.")
            blocos.append("\n".join(texto_aud))
            fontes.append({'id': 'sistema_auditorio', 'titulo': 'Agenda de Reservas do Auditório', 'categoria': 'Sistema / Agenda'})
    except Exception as e:
        print(f"[Aviso buscar reservas]: {e}")

    return "\n\n".join(blocos), fontes


def gerar_resposta_beth(pergunta: str, historico_mensagens: list[dict] = None) -> dict:
    """
    Processa a pergunta utilizando RAG + dados em tempo real do sistema + Gemini API com a persona da Orientadora Beth.
    """
    contexto_docs, fontes_docs = buscar_contexto_relevante(pergunta)
    contexto_sistema, fontes_sistema = buscar_dados_sistema(pergunta)

    partes_contexto = []
    if contexto_sistema:
        partes_contexto.append(contexto_sistema)
    if contexto_docs:
        partes_contexto.append(contexto_docs)

    contexto = "\n\n".join(partes_contexto)
    fontes = fontes_sistema + fontes_docs

    system_instruction = (
        "Você é a **Beth**, Orientadora Virtual e Cérebro de Gestão do **CEJA Profa Rosa Soares**.\n"
        "Seu papel é orientar exclusivamente a **Direção da escola**, fornecendo respostas claras, "
        "precisas, formais porém acolhedoras.\n\n"
        "Você tem acesso integral e prioritário aos DADOS EM TEMPO REAL DO SISTEMA ESCOLAR "
        "(quadro de horários dos professores, cabines de atendimento, registros de faltas e atrasos, "
        "frequência funcional, equipe administrativa e terceirizada, pontos e agenda do auditório) "
        "bem como ao acervo de DOCUMENTOS VIGENTES (regimentos, resoluções, normas e notas técnicas).\n\n"
        "Diretrizes:\n"
        "1. Para perguntas sobre horários, escalas, professores, faltas, atrasos ou funcionários, use "
        "imediatamente as informações extraídas do sistema apresentadas no contexto.\n"
        "2. Se a consulta for sobre a assiduidade de um professor/funcionário e o sistema informar que não há registros de faltas ou atrasos, "
        "informe claramente à Direção que a pessoa está com assiduidade 100% regular (sem faltas/atrasos cadastrados).\n"
        "3. Baseie suas respostas sobre normas e regulamentos nos DOCUMENTOS VIGENTES fornecidos no contexto.\n"
        "4. Se uma norma foi atualizada ou revogada, alerte a Direção sobre a vigência da nova regra.\n"
        "5. Sempre cite a fonte das informações (ex: 'De acordo com o Quadro de Horários da Escola', 'Conforme o Módulo de Presença', etc.).\n"
        "6. Formate as respostas com elegância, usando Markdown (tópicos, negrito, tabelas quando útil)."
    )

    prompt_completo = f"""CONHECIMENTO DISPONÍVEL DO CEJA:
{contexto if contexto else "Nenhum documento ou dado específico cadastrado no momento."}

PERGUNTA DA DIREÇÃO:
{pergunta}
"""

    cliente, motivo_erro = obter_cliente_gemini(retornar_erro=True)
    
    if not cliente:
        # Modo de contingência com mensagem diagnóstica precisa
        aviso_diag = f"*(Modo offline: {motivo_erro})*"
        if not contexto:
            resposta_texto = (
                "Olá! Eu sou a **Beth**, a orientadora virtual do CEJA Profa Rosa Soares. 👩‍🏫\n\n"
                "Ainda não encontrei documentos cadastrados na minha base de conhecimento. "
                "Por favor, acesse a aba **'Acervo de Documentos'** e envie os primeiros arquivos "
                "(PDFs, Word, planilhas, resoluções ou notas de texto) para que eu possa orientar a Direção!\n\n"
                + aviso_diag
            )
        else:
            resposta_texto = (
                f"Olá! Eu sou a **Beth**. Encontrei os seguintes registros e documentos vigentes relacionados à sua consulta:\n\n"
                + "\n".join([f"- **{f['titulo']}** ({f['categoria']})" for f in fontes])
                + f"\n\n{aviso_diag}"
            )
        return {
            'resposta': resposta_texto,
            'fontes': fontes
        }

    # Modelos recomendados em ordem de preferência
    modelos_candidatos = ['gemini-3.1-flash-lite', 'gemini-3.5-flash-lite', 'gemini-3.6-flash', 'gemini-flash-latest']
    ultimo_erro = None

    for modelo in modelos_candidatos:
        try:
            response = cliente.models.generate_content(
                model=modelo,
                contents=prompt_completo,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.2,
                )
            )
            return {
                'resposta': response.text,
                'fontes': fontes
            }
        except Exception as e:
            print(f"[Aviso modelo {modelo}]: {e}")
            ultimo_erro = e
            continue

    print(f"[Erro chamada Gemini]: {ultimo_erro}")
    # Fallback inteligente se houver erro temporário de cota/rede
    return {
        'resposta': (
            f"Olá! Eu sou a **Beth**. Ocorreu uma oscilação na conexão com a inteligência ({str(ultimo_erro)[:100]}), "
            f"mas encontrei estes documentos de referência na nossa base:\n\n"
            + "\n".join([f"- **{f['titulo']}** ({f['categoria']})" for f in fontes])
        ),
        'fontes': fontes
    }


def processar_audio_para_texto(caminho_audio: str) -> str:
    """
    Transcreve um arquivo de áudio utilizando a API multimodal do Gemini.
    """
    cliente = obter_cliente_gemini()
    if not cliente or not os.path.exists(caminho_audio):
        return ""
        
    modelos_audio = ['gemini-3.1-flash-lite', 'gemini-3.5-flash-lite', 'gemini-3.6-flash']
    try:
        arquivo_gemini = cliente.files.upload(file=caminho_audio)
        for modelo in modelos_audio:
            try:
                resposta = cliente.models.generate_content(
                    model=modelo,
                    contents=[
                        arquivo_gemini,
                        "Transcreva fielmente todo o áudio a seguir em português do Brasil e resuma os principais pontos caso seja uma orientação administrativa/pedagógica:"
                    ]
                )
                return resposta.text
            except Exception:
                continue
        return "[Áudio recebido - Transcrição temporariamente indisponível]"
    except Exception as e:
        print(f"[Erro transcrição áudio]: {e}")
        return f"[Áudio recebido - Transcrição indisponível: {e}]"
