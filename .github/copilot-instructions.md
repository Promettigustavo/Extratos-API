# Projeto Extratos - AI Coding Instructions

## Project Overview
Sistema Python para automação de extratos e comprovantes bancários do Santander para múltiplos fundos FIDC (Fundos de Investimento em Direitos Creditórios). Integra com APIs Open Banking do Santander usando autenticação mTLS + OAuth2.

## Architecture & Core Concepts

### 1. Multi-Fund System
- **Central Registry**: `credenciais_bancos.py` contém `SANTANDER_FUNDOS` (dicionário com ~100+ fundos)
- Cada fundo tem: `nome`, `cnpj`, `client_id`, `client_secret`, `cert_path`, `key_path`
- Alguns fundos têm credenciais adicionais: `extrato_client_id`, `extrato_client_secret` para API Balance and Statement

### 2. Authentication Pattern
- **Class**: `SantanderAuth` (em `credenciais_bancos.py`)
- **Factory Method**: `SantanderAuth.criar_por_fundo(fundo_id)` é o padrão preferido
- **mTLS Required**: Todas as chamadas API exigem certificado PEM em `C:\Users\GustavoPrometti\Cert\`
- **Token Caching**: Tokens salvos em `config/santander_token_{fundo_id}.json`, validados antes do uso
- **Token Validation**: Use `_is_token_valid()` antes de cada request (auto-renova se necessário)

### 3. API Modules & Endpoints
Three distinct Santander API products:

**A. Balance and Statement** (`buscar_extratos_bancarios.py`)
- Class: `SantanderExtratosBancarios`
- Endpoints: `/transactions/{account_id}`, `/balances/{account_id}`
- Retorna JSON com transações e saldos
- ⚠️ **NÃO possui endpoint de PDF** - apenas dados JSON

**B. Payment Receipts** (`buscar_comprovantes_santander.py`)
- Class: `SantanderComprovantes`
- Endpoint principal: `/consult_payment_receipts/v1/payment_receipts`
- Baixa PDFs de comprovantes via `/file_payment_receipt/{paymentId}`
- Pasta destino: `./Comprovantes/`

**C. Bank Account Information** (`buscar_extratos.py`)
- Class: `SantanderExtratos`
- Endpoint: `/bank_account_information/v1/banks/{bank_id}/statements`
- Aceita `SantanderAuth` como dependência injetada

### 4. Data Export Pattern
**Excel Output**: Formato padrão é openpyxl com formatação específica:
- Valores monetários: `"R$ {x:,.2f}"` com separadores BR (ponto para milhares, vírgula para decimais)
- Colunas sempre incluem: `Fundo`, `Agência`, `Conta` no início
- Naming: `extrato_{fundo_id}_{branch}_{account}_{timestamp}.xlsx`
- Pasta padrão: `./Extratos/YYYYMMDD/{FUNDO_NOME}/Santander/`

**PDF Output**: Salvos em `./Comprovantes/` com nome original da API

## Critical Workflows

### Running Scripts
```powershell
# Buscar extratos (últimos 7 dias por padrão)
python buscar_extratos_bancarios.py

# Buscar comprovantes de período específico
python buscar_extrato_contas.py  # Interativo

# Testar credenciais de um fundo
python testar_credenciais_extrato.py
```

### Adding New Fund
1. Adicionar entrada em `SANTANDER_FUNDOS` em `credenciais_bancos.py`
2. Incluir `client_id`, `client_secret`, `cnpj`, `nome`
3. Para extratos: adicionar `extrato_client_id`, `extrato_client_secret`
4. Certificados são compartilhados entre fundos (mesmos arquivos PEM)

## Project-Specific Conventions

### Import Pattern
```python
# Sempre usar import condicional para compatibilidade
try:
    from credenciais_bancos import SantanderAuth, SANTANDER_FUNDOS
    HAS_CREDENCIAIS = True
except ImportError:
    HAS_CREDENCIAIS = False
    SantanderAuth = None
```

### Error Handling
- Console output usa emojis: ✅ sucesso, ❌ erro, ⚠️ aviso, 📋 lista, 💰 saldo, 📊 transações
- Print separadores: `"="*80` para seções principais, `"-"*80` para subseções
- Sempre include `traceback.print_exc()` em except blocks

### Date Handling
- Formato interno: `datetime` objects
- Formato API: `"YYYY-MM-DD"` strings
- Default period: 7 dias atrás até hoje
- API limit: máximo 30 dias por request (validation não implementada)

### Account Identifiers
- `branch_code`: código da agência (ex: "2271")
- `account_number`: número da conta (ex: "130137784")
- `account_id`: formato composto `"{branch_code}.{account_number}"` usado nos endpoints

## File Organization
- **Core modules**: `credenciais_bancos.py`, `buscar_*.py`
- **Test scripts**: `testar_*.py`, `exemplo_*.py`
- **Utilities**: `verificar_layout_excel.py`, `comparar_layouts.py`
- **Output**: `Extratos/`, `Comprovantes/`
- **Backup**: `*_backup.py` files são versões antigas (não usar)

## Integration Points

### Pipefy (Partial)
- Token defined: `PIPEFY_API_TOKEN` em `credenciais_bancos.py`
- Integration code incomplete/not used in current scripts
- Consider for future automation

### External Dependencies
- `requests`: HTTP client (com cert parameter para mTLS)
- `pandas`: Excel export via `to_excel(..., engine='openpyxl')`
- `openpyxl`: Excel formatting e verificação de layout
- `pathlib.Path`: Preferred over `os.path` para manipulação de caminhos

## Common Pitfalls

1. **API Confusion**: Balance and Statement ≠ Payment Receipts (diferentes produtos, diferentes credenciais)
2. **Certificate Required**: TODAS as requests precisam `cert=(cert_path, key_path)` - falha com SSL error se omitido
3. **Token Expiration**: Sempre verificar `_is_token_valid()` antes de usar token
4. **Account ID Format**: Endpoints transactions usam `account_id` composto, não separado
5. **Encoding**: Scripts usam UTF-8 explicitamente (`codecs.getwriter("utf-8")`) para output console

## Key Files Reference
- `credenciais_bancos.py` (708 lines): Auth + fund registry
- `buscar_extratos_bancarios.py` (422 lines): Main statement fetching
- `buscar_comprovantes_santander.py` (850 lines): Payment receipts download
- `verificar_layout_excel.py`: Template para validar formato Excel output
