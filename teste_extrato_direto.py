"""
Versão alternativa usando endpoint direto de extrato (bypass do erro 401 em /accounts)
Usa contas fixas conhecidas em vez de tentar listar contas automaticamente
"""

import requests
import json
import base64
from datetime import datetime, timedelta
import pandas as pd
import os
from pathlib import Path

# Tentar importar credenciais
try:
    try:
        from config_credentials import SANTANDER_FUNDOS
        HAS_CREDENCIAIS = True
    except ImportError:
        from credenciais_bancos import SANTANDER_FUNDOS
        HAS_CREDENCIAIS = True
except ImportError:
    HAS_CREDENCIAIS = False
    SANTANDER_FUNDOS = {}
    print("⚠️  Credenciais não disponíveis")

# Configuração para Streamlit Cloud vs local
if os.path.exists('/tmp'):
    # Streamlit Cloud
    CERT_PATH = "/tmp/santander_certs/santander_cert.pem"
    KEY_PATH = "/tmp/santander_certs/santander_key.pem"
else:
    # Local
    CERT_PATH = r"C:\Users\GustavoPrometti\Cert\santander_cert.pem"
    KEY_PATH = r"C:\Users\GustavoPrometti\Cert\santander_key.pem"

BANK_ID = "90400888000142"  # CNPJ do Santander

# Contas conhecidas (baseado em extratos anteriores)
CONTAS_CONHECIDAS = {
    "CONDOLIVRE FIDC": [
        {"agencia": "2271", "conta": "130137784"},
        {"agencia": "2271", "conta": "130176356"}
    ],
}


class SantanderExtratosDireto:
    """Busca extratos usando endpoint direto, evitando erro 401 em /accounts"""
    
    def __init__(self, fundo_config):
        self.client_id = fundo_config["client_id"]
        self.client_secret = fundo_config["client_secret"] 
        self.cnpj = fundo_config["cnpj"]
        self.nome = fundo_config["nome"]
        self.cert_path = CERT_PATH
        self.key_path = KEY_PATH
        self.token = None
        self.token_expira = None
        
    def obter_token(self):
        """Obtém token OAuth2"""
        print(f"🔑 Obtendo token OAuth2...")
        
        url = "https://trust-open.api.santander.com.br/auth/oauth/v2/token"
        
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_b64 = base64.b64encode(auth_string.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "client_credentials",
            "scope": "account_information.balances.read account_information.transactions.read"
        }
        
        try:
            response = requests.post(
                url, 
                headers=headers, 
                data=data, 
                cert=(self.cert_path, self.key_path),
                timeout=30
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data.get("access_token")
                expires_in = token_data.get("expires_in", 900)
                self.token_expira = datetime.now() + timedelta(seconds=expires_in - 60)
                
                print(f"✅ Token obtido com sucesso")
                return True
            else:
                print(f"❌ Erro ao obter token: {response.status_code}")
                print(f"   Resposta: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erro na requisição: {e}")
            return False
    
    def buscar_extrato_conta(self, agencia, conta, data_inicio, data_fim):
        """Busca extrato direto de uma conta específica"""
        print(f"📊 Buscando extrato para {agencia}.{conta}...")
        
        if not self.token:
            return None
            
        # Endpoint direto para extrato
        url = f"https://trust-open.api.santander.com.br/bank_account_information/v1/banks/{BANK_ID}/statements"
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "X-Application-Key": self.client_id,
            "X-CNPJ": self.cnpj
        }
        
        params = {
            "accountNumber": conta,
            "branchCode": agencia,
            "initialDate": data_inicio,
            "finalDate": data_fim
        }
        
        try:
            response = requests.get(
                url,
                headers=headers,
                params=params,
                cert=(self.cert_path, self.key_path),
                timeout=60
            )
            
            print(f"   📡 Resposta: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                print(f"   ❌ Erro: {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ Erro na requisição: {e}")
            return None


def main():
    """Execução principal - testa CONDOLIVRE com contas conhecidas"""
    print("="*80)
    print("BUSCA DE EXTRATOS - MÉTODO DIRETO (Bypass 401)")
    print("="*80)
    
    if not HAS_CREDENCIAIS:
        print("❌ Credenciais não disponíveis")
        return
        
    # Testar só CONDOLIVRE primeiro
    fundo_id = "CONDOLIVRE FIDC" 
    if fundo_id not in SANTANDER_FUNDOS:
        print(f"❌ Fundo {fundo_id} não encontrado")
        return
        
    fundo_config = SANTANDER_FUNDOS[fundo_id]
    
    print(f"🏦 Processando: {fundo_config['nome']}")
    print(f"   CNPJ: {fundo_config['cnpj']}")
    
    # Criar cliente
    cliente = SantanderExtratosDireto(fundo_config)
    
    # Obter token
    if not cliente.obter_token():
        print("❌ Falha na autenticação")
        return
        
    # Período de teste
    data_fim = datetime.now().strftime("%Y-%m-%d")
    data_inicio = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    print(f"📅 Período: {data_inicio} a {data_fim}")
    
    # Buscar extratos das contas conhecidas
    contas = CONTAS_CONHECIDAS.get(fundo_id, [])
    print(f"🔍 Contas conhecidas: {len(contas)}")
    
    for conta_info in contas:
        agencia = conta_info["agencia"]
        conta = conta_info["conta"]
        
        print(f"\n🏪 Processando conta {agencia}.{conta}")
        
        extrato = cliente.buscar_extrato_conta(agencia, conta, data_inicio, data_fim)
        
        if extrato:
            print(f"✅ Extrato obtido com sucesso!")
            
            # Mostrar algumas transações como exemplo
            if "data" in extrato and "transactions" in extrato["data"]:
                transacoes = extrato["data"]["transactions"]
                print(f"   💰 Transações encontradas: {len(transacoes)}")
                
                # Mostrar primeiras transações
                for i, tx in enumerate(transacoes[:3]):
                    valor = tx.get("amount", {}).get("value", 0)
                    descricao = tx.get("description", "N/A")
                    data_tx = tx.get("date", "N/A")
                    print(f"   {i+1}. {data_tx} - R$ {valor} - {descricao}")
                    
                if len(transacoes) > 3:
                    print(f"   ... e mais {len(transacoes)-3} transações")
                    
            else:
                print(f"   📋 Resposta: {json.dumps(extrato, indent=2)[:500]}")
        else:
            print(f"❌ Falha ao obter extrato")


if __name__ == "__main__":
    main()