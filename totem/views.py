"""
App: totem
API pública que alimenta o index.html com dados dinâmicos do banco.
Substituirá o arquivo estático dados_escola.js
"""
import json
import logging
from datetime import date, timedelta
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from professores.models import Professor, HorarioProfessor
from agenda.models import ReservaAuditorio
from .models import MensagemFaleConosco

logger = logging.getLogger(__name__)


def view_totem_publico(request):
    """Exibe o Totem de Autoatendimento público (index.html)."""
    return render(request, 'index.html')


# Mapeamento dia semana (slug → texto) para o totem
DIAS_PT = {
    'segunda': 'Segunda-feira',
    'terca': 'Terça-feira',
    'quarta': 'Quarta-feira',
    'quinta': 'Quinta-feira',
    'sexta': 'Sexta-feira',
    'sabado': 'Sábado',
}

LOCAL_PT = {
    'cabine_linguagens': 'Cabine de Linguagens',
    'cabine_matematica': 'Cabine de Matemática',
    'cabine_ciencias_natureza': 'Cabine de Ciências da Natureza',
    'cabine_ciencias_humanas': 'Cabine de Ciências Humanas',
    'auditorio': 'Auditório',
    'secretaria': 'Secretaria',
    'outro': 'Outro',
}


def _json_cors_response(data, status=200):
    """Retorna JsonResponse com headers CORS abertos para o Totem e GitHub Pages."""
    response = JsonResponse(data, status=status)
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response["Access-Control-Allow-Headers"] = "*"
    return response


@cache_page(60 * 5)  # Cache de 5 minutos
def view_horarios_totem(request):
    """
    GET /api/totem/horarios/
    Retorna a lista de professores com horários aprovados para o ano atual.
    Formato compatível com o index.html existente.
    """
    ano = int(request.GET.get('ano', timezone.now().year))

    professores = Professor.objects.filter(
        ativo=True
    ).prefetch_related(
        'horarios', 'disciplinas_lecionadas'
    ).order_by('classificacao', 'nome_completo')

    resultado = []
    for prof in professores:
        horarios_aprovados = prof.horarios.filter(
            ano_letivo=ano, aprovado=True
        ).order_by('dia_semana', 'hora_inicio')

        if not horarios_aprovados.exists():
            continue

        disciplinas = list(prof.disciplinas_lecionadas.values_list('nome', flat=True))
        if not disciplinas:
            disciplinas = [prof.get_disciplina_ingresso_display()]

        horarios_lista = []
        for h in horarios_aprovados:
            horarios_lista.append({
                'dia': DIAS_PT.get(h.dia_semana, h.dia_semana),
                'inicio': h.hora_inicio.strftime('%H:%M'),
                'fim': h.hora_fim.strftime('%H:%M'),
                'local': LOCAL_PT.get(h.local, h.local_descricao or h.local),
            })

        resultado.append({
            'nome': prof.nome_completo,
            'foto': prof.foto.url if prof.foto else '',
            'disciplinas': disciplinas,
            'horarios': horarios_lista,
        })

    return JsonResponse({
        'ano': ano,
        'gerado_em': timezone.now().isoformat(),
        'horarioProfessores': resultado,
    })


def view_info_escola(request):
    """
    GET /api/totem/escola/
    Retorna informações gerais da escola (fixas por enquanto).
    """
    return JsonResponse({
        'nome': 'CEJA Professora Rosa Soares',
        'cidade': 'Mesquita - RJ',
        'telefone': '(21) 98161-2512',
        'horarioAtendimento': [
            {'dia': 'Segunda a Quinta', 'horario': '08:30 às 20:30'},
            {'dia': 'Sexta-feira', 'horario': '08:30 às 17:00'},
        ],
        'email': 'admcejamesquita@gmail.com',
        'instagram': '@ceja_mesquita',
        'whatsapp': '5521981612512',
    })


