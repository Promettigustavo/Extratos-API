"""
Teste dos endpoints corrigidos conforme collection_contas_prod (2).json
"""
from buscar_extratos_bancarios import SantanderExtratosBancarios
from datetime import datetime, timedelta

print("="*80)
print("TESTE - ENDPOINTS CORRIGIDOS CONFORME COLLECTION")
print("="*80)

# Testar com CONDOLIVRE
fundo_id = "CONDOLIVRE FIDC"
api = SantanderExtratosBancarios(fundo_id)

print("\n1️⃣ TESTE: Listar contas")
print("-"*80)
contas = api.listar_contas()
print(f"\n✅ Total de contas retornadas: {len(contas)}")

if len(contas) > 0:
    print("\n2️⃣ TESTE: Buscar transações (statements)")
    print("-"*80)
    
    # Pegar primeira conta
    conta = contas[0]
    branch_code = conta.get('branchCode')
    account_number = conta.get('number')
    
    print(f"Testando conta: {branch_code}.{account_number}")
    
    # Período de teste
    data_final = datetime(2025, 11, 14)
    data_inicial = datetime(2025, 11, 7)
    
    transacoes = api.buscar_transacoes(
        branch_code=branch_code,
        account_number=account_number,
        data_inicial=data_inicial,
        data_final=data_final,
        limite=50
    )
    
    print(f"\n✅ Total de transações: {len(transacoes)}")
    
    if len(transacoes) > 0:
        print(f"\n📋 Primeira transação:")
        print(f"   {transacoes[0]}")
else:
    print("\n❌ Nenhuma conta retornada - testando com contas conhecidas")
    print("-"*80)
    
    # Testar ambas as contas conhecidas
    contas_testar = [
        ("2271", "130137784"),
        ("2271", "130176356")
    ]
    
    data_final = datetime(2025, 11, 14)
    data_inicial = datetime(2025, 11, 7)
    
    for branch_code, account_number in contas_testar:
        print(f"\n🔍 Testando conta: {branch_code}.{account_number}")
        print("-"*40)
        
        transacoes = api.buscar_transacoes(
            branch_code=branch_code,
            account_number=account_number,
            data_inicial=data_inicial,
            data_final=data_final,
            limite=50
        )
        
        print(f"✅ Total de transações: {len(transacoes)}")
        
        if len(transacoes) > 0:
            print(f"\n📋 Primeira transação:")
            print(f"   {transacoes[0]}")
            break  # Parar se encontrar transações

print("\n" + "="*80)
print("FIM DOS TESTES")
print("="*80)
