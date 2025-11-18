# -*- coding: utf-8 -*-
"""
Teste progressivo de períodos: 30, 60, 90, 180, 365 dias
Objetivo: descobrir qual período máximo a API aceita
"""

from datetime import datetime, timedelta
from collections import Counter

# Mesma lógica do dashboard
import buscar_extratos_bancarios

# Ativar logs para ver detalhes
buscar_extratos_bancarios.VERBOSE = True

from buscar_extratos_bancarios import SantanderExtratosBancarios

print("="*100)
print("TESTE PROGRESSIVO DE PERÍODOS")
print("="*100)

# Testar com fundos que existem
fundos_teste = ["911_BANK", "AMPLIC", "INOVA", "MAKENA", "SEJA"]

# Períodos a testar
periodos_dias = [30, 60, 90, 180, 365]

resultados = {}

for fundo_id in fundos_teste:
    print(f"\n{'='*100}")
    print(f"TESTANDO FUNDO: {fundo_id}")
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
        
        print(f"\n📊 Conta: {branch}.{account}\n")
        
        resultados[fundo_id] = {}
        
        # Testar cada período
        for dias in periodos_dias:
            print(f"\n{'-'*100}")
            print(f"PERÍODO: {dias} DIAS")
            print("-"*100)
            
            data_final = datetime.now()
            data_inicial = data_final - timedelta(days=dias)
            
            print(f"📅 De {data_inicial.strftime('%d/%m/%Y')} até {data_final.strftime('%d/%m/%Y')}")
            
            try:
                transacoes = cliente.buscar_transacoes(
                    branch,
                    account,
                    data_inicial=data_inicial,
                    data_final=data_final,
                    limite=1000
                )
                
                if transacoes:
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
                        
                        resultado = {
                            'sucesso': True,
                            'total': len(transacoes),
                            'primeira_data': primeira,
                            'ultima_data': ultima,
                            'dias_cobertura': (ultima - primeira).days
                        }
                        
                        print(f"\n✅ SUCESSO: {len(transacoes)} transações")
                        print(f"   Primeira: {primeira.strftime('%d/%m/%Y')}")
                        print(f"   Última:   {ultima.strftime('%d/%m/%Y')}")
                        print(f"   Cobertura: {resultado['dias_cobertura']} dias")
                        
                    else:
                        resultado = {
                            'sucesso': True,
                            'total': len(transacoes),
                            'primeira_data': None,
                            'ultima_data': None,
                            'dias_cobertura': 0
                        }
                        print(f"\n✅ {len(transacoes)} transações (sem datas válidas)")
                else:
                    resultado = {
                        'sucesso': True,
                        'total': 0,
                        'primeira_data': None,
                        'ultima_data': None,
                        'dias_cobertura': 0
                    }
                    print(f"\n⚠️ Sem transações")
                
                resultados[fundo_id][dias] = resultado
                
            except Exception as e:
                resultado = {
                    'sucesso': False,
                    'erro': str(e),
                    'total': 0
                }
                resultados[fundo_id][dias] = resultado
                print(f"\n❌ ERRO: {e}")
        
        # Se conseguiu algum período, não precisa testar outros fundos
        if any(r.get('sucesso') and r.get('total', 0) > 0 for r in resultados[fundo_id].values()):
            print(f"\n{'='*100}")
            print(f"✅ {fundo_id} retornou dados! Parando aqui.")
            print("="*100)
            break
            
    except Exception as e:
        print(f"\n❌ Erro ao inicializar {fundo_id}: {e}")
        import traceback
        traceback.print_exc()

# Resumo final
print(f"\n\n{'='*100}")
print("RESUMO FINAL")
print("="*100)

for fundo_id, periodos in resultados.items():
    print(f"\n{fundo_id}:")
    for dias, resultado in periodos.items():
        if resultado.get('sucesso'):
            if resultado.get('total', 0) > 0:
                print(f"  ✅ {dias:3d} dias: {resultado['total']:4d} transações | Cobertura: {resultado['dias_cobertura']:3d} dias")
            else:
                print(f"  ⚠️  {dias:3d} dias: sem transações")
        else:
            print(f"  ❌ {dias:3d} dias: {resultado.get('erro', 'erro desconhecido')[:50]}")

print("\n" + "="*100)
