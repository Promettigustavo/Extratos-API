"""
Script de Validação - Valores e Saldos
Compara com extrato do Santander para MAKENA
"""

from datetime import datetime, timedelta

# Dados do extrato real do Santander que você compartilhou (18/11/2024 a 18/11/2025)
# SALDO ANTERIOR: 57.365,08 em 18/11/2025

print("=" * 100)
print("ANÁLISE DE CÁLCULO DE VALORES E SALDOS")
print("=" * 100)

print("\n📋 REGRAS DE CÁLCULO:")
print("-" * 100)
print("\n1. SALDO ANTERIOR:")
print("   Fórmula: Saldo Anterior = Saldo Atual (API) - Total de Transações do Período")
print("   Onde:")
print("     - Saldo Atual = availableAmount da API (saldo de hoje)")
print("     - Total Transações = Soma de todos os créditos - débitos do período")
print()
print("2. SALDO PROGRESSIVO (linha a linha):")
print("   Fórmula: Saldo[n] = Saldo[n-1] + Valor Transação[n]")
print("   Onde:")
print("     - Saldo[0] = Saldo Anterior")
print("     - Valor > 0 para CRÉDITO")
print("     - Valor < 0 para DÉBITO")
print()
print("3. SINAL DOS VALORES:")
print("   - creditDebitType == 'CREDITO' → valor positivo (+)")
print("   - creditDebitType == 'DEBITO' → valor negativo (-)")

print("\n" + "=" * 100)
print("EXEMPLO DE VALIDAÇÃO COM DADOS REAIS:")
print("=" * 100)

# Exemplo com as primeiras transações do extrato de 18/11/2025
print("\nExtrato Santander - 18/11/2025:")
print("-" * 100)
print("Data         | Histórico                              | Valor (R$)        | Saldo (R$)")
print("-" * 100)
print("18/11/2025   | SALDO ANTERIOR                         |                   | 57.365,08")
print("18/11/2025   | TAR EMISSAO TED CIP PGTO FORNEC        | -5,25             | 57.359,83")
print("18/11/2025   | TAR PIX PGTO FORNEC - MESMA INST       | -7,20             | 57.352,63")
print("18/11/2025   | TAR PIX PGTO FORNEC - OUTRA INST       | -127,80           | 57.224,83")
print("18/11/2025   | PIX RECEBIDO                           | 385.714,00        | 442.938,83")
print("18/11/2025   | RESGATE FUNDO DE INVESTIMENTO          | 48.926.666,13     | 49.369.604,96")

print("\n" + "=" * 100)
print("VERIFICAÇÃO DO CÁLCULO:")
print("=" * 100)

# Simular o cálculo
saldo = 57365.08
print(f"\n1. Saldo Anterior: R$ {saldo:,.2f}")

transacoes_exemplo = [
    ("TAR EMISSAO TED", -5.25),
    ("TAR PIX MESMA INST", -7.20),
    ("TAR PIX OUTRA INST", -127.80),
    ("PIX RECEBIDO", 385714.00),
    ("RESGATE FUNDO", 48926666.13),
]

for i, (descricao, valor) in enumerate(transacoes_exemplo, 2):
    saldo += valor
    print(f"{i}. {descricao:<30s}: {valor:>15,.2f} → Saldo: R$ {saldo:,.2f}")

print("\n" + "=" * 100)
print("PROBLEMAS COMUNS A VERIFICAR:")
print("=" * 100)

print("\n⚠️  PROBLEMA 1: Sinal invertido")
print("   Sintoma: Débitos aparecem positivos, créditos negativos")
print("   Causa: Inversão na lógica if tipo == 'DEBITO'")
print("   Código atual:")
print("     if tipo == 'DEBITO':")
print("         valor = -abs(valor)  # Correto: débito é negativo")
print("     else:")
print("         valor = abs(valor)   # Correto: crédito é positivo")

print("\n⚠️  PROBLEMA 2: Saldo anterior errado")
print("   Sintoma: Primeira linha com saldo muito diferente do Santander")
print("   Causa: Cálculo incorreto do saldo anterior")
print("   Código atual:")
print("     saldo_atual = API.availableAmount  # Saldo de HOJE")
print("     total_transacoes = soma(créditos - débitos)  # Período completo")
print("     saldo_anterior = saldo_atual - total_transacoes")

print("\n⚠️  PROBLEMA 3: Saldo progressivo errado")
print("   Sintoma: Saldo não bate linha a linha com Santander")
print("   Causa: Ordem das transações ou cálculo do saldo")
print("   Código atual:")
print("     saldo = saldo_anterior  # Inicializar")
print("     for transacao in transacoes_ordenadas:")
print("         saldo += valor  # Acumular")

print("\n⚠️  PROBLEMA 4: Valores duplicados ou faltando")
print("   Sintoma: Total de transações diferente do Santander")
print("   Causa: Paginação da API não buscando todas as páginas")

print("\n" + "=" * 100)
print("VALIDAÇÃO RECOMENDADA:")
print("=" * 100)

print("\n1. Compare o SALDO ANTERIOR do nosso extrato com o do Santander")
print("   Nosso: primeira linha após cabeçalho")
print("   Santander: primeira linha (SALDO ANTERIOR)")

print("\n2. Compare VALORES de transações específicas")
print("   Exemplo: 'RESGATE FUNDO DE INVESTIMENTO' de 48.926.666,13")
print("   Deve aparecer com sinal positivo (+) no nosso extrato")

print("\n3. Compare SALDO FINAL")
print("   Última linha do nosso extrato deve bater com última do Santander")

print("\n4. Teste o SALDO PROGRESSIVO (pegue 3 linhas consecutivas):")
print("   Saldo[linha N] = Saldo[linha N-1] + Valor[linha N]")

print("\n" + "=" * 100)
print("SCRIPT DE TESTE RÁPIDO:")
print("=" * 100)

print("\n# Execute este teste com dados reais:")
print("py teste_validacao_saldos.py")

print("\n" + "=" * 100)
