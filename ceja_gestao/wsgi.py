"""
WSGI config for ceja_gestao project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
import sys

# Sincroniza com git ANTES de importar o django application se estiver no servidor
try:
    import subprocess
    _base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if os.path.exists(os.path.join(_base_dir, '.git')):
        res = subprocess.run(['git', 'pull', '--ff-only'], cwd=_base_dir, capture_output=True, timeout=12)
        if res.returncode != 0:
            subprocess.run(['git', 'fetch', 'origin', 'main'], cwd=_base_dir, capture_output=True, timeout=15)
            subprocess.run(['git', 'reset', '--hard', 'origin/main'], cwd=_base_dir, capture_output=True, timeout=15)
except Exception as _ge:
    pass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ceja_gestao.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Executa migrações pendentes de forma segura sem travar stdout/stderr
try:
    import io
    from django.core.management import call_command
    out = io.StringIO()
    call_command('migrate', interactive=False, stdout=out, stderr=out)
except Exception:
    pass
