import pandas as pd
import json
import os
import re
import subprocess

print("=== AGGIORNAMENTO AUTOMATICO DASHBOARD ===")

excel_path = 'DASHBOARD COSTO LAVORO 2025-2026.xlsx'
if not os.path.exists(excel_path):
    print(f"Errore: File {excel_path} non trovato!")
    exit(1)

print("1. Lettura file Excel in corso...")
df = pd.read_excel(excel_path)

for col in ['MESE', 'PERSONA', 'CONTRATTO', 'FUNZIONE']:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip()

months_order = ['GENNAIO', 'FEBBRAIO', 'MARZO', 'APRILE', 'MAGGIO', 'GIUGNO', 'LUGLIO', 'AGOSTO', 'SETTEMBRE', 'OTTOBRE', 'NOVEMBRE', 'DICEMBRE']
df['MESE_NUM'] = df['MESE'].apply(lambda m: months_order.index(m) + 1 if m in months_order else 99)

records = df.to_dict(orient='records')

print(f"   Trovati {len(records)} record. Totale costo: €{df['COSTO AZIENDA'].sum():,.0f}")

print("2. Generazione data.json...")
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(records, f, ensure_ascii=False, indent=2)

print("3. Integrazione dati in index.html...")
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

json_str = json.dumps(records, ensure_ascii=False)
new_block = '/* DATA_START */\n        const EMBEDDED_DATA = ' + json_str + ';\n        /* DATA_END */'

if '/* DATA_START */' in html and '/* DATA_END */' in html:
    html = re.sub(r'/\* DATA_START \*/.*?/\* DATA_END \*/', new_block, html, flags=re.DOTALL)
else:
    print("   Warning: DATA_START markers not found, doing fallback replacement...")
    html = re.sub(r'const EMBEDDED_DATA = \[.*?\];', f'const EMBEDDED_DATA = {json_str};', html, count=1, flags=re.DOTALL)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("4. Invio modifiche a GitHub & Vercel...")
subprocess.run(['git', 'add', '.'], check=True)
subprocess.run(['git', 'commit', '-m', 'Aggiornamento dati da Excel'], check=True)
subprocess.run(['git', 'push', 'origin', 'main'], check=True)

print("==================================================")
print(" FATTO! La Dashboard su Vercel e online si aggiornera in 5 secondi!")
print("==================================================")
