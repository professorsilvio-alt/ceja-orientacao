import os
import django
import re
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ceja_gestao.settings')
django.setup()

from funcionarios.models import FuncionarioAdministrativo
from usuarios.models import Usuario

FUNCIONARIOS_ADM_DATA = [
    {
        "id_vinculo": "40260437/2",
        "matricula": "12064176",
        "nome": "Lenice Luiza de Castro",
        "cargo": "Prof Doc II",
        "disc_ingresso": "Área Integrada",
        "data_ci": "2015-02-02",
        "funcao_atual": "Auxiliar de Secretaria"
    },
    {
        "id_vinculo": "35021942/1",
        "matricula": "50206663",
        "nome": "Iraci de Oliveira Costa Correia",
        "cargo": "Ag. Adm de Biblioteca",
        "disc_ingresso": "Ag. Adm de Biblioteca",
        "data_ci": "2017-12-26",
        "funcao_atual": "Agente Administrativo"
    },
    {
        "id_vinculo": "34259228/1",
        "matricula": "8405789",
        "nome": "Tania Maria Santiago Ribeiro de Azevedo",
        "cargo": "Prof Doc II",
        "disc_ingresso": "Área Integrada",
        "data_ci": "2019-12-05",
        "funcao_atual": "Professor Facilitador EAD"
    },
    {
        "id_vinculo": "39538621/1",
        "matricula": "50206994",
        "nome": "Luci Maria da Silva Dornelas",
        "cargo": "Merendeira",
        "disc_ingresso": "Merendeira",
        "data_ci": "2020-11-17",
        "funcao_atual": "Secretária"
    },
    {
        "id_vinculo": "35005874/1",
        "matricula": "50159730",
        "nome": "Noely França de Azevedo Monteiro",
        "cargo": "Prof Doc II",
        "disc_ingresso": "Área Integrada",
        "data_ci": "2022-07-06",
        "funcao_atual": "Professor Facilitador EAD"
    },
    {
        "id_vinculo": "33075344/1",
        "matricula": "8052094",
        "nome": "Patrícia Pinheiro Madeira",
        "cargo": "Prof Doc II",
        "disc_ingresso": "Área Integrada",
        "data_ci": "2024-03-09",
        "funcao_atual": "Agente de Leitura"
    },
    {
        "id_vinculo": "35002557/1",
        "matricula": "50159631",
        "nome": "Elaine Ambrósio Souto Maior",
        "cargo": "Prof Doc II",
        "disc_ingresso": "Área Integrada",
        "data_ci": "2024-05-04",
        "funcao_atual": "Professor Facilitador EAD"
    },
]

def rodar_importacao_adm():
    print("Iniciando importação de Funcionários Administrativos e criação de Usuários...")
    
    dados_ordenados = sorted(FUNCIONARIOS_ADM_DATA, key=lambda x: x['data_ci'])
    
    funcionarios_criados = 0
    usuarios_criados = 0

    for idx, d in enumerate(dados_ordenados, 1):
        dt_ci = datetime.strptime(d['data_ci'], '%Y-%m-%d').date()
        clean_id = re.sub(r'\D', '', d['id_vinculo'])
        cpf_num = clean_id.zfill(11)
        
        nome = d['nome'].strip()
        partes = nome.lower().split()
        first_part = partes[0]
        last_part = partes[-1] if len(partes) > 1 else 'ceja'
        sufixo = clean_id[-3:]
        email = f"{first_part}.{last_part}.{sufixo}@cejarosasoares.edu.br"

        # Criar ou atualizar FuncionarioAdministrativo
        func, created_func = FuncionarioAdministrativo.objects.update_or_create(
            matricula=d['matricula'],
            defaults={
                'cpf': cpf_num,
                'id_vinculo': d['id_vinculo'],
                'nome_completo': nome,
                'cargo': d['cargo'],
                'disciplina_ingresso': d['disc_ingresso'],
                'funcao_atual': d['funcao_atual'],
                'funcao_ingresso': d['disc_ingresso'],
                'data_ci_movimentacao': dt_ci,
                'data_ingresso_unidade': dt_ci,
                'classificacao': idx,
                'email': email,
                'ativo': True,
            }
        )
        if created_func:
            funcionarios_criados += 1

        # Criar ou atualizar Usuário com perfil 'administrativo'
        user = Usuario.objects.filter(cpf=cpf_num).first()
        if not user:
            user = Usuario.objects.create_user(
                cpf=cpf_num,
                nome_completo=nome,
                email=email,
                perfil='administrativo',
                password=cpf_num,
                id_vinculo=d['id_vinculo'],
                matricula=d['matricula']
            )
            usuarios_criados += 1
        else:
            user.nome_completo = nome
            user.id_vinculo = d['id_vinculo']
            user.matricula = d['matricula']
            user.email = email
            user.perfil = 'administrativo'
            user.save()

    print("Importação dos Funcionários Administrativos concluída com sucesso!")
    print(f"Total Funcionários ADM no banco: {FuncionarioAdministrativo.objects.count()} (Novos nesta execução: {funcionarios_criados})")
    print(f"Total Usuários no banco: {Usuario.objects.count()} (Novos nesta execução: {usuarios_criados})")

if __name__ == '__main__':
    rodar_importacao_adm()
