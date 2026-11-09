import sys
import threading
import io

_migrated = False
_lock = threading.Lock()


class AutoMigrateMiddleware:
    """Executa migrações pendentes automaticamente uma única vez se necessário,
    sem travar o banco de dados nem poluir stdout/stderr.
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
                        out = io.StringIO()
                        call_command('migrate', interactive=False, stdout=out, stderr=out)
                    except Exception as e:
                        pass
        return self.get_response(request)
