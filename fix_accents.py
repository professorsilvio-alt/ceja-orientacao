"""
Script para substituir caracteres UTF-8 corrompidos por caracteres em português correto.
"""
import glob
import os

REPLACEMENTS = {
    'TerÃ§a': 'Terça',
    'terÃ§a': 'terça',
    'Ã§Ã£': 'ção',
    'Ã§Ãµ': 'ções',
    'Ã§': 'ç',
    'Ã£': 'ã',
    'Ã©': 'é',
    'Ã¡': 'á',
    'Ã³': 'ó',
    'Ãº': 'ú',
    'Ãª': 'ê',
    'Ã¢': 'â',
    'Ã\xad': 'í',
    'Ã\x81': 'Á',
    'Ã\x89': 'É',
    'Ã\x93': 'Ó',
    'Ã\x9a': 'Ú',
    'Ã\x87': 'Ç',
    'Ã\x8d': 'Í',
    'Âª': 'ª',
    'Âº': 'º',
}

FILES = [
    'index.html',
    'script.js',
    'dados_escola.js',
    'sync_horarios.py',
    'sync_horarios.js',
    'templates/funcionarios/detalhe_adm.html',
    'templates/funcionarios/detalhe_terc.html',
    'templates/professores/detalhe.html',
    'templates/professores/quadro_horarios_list.html',
    'usuarios/views.py',
    'ceja_gestao/settings.py',
]

def clean_file(filepath):
    if not os.path.exists(filepath):
        return
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    modified = False
    for bad, good in REPLACEMENTS.items():
        if bad in content:
            content = content.replace(bad, good)
            modified = True

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[FIXED] {filepath}")
    else:
        print(f"[OK] {filepath}")

if __name__ == '__main__':
    for fp in FILES:
        clean_file(fp)
