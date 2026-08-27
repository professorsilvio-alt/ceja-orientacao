"""
Script para cadastrar e atualizar todos os funcionários terceirizados da escola
com PIN padrão definido como os 4 primeiros dígitos do CPF.
"""
import os
import sys
import django

# Configura o ambiente Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ceja_gestao.settings')
django.setup()

from funcionarios.models import FuncionarioTerceirizado

FUNCIONARIOS = [
    {
        'nome_completo': 'Mauro Sabino de Andrade',
        'cpf': '98470116720',
        'cargo_funcao': 'Porteiro',
        'empresa_contratante': 'Terceirizada',
        'email': 'maurosabino19@gmail.com',
        'rg': 'Sem RG',
        'data_nascimento': '1985-01-01',
        'data_admissao': '2026-01-01',
        'ativo': True,
    },
    {
        'nome_completo': 'Tânia Mara Molina Azevedo Araújo',
        'cpf': '91242843787',
        'cargo_funcao': 'Copeira',
        'empresa_contratante': 'Terceirizada',
        'email': 'taniamarazevedo2017@gmail.com',
        'rg': 'Sem RG',
        'data_nascimento': '1985-01-01',
        'data_admissao': '2026-01-01',
        'ativo': True,
    },
    {
        'nome_completo': 'Jorge Luiz e Silva Cestari',
        'cpf': '09930989757',
        'cargo_funcao': 'Aux. Secretaria / Apoio Adm',
        'empresa_contratante': 'Terceirizada',
        'email': 'cestario_6@hotmail.com',
        'rg': 'Sem RG',
        'data_nascimento': '1985-01-01',
        'data_admissao': '2026-01-01',
        'ativo': True,
    },
    {
        'nome_completo': 'Anderson Clayton Soares Costa',
        'cpf': '01442077700',
        'cargo_funcao': 'Servente',
        'empresa_contratante': 'Terceirizada',
        'email': 'andersonclaytonsoarescosta@gmail.com',
        'rg': 'Sem RG',
        'data_nascimento': '1985-01-01',
        'data_admissao': '2026-01-01',
        'ativo': True,
    },
    {
        'nome_completo': 'Adriana dos Santos Lima',
        'cpf': '07360655714',
        'cargo_funcao': 'Servente',
        'empresa_contratante': 'Terceirizada',
        'email': 'adriendossantoslima881@gmail.com',
        'rg': 'Sem RG',
        'data_nascimento': '1985-01-01',
        'data_admissao': '2026-01-01',
        'ativo': True,
    },
    {
        'nome_completo': 'Douglas Lima de Souza',
        'cpf': '17180284742',
        'cargo_funcao': 'Servente',
        'empresa_contratante': 'Terceirizada',
        'email': 'limasouzado23@gmail.com',
        'rg': 'Sem RG',
        'data_nascimento': '1985-01-01',
        'data_admissao': '2026-01-01',
        'ativo': True,
    },
    {
        'nome_completo': 'Jorge Antonio Souza Dias',
        'cpf': '59521732768',
        'cargo_funcao': 'Servente',
        'empresa_contratante': 'Terceirizada',
        'email': 'jasd196015@gmail.com',
        'rg': 'Sem RG',
        'data_nascimento': '1985-01-01',
        'data_admissao': '2026-01-01',
        'ativo': True,
    },
    {
        'nome_completo': 'Jovane da Paixão Monteiro Geraldo Mendes',
        'cpf': '03651637751',
        'cargo_funcao': 'Servente',
        'empresa_contratante': 'Terceirizada',
        'email': 'jovanedapaixao@gmail.com',
        'rg': 'Sem RG',
        'data_nascimento': '1985-01-01',
        'data_admissao': '2026-01-01',
        'ativo': True,
    }
]

def importar():
    print("==================================================")
    print("Importando / Atualizando Funcionarios Terceirizados")
    print("==================================================")

    for item in FUNCIONARIOS:
        cpf_limpo = str(item['cpf']).strip().zfill(11)
        pin_padrao = cpf_limpo[:4]  # 4 primeiros dígitos do CPF

        func, created = FuncionarioTerceirizado.objects.get_or_create(
            cpf=cpf_limpo,
            defaults={
                'nome_completo': item['nome_completo'],
                'cargo_funcao': item['cargo_funcao'],
                'empresa_contratante': item['empresa_contratante'],
                'email': item['email'],
                'rg': item['rg'],
                'data_nascimento': item['data_nascimento'],
                'data_admissao': item['data_admissao'],
                'ativo': item['ativo'],
            }
        )

        if not created:
            func.nome_completo = item['nome_completo']
            func.cargo_funcao = item['cargo_funcao']
            func.empresa_contratante = item['empresa_contratante']
            func.email = item['email']
            func.ativo = item['ativo']

        # Define a senha/PIN de ponto (4 primeiros dígitos do CPF)
        func.definir_senha_ponto(pin_padrao)
        func.save()

        status_str = "CADASTRADO" if created else "ATUALIZADO"
        print(f"[OK] [{status_str}] {func.nome_completo}")
        print(f"   Cargo: {func.cargo_funcao} | CPF: {func.cpf} | PIN Padrao: {pin_padrao} | E-mail: {func.email}")

    print("==================================================")
    print(f"Concluido com sucesso! Total de {len(FUNCIONARIOS)} funcionarios cadastrados.")
    print("==================================================")

if __name__ == '__main__':
    importar()
