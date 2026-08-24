import pandas as pd
import json
import re
from datetime import datetime

excel_path = r'C:\Users\PC DIR 2 - SILVIO\Downloads\RCustServidores.xlsx'
df = pd.read_excel(excel_path, header=7)

# Remover duplicatas exatas de vinculo/matricula
df_clean = df.drop_duplicates(subset=['ID/VÍNCULO', 'MATRÍCULA'])

# Agrupar por CPF para que cada servidor apareca exatamente 1 vez
grouped = df_clean.groupby('CPF')

records = []
for cpf_int, group in grouped:
    cpf_num = re.sub(r'\D', '', str(cpf_int)).zfill(11)
    
    row1 = group.iloc[0]
    row2 = group.iloc[1] if len(group) > 1 else None
    
    mat2 = str(row2['MATRÍCULA']).strip() if (row2 is not None and pd.notna(row2.get('MATRÍCULA'))) else (
        str(int(row1['SEGUNDA MATRÍCULA'])).strip() if pd.notna(row1.get('SEGUNDA MATRÍCULA')) and row1.get('SEGUNDA MATRÍCULA') else ''
    )

    rec = {
        'cpf': cpf_num,
        'nome': str(row1['NOME COMPLETO']).strip().title(),
        
        # Posição 1 (Principal)
        'id_vinculo': str(row1['ID/VÍNCULO']).strip(),
        'matricula': str(row1['MATRÍCULA']).strip(),
        'cargo': str(row1['CARGO']).strip() if pd.notna(row1['CARGO']) else '',
        'disciplina_ingresso': str(row1['DISCIPLINA DE INGRESSO']).strip() if pd.notna(row1['DISCIPLINA DE INGRESSO']) else '',
        'funcao': str(row1['FUNÇÃO']).strip() if pd.notna(row1['FUNÇÃO']) else '',
        'tipo_funcao': str(row1['TIPO FUNÇÃO']).strip() if pd.notna(row1['TIPO FUNÇÃO']) else '',
        'regime_contratacao': str(row1['REGIME CONTRATACAO']).strip() if pd.notna(row1['REGIME CONTRATACAO']) else '',
        'data_admissao': str(row1.get('DATA ADMISSÃO')).split(' ')[0] if pd.notna(row1.get('DATA ADMISSÃO')) else '',
        'data_nomeacao': str(row1.get('DATA NOMEACAO')).split(' ')[0] if pd.notna(row1.get('DATA NOMEACAO')) else '',
        'ch_planejamento': int(row1['C.H.\nPLANEJAMENTO']) if pd.notna(row1.get('C.H.\nPLANEJAMENTO')) else None,
        'ch_regencia': int(row1['C.H.\nREGÊNCIA']) if pd.notna(row1.get('C.H.\nREGÊNCIA')) else None,
        'ch_complementacao': int(row1['C.H.\nCOMPLMENTAÇÃO']) if pd.notna(row1.get('C.H.\nCOMPLMENTAÇÃO')) else None,
        'ch_total': int(row1['C.H.\nTOTAL']) if pd.notna(row1.get('C.H.\nTOTAL')) else None,
        
        # Posição 2 (Segunda Matrícula / Acumulação)
        'id_vinculo_acumulacao': str(row2['ID/VÍNCULO']).strip() if row2 is not None else '',
        'matricula_acumulacao': mat2,
        'cargo_acumulacao': str(row2['CARGO']).strip() if (row2 is not None and pd.notna(row2['CARGO'])) else '',
        'disciplina_ingresso_acumulacao': str(row2['DISCIPLINA DE INGRESSO']).strip() if (row2 is not None and pd.notna(row2['DISCIPLINA DE INGRESSO'])) else '',
        'funcao_acumulacao': str(row2['FUNÇÃO']).strip() if (row2 is not None and pd.notna(row2['FUNÇÃO'])) else '',
        'ch_total_acumulacao': int(row2['C.H.\nTOTAL']) if (row2 is not None and pd.notna(row2.get('C.H.\nTOTAL'))) else None,
        'data_admissao_acumulacao': str(row2.get('DATA ADMISSÃO')).split(' ')[0] if (row2 is not None and pd.notna(row2.get('DATA ADMISSÃO'))) else '',
        
        'acumulacao': str(row1['ACUMULAÇÃO']).strip() if pd.notna(row1.get('ACUMULAÇÃO')) else '',
        'endereco': str(row1['ENDEREÇO']).strip() if pd.notna(row1.get('ENDEREÇO')) else '',
        'numero': str(row1['END NUM']).strip() if pd.notna(row1.get('END NUM')) else '',
        'complemento': str(row1['END COMPL']).strip() if pd.notna(row1.get('END COMPL')) else '',
        'bairro': str(row1['BAIRRO']).strip() if pd.notna(row1.get('BAIRRO')) else '',
        'municipio': str(row1['MUNICIPIO END']).strip() if pd.notna(row1.get('MUNICIPIO END')) else '',
        'data_nascimento': str(row1.get('DT NASC')).split(' ')[0] if pd.notna(row1.get('DT NASC')) else '',
        'sexo': str(row1['SEXO']).strip() if pd.notna(row1.get('SEXO')) else '',
        'telefone': str(row1['FONE']).strip() if pd.notna(row1.get('FONE')) else '',
        'celular': str(row1['CELULAR']).strip() if pd.notna(row1.get('CELULAR')) else '',
        'email_interno': str(row1['E-MAIL INTERNO']).strip() if pd.notna(row1.get('E-MAIL INTERNO')) else '',
        'email_google': str(row1['E-MAIL GOOGLE']).strip() if pd.notna(row1.get('E-MAIL GOOGLE')) else '',
        'email_alternativo': str(row1['E-MAIL ALTERNATIVO']).strip() if pd.notna(row1.get('E-MAIL ALTERNATIVO')) else '',
    }
    records.append(rec)

