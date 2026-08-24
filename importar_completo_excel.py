import os
import django
import re
import pandas as pd
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ceja_gestao.settings')
django.setup()

from professores.models import Professor
from funcionarios.models import FuncionarioAdministrativo
from usuarios.models import Usuario

EXCEL_PATH = r'C:\Users\PC DIR 2 - SILVIO\Downloads\RCustServidores.xlsx'

def parse_data(val):
    if pd.isna(val) or not val:
        return None
    if isinstance(val, datetime):
        return val.date()
    val_str = str(val).strip()
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d'):
        try:
            return datetime.strptime(val_str, fmt).date()
        except ValueError:
            pass
    return None

def rodar_importacao_master():
    print(f"Lendo planilha: {EXCEL_PATH}...")
    df = pd.read_excel(EXCEL_PATH, header=7)
    
    # Remover duplicatas exatas de vinculo/matricula
    df_clean = df.drop_duplicates(subset=['ID/VÍNCULO', 'MATRÍCULA'])
    print(f"Total de linhas na planilha: {len(df)}")
    print(f"Total de vinculos/matriculas unicos: {len(df_clean)}")

    # Obter todos os CPFs reais da planilha
    cpfs_reais = set()
    for _, r in df_clean.iterrows():
        c = re.sub(r'\D', '', str(r['CPF'])).zfill(11)
        cpfs_reais.add(c)

    # Limpar registros antigos de professores e funcionarios
    Professor.objects.all().delete()
    FuncionarioAdministrativo.objects.all().delete()

    # Deletar usuarios antigos que possuem CPFs fakes (gerados anteriormente a partir de ID/Vinculo)
    # Mantém superusuários ou o usuário do Diretor Silvio se for 00000000000
    usuarios_fakes = Usuario.objects.exclude(cpf='00000000000').exclude(cpf__in=cpfs_reais)
    cant_del = usuarios_fakes.count()
    usuarios_fakes.delete()
    if cant_del:
        print(f"Removidos {cant_del} usuarios com CPFs temporarios antigos.")

    adm_keywords = ['SERVENTE', 'AGENTE ADM', 'SECRETÁRIO', 'SECRETARIA', 'MERENDEIRA', 'ZELADOR', 'FACILITADOR', 'LEITURA']

    professores_criados = 0
    funcionarios_criados = 0

    for idx, r in df_clean.iterrows():
        id_vinculo = str(r['ID/VÍNCULO']).strip()
        matricula = str(r['MATRÍCULA']).strip()
        matricula_ac = str(int(r['SEGUNDA MATRÍCULA'])).strip() if pd.notna(r.get('SEGUNDA MATRÍCULA')) and r.get('SEGUNDA MATRÍCULA') else ''
        
        cpf_num = re.sub(r'\D', '', str(r['CPF'])).zfill(11)
        nome = str(r['NOME COMPLETO']).strip().title()
        
        cargo = str(r['CARGO']).strip() if pd.notna(r['CARGO']) else ''
        disc_ing = str(r['DISCIPLINA DE INGRESSO']).strip() if pd.notna(r['DISCIPLINA DE INGRESSO']) else ''
        funcao = str(r['FUNÇÃO']).strip() if pd.notna(r['FUNÇÃO']) else ''
        tipo_funcao = str(r['TIPO FUNÇÃO']).strip() if pd.notna(r['TIPO FUNÇÃO']) else ''
        regime = str(r['REGIME CONTRATACAO']).strip() if pd.notna(r['REGIME CONTRATACAO']) else ''
        
        dt_adm = parse_data(r.get('DATA ADMISSÃO'))
        dt_nom = parse_data(r.get('DATA NOMEACAO'))
        dt_nasc = parse_data(r.get('DT NASC'))
        
        ch_plan = int(r['C.H.\nPLANEJAMENTO']) if pd.notna(r.get('C.H.\nPLANEJAMENTO')) else None
        ch_reg = int(r['C.H.\nREGÊNCIA']) if pd.notna(r.get('C.H.\nREGÊNCIA')) else None
        ch_comp = int(r['C.H.\nCOMPLMENTAÇÃO']) if pd.notna(r.get('C.H.\nCOMPLMENTAÇÃO')) else None
        ch_tot = int(r['C.H.\nTOTAL']) if pd.notna(r.get('C.H.\nTOTAL')) else None
        
        acumulacao = str(r['ACUMULAÇÃO']).strip() if pd.notna(r.get('ACUMULAÇÃO')) else ''
        
        endereco = str(r['ENDEREÇO']).strip() if pd.notna(r.get('ENDEREÇO')) else ''
        num = str(r['END NUM']).strip() if pd.notna(r.get('END NUM')) else ''
        compl = str(r['END COMPL']).strip() if pd.notna(r.get('END COMPL')) else ''
        bairro = str(r['BAIRRO']).strip() if pd.notna(r.get('BAIRRO')) else ''
        municipio = str(r['MUNICIPIO END']).strip() if pd.notna(r.get('MUNICIPIO END')) else ''
        
        sexo = str(r['SEXO']).strip() if pd.notna(r.get('SEXO')) else ''
        fone = str(r['FONE']).strip() if pd.notna(r.get('FONE')) else ''
        celular = str(r['CELULAR']).strip() if pd.notna(r.get('CELULAR')) else ''
        
        email_int = str(r['E-MAIL INTERNO']).strip() if pd.notna(r.get('E-MAIL INTERNO')) else ''
        email_goog = str(r['E-MAIL GOOGLE']).strip() if pd.notna(r.get('E-MAIL GOOGLE')) else ''
        email_alt = str(r['E-MAIL ALTERNATIVO']).strip() if pd.notna(r.get('E-MAIL ALTERNATIVO')) else ''
        
        primary_email = email_goog or email_int or email_alt or f"{cpf_num}@cejarosasoares.edu.br"

        # Verificar se é Administrativo ou Professor
        is_adm = any(k in funcao.upper() for k in adm_keywords) or any(k in cargo.upper() for k in ['SERVENTE', 'MERENDEIRA', 'ZELADOR'])

        if is_adm:
            FuncionarioAdministrativo.objects.create(
                cpf=cpf_num,
                id_vinculo=id_vinculo,
                matricula=matricula,
                matricula_acumulacao=matricula_ac,
                nome_completo=nome,
                cargo=cargo,
                disciplina_ingresso=disc_ing,
                funcao_atual=funcao,
                funcao_ingresso=disc_ing,
                tipo_funcao=tipo_funcao,
                regime_contratacao=regime,
                data_admissao=dt_adm,
                data_nomeacao=dt_nom,
                data_ci_movimentacao=dt_adm,
                data_ingresso_unidade=dt_adm,
                ch_total=ch_tot,
                acumulacao=acumulacao,
                data_nascimento=dt_nasc,
                sexo=sexo,
                endereco=endereco,
                numero=num,
                complemento=compl,
                bairro=bairro,
                municipio=municipio,
                email=email_int,
                email_google=email_goog,
                email_alternativo=email_alt,
                telefone=fone,
                celular=celular,
                ativo=True
            )
            funcionarios_criados += 1
            perfil_usuario = 'administrativo'
        else:
            Professor.objects.create(
                cpf=cpf_num,
                id_vinculo=id_vinculo,
                matricula=matricula,
                matricula_acumulacao=matricula_ac,
                nome_completo=nome,
                cargo=cargo,
                disciplina_ingresso=disc_ing,
                funcao=funcao,
                tipo_funcao=tipo_funcao,
                regime_contratacao=regime,
                data_admissao=dt_adm,
                data_nomeacao=dt_nom,
                data_ci_movimentacao=dt_adm,
                data_ingresso_unidade=dt_adm,
                ch_planejamento=ch_plan,
                ch_regencia=ch_reg,
                ch_complementacao=ch_comp,
                ch_total=ch_tot,
                acumulacao=acumulacao,
                data_nascimento=dt_nasc,
                sexo=sexo,
                endereco=endereco,
                numero=num,
                complemento=compl,
                bairro=bairro,
                municipio=municipio,
                email=email_int,
                email_google=email_goog,
                email_alternativo=email_alt,
                telefone=fone,
                celular=celular,
                ativo=True
            )
            professores_criados += 1
            perfil_usuario = 'professor'

        # Se for o Diretor Sílvio, mantém/define o perfil como 'diretor'
        if 'SILVIO LUIZ' in nome.upper():
            perfil_usuario = 'diretor'

        # Criar ou atualizar conta de Usuário (1 conta por CPF real)
        user = Usuario.objects.filter(cpf=cpf_num).first()
        if not user:
            # Garantir e-mail único para criar usuário se já existir um com esse email
            if Usuario.objects.filter(email=primary_email).exists():
                primary_email = f"{cpf_num}@cejarosasoares.edu.br"

            user = Usuario.objects.create_user(
                cpf=cpf_num,
                nome_completo=nome,
                email=primary_email,
                perfil=perfil_usuario,
                password=cpf_num,
                id_vinculo=id_vinculo,
                matricula=matricula,
                telefone=celular or fone
            )
        else:
            user.nome_completo = nome
            user.id_vinculo = id_vinculo
            user.matricula = matricula
            if user.perfil != 'diretor':
                user.perfil = perfil_usuario
            user.save()

    print("Importacao completa finalizada com sucesso!")
    print(f"Professores cadastrados: {Professor.objects.count()}")
    print(f"Funcionarios Administrativos cadastrados: {FuncionarioAdministrativo.objects.count()}")
    print(f"Usuarios ativos do sistema: {Usuario.objects.count()}")

if __name__ == '__main__':
    rodar_importacao_master()
