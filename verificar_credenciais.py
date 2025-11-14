"""Teste para verificar quais credenciais estão sendo carregadas"""

print("="*80)
print("TESTE DE CARREGAMENTO DE CREDENCIAIS")
print("="*80)

# Testar config_credentials
try:
    print("\n1. Testando config_credentials.py...")
    from config_credentials import SANTANDER_FUNDOS as FUNDOS_CONFIG
    print(f"✅ config_credentials carregado")
    print(f"   Total de fundos: {len(FUNDOS_CONFIG)}")
    
    if 'CONDOLIVRE FIDC' in FUNDOS_CONFIG:
        condolivre = FUNDOS_CONFIG['CONDOLIVRE FIDC']
        print(f"   CONDOLIVRE FIDC encontrado:")
        print(f"   - client_id: {condolivre.get('client_id', 'FALTANDO')}")
        print(f"   - client_secret: {condolivre.get('client_secret', 'FALTANDO')[:8]}...")
        print(f"   - nome: {condolivre.get('nome', 'FALTANDO')}")
    else:
        print(f"   ❌ CONDOLIVRE FIDC não encontrado em config_credentials")
        print(f"   Fundos disponíveis: {list(FUNDOS_CONFIG.keys())[:5]}...")
        
except Exception as e:
    print(f"❌ Erro ao carregar config_credentials: {e}")
    import traceback
    traceback.print_exc()

# Testar credenciais_bancos como fallback
try:
    print("\n2. Testando credenciais_bancos.py (fallback)...")
    from credenciais_bancos import SANTANDER_FUNDOS as FUNDOS_BANCOS
    print(f"✅ credenciais_bancos carregado")
    print(f"   Total de fundos: {len(FUNDOS_BANCOS)}")
    
    if 'CONDOLIVRE FIDC' in FUNDOS_BANCOS:
        condolivre = FUNDOS_BANCOS['CONDOLIVRE FIDC']
        print(f"   CONDOLIVRE FIDC encontrado:")
        print(f"   - client_id: {condolivre.get('client_id', 'FALTANDO')}")
        print(f"   - client_secret: {condolivre.get('client_secret', 'FALTANDO')[:8]}...")
        print(f"   - nome: {condolivre.get('nome', 'FALTANDO')}")
    else:
        print(f"   ❌ CONDOLIVRE FIDC não encontrado em credenciais_bancos")
        
except Exception as e:
    print(f"❌ Erro ao carregar credenciais_bancos: {e}")
    import traceback
    traceback.print_exc()

# Testar o que buscar_extratos_bancarios está usando
try:
    print("\n3. Testando buscar_extratos_bancarios.py...")
    from buscar_extratos_bancarios import SANTANDER_FUNDOS as FUNDOS_USADO
    print(f"✅ buscar_extratos_bancarios carregado")
    print(f"   Total de fundos: {len(FUNDOS_USADO)}")
    
    if 'CONDOLIVRE FIDC' in FUNDOS_USADO:
        condolivre = FUNDOS_USADO['CONDOLIVRE FIDC']
        print(f"   CONDOLIVRE FIDC encontrado:")
        print(f"   - client_id: {condolivre.get('client_id', 'FALTANDO')}")
        print(f"   - client_secret: {condolivre.get('client_secret', 'FALTANDO')[:8]}...")
        print(f"   - nome: {condolivre.get('nome', 'FALTANDO')}")
    else:
        print(f"   ❌ CONDOLIVRE FIDC não encontrado no buscar_extratos_bancarios")
        print(f"   Fundos disponíveis: {list(FUNDOS_USADO.keys())[:5]}...")
        
except Exception as e:
    print(f"❌ Erro ao carregar buscar_extratos_bancarios: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("TESTE CONCLUÍDO")
print("="*80)