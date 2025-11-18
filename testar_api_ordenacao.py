"""
Teste real com API do Santander - MAKENA
Busca extratos reais e mostra a ordem que vem da API
"""

import sys
import os
from datetime import datetime, timedelta

# Importar o módulo de extratos - mesma lógica do dashboard
try:
    # Tentar import local primeiro
    try:
        from credenciais_bancos import SantanderAuth, SANTANDER_FUNDOS
    except ImportError:
        from config_credentials import SANTANDER_FUNDOS
        from credenciais_bancos import SantanderAuth
    
    from buscar_extratos_bancarios import SantanderExtratosBancarios
    print("✅ Módulos importados com sucesso\n")
except ImportError as e:
    print(f"❌ Erro ao importar: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Configurar fundo MAKENA
FUNDO_ID = "MAKENA"

print("=" * 100)
print("TESTE REAL - API SANTANDER - ORDENAÇÃO DE TRANSAÇÕES")
print("=" * 100)
print(f"\n🏦 Fundo: {FUNDO_ID}")

# Obter informações do fundo
if FUNDO_ID not in SANTANDER_FUNDOS:
    print(f"❌ Fundo {FUNDO_ID} não encontrado em SANTANDER_FUNDOS")
    print(f"Fundos disponíveis: {list(SANTANDER_FUNDOS.keys())[:5]}...")
    sys.exit(1)

fundo_info = SANTANDER_FUNDOS[FUNDO_ID]
print(f"📋 Nome: {fundo_info.get('nome', 'N/A')}")
print(f"📋 CNPJ: {fundo_info.get('cnpj', 'N/A')}")
print()

# Criar cliente de extratos - passa o FUNDO_ID (string), não o auth
print("🔧 Criando cliente de extratos...")
client = SantanderExtratosBancarios(FUNDO_ID)
print("✅ Cliente criado")
print()

# Definir período - ÚLTIMO ANO (365 dias)
data_final = datetime.now()
data_inicial = data_final - timedelta(days=365)

print(f"📅 Período: ÚLTIMO ANO")
print(f"📅 Data inicial: {data_inicial.strftime('%d/%m/%Y')}")
print(f"📅 Data final: {data_final.strftime('%d/%m/%Y')}")
print()

# Buscar transações - Conta MAKENA
BRANCH_CODE = "2271"
ACCOUNT_NUMBER = "000130107983"

try:
    print("🔄 Buscando transações da API Santander...")
    print(f"   Agência: {BRANCH_CODE}")
    print(f"   Conta: {ACCOUNT_NUMBER}")
    print(f"   Aguarde... (pode demorar para 1 ano de dados)")
    print()
    
    transacoes = client.buscar_transacoes(
        branch_code=BRANCH_CODE,
        account_number=ACCOUNT_NUMBER,
        data_inicial=data_inicial,
        data_final=data_final
    )
    
    print(f"✅ {len(transacoes)} transações encontradas\n")
    
    if not transacoes:
        print("⚠️  Nenhuma transação encontrada no período")
        sys.exit(0)
    
    # Mostrar ordem original da API
    print("=" * 100)
    print("1️⃣ ORDEM ORIGINAL DA API (primeiras 10 transações):")
    print("=" * 100)
    for i, trans in enumerate(transacoes[:10], 1):
        data = trans.get('transactionDate', '')
        nome = trans.get('transactionName', '')[:40]
        valor = float(trans.get('amount', 0))
        print(f"{i:2d}. {data} - {nome:<40s} R$ {valor:>15,.2f}")
    
    if len(transacoes) > 10:
        print(f"\n... ({len(transacoes) - 10} transações omitidas) ...\n")
    
    # Aplicar ordenação do sistema
    def extrair_data_ordenacao(trans):
        data = trans.get('transactionDate', '')
        if data and len(data) >= 10:
            try:
                dt = datetime.strptime(data[:10], '%Y-%m-%d')
                return dt
            except:
                return datetime(9999, 12, 31)
        return datetime(9999, 12, 31)
    
    transacoes_ordenadas = sorted(transacoes, key=extrair_data_ordenacao)
    
    print("=" * 100)
    print("2️⃣ APÓS sorted() - LÓGICA DO SISTEMA (primeiras 10):")
    print("=" * 100)
    for i, trans in enumerate(transacoes_ordenadas[:10], 1):
        data = trans.get('transactionDate', '')
        nome = trans.get('transactionName', '')[:40]
        valor = float(trans.get('amount', 0))
        print(f"{i:2d}. {data} - {nome:<40s} R$ {valor:>15,.2f}")
    
    if len(transacoes_ordenadas) > 20:
        print(f"\n... ({len(transacoes_ordenadas) - 20} transações omitidas) ...\n")
        
        print("ÚLTIMAS 10 transações após sorted():")
        print("-" * 100)
        for i, trans in enumerate(transacoes_ordenadas[-10:], len(transacoes_ordenadas)-9):
            data = trans.get('transactionDate', '')
            nome = trans.get('transactionName', '')[:40]
            valor = float(trans.get('amount', 0))
            print(f"{i:2d}. {data} - {nome:<40s} R$ {valor:>15,.2f}")
    
    # Análise
    print("\n" + "=" * 100)
    print("ANÁLISE DOS RESULTADOS:")
    print("=" * 100)
    
    primeira_api = transacoes[0].get('transactionDate', '')
    ultima_api = transacoes[-1].get('transactionDate', '')
    
    primeira_ordenada = transacoes_ordenadas[0].get('transactionDate', '')
    ultima_ordenada = transacoes_ordenadas[-1].get('transactionDate', '')
    
    print(f"\n📊 ORDEM ORIGINAL DA API:")
    print(f"   Primeira transação: {primeira_api}")
    print(f"   Última transação: {ultima_api}")
    if primeira_api > ultima_api:
        print(f"   Ordem: DECRESCENTE ⬇️  (mais recente → mais antiga)")
    else:
        print(f"   Ordem: CRESCENTE ⬆️  (mais antiga → mais recente)")
    
    print(f"\n📊 APÓS sorted() - LÓGICA ATUAL DO SISTEMA:")
    print(f"   Primeira transação: {primeira_ordenada}")
    print(f"   Última transação: {ultima_ordenada}")
    if primeira_ordenada > ultima_ordenada:
        print(f"   Ordem: DECRESCENTE ⬇️  (mais recente → mais antiga)")
    else:
        print(f"   Ordem: CRESCENTE ⬆️  (mais antiga → mais recente)")
    
    print("\n" + "-" * 100)
    print("VERIFICAÇÃO DO EXTRATO:")
    print("-" * 100)
    
    if primeira_ordenada < ultima_ordenada:
        print(f"\n✅ ORDEM CORRETA!")
        print(f"   sorted() retornou ordem CRESCENTE (mais antiga → mais recente)")
        print(f"\n   📄 No extrato Excel/PDF:")
        print(f"      PRIMEIRA linha deveria mostrar: {primeira_ordenada}")
        print(f"      ÚLTIMA linha deveria mostrar: {ultima_ordenada}")
        print(f"\n   ✅ Isso é o que QUEREMOS: 2024 no início, 2025 no final")
        print(f"\n   Se o extrato está mostrando 2025 primeiro, o problema está:")
        print(f"      • Na geração do Excel (ordem de escrita das linhas)")
        print(f"      • Na geração do PDF (ordem de escrita das linhas)")
        print(f"      • Ou na visualização (improvável)")
    else:
        print(f"\n❌ ORDEM INVERTIDA!")
        print(f"   sorted() retornou ordem DECRESCENTE (mais recente → mais antiga)")
        print(f"\n   📄 No extrato Excel/PDF:")
        print(f"      PRIMEIRA linha está mostrando: {primeira_ordenada}")
        print(f"      ÚLTIMA linha está mostrando: {ultima_ordenada}")
        print(f"\n   ❌ Isso é o PROBLEMA: 2025 no início, 2024 no final")
        print(f"\n   🔧 SOLUÇÃO: Adicionar reverse=True no sorted()")
        print(f"      transacoes_ordenadas = sorted(transacoes, key=extrair_data_ordenacao, reverse=True)")
    
    print("\n" + "=" * 100)
    
except Exception as e:
    print(f"❌ Erro ao buscar transações: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
