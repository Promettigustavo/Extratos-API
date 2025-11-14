# 📊 Extratos Bancários Santander - Kanastra

Sistema de automação para busca e geração de extratos bancários do Santander via Open Banking API para múltiplos fundos FIDC.

## 🚀 Funcionalidades

- ✅ Integração com API Open Banking Santander
- ✅ Suporte para múltiplos fundos FIDC
- ✅ Autenticação mTLS + OAuth2
- ✅ Exportação para Excel (.xlsx) com formatação Kanastra
- ✅ Geração de PDF no formato IBE (Internet Banking Empresarial)
- ✅ Paginação automática para grandes volumes
- ✅ Dashboard web interativo com Streamlit

## 📦 Tecnologias

- Python 3.11+
- Streamlit (Dashboard)
- Pandas + OpenPyXL (Excel)
- ReportLab (PDF)
- Requests (API calls)

## 🎨 Features do Dashboard

- **Seleção de Fundos**: Escolha múltiplos fundos para processar
- **Períodos Pré-configurados**: Hoje, Ontem, Últimos 7/15/30 dias, Este mês, Mês anterior
- **Período Personalizado**: Defina datas específicas
- **Formatos**: Excel (sempre) + PDF (opcional)
- **Visualização de Logs**: Acompanhe o processamento em tempo real
- **Download em Lote**: ZIP com todos os arquivos gerados

## 📊 Formato dos Arquivos

### Excel
- 6 colunas: Data, vazio, Histórico, Documento, Valor R$, Saldo R$
- Formatação com cores Kanastra
- Valores negativos em vermelho (apenas coluna Valor)
- Auto-ajuste de largura de colunas

### PDF
- Layout idêntico ao IBE Santander
- Cores oficiais: RGB(0.933, 0.114, 0.137) para destaques
- Fontes: LiberationSans 7pt (corpo), 18pt (título)
- Tabela de 6 colunas com todas as transações

## 🔐 Configuração de Credenciais

**Para uso no Streamlit Cloud**, configure os secrets em:
`Settings > Secrets` no painel do Streamlit Cloud

Formato:
```toml
[santander]
fundos = '''
{
  "FUNDO_ID": {
    "nome": "Nome do Fundo",
    "cnpj": "12.345.678/0001-90",
    "client_id": "seu_client_id",
    "client_secret": "seu_client_secret",
    "extrato_client_id": "extrato_client_id",
    "extrato_client_secret": "extrato_client_secret",
    "cert_path": "path/to/cert.pem",
    "key_path": "path/to/key.pem"
  }
}
'''

[certificados]
cert_pem = '''
-----BEGIN CERTIFICATE-----
...
-----END CERTIFICATE-----
'''

key_pem = '''
-----BEGIN PRIVATE KEY-----
...
-----END PRIVATE KEY-----
'''
```

## 🏃 Executar Localmente

```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar dashboard
streamlit run dashboard_extratos.py
```

Acesse: http://localhost:8501

## 📁 Estrutura do Projeto

```
.
├── dashboard_extratos.py          # Dashboard Streamlit principal
├── buscar_extratos_bancarios.py   # Core API (Balance & Statement)
├── buscar_comprovantes_santander.py # API Payment Receipts
├── credenciais_bancos.py          # Configuração de credenciais (local)
├── requirements.txt               # Dependências Python
├── .gitignore                     # Arquivos ignorados
└── README.md                      # Este arquivo
```

## 🔄 Fluxo de Processamento

1. **Autenticação**: Obtenção de token OAuth2 com certificados mTLS
2. **Listagem de Contas**: Busca contas bancárias do fundo
3. **Busca de Saldo**: Obtém saldo disponível, bloqueado e investido
4. **Busca de Transações**: Paginação automática (1000 registros/página)
5. **Exportação**: Gera Excel e/ou PDF conforme selecionado
6. **Agrupamento**: Organiza por data/fundo em estrutura de pastas

## 📝 APIs Utilizadas

### Balance and Statement
- Endpoint: `/transactions/{account_id}`
- Endpoint: `/balances/{account_id}`
- Retorna: JSON com transações e saldos

### Payment Receipts
- Endpoint: `/consult_payment_receipts/v1/payment_receipts`
- Endpoint: `/file_payment_receipt/{paymentId}`
- Retorna: PDFs de comprovantes

## 🎯 Casos de Uso

- **Contabilidade**: Exportação mensal de extratos para fechamento
- **Auditoria**: Verificação de movimentações em períodos específicos
- **Compliance**: Documentação de transações para regulatório
- **Gestão de Fundos**: Acompanhamento de múltiplos FIDCs

## 🐛 Troubleshooting

**Nenhuma transação encontrada?**
- Aumente o período de busca (ex: últimos 30 dias)
- Verifique se o fundo teve movimentações recentes

**Erro de autenticação?**
- Verifique se os certificados estão configurados
- Confirme se client_id e client_secret estão corretos
- Token tem validade de 900s (15 min)

**Arquivo não aparece?**
- Verificação busca arquivos dos últimos 15 minutos
- Confira a pasta de saída: `Extratos/YYYYMMDD/FUNDO/Santander/`

## 📄 Licença

© 2025 Kanastra - Todos os direitos reservados

## 👥 Autores

Desenvolvido por Kanastra para automação de processos financeiros.

---

**🔗 Links Úteis**
- [Streamlit Documentation](https://docs.streamlit.io)
- [Open Banking Brasil](https://openbankingbrasil.org.br)
- [Santander Developer Portal](https://developer.santander.com.br)
