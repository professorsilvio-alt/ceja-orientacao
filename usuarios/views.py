"""Views de autenticação e gestão de usuários"""
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from functools import wraps

from .forms import (
    LoginForm, TrocaSenhaForm, RecuperarSenhaForm,
    RedefinirSenhaForm, UsuarioForm
)

User = get_user_model()


import sys
import traceback

def custom_500_view(request):
    """Handler customizado para erros 500 — exibe detalhes do erro para facilitar diagnóstico."""
    type_, value_, tb_ = sys.exc_info()
    error_msg = f"{type_.__name__ if type_ else 'Erro'}: {value_}" if type_ else "Erro Interno no Servidor (500)"
    stack_trace = "".join(traceback.format_exception(type_, value_, tb_)) if tb_ else ""

    return render(request, '500.html', {
        'error_msg': error_msg,
        'stack_trace': stack_trace,
    }, status=500)


# ============================================================
# DECORADORES
# ============================================================

def diretor_required(view_func):
    """Permite acesso apenas a usuários com perfil 'diretor'."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.perfil != 'diretor' and not request.user.is_superuser:
            messages.error(request, 'Acesso restrito à Direção.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def verificar_primeiro_acesso(view_func):
    """Redireciona para troca de senha se for o primeiro acesso."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.primeiro_acesso:
            if request.path != '/trocar-senha/':
                return redirect('trocar_senha')
        return view_func(request, *args, **kwargs)
    return wrapper


# ============================================================
# AUTENTICAÇÃO
# ============================================================

