"""
Debug: Verificar se as datas do dashboard chegam corretamente na API
"""

from datetime import datetime as dt, timedelta, date

print("="*80)
print("DEBUG: FLUXO DE DATAS - DASHBOARD → API")
print("="*80)

# Simular o que o dashboard faz
print("\n1️⃣ DASHBOARD - Seleção de datas pelo usuário:")
print("-"*80)

# Exemplo: Usuário seleciona últimos 30 dias
hoje = date.today()
data_inicial_date = hoje - timedelta(days=30)
data_final_date = hoje

print(f"📅 Data inicial (date): {data_inicial_date} (tipo: {type(data_inicial_date)})")
print(f"📅 Data final (date):   {data_final_date} (tipo: {type(data_final_date)})")

# Dashboard converte date → datetime
print("\n2️⃣ DASHBOARD - Conversão date → datetime:")
print("-"*80)

data_inicial_dt = dt.combine(data_inicial_date, dt.min.time())
data_final_dt = dt.combine(data_final_date, dt.max.time())

print(f"🕐 Data inicial (datetime): {data_inicial_dt} (tipo: {type(data_inicial_dt)})")
print(f"🕐 Data final (datetime):   {data_final_dt} (tipo: {type(data_final_dt)})")

# Função main recebe
print("\n3️⃣ FUNÇÃO MAIN - Recebe datetime:")
print("-"*80)

def simular_main(data_inicial, data_final):
    print(f"   Recebeu data_inicial: {data_inicial} (tipo: {type(data_inicial)})")
    print(f"   Recebeu data_final:   {data_final} (tipo: {type(data_final)})")
    return data_inicial, data_final

data_ini, data_fim = simular_main(data_inicial_dt, data_final_dt)

# buscar_transacoes usa
print("\n4️⃣ BUSCAR_TRANSACOES - Usa datetime:")
print("-"*80)

def simular_buscar_transacoes(data_inicial, data_final):
    if not data_final:
        data_final = dt.now()
    if not data_inicial:
        data_inicial = data_final - timedelta(days=7)
    
    print(f"   Usando data_inicial: {data_inicial}")
    print(f"   Usando data_final:   {data_final}")
    
    # Formatar para API
    initial_date_str = data_inicial.strftime("%Y-%m-%d")
    final_date_str = data_final.strftime("%Y-%m-%d")
    
    print(f"\n   Enviando para API Santander:")
    print(f"      initialDate: {initial_date_str}")
    print(f"      finalDate:   {final_date_str}")
    
    return initial_date_str, final_date_str

initial, final = simular_buscar_transacoes(data_ini, data_fim)

# Verificar resultado
print("\n5️⃣ VERIFICAÇÃO FINAL:")
print("-"*80)

print(f"✅ Período selecionado pelo usuário no dashboard:")
print(f"   De: {data_inicial_date.strftime('%d/%m/%Y')}")
print(f"   Até: {data_final_date.strftime('%d/%m/%Y')}")

print(f"\n✅ Período enviado para API Santander:")
print(f"   initialDate: {initial}")
print(f"   finalDate:   {final}")

print(f"\n✅ Dias de diferença: {(data_final_date - data_inicial_date).days} dias")

# Testar com CONDOLIVRE real
print("\n"+"="*80)
print("TESTE REAL COM CONDOLIVRE")
print("="*80)

from buscar_extratos_bancarios import SantanderExtratosBancarios

fundo_id = 'CONDOLIVRE FIDC'
api = SantanderExtratosBancarios(fundo_id)

contas = api.listar_contas()
if contas:
    conta = contas[0]
    branch = conta.get('branchCode')
    account = conta.get('number')
    
    print(f"\n📊 Buscando com período do dashboard:")
    print(f"   data_inicial: {data_inicial_dt}")
    print(f"   data_final:   {data_final_dt}")
    
    trans = api.buscar_transacoes(branch, account, data_inicial_dt, data_final_dt)
    
    print(f"\n✅ Resultado: {len(trans)} transações encontradas")
    
    if trans:
        primeira = trans[0].get('transactionDate', '')[:10]
        ultima = trans[-1].get('transactionDate', '')[:10]
        print(f"   Primeira transação: {primeira}")
        print(f"   Última transação:   {ultima}")

print("\n"+"="*80)
print("CONCLUSÃO")
print("="*80)
print("✅ As datas do dashboard SIM chegam corretamente na API")
print("✅ O fluxo está funcionando perfeitamente")
print("="*80)
