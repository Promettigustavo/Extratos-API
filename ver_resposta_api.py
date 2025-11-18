"""
Mostra exatamente o que a API do Santander retorna
"""

import sys
import json
from datetime import datetime, timedelta

try:
    try:
        from credenciais_bancos import SANTANDER_FUNDOS
    except ImportError:
        from config_credentials import SANTANDER_FUNDOS
    
    from buscar_extratos_bancarios import SantanderExtratosBancarios
    print("✅ Módulos importados\n")
except ImportError as e:
    print(f"❌ Erro: {e}")
    sys.exit(1)

FUNDO_ID = "MAKENA"

print("=" * 120)
print("RESPOSTA REAL DA API SANTANDER - TRANSAÇÕES")
print("=" * 120)

# Criar cliente
client = SantanderExtratosBancarios(FUNDO_ID)

# Período: hoje - 2 dias (para ter poucas transações e ver tudo)
data_final = datetime.now()
data_inicial = data_final - timedelta(days=2)

print(f"\n📅 Período: {data_inicial.strftime('%d/%m/%Y')} a {data_final.strftime('%d/%m/%Y')}")
print(f"\n🔄 Fazendo requisição para API...\n")

try:
    # Buscar transações
    transacoes = client.buscar_transacoes(
        branch_code="2271",
        account_number="000130107983",
        data_inicial=data_inicial,
        data_final=data_final
    )
    
    print(f"✅ {len(transacoes)} transações recebidas\n")
    
    if not transacoes:
        print("⚠️  Nenhuma transação encontrada neste período")
        sys.exit(0)
    
    # ========== MOSTRAR RESPOSTA COMPLETA DA API ==========
    print("=" * 120)
    print("FORMATO DA RESPOSTA DA API (JSON):")
    print("=" * 120)
    print("\nA API retorna uma lista de objetos JSON. Cada transação tem esta estrutura:\n")
    
    # Mostrar estrutura completa da primeira transação
    primeira_trans = transacoes[0]
    print("EXEMPLO DE UMA TRANSAÇÃO (primeira do período):")
    print("-" * 120)
    print(json.dumps(primeira_trans, indent=2, ensure_ascii=False))
    print("-" * 120)
    
    # ========== CAMPOS IMPORTANTES ==========
    print("\n" + "=" * 120)
    print("CAMPOS IMPORTANTES PARA IDENTIFICAR ENTRADA/SAÍDA:")
    print("=" * 120)
    
    print(f"""
┌─────────────────────────────┬──────────────────────────────────────────────────────────────────┐
│ Campo                       │ Descrição                                                        │
├─────────────────────────────┼──────────────────────────────────────────────────────────────────┤
│ creditDebitType             │ Define se é entrada ou saída:                                    │
│                             │   - "CREDITO" = ENTRADA de dinheiro (positivo)                   │
│                             │   - "DEBITO" = SAÍDA de dinheiro (negativo)                      │
├─────────────────────────────┼──────────────────────────────────────────────────────────────────┤
│ amount                      │ Valor da transação (sempre positivo, sem sinal)                  │
│                             │ Tipo: string (ex: "773388.35")                                   │
├─────────────────────────────┼──────────────────────────────────────────────────────────────────┤
│ transactionDate             │ Data da transação                                                │
│                             │ Formato: "DD/MM/YYYY" (ex: "18/11/2025")                         │
├─────────────────────────────┼──────────────────────────────────────────────────────────────────┤
│ transactionName             │ Descrição/histórico da transação                                 │
│                             │ (ex: "PIX RECEBIDO", "PAGFOR PIX OUTRA INST")                    │
├─────────────────────────────┼──────────────────────────────────────────────────────────────────┤
│ historicComplement          │ Informação adicional (CNPJ, código, etc)                         │
└─────────────────────────────┴──────────────────────────────────────────────────────────────────┘
""")
    
    # ========== EXEMPLOS REAIS ==========
    print("\n" + "=" * 120)
    print(f"EXEMPLOS REAIS DAS {min(15, len(transacoes))} PRIMEIRAS TRANSAÇÕES RECEBIDAS:")
    print("=" * 120)
    
    print(f"\n{'#':<4} | {'Data':<12} | {'Tipo':<8} | {'Valor (R$)':>18} | {'Histórico':<50}")
    print("-" * 120)
    
    for i, trans in enumerate(transacoes[:15], 1):
        data = trans.get('transactionDate', 'N/A')
        tipo = trans.get('creditDebitType', 'N/A')
        valor = float(trans.get('amount', 0))
        historico = trans.get('transactionName', 'N/A')[:50]
        
        # Aplicar sinal baseado no tipo
        if tipo == 'CREDITO':
            tipo_display = '✅ CRÉD'
            valor_com_sinal = f"+{valor:,.2f}"
        else:
            tipo_display = '❌ DÉB'
            valor_com_sinal = f"-{valor:,.2f}"
        
        print(f"{i:<4} | {data:<12} | {tipo_display:<8} | {valor_com_sinal:>18} | {historico:<50}")
    
    # ========== COMO O CÓDIGO INTERPRETA ==========
    print("\n" + "=" * 120)
    print("COMO O CÓDIGO CONVERTE PARA SINAL (+/-):")
    print("=" * 120)
    
    print("""
A API NÃO retorna o sinal (+ ou -) no campo 'amount'.
O campo 'amount' sempre vem como STRING positiva (ex: "773388.35").

O nosso código faz a conversão assim:

    valor = float(trans.get('amount', 0))  # Converte string para número
    tipo = trans.get('creditDebitType', '')
    
    if tipo == 'DEBITO':
        valor_com_sinal = -abs(valor)  # Força negativo
    else:  # CREDITO
        valor_com_sinal = abs(valor)   # Força positivo

Então:
    CREDITO + amount "1000.00" → +1000.00 (entrada de dinheiro)
    DEBITO + amount "500.00"   → -500.00  (saída de dinheiro)
""")
    
    # ========== VALIDAÇÃO ==========
    print("\n" + "=" * 120)
    print("VALIDAÇÃO - SOMA DE CRÉDITOS E DÉBITOS:")
    print("=" * 120)
    
    total_creditos = 0
    total_debitos = 0
    qtd_creditos = 0
    qtd_debitos = 0
    
    for trans in transacoes:
        valor = float(trans.get('amount', 0))
        tipo = trans.get('creditDebitType', '')
        
        if tipo == 'CREDITO':
            total_creditos += valor
            qtd_creditos += 1
        else:
            total_debitos += valor
            qtd_debitos += 1
    
    print(f"""
Período analisado: {data_inicial.strftime('%d/%m/%Y')} a {data_final.strftime('%d/%m/%Y')}

✅ CRÉDITOS (entradas):
   Quantidade: {qtd_creditos} transações
   Total: R$ {total_creditos:,.2f}

❌ DÉBITOS (saídas):
   Quantidade: {qtd_debitos} transações
   Total: R$ {total_debitos:,.2f}

📊 SALDO LÍQUIDO DO PERÍODO:
   R$ {total_creditos:,.2f} - R$ {total_debitos:,.2f} = R$ {total_creditos - total_debitos:,.2f}
""")
    
    # ========== CAMPOS DISPONÍVEIS ==========
    print("\n" + "=" * 120)
    print("TODOS OS CAMPOS DISPONÍVEIS NA PRIMEIRA TRANSAÇÃO:")
    print("=" * 120)
    
    print("\nCampos retornados pela API:")
    for campo in primeira_trans.keys():
        valor = primeira_trans[campo]
        tipo_valor = type(valor).__name__
        print(f"   • {campo:<25} (tipo: {tipo_valor:<10}) = {valor}")
    
    print("\n" + "=" * 120)
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