json_dados = json.dumps(records, ensure_ascii=False, indent=4)
json_dados = json_dados.replace(': null', ': None').replace(': true', ': True').replace(': false', ': False')

python_code = '''import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ceja_gestao.settings')
django.setup()

from professores.models import Professor
from funcionarios.models import FuncionarioAdministrativo
from usuarios.models import Usuario

DADOS = ''' + json_dados + '''

def parse_d(val):
    if not val:
        return None
    val_str = str(val).strip()
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d'):
        try:
            return datetime.strptime(val_str, fmt).date()
        except ValueError:
            pass
    return None

def executar():
    print("Iniciando povoamento automatico com classificacao por antiguidade...")
    cpfs_reais = {r['cpf'] for r in DADOS}
    
    Professor.objects.all().delete()
    FuncionarioAdministrativo.objects.all().delete()
    
    usuarios_fakes = Usuario.objects.exclude(cpf='00000000000').exclude(cpf__in=cpfs_reais)
    usuarios_fakes.delete()

    adm_keywords = ['SERVENTE', 'AGENTE ADM', 'SECRETÁRIO', 'SECRETARIA', 'MERENDEIRA', 'ZELADOR', 'FACILITADOR', 'LEITURA']

    prof_list = []
    adm_list = []

    for r in DADOS:
        cargo = r['cargo']
        funcao = r['funcao']
        is_adm = any(k in funcao.upper() for k in adm_keywords) or any(k in cargo.upper() for k in ['SERVENTE', 'MERENDEIRA', 'ZELADOR'])
        if is_adm:
            adm_list.append(r)
        else:
            prof_list.append(r)

    # Ordenar professores por data de admissao (mais antigos primeiro) para definir classificacao
    def get_adm_key(item):
        d = parse_d(item['data_admissao'])
        return d if d else datetime(2099, 1, 1).date()

    prof_list.sort(key=get_adm_key)
    adm_list.sort(key=get_adm_key)

    for rank, r in enumerate(prof_list, start=1):
        cpf_num = r['cpf']
        id_vinculo = r['id_vinculo']
        matricula = r['matricula']
        matricula_ac = r['matricula_acumulacao']
        nome = r['nome']
        cargo = r['cargo']
        disc_ing = r['disciplina_ingresso']
        funcao = r['funcao']
        tipo_funcao = r['tipo_funcao']
        regime = r['regime_contratacao']
        
        dt_adm = parse_d(r['data_admissao'])
        dt_nom = parse_d(r['data_nomeacao'])
        dt_nasc = parse_d(r['data_nascimento'])
        
        primary_email = r['email_google'] or r['email_interno'] or r['email_alternativo'] or (cpf_num + "@cejarosasoares.edu.br")

        Professor.objects.create(
            cpf=cpf_num, id_vinculo=id_vinculo, matricula=matricula,
            id_vinculo_acumulacao=r['id_vinculo_acumulacao'], matricula_acumulacao=matricula_ac,
            cargo_acumulacao=r['cargo_acumulacao'], disciplina_ingresso_acumulacao=r['disciplina_ingresso_acumulacao'],
            funcao_acumulacao=r['funcao_acumulacao'], ch_total_acumulacao=r['ch_total_acumulacao'],
            data_admissao_acumulacao=parse_d(r['data_admissao_acumulacao']),
            nome_completo=nome, cargo=cargo, disciplina_ingresso=disc_ing, funcao=funcao,
            tipo_funcao=tipo_funcao, regime_contratacao=regime, data_admissao=dt_adm, data_nomeacao=dt_nom,
            data_ci_movimentacao=dt_adm, data_ingresso_unidade=dt_adm, ch_planejamento=r['ch_planejamento'],
            ch_regencia=r['ch_regencia'], ch_complementacao=r['ch_complementacao'], ch_total=r['ch_total'],
            acumulacao=r['acumulacao'], data_nascimento=dt_nasc, sexo=r['sexo'], endereco=r['endereco'],
            numero=r['numero'], complemento=r['complemento'], bairro=r['bairro'], municipio=r['municipio'],
            email=r['email_interno'], email_google=r['email_google'], email_alternativo=r['email_alternativo'],
            telefone=r['telefone'], celular=r['celular'], classificacao=rank, ativo=True
        )

        perfil_usuario = 'diretor' if 'SILVIO LUIZ' in nome.upper() else 'professor'

        user = Usuario.objects.filter(cpf=cpf_num).first()
        if not user:
            if Usuario.objects.filter(email=primary_email).exists():
                primary_email = cpf_num + "@cejarosasoares.edu.br"
            Usuario.objects.create_user(
                cpf=cpf_num, nome_completo=nome, email=primary_email, perfil=perfil_usuario,
                password=cpf_num, id_vinculo=id_vinculo, matricula=matricula, telefone=r['celular'] or r['telefone']
            )
        else:
            user.nome_completo = nome
            user.id_vinculo = id_vinculo
            user.matricula = matricula
            if user.perfil != 'diretor':
                user.perfil = perfil_usuario
            user.save()

    for rank, r in enumerate(adm_list, start=1):
        cpf_num = r['cpf']
        id_vinculo = r['id_vinculo']
        matricula = r['matricula']
        matricula_ac = r['matricula_acumulacao']
        nome = r['nome']
        cargo = r['cargo']
        disc_ing = r['disciplina_ingresso']
        funcao = r['funcao']
        tipo_funcao = r['tipo_funcao']
        regime = r['regime_contratacao']
        
        dt_adm = parse_d(r['data_admissao'])
        dt_nom = parse_d(r['data_nomeacao'])
        dt_nasc = parse_d(r['data_nascimento'])
        
        primary_email = r['email_google'] or r['email_interno'] or r['email_alternativo'] or (cpf_num + "@cejarosasoares.edu.br")

        FuncionarioAdministrativo.objects.create(
            cpf=cpf_num, id_vinculo=id_vinculo, matricula=matricula,
            id_vinculo_acumulacao=r['id_vinculo_acumulacao'], matricula_acumulacao=matricula_ac,
            cargo_acumulacao=r['cargo_acumulacao'], disciplina_ingresso_acumulacao=r['disciplina_ingresso_acumulacao'],
            funcao_acumulacao=r['funcao_acumulacao'], ch_total_acumulacao=r['ch_total_acumulacao'],
            data_admissao_acumulacao=parse_d(r['data_admissao_acumulacao']),
            nome_completo=nome, cargo=cargo, disciplina_ingresso=disc_ing, funcao_atual=funcao,
            funcao_ingresso=disc_ing, tipo_funcao=tipo_funcao, regime_contratacao=regime,
            data_admissao=dt_adm, data_nomeacao=dt_nom, data_ci_movimentacao=dt_adm, data_ingresso_unidade=dt_adm,
            ch_total=r['ch_total'], acumulacao=r['acumulacao'], data_nascimento=dt_nasc, sexo=r['sexo'],
            endereco=r['endereco'], numero=r['numero'], complemento=r['complemento'], bairro=r['bairro'],
            municipio=r['municipio'], email=r['email_interno'], email_google=r['email_google'],
            email_alternativo=r['email_alternativo'], telefone=r['telefone'], celular=r['celular'],
            classificacao=rank, ativo=True
        )

        perfil_usuario = 'diretor' if 'SILVIO LUIZ' in nome.upper() else 'administrativo'

        user = Usuario.objects.filter(cpf=cpf_num).first()
        if not user:
            if Usuario.objects.filter(email=primary_email).exists():
                primary_email = cpf_num + "@cejarosasoares.edu.br"
            Usuario.objects.create_user(
                cpf=cpf_num, nome_completo=nome, email=primary_email, perfil=perfil_usuario,
                password=cpf_num, id_vinculo=id_vinculo, matricula=matricula, telefone=r['celular'] or r['telefone']
            )
        else:
            user.nome_completo = nome
            user.id_vinculo = id_vinculo
            user.matricula = matricula
            if user.perfil != 'diretor':
                user.perfil = perfil_usuario
            user.save()

    print("Povoamento concluido com sucesso!")
    print(f"Professores: {Professor.objects.count()}")
    print(f"Administrativos: {FuncionarioAdministrativo.objects.count()}")
    print(f"Usuarios: {Usuario.objects.count()}")

if __name__ == '__main__':
    executar()
'''

with open('carregar_dados.py', 'w', encoding='utf-8') as f:
    f.write(python_code)

print("Gerado carregar_dados.py com classificacao automatica por antiguidade!")
