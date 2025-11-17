"""
Teste completo de busca de extratos CONDOLIVRE
Testa diferentes endpoints e abordagens para identificar o problema
"""

import requests
import json
import base64
from datetime import datetime, timedelta
import os

# Configuração
CERT_PATH = r"C:\Users\GustavoPrometti\Cert\santander_cert.pem"
KEY_PATH = r"C:\Users\GustavoPrometti\Cert\santander_key.pem"

# Credenciais CONDOLIVRE
CONDOLIVRE = {
    "client_id": "WUrgXgftrP3G9iZXXIqljABiFx9oRBUC",
    "client_secret": "e4FAtyTG6mbDKPFV",
    "cnpj": "42.317.295/0001-74",
    "nome": "CONDOLIVRE FUNDO DE INVESTIMENTO EM DIREITOS CREDITORIOS"
}

# Contas conhecidas
CONTAS = [
    {"agencia": "2271", "conta": "130137784"},
    {"agencia": "2271", "conta": "130176356"}
]

# Período: últimos 30 dias
DATA_FIM = datetime.now().strftime("%Y-%m-%d")
DATA_INICIO = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

print("="*80)
print("TESTE COMPLETO DE EXTRATOS - CONDOLIVRE")
print("="*80)
print(f"📅 Período: {DATA_INICIO} a {DATA_FIM} (30 dias)")
print(f"🏦 Fundo: {CONDOLIVRE['nome']}")
print(f"🆔 CNPJ: {CONDOLIVRE['cnpj']}")
print(f"🔑 Client ID: {CONDOLIVRE['client_id'][:20]}...")
print(f"📋 Contas a testar: {len(CONTAS)}")
print("="*80)


def obter_token():
    """Obtém token OAuth2"""
    print("\n🔐 PASSO 1: Obtendo token OAuth2...")
    
    url = "https://trust-open.api.santander.com.br/auth/oauth/v2/token"
    
    auth_string = f"{CONDOLIVRE['client_id']}:{CONDOLIVRE['client_secret']}"
    auth_b64 = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {auth_b64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    # Testar diferentes escopos
    escopos = [
        "open_banking_balances_statement",
        "account_information.balances.read account_information.transactions.read",
        "account_information.accounts.read account_information.balances.read account_information.transactions.read"
    ]
    
    for i, escopo in enumerate(escopos, 1):
        print(f"\n   Tentativa {i}: Escopo = {escopo}")
        
        data = {
            "grant_type": "client_credentials",
            "scope": escopo
        }
        
        try:
            response = requests.post(
                url, 
                headers=headers, 
                data=data, 
                cert=(CERT_PATH, KEY_PATH),
                timeout=30
            )
            
            if response.status_code == 200:
                token_data = response.json()
                token = token_data.get("access_token")
                expires_in = token_data.get("expires_in", 900)
                scope_recebido = token_data.get("scope", "")
                
                print(f"   ✅ Token obtido!")
                print(f"   ⏱️  Expira em: {expires_in}s")
                print(f"   📋 Escopo recebido: '{scope_recebido}'")
                print(f"   🔑 Token: {token[:30]}...")
                
                return token
            else:
                print(f"   ❌ Erro {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Exceção: {e}")
    
    return None


def teste_endpoint_accounts(token):
    """Testa endpoint /accounts"""
    print("\n\n🧪 PASSO 2: Testando endpoint /accounts...")
    
    url = "https://trust-open.api.santander.com.br/bank_account_information/v1/accounts"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Application-Key": CONDOLIVRE['client_id'],
        "X-CNPJ": CONDOLIVRE['cnpj']
    }
    
    params = {"page": "1", "page-size": "50"}
    
    print(f"   🔗 URL: {url}")
    print(f"   📤 Headers: X-Application-Key, X-CNPJ, Authorization")
    print(f"   📊 Params: {params}")
    
    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            cert=(CERT_PATH, KEY_PATH),
            timeout=30
        )
        
        print(f"   📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Sucesso!")
            print(f"   📋 Resposta: {json.dumps(data, indent=2)[:500]}")
            return data
        else:
            print(f"   ❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exceção: {e}")
    
    return None


