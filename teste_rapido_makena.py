"""
Teste rápido: verificar se há transações de 1 ano atrás para MAKENA
"""

from datetime import datetime, timedelta
from buscar_extratos_bancarios import SantanderExtratosBancarios

# Teste com MAKENA
fundo = "MAKENA"
data_final = datetime.now()
data_inicial = data_final - timedelta(days=365)  # 1 ano atrás

print("="*80)
print(f"TESTE: {fundo}")
print("="*80)
print(f"Período solicitado: {data_inicial.strftime('%d/%m/%Y')} a {data_final.strftime('%d/%m/%Y')}")
print(f"Total de dias: 365")

try:
    # Criar cliente
    print("\n🔧 Criando cliente...")
    cliente = SantanderExtratosBancarios(fundo)
    
    # Listar contas
    print("🏦 Listando contas...")
    contas = cliente.listar_contas()
    
    if not contas:
        print("❌ Nenhuma conta encontrada")
    else:
        print(f"✅ {len(contas)} conta(s) encontrada(s)")
        
        # Testar primeira conta
        conta = contas[0]
        branch = conta.get('branchCode') or conta.get('agencyCode')
        account = conta.get('number') or conta.get('accountNumber')
        
        print(f"\n📊 Buscando transações da conta: {branch}.{account}")
        
        transacoes = cliente.buscar_transacoes(
            branch,
            account,
            data_inicial=data_inicial,
            data_final=data_final
        )
        
        if transacoes:
            print(f"\n✅ {len(transacoes)} transação(ões) encontrada(s)")
            
            # Verificar datas
            if len(transacoes) > 0:
                datas_transacoes = [t.get('transactionDate', '') for t in transacoes if t.get('transactionDate')]
                
                if datas_transacoes:
                    primeira_data = min(datas_transacoes)
                    ultima_data = max(datas_transacoes)
                    
                    print(f"\n📅 Primeira transação: {primeira_data}")
                    print(f"📅 Última transação: {ultima_data}")
                    
                    # Converter para datetime
                    try:
                        dt_primeira = datetime.strptime(primeira_data[:10], '%Y-%m-%d')
                        dt_ultima = datetime.strptime(ultima_data[:10], '%Y-%m-%d')
                        
                        dias_cobertura = (dt_ultima - dt_primeira).days
                        print(f"\n📊 Cobertura real: {dias_cobertura} dias")
                        
                        # Verificar se há transações antigas
                        dias_atras_primeira = (data_final - dt_primeira).days
                        print(f"🔍 Transação mais antiga tem: {dias_atras_primeira} dias atrás")
                        
                        if dias_atras_primeira >= 300:
                            print("✅ SIM! Há transações de quase 1 ano atrás")
                        elif dias_atras_primeira >= 180:
                            print("⚠️ Há transações de ~6 meses atrás")
                        elif dias_atras_primeira >= 90:
                            print("⚠️ Há transações de ~3 meses atrás")
                        else:
                            print(f"❌ Transações mais antigas têm apenas {dias_atras_primeira} dias")
                        
                    except Exception as e:
                        print(f"Erro ao processar datas: {e}")
                
                # Mostrar primeiras 5 e últimas 5 transações
                print(f"\n📋 Primeiras 5 transações:")
                for i, t in enumerate(transacoes[:5], 1):
                    data = t.get('transactionDate', 'N/A')
                    nome = t.get('transactionName', 'N/A')
                    valor = t.get('amount', 0)
                    print(f"  {i}. {data[:10]} - {nome[:50]} - R$ {valor:,.2f}")
                
                if len(transacoes) > 10:
                    print(f"\n📋 Últimas 5 transações:")
                    for i, t in enumerate(transacoes[-5:], 1):
                        data = t.get('transactionDate', 'N/A')
                        nome = t.get('transactionName', 'N/A')
                        valor = t.get('amount', 0)
                        print(f"  {i}. {data[:10]} - {nome[:50]} - R$ {valor:,.2f}")
        else:
            print("❌ Nenhuma transação encontrada")
            
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
