from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse


def diretor_required(view_func):
    """
    Decorador que restringe o acesso estritamente a usuários autenticados
    com perfil de 'diretor' ou 'is_superuser'.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.path.startswith('/cerebro/api/'):
                return JsonResponse({'sucesso': False, 'erro': 'Não autenticado.'}, status=401)
            messages.error(request, 'Faça login para acessar o sistema.')
            return redirect('login')

        is_diretor = (getattr(request.user, 'perfil', None) == 'diretor') or request.user.is_superuser
        if not is_diretor:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.path.startswith('/cerebro/api/'):
                return JsonResponse({'sucesso': False, 'erro': 'Acesso exclusivo para Diretores.'}, status=403)
            messages.error(request, 'Acesso restrito à Direção da escola.')
            return redirect('dashboard')

        return view_func(request, *args, **kwargs)

    return _wrapped_view
