"""Teste CONDOLIVRE com período anterior para verificar se há dados"""

import requests
from datetime import datetime, timedelta
import json

# Importar as credenciais 
try:
    from config_credentials import SANTANDER_FUNDOS
    print("✅ Credenciais carregadas do config_credentials.py")
except:
    from credenciais_bancos import SANTANDER_FUNDOS
    print("✅ Credenciais carregadas do credenciais_bancos.py")

# Credenciais do CONDOLIVRE
condolivre = SANTANDER_FUNDOS['CONDOLIVRE FIDC']
client_id = condolivre['client_id']
client_secret = condolivre['client_secret']
cnpj = condolivre['cnpj']

# Certificados
cert_path = r"C:\Users\GustavoPrometti\Cert\santander_cert.pem"
key_path = r"C:\Users\GustavoPrometti\Cert\santander_key.pem"

print("="*80)
print("TESTE CONDOLIVRE - PERÍODOS DIFERENTES")
print("="*80)
print(f"Fundo: {condolivre['nome']}")
print(f"CNPJ: {cnpj}")
print(f"Client ID: {client_id}")

# Função para obter token
def get_access_token():
    url = "https://trust.api.santander.com.br/oauth/oauth2/v1/token"
    
    data = {
        'grant_type': 'client_credentials',
        'scope': 'account_information.balances.read account_information.transactions.read'
    }
    
    response = requests.post(
        url, 
        data=data,
        auth=(client_id, client_secret),
        cert=(cert_path, key_path),
        verify=True
    )
    
    if response.status_code == 200:
        token_data = response.json()
        return token_data['access_token']
    else:
        print(f"❌ Erro ao obter token: {response.status_code}")
        print(f"Resposta: {response.text}")
        return None

# Função para listar contas
def get_accounts(token):
    url = "https://trust.api.santander.com.br/bank_account_information/v1/accounts"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'X-Application-Key': client_id,
        'X-CNPJ': cnpj
    }
    
    response = requests.get(url, headers=headers, cert=(cert_path, key_path))
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Erro ao listar contas: {response.status_code}")
        print(f"Resposta: {response.text}")
        return None

# Função para buscar transações
def get_transactions(token, account_id, start_date, end_date):
    url = f"https://trust.api.santander.com.br/bank_account_information/v1/accounts/{account_id}/transactions"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'X-Application-Key': client_id,
        'X-CNPJ': cnpj
    }
    
    params = {
        'fromDate': start_date,
        'toDate': end_date
    }
    
    response = requests.get(url, headers=headers, params=params, cert=(cert_path, key_path))
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Erro ao buscar transações: {response.status_code}")
        print(f"Resposta: {response.text}")
        return None

# Obter token
print("\n1. Obtendo token de acesso...")
token = get_access_token()
if not token:
    exit()
print("✅ Token obtido com sucesso")

# Listar contas
print("\n2. Listando contas...")
accounts = get_accounts(token)
if not accounts or not accounts.get('data'):
    print("❌ Nenhuma conta encontrada")
    exit()

print(f"✅ {len(accounts['data'])} contas encontradas")
for account in accounts['data']:
    print(f"   Conta: {account.get('branch_code', 'N/A')}.{account.get('account_number', 'N/A')}")

# Testar diferentes períodos
periods = [
    ("Outubro 2024", "2024-10-01", "2024-10-31"),
    ("Setembro 2024", "2024-09-01", "2024-09-30"),
    ("Agosto 2024", "2024-08-01", "2024-08-31"),
    ("Novembro 2024 (problema atual)", "2024-11-07", "2024-11-14")
]

# Usar a primeira conta para teste
account = accounts['data'][0]
account_id = f"{account['branch_code']}.{account['account_number']}"

print(f"\n3. Testando transações para conta: {account_id}")
print("-" * 80)

for period_name, start_date, end_date in periods:
    print(f"\n📅 {period_name} ({start_date} até {end_date})")
    
    transactions = get_transactions(token, account_id, start_date, end_date)
    
    if transactions:
        total_records = transactions.get('_pageable', {}).get('totalRecords', '0')
        print(f"   💰 Total de registros: {total_records}")
        
        if int(total_records) > 0:
            data_list = transactions.get('data', [])
            print(f"   📊 Transações retornadas: {len(data_list)}")
            
            # Mostrar primeira transação
            if data_list:
                first_transaction = data_list[0]
                amount = first_transaction.get('transactionAmount', {})
                print(f"   🔍 Exemplo: {amount.get('currency', 'BRL')} {amount.get('amount', 0)} - {first_transaction.get('additionalInfo', 'N/A')}")
        else:
            print("   ❌ Nenhuma transação encontrada")
    else:
        print("   ❌ Erro ao buscar transações")

print("\n" + "="*80)
print("TESTE CONCLUÍDO")
print("="*80)