from django.contrib import messages
from django.shortcuts import redirect


def csrf_falhou(request, reason=""):
    """Em vez da tela 403, volta ao login com aviso para tentar novamente."""
    messages.warning(request, "Sua página expirou. Tente entrar novamente.")
    return redirect('/login/')
