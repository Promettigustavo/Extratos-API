"""Teste de transações do CONDOLIVRE em outubro"""
from buscar_extratos_bancarios import SantanderExtratosBancarios
from datetime import datetime

print("="*80)
print("TESTE: CONDOLIVRE - OUTUBRO 2025")
print("="*80)

try:
    # Criar cliente
    cliente = SantanderExtratosBancarios('CONDOLIVRE FIDC')
    
    # Listar contas
    contas = cliente.listar_contas()
    print(f"\n✅ Contas encontradas: {len(contas)}")
    
    if contas:
        conta = contas[0]
        branch = conta['branchCode']
        number = conta['number']
        print(f"   Testando conta: {branch}.{number}")
        
        # Buscar transações de OUTUBRO
        print("\n📊 Buscando transações de OUTUBRO (01/10/2025 a 31/10/2025)...")
        trans_out = cliente.buscar_transacoes(
            branch, 
            number,
            datetime(2025, 10, 1),
            datetime(2025, 10, 31)
        )
        
        print(f"\n{'='*80}")
        print(f"RESULTADO OUTUBRO: {len(trans_out) if trans_out else 0} transação(ões)")
        print(f"{'='*80}")
        
        if trans_out and len(trans_out) > 0:
            print(f"\n✅ SUCESSO! Há transações em outubro!")
            print(f"\nPrimeira transação:")
            print(f"   Data: {trans_out[0].get('transactionDate')}")
            print(f"   Descrição: {trans_out[0].get('transactionName')}")
            print(f"   Valor: R$ {trans_out[0].get('amount')}")
            print(f"   Tipo: {trans_out[0].get('creditDebitType')}")
        else:
            print(f"\n⚠️ Nenhuma transação encontrada em outubro")
            
        # Testar NOVEMBRO também (últimos 7 dias)
        print("\n" + "="*80)
        print("📊 Buscando transações de NOVEMBRO (07/11/2025 a 14/11/2025)...")
        trans_nov = cliente.buscar_transacoes(
            branch,
            number, 
            datetime(2025, 11, 7),
            datetime(2025, 11, 14)
        )
        
        print(f"\n{'='*80}")
        print(f"RESULTADO NOVEMBRO: {len(trans_nov) if trans_nov else 0} transação(ões)")
        print(f"{'='*80}")
        
        if trans_nov and len(trans_nov) > 0:
            print(f"\n✅ Há transações em novembro!")
        else:
            print(f"\n⚠️ Nenhuma transação em novembro (confirmado)")
            
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("TESTE CONCLUÍDO")
print("="*80)
