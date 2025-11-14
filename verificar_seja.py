"""
Verificar transações do fundo SEJA em diferentes períodos
"""

from datetime import datetime, timedelta
from buscar_extratos_bancarios import SantanderExtratosBancarios

print("="*80)
print("VERIFICAÇÃO DETALHADA - FUNDO SEJA")
print("="*80)

fundo_id = 'SEJA'
api = SantanderExtratosBancarios(fundo_id)

# Listar contas
contas = api.listar_contas()
if not contas:
    print("❌ Nenhuma conta encontrada!")
    exit()

conta = contas[0]
branch = conta.get('branchCode')
account = conta.get('number')

print(f"\n📋 Conta encontrada: {branch}.{account}")

# Testar diferentes períodos
periodos = [
    ("Últimos 7 dias", 7),
    ("Últimos 15 dias", 15),
    ("Últimos 30 dias", 30),
    ("Últimos 60 dias", 60),
    ("Últimos 90 dias", 90),
]

hoje = datetime.now()

for nome_periodo, dias in periodos:
    data_inicial = hoje - timedelta(days=dias)
    
    print(f"\n{'='*80}")
    print(f"📅 {nome_periodo} ({data_inicial.strftime('%d/%m/%Y')} a {hoje.strftime('%d/%m/%Y')})")
    print(f"{'='*80}")
    
    transacoes = api.buscar_transacoes(branch, account, data_inicial, hoje)
    
    print(f"✅ Transações encontradas: {len(transacoes)}")
    
    if transacoes:
        # Mostrar primeiras 5 transações
        print(f"\n📊 Primeiras transações:")
        for i, trans in enumerate(transacoes[:5], 1):
            data = trans.get('transactionDate', '')[:10]
            tipo = trans.get('type', '')
            valor = float(trans.get('amount', 0))
            descricao = trans.get('creditDebitType', '')
            print(f"   {i}. {data} | {descricao} | R$ {valor:,.2f} | {tipo}")
        
        if len(transacoes) > 5:
            print(f"   ... e mais {len(transacoes) - 5} transações")
        
        # Mostrar última transação
        ultima = transacoes[-1]
        print(f"\n📌 Última transação:")
        print(f"   Data: {ultima.get('transactionDate', '')[:10]}")
        print(f"   Tipo: {ultima.get('creditDebitType', '')}")
        print(f"   Valor: R$ {float(ultima.get('amount', 0)):,.2f}")
        
        break  # Parar quando encontrar transações

# Verificar saldo
print(f"\n{'='*80}")
print(f"💰 SALDO ATUAL")
print(f"{'='*80}")

saldo_info = api.buscar_saldo(branch, account)
if saldo_info:
    disponivel = saldo_info.get('availableAmount', 0)
    bloqueado = saldo_info.get('blockedAmount', 0)
    investido = saldo_info.get('automaticallyInvestedAmount', 0)
    
    print(f"Disponível: R$ {disponivel:,.2f}")
    print(f"Bloqueado: R$ {bloqueado:,.2f}")
    print(f"Investido automaticamente: R$ {investido:,.2f}")
    print(f"Total: R$ {(disponivel + bloqueado + investido):,.2f}")

print(f"\n{'='*80}")
