# 🔐 Configuração de Autenticação

## ⚠️ IMPORTANTE: O dashboard possui um sistema básico de validação de e-mail que NÃO é seguro.

**Qualquer pessoa pode digitar qualquer e-mail @kanastra.com.br ou @liminedtvm.com e acessar o sistema.**

Para proteger corretamente o aplicativo, use uma das opções abaixo:

---

## ✅ Opção 1: Autenticação Nativa do Streamlit Cloud (RECOMENDADO)

Esta é a forma **mais segura** de proteger o aplicativo.

### Passos:

1. Acesse seu app no [Streamlit Cloud](https://share.streamlit.io/)
2. Clique em **Settings** (⚙️)
3. Vá em **Sharing**
4. Ative **"Viewer authentication"**
5. Escolha **"Restrict viewers"**
6. Adicione os e-mails autorizados:
   - `nome@kanastra.com.br`
   - `outro@kanastra.com.br`
   - `usuario@liminedtvm.com`
7. Clique em **Save**

### Como funciona:
- Usuários precisam fazer login com **Google OAuth**
- Apenas e-mails na lista autorizada podem acessar
- **100% seguro** - gerenciado pelo próprio Streamlit
- Não precisa alterar código

---

## 🔧 Opção 2: Secrets + Lista de E-mails (Desenvolvimento Local)

Para testar localmente ou em staging:

### Passos:

1. **No Streamlit Cloud:**
   - Vá em **Settings > Secrets**
   - Adicione:
   ```toml
   [auth]
   emails_permitidos = [
       "seu.email@kanastra.com.br",
       "outro.email@kanastra.com.br",
       "usuario@liminedtvm.com"
   ]
   ```

2. **Local (desenvolvimento):**
   - Copie `.streamlit/secrets.toml.example` para `.streamlit/secrets.toml`
   - Edite a seção `[auth]` com os e-mails autorizados
   - Adicione `.streamlit/secrets.toml` ao `.gitignore` (já está)

### Como funciona:
- Lista de e-mails em dropdown
- Apenas e-mails cadastrados aparecem
- **Modo desenvolvimento** - não tão seguro quanto OAuth

---

## 📋 Status Atual

**Sistema implementado no código:**
- ✅ Detecção automática de `st.experimental_user` (Streamlit Cloud OAuth)
- ✅ Validação de domínios (@kanastra.com.br, @liminedtvm.com)
- ✅ Fallback para secrets com lista de e-mails
- ✅ Interface de aviso quando autenticação não está configurada

**O que você precisa fazer:**
1. **Configurar "Viewer authentication" no Streamlit Cloud** (5 minutos)
2. Adicionar e-mails autorizados na lista
3. Pronto! Sistema 100% seguro 🔒

---

## 🚀 Deploy

Após configurar a autenticação:

```bash
git add .
git commit -m "docs: adicionar instruções de autenticação"
git push origin main
```

O Streamlit Cloud atualiza automaticamente em 2-3 minutos.

---

## 🆘 Troubleshooting

### "Autenticação não configurada" aparece no app
- Configure "Viewer authentication" em Settings > Sharing
- Ou adicione `[auth]` em Settings > Secrets

### Usuário autenticado mas acesso negado
- Verifique se o e-mail termina com @kanastra.com.br ou @liminedtvm.com
- Adicione o e-mail na lista de autorizados

### Modo desenvolvimento local não funciona
- Certifique-se que `.streamlit/secrets.toml` existe
- Verifique se a seção `[auth]` está presente
- Reinicie o Streamlit: `Ctrl+C` e `streamlit run dashboard_extratos.py`

---

## 📚 Documentação Oficial

- [Streamlit Authentication](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management)
- [Viewer Authentication](https://docs.streamlit.io/streamlit-community-cloud/get-started/share-your-app#restrict-viewers)
