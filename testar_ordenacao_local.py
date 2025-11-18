"""
Teste local da ordenação de transações
Simula exatamente a lógica do buscar_extratos_bancarios.py
"""

from datetime import datetime
import sys

# Simular transações como vêm da API do Santander
# (baseado no que você mostrou - API retorna em ordem decrescente)
transacoes_simuladas = [
    {'transactionDate': '2025-11-18', 'transactionName': 'PIX RECEBIDO', 'amount': 17428.23},
    {'transactionDate': '2025-11-18', 'transactionName': 'PIX RECEBIDO', 'amount': 14316.45},
    {'transactionDate': '2025-11-17', 'transactionName': 'RESGATE FUNDO', 'amount': 64835133.35},
    {'transactionDate': '2025-11-17', 'transactionName': 'PIX RECEBIDO', 'amount': 6501957.24},
    {'transactionDate': '2025-01-02', 'transactionName': 'TED RECEBIDA', 'amount': 10000.00},
    {'transactionDate': '2025-01-02', 'transactionName': 'TED RECEBIDA', 'amount': 12617.91},
    {'transactionDate': '2024-12-31', 'transactionName': 'TAR PIX', 'amount': -19.80},
    {'transactionDate': '2024-12-30', 'transactionName': 'PAGFOR PIX', 'amount': -392000.00},
    {'transactionDate': '2024-12-30', 'transactionName': 'PAGFOR PIX', 'amount': -310363.88},
    {'transactionDate': '2024-11-18', 'transactionName': 'TED RECEBIDA', 'amount': 196072.71},
    {'transactionDate': '2024-11-18', 'transactionName': 'PIX RECEBIDO', 'amount': 246388.75},
    {'transactionDate': '2024-11-18', 'transactionName': 'RESGATE FUNDO', 'amount': 11154620.21},
]

print("=" * 100)
print("TESTE DE ORDENAÇÃO - LÓGICA ATUAL DO SISTEMA")
print("=" * 100)

print("\n1️⃣ TRANSAÇÕES DA API (ordem original - como vem da API):")
print("-" * 100)
for i, trans in enumerate(transacoes_simuladas, 1):
    print(f"{i:2d}. {trans['transactionDate']} - {trans['transactionName']:<30s} R$ {trans['amount']:>15,.2f}")

# ========== APLICAR A LÓGICA EXATA DO CÓDIGO ATUAL ==========

def extrair_data_ordenacao(trans):
    """Função extraída do buscar_extratos_bancarios.py"""
    data = trans.get('transactionDate', '')
    if data and len(data) >= 10:
        try:
            # Converte para datetime para ordenação cronológica real
            dt = datetime.strptime(data[:10], '%Y-%m-%d')
            return dt
        except:
            # Fallback: data muito no futuro para datas inválidas
            return datetime(9999, 12, 31)
    return datetime(9999, 12, 31)

# Ordenar cronologicamente (mais antigo primeiro) - ORDEM CORRETA
transacoes_ordenadas = sorted(transacoes_simuladas, key=extrair_data_ordenacao)

print("\n2️⃣ APÓS sorted() - Lógica atual do sistema:")
print("-" * 100)
for i, trans in enumerate(transacoes_ordenadas, 1):
    print(f"{i:2d}. {trans['transactionDate']} - {trans['transactionName']:<30s} R$ {trans['amount']:>15,.2f}")

# DEBUG: Verificar ordem
if transacoes_ordenadas:
    primeira = transacoes_ordenadas[0].get('transactionDate', '')
    ultima = transacoes_ordenadas[-1].get('transactionDate', '')
    print(f"\n📋 DEBUG: Primeira transação = {primeira}, Última = {ultima}")

print("\n" + "=" * 100)
print("ANÁLISE DO RESULTADO:")
print("=" * 100)

primeira_data = transacoes_ordenadas[0]['transactionDate']
ultima_data = transacoes_ordenadas[-1]['transactionDate']

print(f"\n📅 Primeira data no extrato: {primeira_data}")
print(f"📅 Última data no extrato: {ultima_data}")

# Verificar se está correto
if primeira_data < ultima_data:
    print(f"\n✅ ORDEM CORRETA: {primeira_data} (mais antiga) vem ANTES de {ultima_data} (mais recente)")
    print("\nO extrato deveria mostrar:")
    print(f"  - Início: {primeira_data}")
    print(f"  - Fim: {ultima_data}")
else:
    print(f"\n❌ ORDEM INVERTIDA: {primeira_data} vem DEPOIS de {ultima_data}")
    print("\n⚠️  PROBLEMA: sorted() está retornando em ordem DECRESCENTE!")
    print("   Solução: adicionar reverse=True ao sorted()")

# Testar com reverse=True
print("\n" + "=" * 100)
print("3️⃣ TESTE COM reverse=True (ordem inversa):")
print("=" * 100)

transacoes_reverse = sorted(transacoes_simuladas, key=extrair_data_ordenacao, reverse=True)

print("\nPrimeiras 5 transações com reverse=True:")
for i, trans in enumerate(transacoes_reverse[:5], 1):
    print(f"{i:2d}. {trans['transactionDate']} - {trans['transactionName']:<30s}")

print("\nÚltimas 5 transações com reverse=True:")
for i, trans in enumerate(transacoes_reverse[-5:], len(transacoes_reverse)-4):
    print(f"{i:2d}. {trans['transactionDate']} - {trans['transactionName']:<30s}")

primeira_reverse = transacoes_reverse[0]['transactionDate']
ultima_reverse = transacoes_reverse[-1]['transactionDate']

if primeira_reverse > ultima_reverse:
    print(f"\n❌ COM reverse=True: {primeira_reverse} vem ANTES de {ultima_reverse} - INVERTIDO!")
else:
    print(f"\n✅ COM reverse=True: Ordem seria {primeira_reverse} → {ultima_reverse}")

print("\n" + "=" * 100)
print("CONCLUSÃO:")
print("=" * 100)

if primeira_data < ultima_data:
    print("✅ A lógica atual (sorted sem reverse) está CORRETA")
    print("   O problema pode estar em outro lugar (Excel, PDF, ou exibição)")
else:
    print("❌ A lógica atual (sorted sem reverse) está INVERTIDA")
    print("   SOLUÇÃO: Trocar para sorted(..., reverse=True)")

print("\n" + "=" * 100)
