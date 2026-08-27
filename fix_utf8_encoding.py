"""
Script para corrigir arquivos com UTF-8 duplamente codificado (latin1 -> utf-8).
"""
import glob
import os

FILES_TO_FIX = [
    'index.html',
    'script.js',
    'dados_escola.js',
    'sync_horarios.py',
    'sync_horarios.js',
    'build_carregar_dados.py',
    'carregar_dados.py',
    'importar_completo_excel.py',
    'templates/funcionarios/detalhe_adm.html',
    'templates/funcionarios/detalhe_terc.html',
    'templates/professores/detalhe.html',
    'templates/professores/quadro_horarios_list.html',
    'usuarios/views.py',
    'ceja_gestao/settings.py',
]

def fix_file(filepath):
    if not os.path.exists(filepath):
        return
    with open(filepath, 'rb') as f:
        raw_bytes = f.read()

    try:
        content = raw_bytes.decode('utf-8')
    except UnicodeDecodeError:
        try:
            content = raw_bytes.decode('cp1252')
        except Exception:
            return

    # Se contém padrões de UTF-8 codificado como Latin1/CP1252
    if 'Ã' in content or 'Â' in content:
        try:
            fixed_content = content.encode('latin1').decode('utf-8')
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"✅ Corrigido: {filepath}")
        except Exception as e:
            print(f"⚠️ Não foi possível re-codificar {filepath} via latin1: {e}")

if __name__ == '__main__':
    for fp in FILES_TO_FIX:
        fix_file(fp)
