# -*- coding: utf-8 -*-
"""
Teste de paginação completa - 365 dias
Objetivo: verificar se busca TODAS as páginas de transações
"""

from datetime import datetime, timedelta
from collections import Counter

import buscar_extratos_bancarios
buscar_extratos_bancarios.VERBOSE = True

from buscar_extratos_bancarios import SantanderExtratosBancarios

print("="*100)
print("TESTE: BUSCAR TODAS AS TRANSAÇÕES DE 1 ANO")
print("="*100)

fundo_id = "911_BANK"  # Usar um fundo com bastante movimento

try:
    cliente = SantanderExtratosBancarios(fundo_id)
    contas = cliente.listar_contas()
    
    if not contas:
        print(f"❌ Sem contas para {fundo_id}")
        exit(1)
    
    conta = contas[0]
    branch = conta.get('branchCode') or conta.get('agencyCode')
    account = conta.get('number') or conta.get('accountNumber')
    
    print(f"\n📊 Conta: {branch}.{account}")
    
    # Buscar 365 dias
    data_final = datetime.now()
    data_inicial = data_final - timedelta(days=365)
    
    print(f"📅 Período: {data_inicial.strftime('%d/%m/%Y')} a {data_final.strftime('%d/%m/%Y')}")
    print(f"\n{'='*100}")
    print("BUSCANDO TODAS AS PÁGINAS...")
    print("="*100 + "\n")
    
    transacoes = cliente.buscar_transacoes(
        branch,
        account,
        data_inicial=data_inicial,
        data_final=data_final,
        limite=1000  # 1000 por página
    )
    
    print(f"\n{'='*100}")
    print("RESULTADO FINAL")
    print("="*100)
    
    if transacoes:
        print(f"\n✅ TOTAL: {len(transacoes)} transações")
        
        # Analisar datas
        datas = []
        for t in transacoes:
            data_str = t.get('transactionDate', '')
            if data_str:
                try:
                    # Tentar formato brasileiro primeiro
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
            
            print(f"\n📅 PERÍODO DAS TRANSAÇÕES:")
            print(f"   Primeira: {primeira.strftime('%d/%m/%Y')} ({dias_da_primeira} dias atrás)")
            print(f"   Última:   {ultima.strftime('%d/%m/%Y')}")
            print(f"   Cobertura: {dias_cobertura} dias")
            
            print(f"\n🔍 ANÁLISE:")
            if dias_da_primeira >= 350:
                print(f"   ✅ Dados de ~1 ano completo!")
            elif dias_da_primeira >= 300:
                print(f"   ⚠️ Dados de ~10 meses")
            elif dias_da_primeira >= 180:
                print(f"   ⚠️ Apenas ~6 meses")
            else:
                print(f"   ❌ Apenas ~{dias_da_primeira} dias")
            
            # Mostrar distribuição por mês
            print(f"\n📊 DISTRIBUIÇÃO POR MÊS:")
            meses = Counter([d.strftime('%Y-%m') for d in datas])
            for mes in sorted(meses.keys()):
                print(f"   {mes}: {meses[mes]:4d} transações")
            
            # Verificar se pode ter mais dados
            if len(transacoes) % 1000 == 0:
                print(f"\n⚠️ ATENÇÃO: Total ({len(transacoes)}) é múltiplo de 1000")
                print(f"   Pode haver mais páginas não buscadas!")
            else:
                print(f"\n✅ Total ({len(transacoes)}) não é múltiplo exato de 1000")
                print(f"   Provavelmente todas as páginas foram buscadas")
    else:
        print("\n❌ Nenhuma transação encontrada")

except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*100)