def teste_endpoint_transactions(token, agencia, conta):
    """Testa endpoint /transactions direto"""
    print(f"\n\n🧪 PASSO 3: Testando endpoint /transactions para {agencia}.{conta}...")
    
    account_id = f"{agencia}.{conta}"
    url = f"https://trust-open.api.santander.com.br/bank_account_information/v1/accounts/{account_id}/transactions"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Application-Key": CONDOLIVRE['client_id'],
        "X-CNPJ": CONDOLIVRE['cnpj']
    }
    
    params = {
        "fromBookingDate": DATA_INICIO,
        "toBookingDate": DATA_FIM,
        "page": "1",
        "page-size": "100"
    }
    
    print(f"   🔗 URL: {url}")
    print(f"   📅 Período: {DATA_INICIO} a {DATA_FIM}")
    print(f"   📊 Params: {params}")
    
    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            cert=(CERT_PATH, KEY_PATH),
            timeout=60
        )
        
        print(f"   📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Sucesso!")
            
            # Tentar encontrar transações em diferentes estruturas
            transacoes = []
            
            if "data" in data:
                if isinstance(data["data"], dict) and "transactions" in data["data"]:
                    transacoes = data["data"]["transactions"]
                elif isinstance(data["data"], list):
                    transacoes = data["data"]
            elif "transactions" in data:
                transacoes = data["transactions"]
            elif "_content" in data:
                transacoes = data["_content"]
            
            print(f"   💰 Transações encontradas: {len(transacoes)}")
            
            if transacoes:
                print(f"\n   📋 Primeiras 3 transações:")
                for i, tx in enumerate(transacoes[:3], 1):
                    valor = tx.get("amount", {}).get("value", 0) if isinstance(tx.get("amount"), dict) else tx.get("amount", 0)
                    descricao = tx.get("description", "N/A")
                    data_tx = tx.get("bookingDate") or tx.get("date", "N/A")
                    tipo = tx.get("type", "N/A")
                    
                    print(f"   {i}. {data_tx} | {tipo} | R$ {valor} | {descricao}")
            else:
                print(f"\n   📋 Estrutura da resposta:")
                print(f"   {json.dumps(data, indent=2)[:1000]}")
            
            return transacoes
        else:
            print(f"   ❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exceção: {e}")
        import traceback
        traceback.print_exc()
    
    return None


def teste_endpoint_statements(token, agencia, conta):
    """Testa endpoint /statements (API antiga)"""
    print(f"\n\n🧪 PASSO 4: Testando endpoint /statements para {agencia}.{conta}...")
    
    bank_id = "90400888000142"  # CNPJ Santander
    url = f"https://trust-open.api.santander.com.br/bank_account_information/v1/banks/{bank_id}/statements"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Application-Key": CONDOLIVRE['client_id']
    }
    
    params = {
        "accountNumber": conta,
        "branchCode": agencia,
        "initialDate": DATA_INICIO,
        "finalDate": DATA_FIM
    }
    
    print(f"   🔗 URL: {url}")
    print(f"   📅 Período: {DATA_INICIO} a {DATA_FIM}")
    print(f"   📊 Params: {params}")
    
    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            cert=(CERT_PATH, KEY_PATH),
            timeout=60
        )
        
        print(f"   📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Sucesso!")
            print(f"   📋 Resposta: {json.dumps(data, indent=2)[:1000]}")
            return data
        else:
            print(f"   ❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exceção: {e}")
    
    return None


def main():
    """Execução principal"""
    
    # Verificar certificados
    if not os.path.exists(CERT_PATH):
        print(f"❌ Certificado não encontrado: {CERT_PATH}")
        return
    if not os.path.exists(KEY_PATH):
        print(f"❌ Chave não encontrada: {KEY_PATH}")
        return
    
    print(f"✅ Certificados encontrados")
    
    # Passo 1: Obter token
    token = obter_token()
    if not token:
        print("\n❌ Falha ao obter token. Abortando testes.")
        return
    
    # Passo 2: Testar /accounts
    teste_endpoint_accounts(token)
    
    # Passo 3 e 4: Testar transações para cada conta
    for conta_info in CONTAS:
        agencia = conta_info["agencia"]
        conta = conta_info["conta"]
        
        print(f"\n{'='*80}")
        print(f"🏪 TESTANDO CONTA: {agencia}.{conta}")
        print(f"{'='*80}")
        
        # Testar endpoint /transactions
        transacoes = teste_endpoint_transactions(token, agencia, conta)
        
        # Testar endpoint /statements
        statements = teste_endpoint_statements(token, agencia, conta)
        
        if transacoes:
            print(f"\n✅ CONTA {agencia}.{conta}: {len(transacoes)} transações via /transactions")
        elif statements:
            print(f"\n✅ CONTA {agencia}.{conta}: Dados via /statements")
        else:
            print(f"\n⚠️  CONTA {agencia}.{conta}: Nenhum dado retornado")
    
    print("\n" + "="*80)
    print("TESTE CONCLUÍDO")
    print("="*80)


if __name__ == "__main__":
    main()