def view_auditorio_totem(request):
    """
    GET /api/totem/auditorio/?mes=MM&ano=AAAA
    Retorna as reservas confirmadas do auditório para exibição pública na tela do totem.
    """
    hoje = timezone.now().date()
    ano = int(request.GET.get('ano', hoje.year))
    mes = int(request.GET.get('mes', hoje.month))

    primeiro_dia = date(ano, mes, 1)
    if mes == 12:
        ultimo_dia = date(ano + 1, 1, 1) - timedelta(days=1)
    else:
        ultimo_dia = date(ano, mes + 1, 1) - timedelta(days=1)

    reservas = ReservaAuditorio.objects.filter(
        data__gte=primeiro_dia,
        data__lte=ultimo_dia,
        status__in=['confirmada', 'pendente']
    ).order_by('data', 'hora_inicio')

    lista = []
    for r in reservas:
        lista.append({
            'id': r.id,
            'titulo': r.titulo,
            'tipo': r.tipo,
            'tipo_display': r.get_tipo_display(),
            'descricao': r.descricao or '',
            'data': r.data.isoformat(),
            'hora_inicio': r.hora_inicio.strftime('%H:%M'),
            'hora_fim': r.hora_fim.strftime('%H:%M'),
            'responsavel': r.responsavel,
            'turma_publico': r.turma_publico,
            'status': r.status,
            'badge_color': r.badge_color,
        })

    # Próximas reservas a partir de hoje
    proximas = ReservaAuditorio.objects.filter(
        data__gte=hoje,
        status__in=['confirmada', 'pendente']
    ).order_by('data', 'hora_inicio')[:15]

    proximas_lista = []
    for r in proximas:
        proximas_lista.append({
            'id': r.id,
            'titulo': r.titulo,
            'tipo': r.tipo,
            'tipo_display': r.get_tipo_display(),
            'data': r.data.isoformat(),
            'data_formatada': r.data.strftime('%d/%m/%Y'),
            'hora_inicio': r.hora_inicio.strftime('%H:%M'),
            'hora_fim': r.hora_fim.strftime('%H:%M'),
            'responsavel': r.responsavel,
            'turma_publico': r.turma_publico,
            'badge_color': r.badge_color,
        })

    return JsonResponse({
        'ano': ano,
        'mes': mes,
        'hoje': hoje.isoformat(),
        'reservas': lista,
        'proximas': proximas_lista,
    })


