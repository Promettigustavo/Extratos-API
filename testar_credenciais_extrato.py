"""
Teste de extrato usando credenciais específicas para Saldo e Extrato
"""
import sys
import codecs
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

import requests
from datetime import datetime, timedelta
import json

print("="*80)
print("TESTE COM CREDENCIAIS DE SALDO E EXTRATO")
print("="*80)

# Credenciais específicas para Saldo e Extrato
CLIENT_ID = "nt6TOWXkdRg8W2gmrR9wxmSNcZJTiHle"
CLIENT_SECRET = "lugp4nDNXXu39rXH"
CNPJ_FUNDO = "50.790.524/0001-00"

# Certificados
CERT_PATH = r"C:\Users\GustavoPrometti\Cert\santander_cert.pem"
KEY_PATH = r"C:\Users\GustavoPrometti\Cert\santander_key.pem"

print(f"\n🔑 Client ID: {CLIENT_ID}")
print(f"📋 CNPJ: {CNPJ_FUNDO}")

# PASSO 1: Obter token OAuth2
print("\n" + "="*80)
print("PASSO 1: OBTENDO TOKEN OAUTH2")
print("="*80)

token_url = "https://trust-open.api.santander.com.br/auth/oauth/v2/token"

# Headers corretos (igual ao que funciona em credenciais_bancos.py)
token_headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "X-Application-Key": CLIENT_ID
}

token_data = {
    "grant_type": "client_credentials",
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET
}

