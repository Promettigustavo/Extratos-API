"""
Teste de paginação: verificar se está buscando TODAS as transações
PROBLEMA IDENTIFICADO: _offset estava sendo usado como número de página (1, 2, 3)
quando deveria ser índice de registro (0, 1000, 2000)
"""

from datetime import datetime, timedelta
import buscar_extratos_bancarios

# Ativar logs
buscar_extratos_bancarios.VERBOSE = True

from buscar_extratos_bancarios import SantanderExtratosBancarios

print("="*100)
print("TESTE DE PAGINAÇÃO - MAKENA - 1 ANO")
print("="*100)

fundo = "MAKENA"
data_inicial = datetime.now() - timedelta(days=365)
data_final = datetime.now()

print(f"\nFundo: {fundo}")
print(f"Período: {data_inicial.strftime('%d/%m/%Y')} a {data_final.strftime('%d/%m/%Y')} (365 dias)")
print("\n" + "="*100)

try:
    cliente = SantanderExtratosBancarios(fundo)
    contas = cliente.listar_contas()
    
    if not contas:
        print("❌ Nenhuma conta")
        exit(1)
    
    conta = contas[0]
    branch = conta.get('branchCode') or conta.get('agencyCode')
    account = conta.get('number') or conta.get('accountNumber')
    
    print(f"\n📊 Conta: {branch}.{account}")
    print("\n" + "="*100)
    print("BUSCANDO TRANSAÇÕES COM PAGINAÇÃO CORRIGIDA...")
    print("="*100 + "\n")
    
    transacoes = cliente.buscar_transacoes(
        branch,
        account,
        data_inicial=data_inicial,
        data_final=data_final,
        limite=1000  # 1000 por página
    )
    
    print("\n" + "="*100)
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
            if len(transacoes) >= 1000:
                print(f"   ⚠️ Exatamente {len(transacoes)} transações - pode ter mais páginas!")
                print(f"   Verifique os logs acima para ver se buscou múltiplas páginas")
            
            if dias_da_primeira >= 350:
                print(f"   ✅ Dados de ~1 ano atrás encontrados!")
            elif dias_da_primeira >= 300:
                print(f"   ⚠️ Dados de ~10 meses")
            elif dias_da_primeira >= 180:
                print(f"   ❌ Apenas ~6 meses - limite da API ou paginação?")
            elif dias_da_primeira >= 90:
                print(f"   ❌ Apenas ~3 meses - PROBLEMA DE PAGINAÇÃO")
            else:
                print(f"   ❌ Apenas {dias_da_primeira} dias - ERRO CRÍTICO")
            
            # Mostrar distribuição por mês
            print(f"\n📊 DISTRIBUIÇÃO POR MÊS:")
            from collections import Counter
            meses = Counter([d.strftime('%Y-%m') for d in datas])
            for mes in sorted(meses.keys()):
                print(f"   {mes}: {meses[mes]} transações")
    else:
        print("\n❌ Nenhuma transação encontrada")

except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*100)
