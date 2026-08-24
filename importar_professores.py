import os
import django
import re
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ceja_gestao.settings')
django.setup()

from professores.models import Professor, Disciplina
from usuarios.models import Usuario

PROFESSORES_DATA = [
    {"id_vinculo": "40645924/2", "matricula": "2427227", "nome": "Luis Carlos Henriques Monteiro", "cargo": "professor_i", "disciplina": "educacao_fisica", "data_ci": "1991-02-05"},
    {"id_vinculo": "39994856/2", "matricula": "2423853", "nome": "Gerson do Nascimento", "cargo": "professor_i", "disciplina": "biologia", "data_ci": "1993-05-25"},
    {"id_vinculo": "33289115/1", "matricula": "8396657", "nome": "David Santos da Cunha", "cargo": "professor_i", "disciplina": "geografia", "data_ci": "1999-09-16"},
    {"id_vinculo": "43173896/1", "matricula": "9364506", "nome": "Rafael de Amaral Maia", "cargo": "professor_i", "disciplina": "sociologia", "data_ci": "2007-11-06"},
    {"id_vinculo": "42014310/2", "matricula": "9330671", "nome": "Luciana da Silva Cavalcante", "cargo": "professor_i", "disciplina": "ingles", "data_ci": "2007-12-28"},
    {"id_vinculo": "33380473/3", "matricula": "9285685", "nome": "Ozana Azevedo da Silva Santos", "cargo": "professor_i", "disciplina": "matematica", "data_ci": "2007-12-28"},
    {"id_vinculo": "42782490/1", "matricula": "9340043", "nome": "Wanderley Farias de Souza", "cargo": "professor_i", "disciplina": "ingles", "data_ci": "2007-12-28"},
    {"id_vinculo": "42032768/1", "matricula": "9171927", "nome": "Sílvio Luiz Fernandes Freitas", "cargo": "professor_i", "disciplina": "matematica", "data_ci": "2008-04-18"},
    {"id_vinculo": "32878745/2", "matricula": "9451022", "nome": "Elazaro Moses Mokrabe", "cargo": "professor_i", "disciplina": "biologia", "data_ci": "2008-05-05"},
    {"id_vinculo": "33230366/2", "matricula": "9363334", "nome": "Eliane Santos de Oliveira", "cargo": "professor_i", "disciplina": "educacao_fisica", "data_ci": "2009-02-13"},
    {"id_vinculo": "42027756/1", "matricula": "9171968", "nome": "Delma Patricia Nunes dos Santos", "cargo": "professor_i", "disciplina": "biologia", "data_ci": "2009-09-22"},
    {"id_vinculo": "42635217/2", "matricula": "9416850", "nome": "Viviane Souza de Freitas da Silva", "cargo": "professor_i", "disciplina": "quimica", "data_ci": "2010-02-01"},
    {"id_vinculo": "42809070/2", "matricula": "9447509", "nome": "Arlindo de Mello Junior", "cargo": "professor_i", "disciplina": "matematica", "data_ci": "2011-12-31"},
    {"id_vinculo": "20715870/2", "matricula": "9278862", "nome": "Carlos Alberto da Silva Laurindo", "cargo": "professor_i", "disciplina": "historia", "data_ci": "2011-12-31"},
    {"id_vinculo": "41920678/2", "matricula": "9186669", "nome": "Leandro de Oliveira Moreira", "cargo": "professor_i", "disciplina": "matematica", "data_ci": "2011-12-31"},
    {"id_vinculo": "40145158/2", "matricula": "2824076", "nome": "Eleonora da Silva Paulino Rocha", "cargo": "professor_i", "disciplina": "filosofia", "data_ci": "2013-08-09"},
    {"id_vinculo": "39067432/1", "matricula": "8314544", "nome": "Sandra Helena Batista da Silva", "cargo": "professor_i", "disciplina": "portugues", "data_ci": "2014-02-19"},
    {"id_vinculo": "33514585/2", "matricula": "8338691", "nome": "Isabel Cristina Lemos de Souza", "cargo": "professor_i", "disciplina": "biologia", "data_ci": "2014-09-27"},
    {"id_vinculo": "41875680/2", "matricula": "9193665", "nome": "Elinete da Silva Aquino", "cargo": "professor_i", "disciplina": "sociologia", "data_ci": "2015-02-02"},
    {"id_vinculo": "34835075/1", "matricula": "50149939", "nome": "Jose Carlos Rodrigues de Carvalho", "cargo": "professor_i", "disciplina": "geografia", "data_ci": "2015-02-02"},
    {"id_vinculo": "43323430/3", "matricula": "30337042", "nome": "Marcela Costa Avila", "cargo": "professor_i", "disciplina": "quimica", "data_ci": "2015-02-02"},
    {"id_vinculo": "34834400/2", "matricula": "2911345", "nome": "Maria das Graças Santos Carneiro", "cargo": "professor_i", "disciplina": "portugues", "data_ci": "2015-02-02"},
    {"id_vinculo": "43870813/1", "matricula": "9644394", "nome": "Maxuell Rodrigues Xavier", "cargo": "professor_i", "disciplina": "matematica", "data_ci": "2015-02-02"},
    {"id_vinculo": "5665809/5", "matricula": "9142126", "nome": "Reinaldo Augusto Simões", "cargo": "professor_i", "disciplina": "matematica", "data_ci": "2015-02-02"},
    {"id_vinculo": "40124339/2", "matricula": "8388480", "nome": "Rose Maria da Fonseca Lima", "cargo": "professor_i", "disciplina": "educacao_fisica", "data_ci": "2015-02-02"},
    {"id_vinculo": "43267211/1", "matricula": "9408238", "nome": "Thalles Yvson Alves de Souza", "cargo": "professor_i", "disciplina": "artes", "data_ci": "2015-02-02"},
    {"id_vinculo": "50264362/1", "matricula": "30589881", "nome": "Rafael Souza de Oliveira", "cargo": "professor_i", "disciplina": "espanhol", "data_ci": "2016-02-03"},
    {"id_vinculo": "50347764/2", "matricula": "30848071", "nome": "Leonardo César de Oliveira Marques", "cargo": "professor_i", "disciplina": "fisica", "data_ci": "2016-03-03"},
    {"id_vinculo": "44161689/3", "matricula": "31056526", "nome": "Fabiana Rodrigues de Souza", "cargo": "professor_i", "disciplina": "portugues", "data_ci": "2018-09-13"},
    {"id_vinculo": "43877699/1", "matricula": "9617648", "nome": "Jordan de Aguiar Leal", "cargo": "professor_i", "disciplina": "matematica", "data_ci": "2019-02-02"},
    {"id_vinculo": "42014310/1", "matricula": "9129990", "nome": "Luciana da Silva Cavalcante", "cargo": "professor_i", "disciplina": "ingles", "data_ci": "2019-09-26"},
    {"id_vinculo": "33230366/1", "matricula": "50231752", "nome": "Eliane Santos de Oliveira", "cargo": "professor_i", "disciplina": "educacao_fisica", "data_ci": "2021-03-12"},
    {"id_vinculo": "42032768/2", "matricula": "30307292", "nome": "Sílvio Luiz Fernandes Freitas", "cargo": "professor_i", "disciplina": "matematica", "data_ci": "2021-03-19"},
    {"id_vinculo": "50174789/1", "matricula": "30476170", "nome": "Vitor da Costa Souza", "cargo": "professor_i", "disciplina": "matematica", "data_ci": "2021-10-15"},
    {"id_vinculo": "33421447/1", "matricula": "8255101", "nome": "Mario Medeiros de Farias", "cargo": "professor_i", "disciplina": "sociologia", "data_ci": "2021-12-09"},
    {"id_vinculo": "44161689/1", "matricula": "9721259", "nome": "Fabiana Rodrigues de Souza", "cargo": "professor_i", "disciplina": "portugues", "data_ci": "2022-02-02"},
    {"id_vinculo": "43268889/1", "matricula": "9415043", "nome": "Fernando Lima de Mesquita", "cargo": "professor_i", "disciplina": "filosofia", "data_ci": "2022-04-27"},
    {"id_vinculo": "42561086/1", "matricula": "9260407", "nome": "Daniela Lima de Mesquita Matos", "cargo": "professor_i", "disciplina": "portugues", "data_ci": "2022-07-01"},
    {"id_vinculo": "42561086/2", "matricula": "9505157", "nome": "Daniela Lima de Mesquita Matos", "cargo": "professor_i", "disciplina": "portugues", "data_ci": "2022-07-01"},
    {"id_vinculo": "41925912/5", "matricula": "9556275", "nome": "Alessandra Teixeira Batista Crespo", "cargo": "professor_i", "disciplina": "quimica", "data_ci": "2022-12-23"},
    {"id_vinculo": "42809070/1", "matricula": "9300294", "nome": "Arlindo de Mello Junior", "cargo": "professor_i", "disciplina": "matematica", "data_ci": "2022-12-23"},
    {"id_vinculo": "42108640/4", "matricula": "9703729", "nome": "Izabel Cristina da Cruz Pereira", "cargo": "professor_i", "disciplina": "ingles", "data_ci": "2022-12-23"},
    {"id_vinculo": "43268889/2", "matricula": "9626573", "nome": "Fernando Lima de Mesquita", "cargo": "professor_i", "disciplina": "filosofia", "data_ci": "2023-02-10"},
    {"id_vinculo": "42635217/1", "matricula": "9288572", "nome": "Viviane Souza de Freitas da Silva", "cargo": "professor_i", "disciplina": "quimica", "data_ci": "2023-05-05"},
    {"id_vinculo": "43905129/1", "matricula": "9665225", "nome": "Thamiris dos Santos Couto", "cargo": "professor_i", "disciplina": "portugues", "data_ci": "2023-12-27"},
    {"id_vinculo": "50098403/1", "matricula": "30347868", "nome": "Fabiane Silva Martins", "cargo": "professor_i", "disciplina": "historia", "data_ci": "2024-03-08"},
    {"id_vinculo": "42097428/2", "matricula": "9443938", "nome": "Vitor Oliveira de Vasconcelos", "cargo": "professor_i", "disciplina": "geografia", "data_ci": "2024-03-20"},
    {"id_vinculo": "43891489/2", "matricula": "9718420", "nome": "Edilson Reis de Souza Junior", "cargo": "professor_i", "disciplina": "fisica", "data_ci": "2024-05-16"},
    {"id_vinculo": "42611610/2", "matricula": "9336116", "nome": "Fabiana de Paula Lessa Oliveira", "cargo": "professor_i", "disciplina": "portugues", "data_ci": "2024-05-22"},
]