try:
    response = requests.post(
        token_url,
        headers=token_headers,
        data=token_data,
        cert=(CERT_PATH, KEY_PATH),
        timeout=30
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        token_info = response.json()
        access_token = token_info.get("access_token")
        print(f"✅ Token obtido: {access_token[:50]}...")
        print(f"   Expira em: {token_info.get('expires_in')} segundos")
        
        # PASSO 2: Testar endpoint de contas
        print("\n" + "="*80)
        print("PASSO 2: LISTANDO CONTAS")
        print("="*80)
        
        # Headers para as requisições da API (incluindo X-Application-Key)
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Application-Key": CLIENT_ID
        }
        
        # Testar com código do Santander
        for bank_id in ["0033", "90400888000142"]:
            print(f"\n🔍 Testando com bank_id: {bank_id}")
            url = f"https://trust-open.api.santander.com.br/bank_account_information/v1/banks/{bank_id}/accounts"
            
            # Adicionar parâmetros obrigatórios
            params = {
                "_offset": 1,
                "_limit": 50
            }
            
            response = requests.get(url, headers=headers, params=params, cert=(CERT_PATH, KEY_PATH), timeout=30)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCESSO! Resposta:")
                print(json.dumps(data, indent=2)[:1000])
                
                # A resposta usa '_content' não 'accounts'
                if '_content' in data and len(data['_content']) > 0:
                    account = data['_content'][0]
                    branch_code = account.get('branchCode')
                    account_number = account.get('number')
                    
                    print(f"\n   📋 Primeira conta encontrada:")
                    print(f"      Agência: {branch_code}")
                    print(f"      Conta: {account_number}")
                    
                    # PASSO 3: Buscar extrato
                    print("\n" + "="*80)
                    print("PASSO 3: BUSCANDO EXTRATO")
                    print("="*80)
                    
                    data_final = datetime.now()
                    data_inicial = data_final - timedelta(days=7)
                    
                    # Tentar diferentes formatos de endpoint
                    endpoints_testar = [
                        {
                            "nome": "transactions com account id",
                            "url": f"https://trust-open.api.santander.com.br/bank_account_information/v1/transactions/{branch_code}.{account_number}",
                            "params": {
                                "initialDate": data_inicial.strftime("%Y-%m-%d"),
                                "finalDate": data_final.strftime("%Y-%m-%d"),
                                "_limit": "50",
                                "_nextPage": "1"
                            }
                        },
                        {
                            "nome": "statements direto",
                            "url": f"https://trust-open.api.santander.com.br/bank_account_information/v1/banks/{bank_id}/statements",
                            "params": {
                                "branchCode": branch_code,
                                "accountNumber": account_number,
                                "initialDate": data_inicial.strftime("%Y-%m-%d"),
                                "finalDate": data_final.strftime("%Y-%m-%d"),
                                "_offset": "1",
                                "_limit": "50"
                            }
                        },
                        {
                            "nome": "accounts/{account}/statements",
                            "url": f"https://trust-open.api.santander.com.br/bank_account_information/v1/banks/{bank_id}/accounts/{branch_code}.{account_number}/statements",
                            "params": {
                                "initialDate": data_inicial.strftime("%Y-%m-%d"),
                                "finalDate": data_final.strftime("%Y-%m-%d"),
                                "_offset": "1",
                                "_limit": "50"
                            }
                        },
                        {
                            "nome": "balances com account id",
                            "url": f"https://trust-open.api.santander.com.br/bank_account_information/v1/banks/{bank_id}/balances/{branch_code}.{account_number}",
                            "params": {}
                        }
                    ]
                    
                    for endpoint in endpoints_testar:
                        print(f"\n🔍 Testando: {endpoint['nome']}")
                        print(f"   URL: {endpoint['url']}")
                        if endpoint['params']:
                            print(f"   Params: {endpoint['params']}")
                        
                        response = requests.get(
                            endpoint['url'], 
                            headers=headers, 
                            params=endpoint['params'], 
                            cert=(CERT_PATH, KEY_PATH), 
                            timeout=30
                        )
                        print(f"   Status: {response.status_code}")
                        
                        if response.status_code == 200:
                            data = response.json()
                            print(f"\n✅ SUCESSO com {endpoint['nome']}!")
                            print(json.dumps(data, indent=2)[:2000])
                            
                            # Se for transações, processar e salvar
                            if endpoint['nome'] == "transactions com account id" and '_content' in data:
                                transacoes = data['_content']
                                print(f"\n📊 Total de transações encontradas: {len(transacoes)}")
                                
                                # Exportar para Excel
                                import pandas as pd
                                df = pd.DataFrame(transacoes)
                                
                                # Formatar valores monetários
                                if 'amount' in df.columns:
                                    df['amount'] = df['amount'].apply(lambda x: f"R$ {float(x):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
                                
                                # Salvar em Excel
                                filename = f"extrato_{branch_code}_{account_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                                df.to_excel(filename, index=False, engine='openpyxl')
                                print(f"✅ Extrato salvo em: {filename}")
                            
                            break
                        else:
                            try:
                                erro = response.json()
                                print(f"   ❌ Erro: {json.dumps(erro)[:200]}")
                            except:
                                print(f"   ❌ Erro: {response.text[:200]}")
                    
                    # Continuar apenas se algum endpoint funcionou
                    if response.status_code != 200:
                        print("\n❌ Nenhum endpoint de extrato funcionou")
                        continue
                        
                        # PASSO 4: Tentar baixar PDF do extrato
                        print("\n" + "="*80)
                        print("PASSO 4: TENTANDO BAIXAR PDF DO EXTRATO")
                        print("="*80)
                        
                        # Endpoint para PDF de extrato (pode variar)
                        pdf_endpoints = [
                            f"https://trust-open.api.santander.com.br/bank_account_information/v1/banks/{bank_id}/statements/pdf",
                            f"https://trust-open.api.santander.com.br/bank_account_information/v1/accounts/{account_number}/statements/pdf"
                        ]
                        
                        for pdf_url in pdf_endpoints:
                            print(f"\n🔍 Testando: {pdf_url}")
                            response = requests.get(
                                pdf_url, 
                                headers=headers, 
                                params=params,
                                cert=(CERT_PATH, KEY_PATH), 
                                timeout=30
                            )
                            print(f"   Status: {response.status_code}")
                            
                            if response.status_code == 200:
                                print(f"   ✅ PDF disponível!")
                                print(f"   Content-Type: {response.headers.get('Content-Type')}")
                                print(f"   Tamanho: {len(response.content)} bytes")
                                
                                # Salvar PDF
                                pdf_filename = f"extrato_{bank_id}_{account_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                                with open(pdf_filename, 'wb') as f:
                                    f.write(response.content)
                                print(f"   💾 Salvo: {pdf_filename}")
                            else:
                                print(f"   Resposta: {response.text[:300]}")
                        
                    else:
                        print(f"   ❌ Erro: {response.text[:500]}")
                    
                    break  # Encontrou contas, não precisa testar outro bank_id
                    
            else:
                print(f"   ❌ Erro: {response.text[:500]}")
        
    else:
        print(f"❌ Erro ao obter token: {response.text}")
        
except Exception as e:
    print(f"❌ Exceção: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("FIM DO TESTE")
print("="*80)
