"""
Teste RÁPIDO com API do Santander - MAKENA
Busca apenas últimos 30 dias para análise rápida
"""

import sys
from datetime import datetime, timedelta

# Importar o módulo de extratos
try:
    try:
        from credenciais_bancos import SANTANDER_FUNDOS
    except ImportError:
        from config_credentials import SANTANDER_FUNDOS
    
    from buscar_extratos_bancarios import SantanderExtratosBancarios
    print("✅ Módulos importados\n")
except ImportError as e:
    print(f"❌ Erro: {e}")
    sys.exit(1)

FUNDO_ID = "MAKENA"

print("=" * 100)
print("TESTE RÁPIDO - ÚLTIMOS 30 DIAS")
print("=" * 100)
print(f"\n🏦 Fundo: {FUNDO_ID}\n")

# Criar cliente
client = SantanderExtratosBancarios(FUNDO_ID)

# Período: últimos 30 dias
data_final = datetime.now()
data_inicial = data_final - timedelta(days=30)

print(f"📅 Período: {data_inicial.strftime('%d/%m/%Y')} a {data_final.strftime('%d/%m/%Y')}")
print(f"\n🔄 Buscando transações...\n")

try:
    transacoes = client.buscar_transacoes(
        branch_code="2271",
        account_number="000130107983",
        data_inicial=data_inicial,
        data_final=data_final
    )
    
    print(f"✅ {len(transacoes)} transações encontradas\n")
    
    if not transacoes:
        print("⚠️  Nenhuma transação encontrada")
        sys.exit(0)
    
    # Mostrar primeiras e últimas da API
    print("=" * 100)
    print("ORDEM ORIGINAL DA API:")
    print("=" * 100)
    print("\nPrimeiras 5 transações:")
    for i, t in enumerate(transacoes[:5], 1):
        data = t.get('transactionDate', '')
        nome = t.get('transactionName', '')[:40]
        print(f"{i}. {data} - {nome}")
    
    print("\nÚltimas 5 transações:")
    for i, t in enumerate(transacoes[-5:], len(transacoes)-4):
        data = t.get('transactionDate', '')
        nome = t.get('transactionName', '')[:40]
        print(f"{i}. {data} - {nome}")
    
    # Aplicar sorted()
    def extrair_data_ordenacao(trans):
        data = trans.get('transactionDate', '')
        if data and len(data) >= 10:
            try:
                # Converter DD/MM/YYYY para datetime
                dt = datetime.strptime(data, '%d/%m/%Y')
                return dt
            except:
                try:
                    # Tentar YYYY-MM-DD
                    dt = datetime.strptime(data[:10], '%Y-%m-%d')
                    return dt
                except:
                    return datetime(9999, 12, 31)
        return datetime(9999, 12, 31)
    
    transacoes_ordenadas = sorted(transacoes, key=extrair_data_ordenacao)
    
    print("\n" + "=" * 100)
    print("APÓS sorted() (LÓGICA ATUAL):")
    print("=" * 100)
    print("\nPrimeiras 5 transações:")
    for i, t in enumerate(transacoes_ordenadas[:5], 1):
        data = t.get('transactionDate', '')
        nome = t.get('transactionName', '')[:40]
        print(f"{i}. {data} - {nome}")
    
    print("\nÚltimas 5 transações:")
    for i, t in enumerate(transacoes_ordenadas[-5:], len(transacoes_ordenadas)-4):
        data = t.get('transactionDate', '')
        nome = t.get('transactionName', '')[:40]
        print(f"{i}. {data} - {nome}")
    
    # Análise
    print("\n" + "=" * 100)
    print("ANÁLISE:")
    print("=" * 100)
    
    primeira_api = transacoes[0].get('transactionDate', '')
    ultima_api = transacoes[-1].get('transactionDate', '')
    primeira_ord = transacoes_ordenadas[0].get('transactionDate', '')
    ultima_ord = transacoes_ordenadas[-1].get('transactionDate', '')
    
    print(f"\n📊 API Original:")
    print(f"   Primeira: {primeira_api}")
    print(f"   Última: {ultima_api}")
    
    print(f"\n📊 Após sorted():")
    print(f"   Primeira: {primeira_ord}")
    print(f"   Última: {ultima_ord}")
    
    # Converter para comparação
    try:
        dt_primeira = datetime.strptime(primeira_ord, '%d/%m/%Y')
        dt_ultima = datetime.strptime(ultima_ord, '%d/%m/%Y')
        
        if dt_primeira < dt_ultima:
            print(f"\n✅ ORDEM CORRETA!")
            print(f"   sorted() retornou: mais antiga ({primeira_ord}) → mais recente ({ultima_ord})")
            print(f"\n   📄 No extrato Excel/PDF DEVERIA aparecer:")
            print(f"      1ª linha: {primeira_ord}")
            print(f"      Última linha: {ultima_ord}")
        else:
            print(f"\n❌ ORDEM INVERTIDA!")
            print(f"   sorted() retornou: mais recente ({primeira_ord}) → mais antiga ({ultima_ord})")
            print(f"\n   🔧 SOLUÇÃO: Adicionar reverse=True no sorted()")
    except:
        print("\n⚠️  Não foi possível comparar datas")
    
    print("\n" + "=" * 100)
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
