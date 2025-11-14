"""
Teste de acesso aos endpoints de extrato bancário
"""
import sys
import codecs
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

from credenciais_bancos import SantanderAuth
import requests
from datetime import datetime, timedelta

print("="*80)
print("TESTE DE ACESSO A EXTRATOS BANCÁRIOS - API SANTANDER")
print("="*80)

# Criar autenticação
auth = SantanderAuth.criar_por_fundo("911_BANK")
cnpj = auth.fundo_cnpj.replace(".", "").replace("/", "").replace("-", "")

print(f"\n📋 Fundo: {auth.fundo_nome}")
print(f"   CNPJ: {auth.fundo_cnpj} ({cnpj})")

# Obter token e certificados
token = auth.obter_token_acesso()
cert_tuple = auth._get_cert_tuple()

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

print("\n" + "="*80)
print("TESTANDO ENDPOINTS DE EXTRATO")
print("="*80)

# 1. Listar contas
print("\n1️⃣ Testando: GET /bank_account_information/v1/banks/{cnpj}/accounts")
url_contas = f"https://trust-open.api.santander.com.br/bank_account_information/v1/banks/{cnpj}/accounts"
print(f"   URL: {url_contas}")

try:
    response = requests.get(url_contas, headers=headers, cert=cert_tuple, timeout=30)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ SUCESSO! Resposta: {response.text[:200]}")
    else:
        print(f"   ❌ ERRO: {response.text[:500]}")
except Exception as e:
    print(f"   ❌ Exceção: {e}")

# 2. Testar saldo (se soubermos o accountId)
print("\n2️⃣ Testando: GET /bank_account_information/v1/accounts/{accountId}/balances")
print("   ⚠️ Precisa de accountId - pulando por enquanto")

# 3. Testar extrato
print("\n3️⃣ Testando: GET /bank_account_information/v1/accounts/{accountId}/statements")
print("   ⚠️ Precisa de accountId - pulando por enquanto")

# 4. Testar PDF de extrato
print("\n4️⃣ Testando: GET /bank_account_information/v1/accounts/{accountId}/statements/pdf")
print("   ⚠️ Precisa de accountId - pulando por enquanto")

print("\n" + "="*80)
print("RESULTADO DO TESTE")
print("="*80)
print("""
Se o endpoint de contas retornou 200 ✅:
  → Suas credenciais TÊM acesso a extratos bancários!
  → Posso implementar download de PDFs de extrato
  
Se retornou 401 ❌:
  → Suas credenciais NÃO têm permissão para extratos
  → Só conseguimos acessar comprovantes de pagamento
  → Precisa solicitar novo scope/permissão ao Santander
""")
