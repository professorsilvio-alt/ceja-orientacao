import os
import re
import json
from django.conf import settings
from .models import DocumentoCerebro, FragmentoConhecimento

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


def obter_cliente_gemini(retornar_erro=False):
    """
    Retorna o cliente Google GenAI ou (cliente, erro_msg) com diagnóstico preciso.
    Compatível com ambiente local e PythonAnywhere.
    """
    from pathlib import Path

    if not GENAI_AVAILABLE:
        msg = "A biblioteca 'google-genai' não está instalada no ambiente Python do servidor. No terminal, execute: pip install google-genai"
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


def gerar_resposta_beth(pergunta: str, historico_mensagens: list[dict] = None) -> dict:
    """
    Processa a pergunta utilizando RAG + Gemini API com a persona da Orientadora Beth.
    """
    contexto, fontes = buscar_contexto_relevante(pergunta)
    
    system_instruction = (
        "Você é a **Beth**, Orientadora Virtual e Cérebro de Gestão do **CEJA Profa Rosa Soares**.\n"
        "Seu papel é orientar exclusivamente a **Direção da escola**, fornecendo respostas claras, "
        "precisas, formais porém acolhedoras, baseadas estritamente nos documentos, normativas, "
        "regimentos, leis, horários e orientações cadastrados na base de conhecimento da escola.\n\n"
        "Diretrizes:\n"
        "1. Baseie suas respostas prioritariamente nos DOCUMENTOS VIGENTES fornecidos no contexto.\n"
        "2. Se uma norma foi atualizada ou revogada, alerte a Direção sobre a vigência da nova regra.\n"
        "3. Sempre que citar uma informação, indique a fonte ou número da normativa correspondente.\n"
        "4. Se a resposta não constar na base de documentos, informe educadamente que a informação "
        "ainda não foi cadastrada no seu acervo e sugira que a Direção faça o upload do respectivo documento.\n"
        "5. Formate as respostas com elegância, usando Markdown (tópicos, negrito, tabelas quando útil)."
    )

    prompt_completo = f"""CONHECIMENTO DISPONÍVEL DO CEJA:
{contexto if contexto else "Nenhum documento cadastrado no momento."}

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
                f"Olá! Eu sou a **Beth**. Encontrei os seguintes documentos vigentes relacionados à sua consulta:\n\n"
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
