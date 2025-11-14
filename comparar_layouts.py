import pandas as pd

print('=' * 80)
print('COMPARAÇÃO: EXEMPLO vs GERADO')
print('=' * 80)

print('\n=== ARQUIVO EXEMPLO ===')
df_exemplo = pd.read_excel('exportar-Santander - Extrato 14 de novembro de 2025-2271-130176356 (2).xls', header=None)
for i, row in df_exemplo.iterrows():
    print(f'L{i+1}:', list(row))

print('\n' + '=' * 80)
print('=== ARQUIVO GERADO ===')
df_gerado = pd.read_excel('exportar-Santander - Extrato 14 de novembro de 2025-2271-130137784.xlsx', header=None)
for i, row in df_gerado.iterrows():
    print(f'L{i+1}:', list(row))

print('\n' + '=' * 80)
print('COMPARAÇÃO')
print('=' * 80)
print(f'Exemplo: {len(df_exemplo)} linhas, {len(df_exemplo.columns)} colunas')
print(f'Gerado:  {len(df_gerado)} linhas, {len(df_gerado.columns)} colunas')
