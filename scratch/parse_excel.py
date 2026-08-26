import pandas as pd

excel_path = r'C:\Users\PC DIR 2 - SILVIO\Downloads\RCustServidores.xlsx'
df = pd.read_excel(excel_path, header=7)

# Drop exact duplicate rows
df_unique = df.drop_duplicates(subset=['ID/VÍNCULO', 'MATRÍCULA'])

print(f"Total rows in sheet: {len(df)}")
print(f"Unique vinculos: {len(df_unique)}")

for idx, r in df_unique.iterrows():
    id_v = r['ID/VÍNCULO']
    mat = r['MATRÍCULA']
    cpf = str(r['CPF']).zfill(11)
    nome = r['NOME COMPLETO']
    cargo = r['CARGO']
    func = r['FUNÇÃO']
    disc = r['DISCIPLINA DE INGRESSO']
    print(f"[{idx}] Vinculo: {id_v} | Mat: {mat} | CPF: {cpf} | Nome: {nome}")
    print(f"     Cargo: {cargo} | Função: {func} | Disc: {disc}\n")
