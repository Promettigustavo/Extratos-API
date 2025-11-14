# 🚀 Guia de Deploy no Streamlit Cloud

## 📋 Pré-requisitos

1. ✅ Conta no [GitHub](https://github.com)
2. ✅ Conta no [Streamlit Cloud](https://streamlit.io/cloud)
3. ✅ Certificados Santander (.pem files)
4. ✅ Credenciais dos fundos (client_id, client_secret)

## 🔧 Passo a Passo

### 1️⃣ Criar Repositório no GitHub

```bash
# No terminal, dentro da pasta do projeto
cd "c:\Users\GustavoPrometti\OneDrive - Kanastra\Documentos\Kanastra\Projeto Extratos"

# Inicializar Git
git init

# Adicionar todos os arquivos (exceto os do .gitignore)
git add .

# Commit inicial
git commit -m "🎉 Initial commit - Extratos Bancários Santander"

# Adicionar repositório remoto
git remote add origin https://github.com/Promettigustavo/Extratos-API.git

# Enviar para GitHub
git branch -M main
git push -u origin main
```

### 2️⃣ Configurar Secrets no Streamlit Cloud

1. Acesse [Streamlit Cloud](https://share.streamlit.io)
2. Clique em **"New app"**
3. Selecione o repositório: `Promettigustavo/Extratos-API`
4. Main file path: `dashboard_extratos.py`
5. Antes de fazer deploy, clique em **"Advanced settings"**
6. Na seção **"Secrets"**, cole o conteúdo adaptado do arquivo `.streamlit/secrets.toml.example`

**Formato dos Secrets:**

```toml
[santander]
fundos = '''
{
  "CONDOLIVRE FIDC": {
    "nome": "CONDOLIVRE FUNDO DE INVESTIMENTO EM DIREITOS CREDITORIOS",
    "cnpj": "42.317.295/0001-74",
    "client_id": "WUrgXgftrP3G9iZXXIqljABiFx9oRBUC",
    "client_secret": "e4FAtyTG6mbDKPFV"
  },
  "SEJA": {
    "nome": "SEJA FUNDO DE INVESTIMENTO EM DIREITOS CREDITORIOS",
    "cnpj": "24.987.402/0001-90",
    "client_id": "AUkiz79AzIzOWCmrPlTJG1mrallQDGTj",
    "client_secret": "2GYZYfWZMb0TVm4O"
  }
}
'''

[certificados]
cert_pem = '''
-----BEGIN CERTIFICATE-----
[COLE O CONTEÚDO COMPLETO DO ARQUIVO santander_cert.pem]
-----END CERTIFICATE-----
'''

key_pem = '''
-----BEGIN PRIVATE KEY-----
[COLE O CONTEÚDO COMPLETO DO ARQUIVO santander_key.pem]
-----END PRIVATE KEY-----
'''
```

### 3️⃣ Deploy

1. Clique em **"Deploy!"**
2. Aguarde o build (~2-3 minutos)
3. Pronto! Seu app estará no ar em: `https://[seu-app].streamlit.app`

## 🔐 Como Obter os Certificados

```bash
# No Windows PowerShell
cd "C:\Users\GustavoPrometti\Cert"

# Ver conteúdo do certificado
Get-Content santander_cert.pem

# Ver conteúdo da chave privada
Get-Content santander_key.pem
```

**Copie TODO o conteúdo** (incluindo as linhas `-----BEGIN...-----` e `-----END...-----`)

## ⚙️ Configurações Adicionais (Opcional)

### Adicionar Mais Fundos

Edite os secrets no Streamlit Cloud:
1. Settings > Secrets
2. Adicione novos fundos no JSON dentro de `[santander] fundos`

Exemplo:
```toml
[santander]
fundos = '''
{
  "FUNDO_1": { ... },
  "FUNDO_2": { ... },
  "NOVO_FUNDO": {
    "nome": "Nome Completo do Fundo",
    "cnpj": "XX.XXX.XXX/XXXX-XX",
    "client_id": "seu_client_id",
    "client_secret": "seu_client_secret"
  }
}
'''
```

### Atualizar Credenciais

1. Streamlit Cloud > Seu App > Settings
2. Secrets > Editar
3. Salvar (auto-redeploy)

## 🐛 Troubleshooting

### Erro: "Credenciais não encontradas"
- ✅ Verifique se os secrets estão configurados corretamente
- ✅ Confirme que o JSON está válido (use [jsonlint.com](https://jsonlint.com))

### Erro: "SSL Certificate Verify Failed"
- ✅ Verifique se colou os certificados completos (incluindo BEGIN/END)
- ✅ Não deve haver espaços extras ou quebras de linha incorretas

### Erro: "Invalid grant"
- ✅ Confirme client_id e client_secret corretos
- ✅ Verifique se os certificados correspondem às credenciais

### App muito lento
- ✅ Use períodos menores (7-15 dias ao invés de 90)
- ✅ Selecione menos fundos por vez
- ✅ Desmarque geração de PDF se não for necessário

## 🔄 Atualizar o App

```bash
# Fazer alterações no código
# ...

# Commit e push
git add .
git commit -m "✨ Descrição das mudanças"
git push

# O Streamlit Cloud fará redeploy automático
```

## 📊 Monitoramento

- **Logs**: Streamlit Cloud > Manage app > Logs
- **Métricas**: View logs para ver processamento em tempo real
- **Status**: Indicador verde = online, vermelho = erro

## 🔗 Links Úteis

- [Documentação Streamlit Cloud](https://docs.streamlit.io/streamlit-community-cloud)
- [Gerenciar Secrets](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
- [Git Basics](https://docs.github.com/pt/get-started/using-git/about-git)

## 📞 Suporte

Em caso de dúvidas:
1. Verifique os logs no Streamlit Cloud
2. Confira a documentação do projeto (README.md)
3. Entre em contato com o time Kanastra

---

**✅ Checklist Final**

- [ ] Repositório criado no GitHub
- [ ] Arquivos enviados (git push)
- [ ] Secrets configurados no Streamlit Cloud
- [ ] Certificados colados corretamente
- [ ] Deploy realizado com sucesso
- [ ] App testado e funcionando
- [ ] URL compartilhada com a equipe

🎉 **Parabéns! Seu app está no ar!**
