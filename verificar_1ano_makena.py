"""
Verificação detalhada: O que a API Santander realmente retorna para MAKENA
com período de 1 ano?
"""

from datetime import datetime, timedelta
import sys

# Habilitar logs verbose
import buscar_extratos_bancarios
buscar_extratos_bancarios.VERBOSE = True

from buscar_extratos_bancarios import SantanderExtratosBancarios

fundo = "MAKENA"
data_final = datetime.now()
data_inicial = data_final - timedelta(days=365)

print("="*100)
print(f"VERIFICAÇÃO DETALHADA: {fundo}")
print("="*100)
print(f"📅 Período SOLICITADO:")
print(f"   Início: {data_inicial.strftime('%d/%m/%Y %H:%M:%S')}")
print(f"   Fim:    {data_final.strftime('%d/%m/%Y %H:%M:%S')}")
print(f"   Total:  365 dias")
print("="*100)

try:
    cliente = SantanderExtratosBancarios(fundo)
    contas = cliente.listar_contas()
    
    if not contas:
        print("❌ Nenhuma conta encontrada")
        sys.exit(1)
    
    conta = contas[0]
    branch = conta.get('branchCode') or conta.get('agencyCode')
    account = conta.get('number') or conta.get('accountNumber')
    
    print(f"\n📊 Conta: {branch}.{account}")
    print("\n" + "="*100)
    print("CHAMANDO API...")
    print("="*100)
    
    # Buscar com logs verbose ativados
    transacoes = cliente.buscar_transacoes(
        branch,
        account,
        data_inicial=data_inicial,
        data_final=data_final
    )
    
    print("\n" + "="*100)
    print("ANÁLISE DOS RESULTADOS")
    print("="*100)
    
    if not transacoes:
        print("❌ API retornou 0 transações")
    else:
        print(f"✅ API retornou {len(transacoes)} transações")
        
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
            
            print(f"\n📅 DATAS DAS TRANSAÇÕES RETORNADAS:")
            print(f"   Primeira: {primeira.strftime('%d/%m/%Y')}")
            print(f"   Última:   {ultima.strftime('%d/%m/%Y')}")
            print(f"   Período:  {(ultima - primeira).days} dias")
            
            # Verificar se realmente pegou 1 ano
            dias_da_primeira = (data_final - primeira).days
            print(f"\n🔍 VERIFICAÇÃO:")
            print(f"   Transação mais antiga foi há {dias_da_primeira} dias")
            
            if dias_da_primeira >= 350:
                print(f"   ✅ SIM! API retornou dados de ~1 ano atrás ({dias_da_primeira} dias)")
            elif dias_da_primeira >= 300:
                print(f"   ⚠️ API retornou dados de ~10 meses ({dias_da_primeira} dias)")
            elif dias_da_primeira >= 180:
                print(f"   ⚠️ API retornou apenas ~6 meses ({dias_da_primeira} dias)")
            elif dias_da_primeira >= 90:
                print(f"   ⚠️ API retornou apenas ~3 meses ({dias_da_primeira} dias)")
            elif dias_da_primeira >= 30:
                print(f"   ❌ API retornou apenas ~1 mês ({dias_da_primeira} dias)")
            else:
                print(f"   ❌ API retornou apenas {dias_da_primeira} dias")
            
            # Comparar com solicitado
            print(f"\n📊 COMPARAÇÃO:")
            print(f"   Solicitado: {data_inicial.strftime('%d/%m/%Y')} a {data_final.strftime('%d/%m/%Y')}")
            print(f"   Recebido:   {primeira.strftime('%d/%m/%Y')} a {ultima.strftime('%d/%m/%Y')}")
            
            if primeira.date() <= data_inicial.date():
                print(f"   ✅ API respeitou a data inicial solicitada")
            else:
                diff_dias = (primeira - data_inicial).days
                print(f"   ❌ API retornou dados apenas a partir de {diff_dias} dias DEPOIS do solicitado")
                print(f"   ⚠️ LIMITE DA API: aparentemente {dias_da_primeira} dias para trás")
        
        # Mostrar amostra
        print(f"\n📋 AMOSTRA (primeiras 3 transações):")
        for i, t in enumerate(transacoes[:3], 1):
            data = t.get('transactionDate', 'N/A')[:10]
            nome = t.get('transactionName', 'N/A')[:40]
            valor = t.get('amount', 0)
            print(f"   {i}. {data} - {nome} - R$ {valor:,.2f}")
        
        if len(transacoes) > 3:
            print(f"\n📋 AMOSTRA (últimas 3 transações):")
            for i, t in enumerate(transacoes[-3:], len(transacoes)-2):
                data = t.get('transactionDate', 'N/A')[:10]
                nome = t.get('transactionName', 'N/A')[:40]
                valor = t.get('amount', 0)
                print(f"   {i}. {data} - {nome} - R$ {valor:,.2f}")

except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*100)
