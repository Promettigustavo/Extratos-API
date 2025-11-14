"""
Configuração de credenciais para Streamlit Cloud
Usa st.secrets quando disponível, caso contrário carrega do arquivo local
"""

import os
from pathlib import Path
import tempfile

# Tentar importar streamlit para usar secrets
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False
    st = None


def get_fundos_config():
    """
    Retorna configuração de fundos.
    Prioridade: Streamlit Secrets > Arquivo Local
    """
    # Se estiver no Streamlit Cloud, usar secrets
    if HAS_STREAMLIT and hasattr(st, 'secrets'):
        try:
            # Verificar se secrets estão configurados
            if "santander_fundos" not in st.secrets:
                raise KeyError("santander_fundos não encontrado nos secrets")
            
            # Criar diretório temporário para certificados
            cert_dir = Path(tempfile.gettempdir()) / "santander_certs"
            cert_dir.mkdir(exist_ok=True)
            
            # Salvar certificados em arquivos temporários
            cert_path = cert_dir / "santander_cert.pem"
            key_path = cert_dir / "santander_key.pem"
            
            # Processar certificados (remover \n e adicionar quebras de linha reais)
            cert_content = st.secrets["santander_fundos"]["cert_pem"].replace("\\n", "\n")
            key_content = st.secrets["santander_fundos"]["key_pem"].replace("\\n", "\n")
            
            cert_path.write_text(cert_content)
            key_path.write_text(key_content)
            
            # Verificar se arquivos foram criados
            print(f"📄 Certificado salvo: {cert_path} ({cert_path.stat().st_size} bytes)")
            print(f"🔑 Chave privada salva: {key_path} ({key_path.stat().st_size} bytes)")
            
            # Construir dicionário de fundos a partir dos secrets
            fundos = {}
            for key in st.secrets["santander_fundos"]:
                # Pular certificados
                if key in ["cert_pem", "key_pem"]:
                    continue
                
                fundo_config = dict(st.secrets["santander_fundos"][key])
                fundo_config["cert_path"] = str(cert_path)
                fundo_config["key_path"] = str(key_path)
                
                fundos[key] = fundo_config
            
            print(f"✅ {len(fundos)} fundos carregados dos secrets do Streamlit")
            return fundos
            
        except Exception as e:
            print(f"⚠️ Erro ao carregar secrets: {e}")
            print("📁 Tentando carregar credenciais locais...")
    
    # Fallback: carregar do arquivo local
    try:
        from credenciais_bancos import SANTANDER_FUNDOS
        print(f"✅ {len(SANTANDER_FUNDOS)} fundos carregados do arquivo local")
        return SANTANDER_FUNDOS
    except ImportError:
        raise Exception(
            "❌ Credenciais não encontradas!\n"
            "Configure os secrets no Streamlit Cloud ou crie o arquivo credenciais_bancos.py localmente."
        )


def get_pipefy_token():
    """
    Retorna token do Pipefy.
    Prioridade: Streamlit Secrets > Variável de Ambiente
    """
    if HAS_STREAMLIT and hasattr(st, 'secrets'):
        try:
            return st.secrets.get("pipefy", {}).get("api_token", "")
        except:
            pass
    
    return os.getenv("PIPEFY_API_TOKEN", "")


# Exportar configurações
SANTANDER_FUNDOS = get_fundos_config()
PIPEFY_API_TOKEN = get_pipefy_token()

# Importar classe de autenticação se disponível
try:
    from credenciais_bancos import SantanderAuth
except ImportError:
    # Criar versão simplificada se não existir
    import requests
    import base64
    from datetime import datetime, timedelta
    
    class SantanderAuth:
        """Classe de autenticação OAuth2 para Santander"""
        
        TOKEN_URL = "https://api-auth.santander.com.br/auth/oauth/v2/token"
        SCOPES = {
            "comprovantes": "open_banking_payment_receipts",
            "extratos": "open_banking_balances_statement"
        }
        
        def __init__(self, client_id: str, client_secret: str, cert_path: str, key_path: str, scope_type: str = "extratos"):
            self.client_id = client_id
            self.client_secret = client_secret
            self.cert_path = cert_path
            self.key_path = key_path
            self.scope = self.SCOPES.get(scope_type, self.SCOPES["extratos"])
            self.token = None
            self.token_expiry = None
        
        @classmethod
        def criar_por_fundo(cls, fundo_id: str, scope_type: str = "extratos"):
            """Factory method para criar autenticação a partir do ID do fundo"""
            if fundo_id not in SANTANDER_FUNDOS:
                raise ValueError(f"Fundo '{fundo_id}' não encontrado na configuração")
            
            fundo = SANTANDER_FUNDOS[fundo_id]
            
            # Usar credenciais específicas de extrato se disponíveis
            if scope_type == "extratos" and "extrato_client_id" in fundo:
                client_id = fundo["extrato_client_id"]
                client_secret = fundo["extrato_client_secret"]
            else:
                client_id = fundo["client_id"]
                client_secret = fundo["client_secret"]
            
            return cls(
                client_id=client_id,
                client_secret=client_secret,
                cert_path=fundo["cert_path"],
                key_path=fundo["key_path"],
                scope_type=scope_type
            )
        
        def _is_token_valid(self) -> bool:
            """Verifica se o token ainda é válido"""
            if not self.token or not self.token_expiry:
                return False
            return datetime.now() < self.token_expiry
        
        def obter_token(self) -> str:
            """Obtém ou renova o token OAuth2"""
            if self._is_token_valid():
                return self.token
            
            payload = {
                "grant_type": "client_credentials",
                "scope": self.scope
            }
            
            auth_string = f"{self.client_id}:{self.client_secret}"
            auth_b64 = base64.b64encode(auth_string.encode()).decode()
            
            headers = {
                "Authorization": f"Basic {auth_b64}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            # Debug: verificar se certificados existem
            from pathlib import Path
            cert_exists = Path(self.cert_path).exists()
            key_exists = Path(self.key_path).exists()
            print(f"🔐 Certificado existe: {cert_exists} ({self.cert_path})")
            print(f"🔑 Chave existe: {key_exists} ({self.key_path})")
            
            response = requests.post(
                self.TOKEN_URL,
                headers=headers,
                data=payload,
                cert=(self.cert_path, self.key_path),
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            self.token = data["access_token"]
            expires_in = data.get("expires_in", 900)
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in - 60)
            
            return self.token
