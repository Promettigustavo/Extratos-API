"""
Script para debugar ordenação de transações
"""

from datetime import datetime

# Simular transações da API (ordem que vem da API)
transacoes_api = [
    {'transactionDate': '2025-11-18', 'transactionName': 'Transação 1'},
    {'transactionDate': '2025-11-17', 'transactionName': 'Transação 2'},
    {'transactionDate': '2025-11-17', 'transactionName': 'Transação 3'},
    {'transactionDate': '2024-10-28', 'transactionName': 'Transação 4'},
    {'transactionDate': '2024-10-29', 'transactionName': 'Transação 5'},
]

print("=" * 80)
print("TRANSAÇÕES DA API (ordem original):")
print("=" * 80)
for i, trans in enumerate(transacoes_api, 1):
    print(f"{i}. {trans['transactionDate']} - {trans['transactionName']}")

# Aplicar a mesma lógica do código
from itertools import groupby

def extrair_data_ordenacao(trans):
    data = trans.get('transactionDate', '')
    if data and len(data) >= 10:
        try:
            dt = datetime.strptime(data[:10], '%Y-%m-%d')
            return dt
        except:
            return datetime(9999, 12, 31)
    return datetime(9999, 12, 31)

# Ordenar cronologicamente (mais antigo primeiro)
transacoes_cronologicas = sorted(transacoes_api, key=extrair_data_ordenacao)

print("\n" + "=" * 80)
print("APÓS ORDENAÇÃO CRONOLÓGICA (sorted):")
print("=" * 80)
for i, trans in enumerate(transacoes_cronologicas, 1):
    print(f"{i}. {trans['transactionDate']} - {trans['transactionName']}")

# Agrupar por data e reverter ordem dentro de cada grupo
transacoes_ordenadas = []
for data, grupo in groupby(transacoes_cronologicas, key=lambda x: x.get('transactionDate', '')):
    transacoes_do_dia = list(grupo)
    transacoes_do_dia.reverse()
    transacoes_ordenadas.extend(transacoes_do_dia)

print("\n" + "=" * 80)
print("APÓS GROUPBY + REVERSE (resultado final):")
print("=" * 80)
for i, trans in enumerate(transacoes_ordenadas, 1):
    print(f"{i}. {trans['transactionDate']} - {trans['transactionName']}")

print("\n" + "=" * 80)
print("ANÁLISE:")
print("=" * 80)
primeira = transacoes_ordenadas[0]['transactionDate']
ultima = transacoes_ordenadas[-1]['transactionDate']
print(f"Primeira data: {primeira}")
print(f"Última data: {ultima}")
print(f"Ordem correta? {primeira < ultima} (primeira deve ser menor que última)")
