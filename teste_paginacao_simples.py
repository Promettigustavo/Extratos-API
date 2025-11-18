# -*- coding: utf-8 -*-
"""
Teste de paginação usando a mesma lógica do dashboard
"""

from datetime import datetime, timedelta
from collections import Counter

# Mesma lógica do dashboard
import buscar_extratos_bancarios

# Ativar logs para ver a paginação
buscar_extratos_bancarios.VERBOSE = True

from buscar_extratos_bancarios import SantanderExtratosBancarios

print("="*100)
print("TESTE DE PAGINACAO - 30 DIAS")
print("="*100)

# Testar com fundos que existem
fundos_teste = ["911_BANK", "AMPLIC", "INOVA", "MAKENA", "SEJA"]

for fundo_id in fundos_teste:
    print(f"\n{'='*100}")
    print(f"TESTANDO: {fundo_id}")
    print("="*100)
    
    try:
        cliente = SantanderExtratosBancarios(fundo_id)
        contas = cliente.listar_contas()
        
        if not contas:
            print(f"❌ {fundo_id}: Sem contas")
            continue
        
        conta = contas[0]
        branch = conta.get('branchCode') or conta.get('agencyCode')
        account = conta.get('number') or conta.get('accountNumber')
        
        print(f"\n📊 Conta: {branch}.{account}")
        
        # Buscar 30 dias (período menor e seguro)
        data_final = datetime.now()
        data_inicial = data_final - timedelta(days=30)
        
        print(f"📅 Período: {data_inicial.strftime('%d/%m/%Y')} a {data_final.strftime('%d/%m/%Y')}")
        print(f"\n{'='*100}")
        print("BUSCANDO TRANSAÇÕES (observe os logs de paginação)...")
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
            print(f"\n✅ Total: {len(transacoes)} transações")
            
            # Analisar datas
            datas = []
            for t in transacoes:
                data_str = t.get('transactionDate', '')
                if data_str:
                    try:
                        dt = datetime.strptime(data_str[:10], '%Y-%m-%d')
                        datas.append(dt)
                    except:
                        pass
            
            if datas:
                primeira = min(datas)
                ultima = max(datas)
                dias_cobertura = (ultima - primeira).days
                
                print(f"\n📅 Cobertura:")
                print(f"   Primeira: {primeira.strftime('%d/%m/%Y')}")
                print(f"   Última:   {ultima.strftime('%d/%m/%Y')}")
                print(f"   Total:    {dias_cobertura} dias")
                
                # Verificar se tem múltiplas páginas
                if len(transacoes) >= 1000:
                    print(f"\n⚠️ {len(transacoes)} transações - VERIFIQUE LOGS DE PAGINAÇÃO ACIMA")
                
                # Distribuição mensal
                meses = Counter([d.strftime('%Y-%m') for d in datas])
                print(f"\n📊 Por mês:")
                for mes in sorted(meses.keys()):
                    print(f"   {mes}: {meses[mes]}")
                
                # SUCESSO - pode parar aqui
                print(f"\n✅ {fundo_id} funcionou! Teste completo.")
                break
        else:
            print(f"\n❌ Sem transações")
            
    except Exception as e:
        print(f"\n❌ Erro em {fundo_id}: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*100)
