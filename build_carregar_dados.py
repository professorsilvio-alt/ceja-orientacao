import pandas as pd
import json
import re
from datetime import datetime

excel_path = r'C:\Users\PC DIR 2 - SILVIO\Downloads\RCustServidores.xlsx'
df = pd.read_excel(excel_path, header=7)
df_clean = df.drop_duplicates(subset=['ID/VÍNCULO', 'MATRÍCULA'])

records = []
for _, r in df_clean.iterrows():
    rec = {
        'id_vinculo': str(r['ID/VÍNCULO']).strip(),
        'matricula': str(r['MATRÍCULA']).strip(),
        'matricula_acumulacao': str(int(r['SEGUNDA MATRÍCULA'])).strip() if pd.notna(r.get('SEGUNDA MATRÍCULA')) and r.get('SEGUNDA MATRÍCULA') else '',
        'cpf': re.sub(r'\D', '', str(r['CPF'])).zfill(11),
        'nome': str(r['NOME COMPLETO']).strip().title(),
        'cargo': str(r['CARGO']).strip() if pd.notna(r['CARGO']) else '',
        'disciplina_ingresso': str(r['DISCIPLINA DE INGRESSO']).strip() if pd.notna(r['DISCIPLINA DE INGRESSO']) else '',
        'funcao': str(r['FUNÇÃO']).strip() if pd.notna(r['FUNÇÃO']) else '',
        'tipo_funcao': str(r['TIPO FUNÇÃO']).strip() if pd.notna(r['TIPO FUNÇÃO']) else '',
        'regime_contratacao': str(r['REGIME CONTRATACAO']).strip() if pd.notna(r['REGIME CONTRATACAO']) else '',
        'data_admissao': str(r.get('DATA ADMISSÃO')).split(' ')[0] if pd.notna(r.get('DATA ADMISSÃO')) else '',
        'data_nomeacao': str(r.get('DATA NOMEACAO')).split(' ')[0] if pd.notna(r.get('DATA NOMEACAO')) else '',
        'data_nascimento': str(r.get('DT NASC')).split(' ')[0] if pd.notna(r.get('DT NASC')) else '',
        'ch_planejamento': int(r['C.H.\nPLANEJAMENTO']) if pd.notna(r.get('C.H.\nPLANEJAMENTO')) else None,
        'ch_regencia': int(r['C.H.\nREGÊNCIA']) if pd.notna(r.get('C.H.\nREGÊNCIA')) else None,
        'ch_complementacao': int(r['C.H.\nCOMPLMENTAÇÃO']) if pd.notna(r.get('C.H.\nCOMPLMENTAÇÃO')) else None,
        'ch_total': int(r['C.H.\nTOTAL']) if pd.notna(r.get('C.H.\nTOTAL')) else None,
        'acumulacao': str(r['ACUMULAÇÃO']).strip() if pd.notna(r.get('ACUMULAÇÃO')) else '',
        'endereco': str(r['ENDEREÇO']).strip() if pd.notna(r.get('ENDEREÇO')) else '',
        'numero': str(r['END NUM']).strip() if pd.notna(r.get('END NUM')) else '',
        'complemento': str(r['END COMPL']).strip() if pd.notna(r.get('END COMPL')) else '',
        'bairro': str(r['BAIRRO']).strip() if pd.notna(r.get('BAIRRO')) else '',
        'municipio': str(r['MUNICIPIO END']).strip() if pd.notna(r.get('MUNICIPIO END')) else '',
        'sexo': str(r['SEXO']).strip() if pd.notna(r.get('SEXO')) else '',
        'telefone': str(r['FONE']).strip() if pd.notna(r.get('FONE')) else '',
        'celular': str(r['CELULAR']).strip() if pd.notna(r.get('CELULAR')) else '',
        'email_interno': str(r['E-MAIL INTERNO']).strip() if pd.notna(r.get('E-MAIL INTERNO')) else '',
        'email_google': str(r['E-MAIL GOOGLE']).strip() if pd.notna(r.get('E-MAIL GOOGLE')) else '',
        'email_alternativo': str(r['E-MAIL ALTERNATIVO']).strip() if pd.notna(r.get('E-MAIL ALTERNATIVO')) else '',
    }
    records.append(rec)