def view_login(request):
    """Tela de login por CPF + senha."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        cpf = form.cleaned_data['cpf']
        password = form.cleaned_data['password']
        user = authenticate(request, username=cpf, password=password)
        if user:
            login(request, user)
            user.ultimo_login_sistema = timezone.now()
            user.save(update_fields=['ultimo_login_sistema'])
            if user.primeiro_acesso:
                messages.warning(request, 'Por segurança, você precisa criar uma nova senha para continuar.')
                return redirect('trocar_senha')
            return redirect('dashboard')
        else:
            messages.error(request, 'CPF ou senha incorretos. Verifique e tente novamente.')

    return render(request, 'usuarios/login.html', {'form': form})


@login_required
def view_logout(request):
    logout(request)
    return redirect('login')


@login_required
def view_trocar_senha(request):
    """Troca de senha — obrigatória no primeiro acesso."""
    form = TrocaSenhaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        request.user.set_password(form.cleaned_data['nova_senha'])
        request.user.primeiro_acesso = False
        request.user.save()
        # Faz o re-login para não perder a sessão
        user = authenticate(request, username=request.user.cpf, password=form.cleaned_data['nova_senha'])
        if user:
            login(request, user)
        messages.success(request, 'Senha atualizada com sucesso!')
        return redirect('dashboard')

    return render(request, 'usuarios/trocar_senha.html', {
        'form': form,
        'obrigatorio': request.user.primeiro_acesso
    })


def view_recuperar_senha(request):
    """Envia e-mail com link de redefinição de senha."""
    form = RecuperarSenhaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        try:
            user = User.objects.get(email=email, is_active=True)
            token = str(uuid.uuid4()).replace('-', '')
            user.token_recuperacao = token
            user.token_expiracao = timezone.now() + timedelta(hours=2)
            user.save(update_fields=['token_recuperacao', 'token_expiracao'])

            link = f"{settings.BASE_URL}/redefinir-senha/{token}/"
            send_mail(
                subject='CEJA — Redefinição de Senha',
                message=(
                    f'Olá, {user.primeiro_nome}!\n\n'
                    f'Você solicitou a redefinição de senha do sistema CEJA.\n'
                    f'Clique no link abaixo para criar uma nova senha:\n\n'
                    f'{link}\n\n'
                    f'Este link expira em 2 horas.\n\n'
                    f'Se não foi você quem solicitou, ignore este e-mail.\n\n'
                    f'CEJA Profa Rosa Soares — Mesquita/RJ'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,
            )
        except User.DoesNotExist:
            pass  # Não revela se o e-mail existe

        # Sempre exibe a mesma mensagem (segurança)
        messages.success(request, 'Se o e-mail estiver cadastrado, você receberá as instruções em breve.')
        return redirect('login')

    return render(request, 'usuarios/recuperar_senha.html', {'form': form})


def view_redefinir_senha(request, token):
    """Redefine a senha a partir do token recebido por e-mail."""
    try:
        user = User.objects.get(token_recuperacao=token, is_active=True)
    except User.DoesNotExist:
        messages.error(request, 'Link inválido ou expirado.')
        return redirect('login')

    if user.token_expiracao < timezone.now():
        messages.error(request, 'Este link expirou. Solicite um novo.')
        return redirect('recuperar_senha')

    form = RedefinirSenhaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user.set_password(form.cleaned_data['nova_senha'])
        user.token_recuperacao = ''
        user.token_expiracao = None
        user.primeiro_acesso = False
        user.save()
        messages.success(request, 'Senha redefinida com sucesso! Faça o login.')
        return redirect('login')

    return render(request, 'usuarios/redefinir_senha.html', {'form': form})


# ============================================================
# DASHBOARD
# ============================================================

@login_required
@verificar_primeiro_acesso
def view_dashboard(request):
    """Dashboard principal — conteúdo varia por perfil."""
    from professores.models import Professor
    from funcionarios.models import FuncionarioAdministrativo, FuncionarioTerceirizado
    from agenda.models import RegistroPresenca, ReservaAuditorio

    contexto = {
        'usuario': request.user,
    }

    if request.user.perfil == 'diretor' or request.user.is_superuser:
        contexto.update({
            'total_professores': Professor.objects.count(),
            'total_administrativos': FuncionarioAdministrativo.objects.count(),
            'total_terceirizados': FuncionarioTerceirizado.objects.count(),
            'total_usuarios': User.objects.filter(is_active=True).count(),
            'ausencias_hoje': RegistroPresenca.objects.filter(
                data=timezone.now().date()
            ).count(),
            'proximas_reservas': ReservaAuditorio.objects.filter(
                data__gte=timezone.now().date()
            ).order_by('data', 'hora_inicio')[:5],
        })

    return render(request, 'dashboard.html', contexto)


# ============================================================
# CRUD DE USUÁRIOS E PERMISSÕES (somente Diretor)
# ============================================================

@diretor_required
def view_listar_usuarios(request):
    perfil_filtro = request.GET.get('perfil', '')
    busca = request.GET.get('q', '').strip()

    qs = User.objects.all()

    if perfil_filtro:
        qs = qs.filter(perfil=perfil_filtro)

    if busca:
        qs = qs.filter(
            Q(nome_completo__icontains=busca) |
            Q(cpf__icontains=busca) |
            Q(email__icontains=busca)
        )

    qs = qs.order_by('perfil', 'nome_completo')

    contagem_perfis = {
        'todos': User.objects.count(),
        'diretor': User.objects.filter(perfil='diretor').count(),
        'professor': User.objects.filter(perfil='professor').count(),
        'administrativo': User.objects.filter(perfil='administrativo').count(),
        'terceirizado': User.objects.filter(perfil='terceirizado').count(),
    }

    return render(request, 'usuarios/listar.html', {
        'usuarios': qs,
        'perfil_filtro': perfil_filtro,
        'busca': busca,
        'contagem': contagem_perfis,
        'perfil_choices': User.PERFIL_CHOICES,
    })


@diretor_required
def view_alterar_perfil_rapido(request, cpf):
    """Permite ao Diretor alterar rapidamente o perfil de acesso de qualquer usuário."""
    user = get_object_or_404(User, pk=cpf)
    if request.method == 'POST':
        novo_perfil = request.POST.get('perfil')
        if novo_perfil in dict(User.PERFIL_CHOICES):
            perfil_antigo = user.get_perfil_display()
            user.perfil = novo_perfil
            if novo_perfil == 'diretor':
                user.is_staff = True
            user.save()
            messages.success(
                request,
                f'Perfil de {user.nome_completo} alterado de "{perfil_antigo}" para "{user.get_perfil_display()}".'
            )
    return redirect('listar_usuarios')


@diretor_required
def view_criar_usuario(request):
    form = UsuarioForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        cpf_limpo = form.cleaned_data['cpf']
        user.set_password(cpf_limpo)  # Senha inicial = CPF
        user.primeiro_acesso = True
        user.save()
        messages.success(request, f'Usuário {user.nome_completo} criado. Senha inicial: CPF.')
        return redirect('listar_usuarios')
    return render(request, 'usuarios/form.html', {'form': form, 'titulo': 'Novo Usuário'})


@diretor_required
def view_editar_usuario(request, cpf):
    user = get_object_or_404(User, pk=cpf)
    form = UsuarioForm(request.POST or None, instance=user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Usuário atualizado com sucesso.')
        return redirect('listar_usuarios')
    return render(request, 'usuarios/form.html', {
        'form': form,
        'titulo': f'Editar: {user.nome_completo}',
        'usuario': user,
    })


@diretor_required
def view_resetar_senha_usuario(request, cpf):
    """Diretor reseta a senha de um usuário para o CPF dele."""
    user = get_object_or_404(User, pk=cpf)
    if request.method == 'POST':
        user.set_password(cpf)
        user.primeiro_acesso = True
        user.save()
        messages.success(request, f'Senha de {user.primeiro_nome} resetada para o CPF.')
    return redirect('listar_usuarios')
