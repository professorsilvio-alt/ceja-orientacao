"""Backend de autenticação por CPF"""
from django.contrib.auth import get_user_model
import re

User = get_user_model()


class CPFBackend:
    """
    Autentica usando CPF (somente dígitos) + senha.
    Aceita CPF com ou sem formatação (pontos e traço).
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username:
            return None
        # Remove formatação do CPF
        cpf = re.sub(r'\D', '', str(username))
        try:
            user = User.objects.get(cpf=cpf)
        except User.DoesNotExist:
            return None

        if user.check_password(password) and user.is_active:
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
