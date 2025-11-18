"""
Teste rápido de ordenação
"""

from datetime import datetime
from itertools import groupby

# Simular transações como vem da API (vou testar com ordem inversa)
transacoes_api = [
    {'transactionDate': '2025-11-18', 'transactionName': 'Trans 18/11/2025'},
    {'transactionDate': '2025-11-17', 'transactionName': 'Trans 17/11/2025'},
    {'transactionDate': '2025-10-30', 'transactionName': 'Trans 30/10/2025'},
    {'transactionDate': '2024-10-29', 'transactionName': 'Trans 29/10/2024'},
    {'transactionDate': '2024-10-28', 'transactionName': 'Trans 28/10/2024'},
]

print("\n" + "="*80)
print("SIMULAÇÃO: Transações da API (ordem que chega)")
print("="*80)
for i, t in enumerate(transacoes_api, 1):
    print(f"{i}. {t['transactionDate']} - {t['transactionName']}")

# Aplicar ordenação do código atual
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

print("\n" + "="*80)
print("APÓS sorted() - Mais antigo primeiro")
print("="*80)
for i, t in enumerate(transacoes_cronologicas, 1):
    print(f"{i}. {t['transactionDate']} - {t['transactionName']}")

# Agrupar por data e reverter dentro de cada grupo
transacoes_ordenadas = []
for data, grupo in groupby(transacoes_cronologicas, key=lambda x: x.get('transactionDate', '')):
    transacoes_do_dia = list(grupo)
    transacoes_do_dia.reverse()
    transacoes_ordenadas.extend(transacoes_do_dia)

print("\n" + "="*80)
print("RESULTADO FINAL (após groupby + reverse)")
print("="*80)
for i, t in enumerate(transacoes_ordenadas, 1):
    print(f"{i}. {t['transactionDate']} - {t['transactionName']}")

print("\n" + "="*80)
print("VERIFICAÇÃO:")
print("="*80)
primeira = transacoes_ordenadas[0]['transactionDate']
ultima = transacoes_ordenadas[-1]['transactionDate']
print(f"✓ Primeira transação: {primeira}")
print(f"✓ Última transação: {ultima}")

if primeira < ultima:
    print(f"\n✅ CORRETO: {primeira} (2024) vem ANTES de {ultima} (2025)")
else:
    print(f"\n❌ ERRO: {primeira} vem DEPOIS de {ultima} - ordem invertida!")

print("\nO que DEVERIA aparecer no extrato:")
print("1ª linha: 28/10/2024 (mais antiga)")
print("Última linha: 18/11/2025 (mais recente)")
print("="*80)