def rodar_importacao():
    print("Iniciando importação de professores e usuários...")
    
    # Ordenar por data da CI para definir classificação (ordem de chegada)
    dados_ordenados = sorted(PROFESSORES_DATA, key=lambda x: x['data_ci'])
    
    professores_criados = 0
    usuarios_criados = 0

    for idx, d in enumerate(dados_ordenados, 1):
        dt_ci = datetime.strptime(d['data_ci'], '%Y-%m-%d').date()
        clean_id = re.sub(r'\D', '', d['id_vinculo'])
        cpf_num = clean_id.zfill(11)
        
        # Nome formatado e email único por id_vinculo
        nome = d['nome'].strip()
        partes = nome.lower().split()
        first_part = partes[0]
        last_part = partes[-1] if len(partes) > 1 else 'ceja'
        sufixo = clean_id[-3:]
        email = f"{first_part}.{last_part}.{sufixo}@cejarosasoares.edu.br"

        # Criar ou atualizar Professor
        prof, created_prof = Professor.objects.update_or_create(
            matricula=d['matricula'],
            defaults={
                'cpf': cpf_num,
                'nome_completo': nome,
                'cargo': d['cargo'],
                'disciplina_ingresso': d['disciplina'],
                'data_ci_movimentacao': dt_ci,
                'data_ingresso_unidade': dt_ci,
                'classificacao': idx,
                'email': email,
                'ativo': True,
            }
        )
        if created_prof:
            professores_criados += 1

        # Criar ou atualizar Usuário
        user = Usuario.objects.filter(cpf=cpf_num).first()
        if not user:
            user = Usuario.objects.create_user(
                cpf=cpf_num,
                nome_completo=nome,
                email=email,
                perfil='professor',
                password=cpf_num
            )
            usuarios_criados += 1
        else:
            user.nome_completo = nome
            user.email = email
            user.save()

    print("Importação concluída com sucesso!")
    print(f"Total Professores no banco: {Professor.objects.count()} (Novos nesta execução: {professores_criados})")
    print(f"Total Usuários no banco: {Usuario.objects.count()} (Novos nesta execução: {usuarios_criados})")

if __name__ == '__main__':
    rodar_importacao()
