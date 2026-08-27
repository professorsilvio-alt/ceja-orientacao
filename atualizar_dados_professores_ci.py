"""
Script para atualizar as Datas da C.I. de Movimentação, Matrículas, IDs e 
calcular a Classificação automática dos professores por ordem cronológica.
"""
import os
import sys
import unicodedata
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ceja_gestao.settings')
django.setup()

from professores.models import Professor
from datetime import datetime

DADOS_EXCEL = [
    {"id_vinculo": "40645924/2", "matricula": "2427227", "nome": "Luis Carlos Henriques Monteiro", "cargo": "Prof Doc I", "disciplina": "Educação Física", "ci_date": "1991-02-05"},
    {"id_vinculo": "39994856/2", "matricula": "2423853", "nome": "Gerson do Nascimento", "cargo": "Prof Doc I", "disciplina": "Ciências", "ci_date": "1993-05-25"},
    {"id_vinculo": "33289115/1", "matricula": "8396657", "nome": "David Santos da Cunha", "cargo": "Prof Doc I", "disciplina": "Geografia", "ci_date": "1999-09-16"},
    {"id_vinculo": "43173896/1", "matricula": "9364506", "nome": "Rafael de Amaral Maia", "cargo": "Prof Doc I", "disciplina": "Sociologia", "ci_date": "2007-11-06"},
    {"id_vinculo": "42014310/2", "matricula": "9330671", "nome": "Luciana da Silva Cavalcante", "cargo": "Prof Doc I", "disciplina": "Inglês", "ci_date": "2007-12-28"},
    {"id_vinculo": "33380473/3", "matricula": "9285685", "nome": "Ozana Azevedo da Silva Santos", "cargo": "Prof Doc I", "disciplina": "Matemática", "ci_date": "2007-12-28"},
    {"id_vinculo": "42782490/1", "matricula": "9340043", "nome": "Wanderley Farias de Souza", "cargo": "Prof Doc I", "disciplina": "Inglês", "ci_date": "2007-12-28"},
    {"id_vinculo": "42032768/1", "matricula": "9171927", "nome": "Sílvio Luiz Fernandes Freitas", "cargo": "Prof Doc I", "disciplina": "Matemática", "ci_date": "2008-04-18"},
    {"id_vinculo": "32878745/2", "matricula": "9451022", "nome": "Elazaro Moses Mokrabe", "cargo": "Prof Doc I", "disciplina": "Ciências", "ci_date": "2008-05-05"},
    {"id_vinculo": "33230366/2", "matricula": "9363334", "nome": "Eliane Santos de Oliveira", "cargo": "Prof Doc I", "disciplina": "Educação Física", "ci_date": "2009-02-13"},
    {"id_vinculo": "42027756/1", "matricula": "9171968", "nome": "Delma Patricia Nunes dos Santos", "cargo": "Prof Doc I", "disciplina": "Ciências", "ci_date": "2009-09-22"},
    {"id_vinculo": "42635217/2", "matricula": "9416850", "nome": "Viviane Souza de Freitas da Silva", "cargo": "Prof Doc I", "disciplina": "Química", "ci_date": "2010-02-01"},
    {"id_vinculo": "42809070/2", "matricula": "9447509", "nome": "Arlindo de Mello Junior", "cargo": "Prof Doc I", "disciplina": "Matemática", "ci_date": "2011-12-31"},
    {"id_vinculo": "20715870/2", "matricula": "9278862", "nome": "Carlos Alberto da Silva Laurindo", "cargo": "Prof Doc I", "disciplina": "História", "ci_date": "2011-12-31"},
    {"id_vinculo": "41920678/2", "matricula": "9186669", "nome": "Leandro de Oliveira Moreira", "cargo": "Prof Doc I", "disciplina": "Matemática", "ci_date": "2011-12-31"},
    {"id_vinculo": "40145158/2", "matricula": "2824076", "nome": "Eleonora da Silva Paulino Rocha", "cargo": "Prof Doc I", "disciplina": "Filosofia", "ci_date": "2013-08-09"},
    {"id_vinculo": "39067432/1", "matricula": "8314544", "nome": "Sandra Helena Batista da Silva", "cargo": "Prof Doc I", "disciplina": "Língua Portuguesa", "ci_date": "2014-02-19"},
    {"id_vinculo": "33514585/2", "matricula": "8338691", "nome": "Isabel Cristina Lemos de Souza", "cargo": "Prof Doc I", "disciplina": "Biologia", "ci_date": "2014-09-27"},
    {"id_vinculo": "41875680/2", "matricula": "9193665", "nome": "Elinete da Silva Aquino", "cargo": "Prof Doc I", "disciplina": "Sociologia", "ci_date": "2015-02-02"},
    {"id_vinculo": "34835075/1", "matricula": "50149939", "nome": "Jose Carlos Rodrigues de Carvalho", "cargo": "Prof Doc I", "disciplina": "Geografia", "ci_date": "2015-02-02"},
    {"id_vinculo": "43323430/3", "matricula": "30337042", "nome": "Marcela Costa Avila", "cargo": "Prof Doc I", "disciplina": "Química", "ci_date": "2015-02-02"},
    {"id_vinculo": "34834400/2", "matricula": "2911345", "nome": "Maria das Graças Santos Carneiro", "cargo": "Prof Doc I", "disciplina": "Língua Portuguesa", "ci_date": "2015-02-02"},
    {"id_vinculo": "43870813/1", "matricula": "9644394", "nome": "Maxuell Rodrigues Xavier", "cargo": "Prof Doc I", "disciplina": "Matemática", "ci_date": "2015-02-02"},
    {"id_vinculo": "5665809/5", "matricula": "9142126", "nome": "Reinaldo Augusto Simões", "cargo": "Prof Doc I", "disciplina": "Matemática", "ci_date": "2015-02-02"},
    {"id_vinculo": "40124339/2", "matricula": "8388480", "nome": "Rose Maria da Fonseca Lima", "cargo": "Prof Doc I", "disciplina": "Educação Física", "ci_date": "2015-02-02"},
    {"id_vinculo": "43267211/1", "matricula": "9408238", "nome": "Thalles Yvson Alves de Souza", "cargo": "Prof Doc I", "disciplina": "Educação Artística", "ci_date": "2015-02-02"},
    {"id_vinculo": "50264362/1", "matricula": "30589881", "nome": "Rafael Souza de Oliveira", "cargo": "Prof Doc I", "disciplina": "Espanhol", "ci_date": "2016-02-03"},
    {"id_vinculo": "50347764/2", "matricula": "30848071", "nome": "Leonardo César de Oliveira Marques", "cargo": "Prof Doc I", "disciplina": "Física", "ci_date": "2016-03-03"},
    {"id_vinculo": "44161689/3", "matricula": "31056526", "nome": "Fabiana Rodrigues de Souza", "cargo": "Prof Doc I", "disciplina": "Língua Portuguesa", "ci_date": "2018-09-13"},
    {"id_vinculo": "43877699/1", "matricula": "9617648", "nome": "Jordan de Aguiar Leal", "cargo": "Prof Doc I", "disciplina": "Matemática", "ci_date": "2019-02-02"},
    {"id_vinculo": "42014310/1", "matricula": "9129990", "nome": "Luciana da Silva Cavalcante", "cargo": "Prof Doc I", "disciplina": "Inglês", "ci_date": "2019-09-26"},
    {"id_vinculo": "33230366/1", "matricula": "50231752", "nome": "Eliane Santos de Oliveira", "cargo": "Prof Doc I", "disciplina": "Educação Física", "ci_date": "2021-03-12"},
    {"id_vinculo": "42032768/2", "matricula": "30307292", "nome": "Sílvio Luiz Fernandes Freitas", "cargo": "Prof Doc I", "disciplina": "Matemática", "ci_date": "2021-03-19"},
    {"id_vinculo": "50174789/1", "matricula": "30476170", "nome": "Vitor da Costa Souza", "cargo": "Prof Doc I", "disciplina": "Matemática", "ci_date": "2021-10-15"},
    {"id_vinculo": "33421447/1", "matricula": "8255101", "nome": "Mario Medeiros de Farias", "cargo": "Prof Doc I", "disciplina": "Sociologia", "ci_date": "2021-12-09"},
    {"id_vinculo": "44161689/1", "matricula": "9721259", "nome": "Fabiana Rodrigues de Souza", "cargo": "Prof Doc I", "disciplina": "Língua Portuguesa", "ci_date": "2022-02-02"},
    {"id_vinculo": "43268889/1", "matricula": "9415043", "nome": "Fernando Lima de Mesquita", "cargo": "Prof Doc I", "disciplina": "Filosofia", "ci_date": "2022-04-27"},
    {"id_vinculo": "42561086/1", "matricula": "9260407", "nome": "Daniela Lima de Mesquita Matos", "cargo": "Prof Doc I", "disciplina": "Língua Portuguesa", "ci_date": "2022-07-01"},
    {"id_vinculo": "42561086/2", "matricula": "9505157", "nome": "Daniela Lima de Mesquita Matos", "cargo": "Prof Doc I", "disciplina": "Língua Portuguesa", "ci_date": "2022-07-01"},
    {"id_vinculo": "41925912/5", "matricula": "9556275", "nome": "Alessandra Teixeira Batista Crespo", "cargo": "Prof Doc I", "disciplina": "Química", "ci_date": "2022-12-23"},
    {"id_vinculo": "42809070/1", "matricula": "9300294", "nome": "Arlindo de Mello Junior", "cargo": "Prof Doc I", "disciplina": "Matemática", "ci_date": "2022-12-23"},
    {"id_vinculo": "42108640/4", "matricula": "9703729", "nome": "Izabel Cristina da Cruz Pereira", "cargo": "Prof Doc I", "disciplina": "Inglês", "ci_date": "2022-12-23"},
    {"id_vinculo": "43268889/2", "matricula": "9626573", "nome": "Fernando Lima de Mesquita", "cargo": "Prof Doc I", "disciplina": "Filosofia", "ci_date": "2023-02-10"},
    {"id_vinculo": "42635217/1", "matricula": "9288572", "nome": "Viviane Souza de Freitas da Silva", "cargo": "Prof Doc I", "disciplina": "Química", "ci_date": "2023-05-05"},
    {"id_vinculo": "43905129/1", "matricula": "9665225", "nome": "Thamiris dos Santos Couto", "cargo": "Prof Doc I", "disciplina": "Língua Portuguesa", "ci_date": "2023-12-27"},
    {"id_vinculo": "50098403/1", "matricula": "30347868", "nome": "Fabiane Silva Martins", "cargo": "Prof Doc I", "disciplina": "História", "ci_date": "2024-03-08"},
    {"id_vinculo": "42097428/2", "matricula": "9443938", "nome": "Vitor Oliveira de Vasconcelos", "cargo": "Prof Doc I", "disciplina": "Geografia", "ci_date": "2024-03-20"},
    {"id_vinculo": "43891489/2", "matricula": "9718420", "nome": "Edilson Reis de Souza Junior", "cargo": "Prof Doc I", "disciplina": "Física", "ci_date": "2024-05-16"},
    {"id_vinculo": "42611610/2", "matricula": "9336116", "nome": "Fabiana de Paula Lessa Oliveira", "cargo": "Prof Doc I", "disciplina": "Língua Portuguesa", "ci_date": "2024-05-22"},
]

