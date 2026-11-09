import io
import os
import base64
import qrcode
from django.conf import settings
from .models import ConfiguracaoCarteira


def gerar_qrcode_base64(texto: str) -> str:
    """
    Gera um QR Code em alta resolução e retorna no formato data URI (base64 PNG).
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=6,
        border=1,
    )
    qr.add_data(texto)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64}"


def gerar_codigo_barras_svg(matricula: str) -> str:
    """
    Gera um código de barras Code 39 limpo e compatível em formato SVG vetorial.
    Garante barras pretas nítidas sem depender de conexões externas.
    """
    code39_map = {
        '0': '000110100', '1': '100100001', '2': '001100001', '3': '101100000',
        '4': '000110001', '5': '100110000', '6': '001110000', '7': '000100101',
        '8': '100100100', '9': '001100100', 'A': '100001001', 'B': '001001001',
        'C': '101001000', 'D': '000011001', 'E': '100011000', 'F': '001011000',
        'G': '000001101', 'H': '100001100', 'I': '001001100', 'J': '000011100',
        '*': '010010100', '-': '010000101', '.': '110000100', ' ': '011000100'
    }

    raw = '*' + str(matricula).strip().upper() + '*'
    bars = []
    
    # Cada caractere é composto por 9 elementos (5 barras e 4 espaços)
    for ch in raw:
        pattern = code39_map.get(ch, code39_map['0'])
        for i, val in enumerate(pattern):
            is_bar = (i % 2 == 0)
            is_wide = (val == '1')
            bars.append((is_bar, 3 if is_wide else 1))
        # Espaço separador entre caracteres
        bars.append((False, 1))

    total_units = sum(width for _, width in bars)
    height = 42

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total_units} {height}" '
        f'width="100%" height="{height}px" shape-rendering="crispEdges">'
    ]

    current_x = 0
    for is_bar, width in bars:
        if is_bar:
            svg_parts.append(
                f'<rect x="{current_x}" y="0" width="{width}" height="{height}" fill="#000000" />'
            )
        current_x += width

    svg_parts.append('</svg>')
    return "".join(svg_parts)


def obter_assinatura_base64() -> str:
    """
    Carrega o arquivo seguro da assinatura do Diretor e converte para base64.
    Não expõe o arquivo diretamente via URL estática.
    """
    caminhos_possiveis = [
        os.path.join(settings.BASE_DIR, 'media', 'seguro', 'assinatura_silvio.png'),
        r"G:\Meu Drive\TRABALHO DIREÇÃO\1 - SILVIO\Assinatura.png",
        os.path.join(settings.BASE_DIR, 'scratch', 'assinatura.png'),
    ]

    for p in caminhos_possiveis:
        if os.path.exists(p):
            try:
                with open(p, 'rb') as f:
                    b64 = base64.b64encode(f.read()).decode('utf-8')
                    return f"data:image/png;base64,{b64}"
            except Exception as e:
                continue

    return ""


def obter_brasao_base64() -> str:
    """
    Retorna o brasão do CEJA em base64 para uso local e impressão offline.
    """
    p = os.path.join(settings.BASE_DIR, 'static', 'brasao_ceja.png')
    if os.path.exists(p):
        try:
            with open(p, 'rb') as f:
                b64 = base64.b64encode(f.read()).decode('utf-8')
                return f"data:image/png;base64,{b64}"
        except Exception:
            pass
    return ""