python_code = '''import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ceja_gestao.settings')
django.setup()

from professores.models import Professor
from funcionarios.models import FuncionarioAdministrativo
from usuarios.models import Usuario

DADOS = ''' + json.dumps(records, ensure_ascii=False, indent=4) + '''

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
    print("Iniciando povoamento automatico de professores, funcionarios e usuarios...")
    cpfs_reais = {r['cpf'] for r in DADOS}
    
    Professor.objects.all().delete()
    FuncionarioAdministrativo.objects.all().delete()
    
    usuarios_fakes = Usuario.objects.exclude(cpf='00000000000').exclude(cpf__in=cpfs_reais)
    usuarios_fakes.delete()

    adm_keywords = ['SERVENTE', 'AGENTE ADM', 'SECRETÁRIO', 'SECRETARIA', 'MERENDEIRA', 'ZELADOR', 'FACILITADOR', 'LEITURA']

    for r in DADOS:
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
        
        is_adm = any(k in funcao.upper() for k in adm_keywords) or any(k in cargo.upper() for k in ['SERVENTE', 'MERENDEIRA', 'ZELADOR'])

        if is_adm:
            FuncionarioAdministrativo.objects.create(
                cpf=cpf_num, id_vinculo=id_vinculo, matricula=matricula, matricula_acumulacao=matricula_ac,
                nome_completo=nome, cargo=cargo, disciplina_ingresso=disc_ing, funcao_atual=funcao,
                funcao_ingresso=disc_ing, tipo_funcao=tipo_funcao, regime_contratacao=regime,
                data_admissao=dt_adm, data_nomeacao=dt_nom, data_ci_movimentacao=dt_adm, data_ingresso_unidade=dt_adm,
                ch_total=r['ch_total'], acumulacao=r['acumulacao'], data_nascimento=dt_nasc, sexo=r['sexo'],
                endereco=r['endereco'], numero=r['numero'], complemento=r['complemento'], bairro=r['bairro'],
                municipio=r['municipio'], email=r['email_interno'], email_google=r['email_google'],
                email_alternativo=r['email_alternativo'], telefone=r['telefone'], celular=r['celular'], ativo=True
            )
            perfil_usuario = 'administrativo'
        else:
            Professor.objects.create(
                cpf=cpf_num, id_vinculo=id_vinculo, matricula=matricula, matricula_acumulacao=matricula_ac,
                nome_completo=nome, cargo=cargo, disciplina_ingresso=disc_ing, funcao=funcao,
                tipo_funcao=tipo_funcao, regime_contratacao=regime, data_admissao=dt_adm, data_nomeacao=dt_nom,
                data_ci_movimentacao=dt_adm, data_ingresso_unidade=dt_adm, ch_planejamento=r['ch_planejamento'],
                ch_regencia=r['ch_regencia'], ch_complementacao=r['ch_complementacao'], ch_total=r['ch_total'],
                acumulacao=r['acumulacao'], data_nascimento=dt_nasc, sexo=r['sexo'], endereco=r['endereco'],
                numero=r['numero'], complemento=r['complemento'], bairro=r['bairro'], municipio=r['municipio'],
                email=r['email_interno'], email_google=r['email_google'], email_alternativo=r['email_alternativo'],
                telefone=r['telefone'], celular=r['celular'], ativo=True
            )
            perfil_usuario = 'professor'

        if 'SILVIO LUIZ' in nome.upper():
            perfil_usuario = 'diretor'

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

print("Gerado carregar_dados.py com sucesso!")
