import pandas as pd
import re

excel_path = r'C:\Users\PC DIR 2 - SILVIO\Downloads\RCustServidores.xlsx'
df = pd.read_excel(excel_path, header=7)

# Unicidade por vinculo primeiro
df_clean = df.drop_duplicates(subset=['ID/VÍNCULO', 'MATRÍCULA'])

# Agrupar por CPF
grouped = df_clean.groupby('CPF')

print(f"Total Unique CPFs: {len(grouped)}")

prof_count = 0
adm_count = 0

for cpf_int, group in grouped:
    cpf = str(cpf_int).zfill(11)
    nome = group.iloc[0]['NOME COMPLETO']
    num_vinculos = len(group)
    
    row1 = group.iloc[0]
    row2 = group.iloc[1] if num_vinculos > 1 else None
    
    print(f"CPF: {cpf} | Nome: {nome} | Vínculos na escola: {num_vinculos}")
    print(f"   Posição 1: ID {row1['ID/VÍNCULO']} | Mat: {row1['MATRÍCULA']} | Cargo: {row1['CARGO']} | Func: {row1['FUNÇÃO']}")
    if row2 is not None:
        print(f"   Posição 2 (Acumulação): ID {row2['ID/VÍNCULO']} | Mat: {row2['MATRÍCULA']} | Cargo: {row2['CARGO']} | Func: {row2['FUNÇÃO']}")
    print("-" * 80)
