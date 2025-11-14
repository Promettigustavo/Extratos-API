from buscar_extratos_bancarios import SantanderExtratosBancarios
from datetime import datetime, timedelta
import requests

fundo_id = 'CONDOLIVRE FIDC'
api = SantanderExtratosBancarios(fundo_id)

# Obter token
token = api.obter_token_acesso()
print(f"Token: {token[:50]}..." if token else "Sem token")

# Listar contas
contas = api.listar_contas()
if contas:
    conta = contas[0]
    branch = conta.get('branchCode')
    account = conta.get('number')
    print(f"\nConta: {branch}.{account}")
    
    # Testar com diferentes períodos
    periodos = [
        ("Últimos 7 dias", 7),
        ("Últimos 14 dias", 14),
        ("Últimos 30 dias", 30),
        ("Últimos 60 dias", 60)
    ]
    
    for nome, dias in periodos:
        data_inicial = datetime.now() - timedelta(days=dias)
        data_final = datetime.now()
        
        account_id = f"{branch}.{account}"
        url = f"https://trust-open.api.santander.com.br/bank_account_information/v1/transactions/{account_id}"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Application-Key": api.client_id
        }
        
        params = {
            "initialDate": data_inicial.strftime("%Y-%m-%d"),
            "finalDate": data_final.strftime("%Y-%m-%d"),
            "_limit": "1000",
            "_nextPage": "1"
        }
        
        print(f"\n{'='*80}")
        print(f"{nome}: {params['initialDate']} a {params['finalDate']}")
        print(f"{'='*80}")
        
        response = requests.get(
            url,
            headers=headers,
            params=params,
            cert=(api.cert_path, api.key_path),
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            transacoes = data.get("_content", [])
            print(f"Transações: {len(transacoes)}")
            
            if transacoes:
                print(f"\nPrimeiras 3 transações:")
                for i, t in enumerate(transacoes[:3], 1):
                    print(f"\n{i}. {t.get('transactionDate')}: {t.get('transactionName')}")
                    print(f"   Valor: R$ {t.get('amount')} ({t.get('creditDebitType')})")
                break  # Se encontrou, para
        else:
            print(f"Erro: {response.text[:500]}")
