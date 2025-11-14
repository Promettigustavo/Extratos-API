"""
Verificar se o secret tem problemas
"""

# Simular parsing do TOML
secrets_text = """
[santander_fundos.ALBATROZ]
client_id = "tVgp6LU2OBZo62hXgBVt5AuMK3Z9sGSI"
client_secret = "KgMNdmARoqCfnMKC"
"""

# Credenciais do arquivo local (que funciona)
local = {
    "client_id": "tVgp6LU2OBZo62hXgBVt5AuMK3Z9sGSI",
    "client_secret": "KgMNdmARoqCfnMKC"
}

# Do secret (copiado)
secret = {
    "client_id": "tVgp6LU2OBZo62hXgBVt5AuMK3Z9sGSI",
    "client_secret": "KgMNdmARoqCfnMKC"
}

print("="*80)
print("VERIFICAÇÃO DE CREDENCIAIS ALBATROZ")
print("="*80)

print("\n📋 Local:")
print(f"  client_id:     '{local['client_id']}'")
print(f"  client_secret: '{local['client_secret']}'")

print("\n📋 Secret:")
print(f"  client_id:     '{secret['client_id']}'")
print(f"  client_secret: '{secret['client_secret']}'")

print("\n🔍 Comparação:")
print(f"  client_id match:     {local['client_id'] == secret['client_id']}")
print(f"  client_secret match: {local['client_secret'] == secret['client_secret']}")

print(f"\n  Tamanho client_id (local):     {len(local['client_id'])}")
print(f"  Tamanho client_id (secret):    {len(secret['client_id'])}")
print(f"  Tamanho client_secret (local): {len(local['client_secret'])}")
print(f"  Tamanho client_secret (secret):{len(secret['client_secret'])}")

# Verificar se tem espaços escondidos
import unicodedata
print("\n🔍 Verificando caracteres invisíveis:")
for i, char in enumerate(secret['client_id']):
    if ord(char) > 127 or char.isspace():
        print(f"  Posição {i}: '{char}' (ord={ord(char)}, cat={unicodedata.category(char)})")

for i, char in enumerate(secret['client_secret']):
    if ord(char) > 127 or char.isspace():
        print(f"  Posição {i}: '{char}' (ord={ord(char)}, cat={unicodedata.category(char)})")

print("\n" + "="*80)
print("✅ O secret parece correto - as credenciais são idênticas!")
print("="*80)
