"""
Testar qual URL de autenticação do Santander funciona
"""

import requests

# Certificados locais
cert_path = r"C:\Users\GustavoPrometti\Cert\santander_cert.pem"
key_path = r"C:\Users\GustavoPrometti\Cert\santander_key.pem"

# URLs para testar
urls = [
    "https://api-auth.santander.com.br/auth/oauth/v2/token",
    "https://trust-open.api.santander.com.br/auth/oauth/v2/token",
    "https://ob-auth.santander.com.br/auth/oauth/v2/token",
]

print("Testando URLs de autenticação Santander...")
print("="*80)

for url in urls:
    print(f"\n🔍 Testando: {url}")
    try:
        # Apenas testar conexão (vai dar erro de auth, mas isso é ok)
        response = requests.post(
            url,
            data={"grant_type": "client_credentials"},
            cert=(cert_path, key_path),
            timeout=10
        )
        print(f"   ✅ Conectou! Status: {response.status_code}")
        print(f"   Resposta: {response.text[:200]}")
    except requests.exceptions.SSLError as e:
        print(f"   ⚠️  Erro SSL: {str(e)[:100]}")
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ Erro de conexão: {str(e)[:100]}")
    except Exception as e:
        print(f"   ❌ Erro: {type(e).__name__}: {str(e)[:100]}")

print("\n" + "="*80)
print("Teste concluído!")
