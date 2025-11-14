"""
Teste direto da API do Santander para CONDOLIVRE
Período: Outubro 2025
"""

import requests
import base64
from datetime import datetime

# Configurações
FUNDO_ID = "CONDOLIVRE FIDC"
CLIENT_ID = "WUrgXgftrP3G9iZXXIqljABiFx9oRBUC"
CLIENT_SECRET = "e4FAtyTG6mbDKPFV"
CERT_PATH = r"C:\Users\GustavoPrometti\Cert\santander_cert.pem"
KEY_PATH = r"C:\Users\GustavoPrometti\Cert\santander_key.pem"

print("="*80)
print("TESTE DIRETO API SANTANDER - CONDOLIVRE")
print("="*80)

# PASSO 1: Obter Token OAuth2
print("\n🔑 PASSO 1: Obtendo token OAuth2...")
token_url = "https://trust-open.api.santander.com.br/auth/oauth/v2/token"
auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
auth_b64 = base64.b64encode(auth_string.encode()).decode()

headers = {
    "Authorization": f"Basic {auth_b64}",
    "Content-Type": "application/x-www-form-urlencoded"
}

data = {
    "grant_type": "client_credentials"
}

try:
    response = requests.post(
        token_url,
        headers=headers,
        data=data,
        cert=(CERT_PATH, KEY_PATH),
        timeout=30
    )
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get("access_token")
        print(f"✅ Token obtido com sucesso!")
        print(f"   Token (primeiros 20 chars): {access_token[:20]}...")
    else:
        print(f"❌ Erro ao obter token: {response.status_code}")
        print(f"   Resposta: {response.text}")
        exit(1)
        
except Exception as e:
    print(f"❌ Exceção ao obter token: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# PASSO 2: Listar Contas
print("\n🏦 PASSO 2: Listando contas...")
accounts_url = "https://trust-open.api.santander.com.br/bank_account_information/v1/accounts"

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
    "X-Application-Key": CLIENT_ID
}

try:
    response = requests.get(
        accounts_url,
        headers=headers,
        cert=(CERT_PATH, KEY_PATH),
        timeout=30
    )
    
    if response.status_code == 200:
        accounts_data = response.json()
        accounts = accounts_data.get("_content", [])
        print(f"✅ {len(accounts)} conta(s) encontrada(s)")
        
        if accounts:
            conta = accounts[0]
            branch_code = conta.get('branchCode')
            account_number = conta.get('number')
            print(f"   Conta de teste: {branch_code}.{account_number}")
        else:
            print("❌ Nenhuma conta encontrada")
            exit(1)
    else:
        print(f"❌ Erro ao listar contas: {response.status_code}")
        print(f"   Resposta: {response.text}")
        exit(1)
        
except Exception as e:
    print(f"❌ Exceção ao listar contas: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# PASSO 3: Buscar Transações de OUTUBRO 2025
print("\n📊 PASSO 3: Buscando transações de OUTUBRO 2025...")
account_id = f"{branch_code}.{account_number}"
transactions_url = f"https://trust-open.api.santander.com.br/bank_account_information/v1/transactions/{account_id}"

params = {
    "initialDate": "2025-10-01",
    "finalDate": "2025-10-31",
    "_limit": "100",
    "_nextPage": "1"
}

print(f"   URL: {transactions_url}")
print(f"   Período: 01/10/2025 a 31/10/2025")
print(f"   Conta: {account_id}")

try:
    response = requests.get(
        transactions_url,
        headers=headers,
        params=params,
        cert=(CERT_PATH, KEY_PATH),
        timeout=30
    )
    
    print(f"\n📡 Status da resposta: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n📋 Resposta completa:")
        print(f"   Keys: {list(data.keys())}")
        
        transacoes = data.get("_content", [])
        total_records = data.get("_pageable", {}).get("totalRecords", "0")
        
        print(f"\n{'='*80}")
        print(f"RESULTADO: {len(transacoes)} transação(ões) retornada(s)")
        print(f"Total de registros (_pageable): {total_records}")
        print(f"{'='*80}")
        
        if transacoes and len(transacoes) > 0:
            print(f"\n✅ SUCESSO! Há {len(transacoes)} transação(ões) em OUTUBRO!")
            print(f"\n📝 Primeira transação:")
            trans = transacoes[0]
            print(f"   Data: {trans.get('transactionDate')}")
            print(f"   Descrição: {trans.get('transactionName')}")
            print(f"   Valor: R$ {trans.get('amount')}")
            print(f"   Tipo: {trans.get('creditDebitType')}")
            print(f"   Documento: {trans.get('documentNumber')}")
            
            if len(transacoes) > 1:
                print(f"\n   ... e mais {len(transacoes) - 1} transação(ões)")
        else:
            print(f"\n⚠️ Nenhuma transação encontrada em OUTUBRO 2025")
            print(f"   Isso pode significar:")
            print(f"   • Conta sem movimentação nesse período")
            print(f"   • API com delay na disponibilização dos dados")
            print(f"   • Período de carência/processamento")
    else:
        print(f"❌ Erro ao buscar transações: {response.status_code}")
        print(f"   Resposta: {response.text[:500]}")
        
except Exception as e:
    print(f"❌ Exceção ao buscar transações: {e}")
    import traceback
    traceback.print_exc()

# PASSO 4: Testar também NOVEMBRO (confirmação)
print("\n" + "="*80)
print("📊 PASSO 4: Testando NOVEMBRO 2025 (07-14)...")

params_nov = {
    "initialDate": "2025-11-07",
    "finalDate": "2025-11-14",
    "_limit": "100",
    "_nextPage": "1"
}

try:
    response_nov = requests.get(
        transactions_url,
        headers=headers,
        params=params_nov,
        cert=(CERT_PATH, KEY_PATH),
        timeout=30
    )
    
    if response_nov.status_code == 200:
        data_nov = response_nov.json()
        transacoes_nov = data_nov.get("_content", [])
        total_nov = data_nov.get("_pageable", {}).get("totalRecords", "0")
        
        print(f"\n{'='*80}")
        print(f"RESULTADO NOVEMBRO: {len(transacoes_nov)} transação(ões)")
        print(f"Total de registros: {total_nov}")
        print(f"{'='*80}")
        
        if len(transacoes_nov) > 0:
            print(f"✅ Há transações em novembro")
        else:
            print(f"⚠️ Confirmado: nenhuma transação em novembro")
            
except Exception as e:
    print(f"❌ Erro ao testar novembro: {e}")

print("\n" + "="*80)
print("TESTE CONCLUÍDO")
print("="*80)
