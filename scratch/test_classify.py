import pandas as pd

excel_path = r'C:\Users\PC DIR 2 - SILVIO\Downloads\RCustServidores.xlsx'
df = pd.read_excel(excel_path, header=7)

df_clean = df.drop_duplicates(subset=['ID/VÍNCULO', 'MATRÍCULA'])

adm_keywords = ['SERVENTE', 'AGENTE ADM', 'SECRETÁRIO', 'SECRETARIA', 'MERENDEIRA', 'ZELADOR', 'FACILITADOR', 'LEITURA']

profs = []
adms = []

for idx, r in df_clean.iterrows():
    func = str(r['FUNÇÃO']).upper()
    cargo = str(r['CARGO']).upper()
    
    if any(k in func for k in adm_keywords) or any(k in cargo for k in ['SERVENTE', 'MERENDEIRA', 'ZELADOR']):
        adms.append(r)
    else:
        profs.append(r)

print(f"Total Unique Vinculos: {len(df_clean)}")
print(f"Professores: {len(profs)}")
print(f"Administrativos: {len(adms)}\n")

print("=== ADMINISTRATIVE STAFF (ADM) ===")
for r in adms:
    print(f"{r['ID/VÍNCULO']} | Mat: {r['MATRÍCULA']} | {r['NOME COMPLETO']} | Cargo: {r['CARGO']} | Func: {r['FUNÇÃO']}")

print("\n=== PROFESSORES ===")
for r in profs:
    print(f"{r['ID/VÍNCULO']} | Mat: {r['MATRÍCULA']} | {r['NOME COMPLETO']} | Cargo: {r['CARGO']} | Func: {r['FUNÇÃO']}")
