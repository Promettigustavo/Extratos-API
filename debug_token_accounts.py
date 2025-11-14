"""Teste específico para debug do token e API accounts"""

import json
from buscar_extratos_bancarios import SantanderExtratosBancarios

print("="*80)
print("DEBUG: TESTE TOKEN E API ACCOUNTS")
print("="*80)

# Testar com CONDOLIVRE
try:
    print("1. 🔐 Testando obtenção de token...")
    cliente = SantanderExtratosBancarios('CONDOLIVRE FIDC')
    
    # Debug das credenciais
    print(f"   Client ID: {cliente.client_id}")
    print(f"   CNPJ: {cliente.cnpj}")
    print(f"   Cert Path: {cliente.cert_path}")
    print(f"   Key Path: {cliente.key_path}")
    
    # Tentar obter token
    token = cliente.obter_token_acesso()
    
    if token:
        print(f"✅ Token obtido: {token[:20]}...")
        
        print("\n2. 🏦 Testando listagem de contas...")
        contas = cliente.listar_contas()
        
        if contas:
            print(f"✅ {len(contas)} conta(s) encontrada(s)!")
            for i, conta in enumerate(contas, 1):
                print(f"   Conta {i}: {json.dumps(conta, indent=2)}")
        else:
            print("❌ Nenhuma conta encontrada!")
            print("   Possíveis causas:")
            print("   - Endpoint incorreto")
            print("   - Headers incorretos") 
            print("   - Escopo do token insuficiente")
            print("   - Credenciais sem permissão para contas")
    else:
        print("❌ Falha ao obter token!")
        print("   Verifique:")
        print("   - Client ID e Client Secret corretos")
        print("   - Certificados válidos e acessíveis")
        print("   - URL do endpoint de token")

except Exception as e:
    print(f"❌ Erro geral: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("CONCLUSÃO")
print("="*80)
print("Se o token é obtido mas não há contas:")
print("- Problema no endpoint /accounts")
print("- Problema no escopo do token") 
print("- Problema nos headers da requisição")
print("")
print("Se o token não é obtido:")
print("- Problema nas credenciais")
print("- Problema nos certificados")
print("="*80)