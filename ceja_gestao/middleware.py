import sys
import threading

_migrated = False
_lock = threading.Lock()


class AutoMigrateMiddleware:
    """Executa migrações pendentes automaticamente na primeira requisição recebida pelo servidor.
    
    Isso garante que em ambientes como o PythonAnywhere, onde o reload não executa
    o comando 'python manage.py migrate' no terminal, o banco de dados seja atualizado
    automaticamente sem quebrar as views.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        global _migrated
        if not _migrated:
            with _lock:
                if not _migrated:
                    _migrated = True
                    try:
                        from django.core.management import call_command
                        call_command('migrate', interactive=False)
                    except Exception as e:
                        print(f'[AutoMigrateMiddleware] Erro ao aplicar migrações: {e}', file=sys.stderr)
        return self.get_response(request)
