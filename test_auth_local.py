"""
Teste rápido de autenticação local com ALBATROZ
"""

from buscar_extratos_bancarios import SantanderExtratosBancarios

print("="*80)
print("TESTE DE AUTENTICAÇÃO - ALBATROZ")
print("="*80)

try:
    api = SantanderExtratosBancarios("ALBATROZ")
    
    token = api.obter_token_acesso()
    
    if token:
        print(f"\n✅ Token obtido com sucesso!")
        print(f"Token: {token[:20]}...")
        
        # Tentar listar contas
        contas = api.listar_contas()
        print(f"\n📋 Contas encontradas: {len(contas)}")
        for conta in contas:
            print(f"   • {conta.get('branchCode')} - {conta.get('number')}")
    else:
        print("\n❌ Falha ao obter token")
        
except Exception as e:
    print(f"\n❌ Erro: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
