# -*- coding: utf-8 -*-
"""
Teste: 2 ANOS de transações (730 dias)
"""

from datetime import datetime, timedelta
from collections import Counter

import buscar_extratos_bancarios
buscar_extratos_bancarios.VERBOSE = True

from buscar_extratos_bancarios import SantanderExtratosBancarios

print("="*100)
print("TESTE: BUSCAR 2 ANOS DE TRANSAÇÕES")
print("="*100)

fundo_id = "911_BANK"

try:
    cliente = SantanderExtratosBancarios(fundo_id)
    contas = cliente.listar_contas()
    
    if not contas:
        print(f"❌ Sem contas")
        exit(1)
    
    conta = contas[0]
    branch = conta.get('branchCode')
    account = conta.get('number')
    
    print(f"\n📊 Conta: {branch}.{account}")
    
    # Buscar 2 ANOS (730 dias)
    data_final = datetime.now()
    data_inicial = data_final - timedelta(days=730)
    
    print(f"📅 Período: {data_inicial.strftime('%d/%m/%Y')} a {data_final.strftime('%d/%m/%Y')} (730 dias)")
    print(f"\n{'='*100}")
    print("BUSCANDO...")
    print("="*100 + "\n")
    
    transacoes = cliente.buscar_transacoes(
        branch,
        account,
        data_inicial=data_inicial,
        data_final=data_final,
        limite=1000
    )
    
    print(f"\n{'='*100}")
    print("RESULTADO")
    print("="*100)
    
    if transacoes:
        print(f"\n✅ TOTAL: {len(transacoes)} transações")
        
        # Analisar datas
        datas = []
        for t in transacoes:
            data_str = t.get('transactionDate', '')
            if data_str:
                try:
                    if '/' in data_str:
                        dt = datetime.strptime(data_str, '%d/%m/%Y')
                    else:
                        dt = datetime.strptime(data_str[:10], '%Y-%m-%d')
                    datas.append(dt)
                except:
                    pass
        
        if datas:
            primeira = min(datas)
            ultima = max(datas)
            dias_cobertura = (ultima - primeira).days
            dias_da_primeira = (datetime.now() - primeira).days
            
            print(f"\n📅 COBERTURA:")
            print(f"   Primeira: {primeira.strftime('%d/%m/%Y')} ({dias_da_primeira} dias atrás)")
            print(f"   Última:   {ultima.strftime('%d/%m/%Y')}")
            print(f"   Total:    {dias_cobertura} dias")
            
            if dias_da_primeira >= 700:
                print(f"\n✅ ~2 ANOS de dados!")
            elif dias_da_primeira >= 350:
                print(f"\n✅ ~1 ano de dados")
            else:
                print(f"\n⚠️ Apenas {dias_da_primeira} dias")
            
            # Distribuição mensal
            print(f"\n📊 DISTRIBUIÇÃO MENSAL:")
            meses = Counter([d.strftime('%Y-%m') for d in datas])
            for mes in sorted(meses.keys()):
                print(f"   {mes}: {meses[mes]:4d}")
    else:
        print("\n❌ Sem transações")

except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*100)