@csrf_exempt
def api_enviar_feedback(request):
    """
    POST /api/totem/feedback/
    Recebe mensagens enviadas pelo Fale Conosco, salva no banco de dados
    e dispara o e-mail via servidor SMTP oficial do Gmail do CEJA.
    """
    if request.method == 'OPTIONS':
        return _json_cors_response({'success': True})

    if request.method != 'POST':
        return _json_cors_response({'success': False, 'error': 'Método não permitido.'}, status=405)

    tipo = 'sugestao'
    assunto = 'Geral'
    mensagem = ''
    nome = ''
    contato = ''

    if request.content_type == 'application/json' or (request.body and request.body.startswith(b'{')):
        try:
            data = json.loads(request.body.decode('utf-8'))
            tipo = data.get('type') or data.get('tipo', 'sugestao')
            assunto = data.get('topic') or data.get('assunto', 'Geral')
            mensagem = data.get('message') or data.get('mensagem', '')
            nome = data.get('name') or data.get('nome', '')
            contato = data.get('contact') or data.get('contato', '')
        except Exception as e:
            logger.warning(f"Erro ao decodificar JSON do feedback: {e}")
            tipo = request.POST.get('type') or request.POST.get('tipo', 'sugestao')
            assunto = request.POST.get('topic') or request.POST.get('assunto', 'Geral')
            mensagem = request.POST.get('message') or request.POST.get('mensagem', '')
    else:
        tipo = request.POST.get('type') or request.POST.get('tipo', 'sugestao')
        assunto = request.POST.get('topic') or request.POST.get('assunto', 'Geral')
        mensagem = request.POST.get('message') or request.POST.get('mensagem', '')
        nome = request.POST.get('name') or request.POST.get('nome', '')
        contato = request.POST.get('contact') or request.POST.get('contato', '')

    mensagem = (mensagem or '').strip()
    if len(mensagem) < 5:
        return _json_cors_response({'success': False, 'error': 'A mensagem deve ter pelo menos 5 caracteres.'}, status=400)

    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '')).split(',')[0].strip()

    # 1. Salva no banco de dados (garante registro imediato e permanente)
    msg_obj = MensagemFaleConosco.objects.create(
        tipo=tipo,
        assunto=assunto,
        mensagem=mensagem,
        nome=nome,
        contato=contato,
        ip_origem=ip,
        criado_em=timezone.now()
    )

    tipo_map = {
        'sugestao': 'Sugestão 💡',
        'reclamacao': 'Reclamação ⚠️',
        'elogio': 'Elogio ⭐',
        'outro': 'Outro Assunto 💬',
    }
    tipo_nome = tipo_map.get(tipo, tipo.capitalize())

    subject = f'[CEJA Fale Conosco] {tipo_nome}: {assunto}'
    destinatario = getattr(settings, 'EMAIL_HOST_USER', 'admcejamesquita@gmail.com')

    body_txt = (
        f"============================================================\n"
        f"💬 CEJA - MENSAGEM DO FALE CONOSCO (TOTEM / SITE PÚBLICO)\n"
        f"============================================================\n\n"
        f"📌 Tipo: {tipo_nome}\n"
        f"🏷️ Assunto: {assunto}\n"
        f"📅 Data/Hora: {msg_obj.criado_em.strftime('%d/%m/%Y às %H:%M:%S')}\n"
        f"👤 Remetente: {nome or 'Anônimo'}\n"
        f"{f'📞 Contato: {contato}\n' if contato else ''}"
        f"\n📝 Mensagem:\n"
        f"------------------------------------------------------------\n"
        f"{mensagem}\n"
        f"------------------------------------------------------------\n\n"
        f"🌐 IP de envio: {ip}\n"
        f"CEJA Professora Rosa Soares — Mesquita / RJ\n"
    )

    body_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
      <div style="background: #0f172a; color: #ffffff; padding: 22px; text-align: center;">
        <h2 style="margin: 0 0 4px 0; font-size: 20px; font-weight: bold; color: #ffffff;">CEJA Profa Rosa Soares</h2>
        <p style="margin: 0; font-size: 13px; color: #94a3b8;">Nova mensagem recebida pelo Fale Conosco</p>
      </div>
      <div style="padding: 24px;">
        <div style="margin-bottom: 16px;">
          <span style="display: inline-block; padding: 4px 12px; background: #dbeafe; color: #1e40af; border-radius: 20px; font-weight: bold; font-size: 12px;">{tipo_nome}</span>
          <span style="display: inline-block; padding: 4px 12px; background: #f1f5f9; color: #334155; border-radius: 20px; font-weight: 600; font-size: 12px; margin-left: 6px;">{assunto}</span>
        </div>
        <div style="background: #f8fafc; border-left: 4px solid #3b82f6; padding: 16px; border-radius: 6px; margin-bottom: 20px; font-size: 15px; line-height: 1.6; color: #1e293b; white-space: pre-line;">
{mensagem}
        </div>
        <table style="width: 100%; border-collapse: collapse; font-size: 13px; color: #64748b;">
          <tr>
            <td style="padding: 6px 0; font-weight: bold; width: 110px;">Data/Hora:</td>
            <td style="padding: 6px 0; color: #0f172a;">{msg_obj.criado_em.strftime('%d/%m/%Y às %H:%M:%S')}</td>
          </tr>
          <tr>
            <td style="padding: 6px 0; font-weight: bold;">Remetente:</td>
            <td style="padding: 6px 0; color: #0f172a;">{nome or 'Anônimo'}</td>
          </tr>
          {f'<tr><td style="padding: 6px 0; font-weight: bold;">Contato:</td><td style="padding: 6px 0; color: #0f172a;">{contato}</td></tr>' if contato else ''}
        </table>
      </div>
      <div style="background: #f8fafc; padding: 12px; text-align: center; font-size: 12px; color: #64748b; border-top: 1px solid #e2e8f0;">
        CEJA Professora Rosa Soares — Mesquita / RJ
      </div>
    </div>
    """

    email_enviado = False
    try:
        send_mail(
            subject=subject,
            message=body_txt,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[destinatario],
            html_message=body_html,
            fail_silently=False,
        )
        email_enviado = True
        msg_obj.email_enviado = True
        msg_obj.save(update_fields=['email_enviado'])
        logger.info(f"E-mail de Fale Conosco enviado com sucesso para {destinatario}")
    except Exception as e:
        msg_obj.erro_envio = str(e)
        msg_obj.save(update_fields=['erro_envio'])
        logger.error(f"Erro ao enviar e-mail de Fale Conosco via SMTP: {e}")

    return _json_cors_response({
        'success': True,
        'message': 'Mensagem enviada com sucesso!',
        'id': msg_obj.id,
        'email_enviado': email_enviado,
    })


@csrf_exempt
def api_listar_feedbacks(request):
    """
    GET /api/totem/feedback/listar/
    Retorna as mensagens registradas para exibição no painel administrativo do Totem.
    """
    if request.method == 'OPTIONS':
        return _json_cors_response({'success': True})

    msgs = MensagemFaleConosco.objects.all().order_by('-criado_em')[:100]
    data = [{
        'id': str(m.id),
        'timestamp': m.criado_em.strftime('%d/%m/%Y %H:%M'),
        'type': m.tipo,
        'topic': m.assunto,
        'message': m.mensagem,
        'email_enviado': m.email_enviado,
    } for m in msgs]
    return _json_cors_response({'success': True, 'feedbacks': data})
