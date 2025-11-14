"""
Testar autenticação de todos os fundos
"""

import requests
import base64
from credenciais_bancos import SANTANDER_FUNDOS

cert_path = r"C:\Users\GustavoPrometti\Cert\santander_cert.pem"
key_path = r"C:\Users\GustavoPrometti\Cert\santander_key.pem"
url = "https://trust-open.api.santander.com.br/auth/oauth/v2/token"

print("="*80)
print("TESTE DE AUTENTICAÇÃO - TODOS OS FUNDOS")
print("="*80)

fundos_ok = []
fundos_erro = []

for fundo_id, config in sorted(SANTANDER_FUNDOS.items()):
    client_id = config.get("client_id", "")
    client_secret = config.get("client_secret", "")
    
    if not client_id or not client_secret:
        print(f"\n⚠️  {fundo_id}: Sem credenciais configuradas")
        fundos_erro.append((fundo_id, "Sem credenciais"))
        continue
    
    print(f"\n🔍 Testando: {fundo_id}")
    
    try:
        # Método X-Application-Key (mais comum)
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
            cert=(cert_path, key_path),
            timeout=10
        )
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token", "")
            print(f"   ✅ OK - Token: {token[:30]}...")
            fundos_ok.append(fundo_id)
        else:
            erro = response.json().get("error_description", response.text[:100])
            print(f"   ❌ Erro {response.status_code}: {erro}")
            fundos_erro.append((fundo_id, f"{response.status_code} - {erro}"))
            
    except Exception as e:
        print(f"   ❌ Exceção: {str(e)[:100]}")
        fundos_erro.append((fundo_id, f"Exceção: {str(e)[:50]}"))

# Resumo
print("\n" + "="*80)
print("RESUMO")
print("="*80)

print(f"\n✅ Fundos com autenticação OK: {len(fundos_ok)}/{len(SANTANDER_FUNDOS)}")
for fundo in fundos_ok:
    print(f"   • {fundo}")

if fundos_erro:
    print(f"\n❌ Fundos com erro: {len(fundos_erro)}/{len(SANTANDER_FUNDOS)}")
    for fundo, erro in fundos_erro:
        print(f"   • {fundo}: {erro}")

print("\n" + "="*80)
print(f"Taxa de sucesso: {len(fundos_ok)*100//len(SANTANDER_FUNDOS)}%")
print("="*80)
