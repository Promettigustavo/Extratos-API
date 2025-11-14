"""Verificar conteúdo do arquivo da segunda conta do CONDOLIVRE"""

import pandas as pd
import os

print("="*80)
print("VERIFICAÇÃO: SEGUNDA CONTA CONDOLIVRE - 130176356")
print("="*80)

arquivo = "exportar-Santander - Extrato 14 de novembro de 2025-2271-130176356 (1).xls"

if os.path.exists(arquivo):
    print(f"✅ Arquivo encontrado: {arquivo}")
    print(f"📊 Tamanho: {os.path.getsize(arquivo):,} bytes")
    
    try:
        df = pd.read_excel(arquivo, header=None)
        print(f"📋 Dimensões: {df.shape[0]} linhas x {df.shape[1]} colunas")
        
        print(f"\n📄 Conteúdo completo:")
        for i, row in df.iterrows():
            valores = [str(v) if pd.notna(v) else '' for v in row]
            print(f"   L{i+1}: {valores}")
        
        # Procurar por indícios do nome do fundo
        print(f"\n🔍 Procurando referências ao CONDOLIVRE...")
        fundo_encontrado = False
        for i, row in df.iterrows():
            for col in row:
                if pd.notna(col) and isinstance(col, str):
                    if "CONDOLIVRE" in col.upper() or "CREDITORIOS" in col.upper():
                        print(f"   ✅ Linha {i+1}: {col}")
                        fundo_encontrado = True
        
        if not fundo_encontrado:
            print("   ⚠️ Nome do fundo não encontrado explicitamente")
        
        # Verificar se há saldo
        print(f"\n💰 Procurando informações de saldo...")
        for i, row in df.iterrows():
            for col in row:
                if pd.notna(col) and isinstance(col, str):
                    if "R$" in col or "saldo" in col.lower():
                        print(f"   💰 Linha {i+1}: {col}")
        
        # Verificar estrutura vs conta principal
        print(f"\n🔄 Comparação com estrutura esperada:")
        print(f"   Agência: 2271")
        print(f"   Conta: 130176356")
        print(f"   Linhas no arquivo: {len(df)}")
        
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {e}")

else:
    print(f"❌ Arquivo não encontrado: {arquivo}")

# Verificar também se há outros arquivos com essa conta
print(f"\n🔍 Outros arquivos com conta 130176356:")
for arquivo_alt in os.listdir('.'):
    if "130176356" in arquivo_alt and arquivo_alt.endswith(('.xlsx', '.xls', '.pdf')):
        print(f"   📄 {arquivo_alt}")

print(f"\n" + "="*80)
print("CONCLUSÃO")
print("="*80)
print("Se o arquivo contém dados reais com estrutura similar")
print("aos arquivos da conta 130137784, então o CONDOLIVRE")
print("possui DUAS contas bancárias:")
print("   • 2271.130137784 (conta principal)")
print("   • 2271.130176356 (conta secundária)")
print("="*80)