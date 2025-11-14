"""
Testar autenticação com diferentes métodos
"""

import requests
import base64

cert_path = r"C:\Users\GustavoPrometti\Cert\santander_cert.pem"
key_path = r"C:\Users\GustavoPrometti\Cert\santander_key.pem"

# Credenciais do 911_BANK (que funciona)
client_id = "3ZYICW0BDAwihhCwP4Tx08EtKYHFb2JG"
client_secret = "dAsx4AFNd7gNe8Lt"

url = "https://trust-open.api.santander.com.br/auth/oauth/v2/token"

print("="*80)
print("TESTANDO MÉTODOS DE AUTENTICAÇÃO")
print("="*80)

# Método 1: Basic Auth + Scope no body
print("\n1️⃣ Método Basic Auth + Scope")
auth_string = f"{client_id}:{client_secret}"
auth_b64 = base64.b64encode(auth_string.encode()).decode()

response = requests.post(
    url,
    headers={
        "Authorization": f"Basic {auth_b64}",
        "Content-Type": "application/x-www-form-urlencoded"
    },
    data={
        "grant_type": "client_credentials",
        "scope": "open_banking_balances_statement"
    },
    cert=(cert_path, key_path)
)
print(f"Status: {response.status_code}")
print(f"Resposta: {response.text[:300]}")

# Método 2: X-Application-Key + credentials no body
print("\n2️⃣ Método X-Application-Key")
response = requests.post(
    url,
    headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Application-Key": client_id
    },
    data={
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    },
    cert=(cert_path, key_path)
)
print(f"Status: {response.status_code}")
print(f"Resposta: {response.text[:300]}")

# Método 3: Só credentials no body
print("\n3️⃣ Método credentials no body")
response = requests.post(
    url,
    headers={
        "Content-Type": "application/x-www-form-urlencoded"
    },
    data={
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    },
    cert=(cert_path, key_path)
)
print(f"Status: {response.status_code}")
print(f"Resposta: {response.text[:300]}")

print("\n" + "="*80)
