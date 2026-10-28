"""Context processor para injetar comunicados pendentes do Diário de Bordo nos templates."""
from django.db.models import Q


def diario_bordo_context(request):
    """
    Disponibiliza para os templates:
    - is_diretor_usuario: booleano se o usuário tem privilégio de direção
    - diario_pendentes_count: quantidade de comunicados pendentes de leitura pelo usuário
    - diario_pendentes_lista: lista com as ocorrências não lidas para exibição imediata
    """
    if not hasattr(request, 'user') or not request.user.is_authenticated:
        return {'is_diretor_usuario': False, 'diario_pendentes_count': 0, 'diario_pendentes_lista': []}

    is_diretor = (getattr(request.user, 'perfil', None) == 'diretor') or getattr(request.user, 'is_superuser', False)

    if not is_diretor:
        return {'is_diretor_usuario': False, 'diario_pendentes_count': 0, 'diario_pendentes_lista': []}

    try:
        from .models import OcorrenciaDiario
        # Ocorrências ativas que NÃO foram criadas por este usuário e que ele ainda NÃO leu
        qs_pendentes = OcorrenciaDiario.objects.filter(
            ativo=True
        ).exclude(
            autor=request.user
        ).exclude(
            leituras__usuario=request.user
        ).select_related('autor').order_by('-criado_em')

        count = qs_pendentes.count()
        lista = list(qs_pendentes[:10]) if count > 0 else []

        return {
            'is_diretor_usuario': True,
            'diario_pendentes_count': count,
            'diario_pendentes_lista': lista,
        }
    except Exception:
        # Previne falhas se as tabelas ainda não foram migradas
        return {
            'is_diretor_usuario': is_diretor,
            'diario_pendentes_count': 0,
            'diario_pendentes_lista': [],
        }

