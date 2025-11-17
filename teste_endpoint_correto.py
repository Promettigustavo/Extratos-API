"""
Teste com endpoint correto que funcionava antes
"""

import requests
import json
import base64
from datetime import datetime, timedelta

CERT_PATH = r"C:\Users\GustavoPrometti\Cert\santander_cert.pem"
KEY_PATH = r"C:\Users\GustavoPrometti\Cert\santander_key.pem"

CONDOLIVRE = {
    "client_id": "WUrgXgftrP3G9iZXXIqljABiFx9oRBUC",
    "client_secret": "e4FAtyTG6mbDKPFV",
    "cnpj": "42.317.295/0001-74"
}

DATA_FIM = datetime.now().strftime("%Y-%m-%d")
DATA_INICIO = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

print("="*80)
print("TESTE COM ENDPOINT CORRETO - /transactions/{account_id}")
print("="*80)

# Obter token
url_token = "https://trust-open.api.santander.com.br/auth/oauth/v2/token"
auth_string = f"{CONDOLIVRE['client_id']}:{CONDOLIVRE['client_secret']}"
auth_b64 = base64.b64encode(auth_string.encode()).decode()

headers_token = {
    "Authorization": f"Basic {auth_b64}",
    "Content-Type": "application/x-www-form-urlencoded"
}

data_token = {
    "grant_type": "client_credentials",
    "scope": "open_banking_balances_statement"
}

print("\n🔐 Obtendo token...")
response_token = requests.post(
    url_token, 
    headers=headers_token, 
    data=data_token, 
    cert=(CERT_PATH, KEY_PATH),
    timeout=30
)

if response_token.status_code != 200:
    print(f"❌ Erro ao obter token: {response_token.status_code}")
    print(response_token.text)
    exit(1)

token = response_token.json()["access_token"]
print(f"✅ Token obtido: {token[:30]}...")

# Testar com endpoint correto
contas = [
    {"agencia": "2271", "conta": "130137784"},
    {"agencia": "2271", "conta": "130176356"}
]

for conta_info in contas:
    agencia = conta_info["agencia"]
    conta = conta_info["conta"]
    
    # Formatar corretamente: agência 4 dígitos + conta 12 dígitos
    agencia_formatada = agencia.zfill(4)
    conta_formatada = conta.zfill(12)
    account_id = f"{agencia_formatada}.{conta_formatada}"
    
    print(f"\n{'='*80}")
    print(f"🏪 Testando conta: {account_id}")
    print(f"   Original: {agencia}.{conta}")
    print(f"{'='*80}")
    
    # ENDPOINT CORRETO (funcionava antes)
    url = f"https://trust-open.api.santander.com.br/bank_account_information/v1/transactions/{account_id}"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Application-Key": CONDOLIVRE['client_id'],
        "X-CNPJ": CONDOLIVRE['cnpj']
    }
    
    params = {
        "fromBookingDate": DATA_INICIO,
        "toBookingDate": DATA_FIM,
        "_limit": "100",
        "_offset": "0"
    }
    
    print(f"📡 URL: {url}")
    print(f"📅 Período: {DATA_INICIO} a {DATA_FIM}")
    print(f"📊 Params: {params}")
    
    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            cert=(CERT_PATH, KEY_PATH),
            timeout=60
        )
        
        print(f"\n📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCESSO!")
            
            # Procurar transações
            transacoes = []
            if "_content" in data:
                transacoes = data["_content"]
            elif "data" in data:
                transacoes = data["data"]
            elif "transactions" in data:
                transacoes = data["transactions"]
            
            print(f"💰 Transações encontradas: {len(transacoes)}")
            
            if transacoes:
                print(f"\n📋 Primeiras 5 transações:")
                for i, tx in enumerate(transacoes[:5], 1):
                    valor = tx.get("amount", 0)
                    descricao = tx.get("description", "N/A")
                    data_tx = tx.get("bookingDate") or tx.get("date", "N/A")
                    tipo = tx.get("type", "N/A")
                    print(f"  {i}. {data_tx} | {tipo} | R$ {valor} | {descricao}")
            else:
                print(f"\n📋 Estrutura da resposta:")
                print(json.dumps(data, indent=2)[:1500])
        else:
            print(f"❌ Erro: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Exceção: {e}")
        import traceback
        traceback.print_exc()

print(f"\n{'='*80}")
print("TESTE CONCLUÍDO")
print(f"{'='*80}")
