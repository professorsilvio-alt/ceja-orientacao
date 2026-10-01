"""
WSGI config for ceja_gestao project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ceja_gestao.settings')

application = get_wsgi_application()

# Tenta sincronizar com git pull se estiver em ambiente com git configurado (ex: servidor de produção)
try:
    import subprocess
    _base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if os.path.exists(os.path.join(_base_dir, '.git')):
        subprocess.run(['git', 'pull', '--ff-only'], cwd=_base_dir, capture_output=True, timeout=12)
except Exception as _ge:
    pass

# Executa migrações pendentes automaticamente ao iniciar/recarregar o servidor
try:
    from django.core.management import call_command
    call_command('migrate', interactive=False)
except Exception as _e:
    print('Auto-migrate aviso:', _e, file=sys.stderr)

