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

# Executa migrações pendentes automaticamente ao iniciar/recarregar o servidor
try:
    from django.core.management import call_command
    call_command('migrate', interactive=False)
except Exception as _e:
    print('Auto-migrate aviso:', _e, file=sys.stderr)