def norm(text):
    if not text: return ''
    n = unicodedata.normalize('NFD', text)
    return ''.join(c for c in n if unicodedata.category(c) != 'Mn').lower().strip()

def executar():
    print("==================================================")
    print("Atualizando Datas de C.I., Matriculas e Classificacao")
    print("==================================================")

    # 1. Mapeia professores existentes
    profs_existentes = list(Professor.objects.all())
    
    # Registra quais registros do Excel já foram processados
    processados = set()

    for idx, item in enumerate(DADOS_EXCEL, 1):
        nome_item = item['nome']
        matr_item = item['matricula']
        id_item = item['id_vinculo']
        ci_dt = datetime.strptime(item['ci_date'], '%Y-%m-%d').date()

        # Busca por matrícula principal ou de acumulação ou nome
        prof_encontrado = None
        for p in profs_existentes:
            if p.matricula == matr_item or p.matricula_acumulacao == matr_item:
                prof_encontrado = p
                break
            if p.id_vinculo == id_item or p.id_vinculo_acumulacao == id_item:
                prof_encontrado = p
                break
            if norm(p.nome_completo) == norm(nome_item):
                prof_encontrado = p
                break

        if prof_encontrado:
            # Se for a 1ª vez que encontramos esse professor, é a 1ª matrícula
            if prof_encontrado.pk not in processados:
                prof_encontrado.nome_completo = item['nome']
                prof_encontrado.matricula = matr_item
                prof_encontrado.id_vinculo = id_item
                prof_encontrado.cargo = item['cargo']
                prof_encontrado.disciplina_ingresso = item['disciplina']
                prof_encontrado.data_ci_movimentacao = ci_dt
                if not prof_encontrado.data_ingresso_unidade:
                    prof_encontrado.data_ingresso_unidade = ci_dt
                prof_encontrado.situacao_matricula_1 = 'ativo'
                prof_encontrado.ativo = True
                prof_encontrado.save()
                processados.add(prof_encontrado.pk)
                print(f"[OK 1ª Matrícula] {prof_encontrado.nome_completo} | C.I.: {ci_dt.strftime('%d/%m/%Y')} | Matr.: {matr_item}")
            else:
                # É a 2ª matrícula (acumulação) do mesmo professor
                prof_encontrado.id_vinculo_acumulacao = id_item
                prof_encontrado.matricula_acumulacao = matr_item
                prof_encontrado.cargo_acumulacao = item['cargo']
                prof_encontrado.disciplina_ingresso_acumulacao = item['disciplina']
                prof_encontrado.data_admissao_acumulacao = ci_dt
                prof_encontrado.situacao_matricula_2 = 'ativo'
                prof_encontrado.save()
                print(f"[OK 2ª Matrícula / Acumulação] {prof_encontrado.nome_completo} | Matr. 2: {matr_item} | ID 2: {id_item}")
        else:
            # Não existe no banco: cria novo professor
            cpf_dummy = f"000{idx:02d}00000"[:11]
            novo_p = Professor.objects.create(
                cpf=cpf_dummy,
                nome_completo=item['nome'],
                matricula=matr_item,
                id_vinculo=id_item,
                cargo=item['cargo'],
                disciplina_ingresso=item['disciplina'],
                data_ci_movimentacao=ci_dt,
                data_ingresso_unidade=ci_dt,
                situacao_matricula_1='ativo',
                ativo=True
            )
            processados.add(novo_p.pk)
            print(f"[CRIADO] {novo_p.nome_completo} | C.I.: {ci_dt.strftime('%d/%m/%Y')} | Matr.: {matr_item}")

    # 2. Recalcula a Classificação de Todos os Professores Ativos pela Data da C.I.
    print("\n==================================================")
    print("Recalculando a Classificacao Oficial dos Servidores...")
    print("==================================================")

    professores_ativos = list(Professor.objects.filter(ativo=True))
    
    # Ordena por data_ci_movimentacao ascending (mais antigos em 1º)
    def key_ordem(p):
        d = p.data_ci_movimentacao or p.data_ingresso_unidade or p.data_admissao
        return (d if d else datetime(2099, 1, 1).date(), norm(p.nome_completo))

    professores_ativos.sort(key=key_ordem)

    for rank, p in enumerate(professores_ativos, 1):
        p.classificacao = rank
        p.save(update_fields=['classificacao'])
        dt_str = p.data_ci_movimentacao.strftime('%d/%m/%Y') if p.data_ci_movimentacao else "Sem Data"
        print(f"  Posição #{rank:02d} | {p.nome_completo[:35]:<35} | C.I.: {dt_str} | Matr.: {p.matricula}")

    print("==================================================")
    print(f"Processo concluido com sucesso! Total de {len(professores_ativos)} professores classificados.")
    print("==================================================")

if __name__ == '__main__':
    executar()
