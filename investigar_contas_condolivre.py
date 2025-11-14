"""Script para verificar se CONDOLIVRE possui múltiplas contas bancárias"""

import os
import glob
from datetime import datetime

print("="*80)
print("INVESTIGAÇÃO: CONDOLIVRE - MÚLTIPLAS CONTAS?")
print("="*80)

# 1. Verificar arquivos gerados históricos
print("\n1. 🔍 Procurando arquivos históricos do CONDOLIVRE...")

# Buscar em extratos
extratos_paths = [
    "./Extratos/**/*CONDOLIVRE*/*.xlsx",
    "./Extratos/**/*CONDOLIVRE*/*.pdf",
    "./*CONDOLIVRE*.xlsx",
    "./*CONDOLIVRE*.pdf"
]

contas_encontradas = set()
arquivos_encontrados = []

for pattern in extratos_paths:
    arquivos = glob.glob(pattern, recursive=True)
    arquivos_encontrados.extend(arquivos)

print(f"📁 Arquivos encontrados: {len(arquivos_encontrados)}")

for arquivo in arquivos_encontrados:
    print(f"   - {arquivo}")
    
    # Extrair números de conta do nome do arquivo
    nome = os.path.basename(arquivo)
    
    # Padrões possíveis: agencia-conta
    if "-" in nome:
        partes = nome.split("-")
        for parte in partes:
            if parte.isdigit() and len(parte) >= 8:  # Número de conta
                contas_encontradas.add(parte)

print(f"\n2. 📊 Contas identificadas nos arquivos: {len(contas_encontradas)}")
for conta in sorted(contas_encontradas):
    print(f"   - {conta}")

# 2. Verificar informações conhecidas dos scripts
print(f"\n3. 🔍 Contas conhecidas nos scripts de teste:")
contas_scripts = [
    ("130137784", "Conta padrão nos testes"),
    ("130176356", "Conta encontrada em comparar_layouts.py"),
]

for conta, origem in contas_scripts:
    print(f"   - {conta} ({origem})")

# 3. Simular consulta da API accounts (o que aconteceria no Streamlit Cloud)
print(f"\n4. 🎯 Simulação de resposta da API /accounts para CONDOLIVRE:")
print(f"   (Esta seria a resposta real da API no Streamlit Cloud)")

# Baseado no padrão de outros fundos, simular múltiplas contas
simulacao_contas = [
    {
        "branch_code": "2271", 
        "account_number": "130137784",
        "tipo": "Conta Principal"
    },
    {
        "branch_code": "2271", 
        "account_number": "130176356", 
        "tipo": "Conta Secundária (possível)"
    }
]

print(f"   📋 Possíveis contas baseadas em evidências:")
for i, conta in enumerate(simulacao_contas, 1):
    account_id = f"{conta['branch_code']}.{conta['account_number']}"
    print(f"      {i}. {account_id} - {conta['tipo']}")

# 4. Verificar padrão de outros fundos
print(f"\n5. 🔍 Verificando se outros fundos têm múltiplas contas...")

try:
    from credenciais_bancos import SANTANDER_FUNDOS
    
    # Contar fundos que podem ter múltiplas contas
    fundos_multiplos = []
    
    # Verificar se há algum padrão nos nomes ou CNPJs que indique contas múltiplas
    for fundo_id, info in SANTANDER_FUNDOS.items():
        if "FIDC" in fundo_id:
            fundos_multiplos.append(fundo_id)
    
    print(f"   📊 Total de FIDCs: {len(fundos_multiplos)}")
    print(f"   📋 FIDCs similares ao CONDOLIVRE: {len([f for f in fundos_multiplos if 'FIDC' in f])}")
    
except:
    print("   ❌ Não foi possível carregar credenciais")

# 5. Conclusão baseada em evidências
print(f"\n" + "="*80)
print("📝 CONCLUSÃO BASEADA EM EVIDÊNCIAS")
print("="*80)

if len(contas_encontradas) > 1:
    print("✅ CONDOLIVRE provavelmente TEM múltiplas contas:")
    print(f"   - Evidência: {len(contas_encontradas)} contas diferentes encontradas em arquivos")
    for conta in sorted(contas_encontradas):
        print(f"     • {conta}")
elif len(contas_scripts) > 1:
    print("⚠️ CONDOLIVRE PODE TER múltiplas contas:")
    print(f"   - Evidência: {len(contas_scripts)} contas referenciadas em scripts")
    for conta, origem in contas_scripts:
        print(f"     • {conta} ({origem})")
else:
    print("🤔 CONDOLIVRE parece ter apenas UMA conta:")
    print("   - Apenas uma conta (130137784) encontrada consistentemente")

print(f"\n💡 RECOMENDAÇÃO:")
print(f"   Execute o dashboard no Streamlit Cloud e verifique os logs")
print(f"   para ver quantas contas são retornadas pela API /accounts")
print(f"   do CONDOLIVRE. A API irá mostrar todas as contas disponíveis.")

print("="*80)