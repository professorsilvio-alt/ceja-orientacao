"""
Utilitários do app funcionarios (Envio de e-mail de confirmação de ponto).
"""
import threading
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def _enviar_email_async(subject, body_html, body_text, to_email, photo_path=None):
    """Executa o envio de e-mail em uma thread separada para não travar a requisição HTTP."""
    try:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@cejarosasoares.edu.br')
        email = EmailMultiAlternatives(
            subject=subject,
            body=body_text,
            from_email=from_email,
            to=[to_email]
        )
        email.attach_alternative(body_html, "text/html")
        
        # Opcional: Anexar a foto se existir no disco
        if photo_path:
            try:
                email.attach_file(photo_path)
            except Exception as e:
                print(f"[Email Ponto] Aviso: não foi possível anexar foto: {e}")

        email.send(fail_silently=True)
        print(f"[Email Ponto] Confirmação enviada com sucesso para {to_email}")
    except Exception as e:
        print(f"[Email Ponto] Erro ao enviar e-mail de confirmação: {e}")


def enviar_email_confirmacao_ponto(registro):
    """
    Monta e dispara a confirmação de batida de ponto por e-mail para o funcionário terceirizado.
    """
    if not registro or not registro.funcionario or not registro.funcionario.email:
        print("[Email Ponto] Funcionário sem e-mail cadastrado. Envio ignorado.")
        return False

    func = registro.funcionario
    data_hora_str = registro.data_hora.strftime("%d/%m/%Y às %H:%M:%S")
    tipo_str = registro.get_tipo_display()

    subject = f"📋 Comprovante de Ponto — {tipo_str} — CEJA Profa Rosa Soares"

    body_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }}
        .card {{ max-width: 580px; margin: 0 auto; background: #1e293b; border: 1px solid #334155; border-radius: 12px; overflow: hidden; padding: 24px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }}
        .header {{ text-align: center; border-bottom: 2px solid #38bdf8; padding-bottom: 16px; margin-bottom: 20px; }}
        .header h2 {{ color: #38bdf8; margin: 0 0 6px 0; font-size: 1.4rem; }}
        .header p {{ color: #94a3b8; font-size: 0.9rem; margin: 0; }}
        .badge {{ display: inline-block; padding: 8px 16px; border-radius: 20px; font-weight: bold; font-size: 1rem; background: #0284c7; color: #ffffff; text-align: center; margin: 12px 0; }}
        .info-row {{ display: flex; justify-content: space-between; margin-bottom: 12px; border-bottom: 1px solid #334155; padding-bottom: 8px; font-size: 0.95rem; }}
        .label {{ color: #94a3b8; font-weight: 600; }}
        .value {{ color: #f1f5f9; font-weight: bold; }}
        .footer {{ text-align: center; font-size: 0.8rem; color: #64748b; margin-top: 24px; border-top: 1px solid #334155; padding-top: 12px; }}
      </style>
    </head>
    <body>
      <div class="card">
        <div class="header">
          <h2>CEJA Professora Rosa Soares</h2>
          <p>Sistema de Controle de RH e Registro de Ponto</p>
        </div>
        
        <p style="font-size: 1.05rem; color: #e2e8f0;">Olá, <strong>{func.nome_completo}</strong>!</p>
        <p style="color: #cbd5e1;">Sua batida de ponto foi registrada no sistema com sucesso. Confira os detalhes abaixo:</p>
        
        <div style="text-align: center;">
          <div class="badge">{tipo_str}</div>
        </div>

        <div style="margin-top: 16px;">
          <div class="info-row">
            <span class="label">Data e Horário:</span>
            <span class="value">{data_hora_str}</span>
          </div>
          <div class="info-row">
            <span class="label">Empresa Contratante:</span>
            <span class="value">{func.empresa_contratante}</span>
          </div>
          <div class="info-row">
            <span class="label">Cargo / Função:</span>
            <span class="value">{func.cargo_funcao}</span>
          </div>
          <div class="info-row">
            <span class="label">CPF:</span>
            <span class="value">***.{func.cpf[3:6]}.{func.cpf[6:9]}-**</span>
          </div>
        </div>

        <p style="font-size:0.85rem; color:#94a3b8; margin-top: 16px;">
          * Este é um e-mail de confirmação automático gerado pelo terminal de ponto do CEJA. Uma cópia da sua foto no momento do registro foi armazenada com segurança.
        </p>

        <div class="footer">
          CEJA Professora Rosa Soares &copy; 2026 — Controle de Frequência e RH
        </div>
      </div>
    </body>
    </html>
    """

    body_text = f"""
    CEJA Professora Rosa Soares - Registro de Ponto
    
    Olá, {func.nome_completo}!
    
    Sua batida de ponto foi registrada com sucesso:
    - Tipo: {tipo_str}
    - Data e Horário: {data_hora_str}
    - Empresa: {func.empresa_contratante}
    - Cargo: {func.cargo_funcao}
    
    CEJA Professora Rosa Soares (2026)
    """

    photo_path = None
    if registro.foto:
        try:
            photo_path = registro.foto.path
        except Exception as e:
            print(f"[Email Ponto] Aviso: não foi possível obter o caminho do arquivo de foto: {e}")

    # Thread para não travar a requisição do usuário
    thread = threading.Thread(
        target=_enviar_email_async,
        args=(subject, body_html, body_text, func.email, photo_path)
    )
    thread.daemon = True
    thread.start()

    registro.email_enviado = True
    registro.save(update_fields=['email_enviado'])
    return True
