"""
Script para buscar extratos bancários via API Santander
Busca transações de contas bancárias para todos os fundos configurados
Salva em Excel com formatação de valores em R$

IMPORTANTE: Este script usa a API "Balance and Statement" do Santander que:
- ✅ Retorna transações em JSON (via endpoint /transactions)
- ✅ Retorna saldo em tempo real
- ❌ NÃO possui endpoint para download de PDF de extrato
- ⚠️  Requer credenciais específicas diferentes das de "Payment Receipts"
"""

import requests
import json
import base64
from datetime import datetime, timedelta
import pandas as pd
import os
from pathlib import Path
import uuid
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

# Controle de verbosidade (pode ser alterado externamente)
VERBOSE = True


def log(mensagem):
    """Print condicional baseado em VERBOSE"""
    if VERBOSE:
        print(mensagem)


# Tentar importar credenciais - suporta Streamlit Cloud e local
try:
    # Primeiro tenta config_credentials (suporta Streamlit Secrets)
    try:
        from config_credentials import SANTANDER_FUNDOS
        HAS_CREDENCIAIS = True
    except ImportError:
        # Fallback para credenciais locais
        from credenciais_bancos import SANTANDER_FUNDOS
        HAS_CREDENCIAIS = True
except ImportError:
    HAS_CREDENCIAIS = False
    SANTANDER_FUNDOS = {}
    log("⚠️  Credenciais não disponíveis")

# Configurações para extrato
CERT_PATH = r"C:\Users\GustavoPrometti\Cert\santander_cert.pem"
KEY_PATH = r"C:\Users\GustavoPrometti\Cert\santander_key.pem"
BANK_ID = "90400888000142"  # CNPJ do Santander


class SantanderExtratosBancarios:
    """Classe para buscar extratos bancários via API Santander"""
    
    def __init__(self, fundo_id):
        """Inicializa com credenciais do fundo"""
        if fundo_id not in SANTANDER_FUNDOS:
            raise ValueError(f"Fundo {fundo_id} não configurado")
        
        creds = SANTANDER_FUNDOS[fundo_id]
        
        # Usar client_id e client_secret padrão (mesmos para todas as APIs)
        if "client_id" not in creds or "client_secret" not in creds:
            raise ValueError(f"Fundo {fundo_id} não possui credenciais configuradas")
        
        if not creds["client_id"] or not creds["client_secret"]:
            raise ValueError(f"Fundo {fundo_id} possui credenciais vazias")
        
        self.fundo_id = fundo_id
        self.fundo_nome = creds.get('nome', fundo_id)  # Nome do fundo para usar nos arquivos
        self.creds = creds  # Armazenar credenciais completas
        self.client_id = creds["client_id"]
        self.client_secret = creds["client_secret"]
        self.cnpj = creds["cnpj"]
        self.cert_path = creds.get("cert_path", CERT_PATH)
        self.key_path = creds.get("key_path", KEY_PATH)
        self.token = None
        self.token_expira = None
        
        # Debug: mostrar caminhos dos certificados
        log(f"🔐 Certificados configurados:")
        log(f"   cert_path: {self.cert_path}")
        log(f"   key_path: {self.key_path}")
        
        # Contas conhecidas como fallback para erro 401 em /accounts
        self.contas_conhecidas = {
            "CONDOLIVRE FUNDO DE INVESTIMENTO EM DIREITOS CREDITORIOS": [
                {"branchCode": "2271", "number": "130137784"},
                {"branchCode": "2271", "number": "130176356"}
            ],
            # Adicionar outras conforme necessário
        }
        
    def obter_contas_conhecidas(self):
        """
        Retorna contas conhecidas para o fundo atual
        Usado como fallback quando /accounts retorna 401
        """
        return self.contas_conhecidas.get(self.fundo_nome, [])
        
    def obter_token_acesso(self):
        """Obtém token OAuth2 para autenticação"""
        # Verificar se token ainda é válido
        if self.token and self.token_expira and datetime.now() < self.token_expira:
            return self.token
        
        log(f"\n🔑 Obtendo token OAuth2 para fundo {self.fundo_id}...")
        log(f"   Client ID: {self.client_id[:10]}...")
        log(f"   CNPJ: {self.cnpj}")
        
        # URL que funciona (testado localmente e no Streamlit Cloud)
        url = "https://trust-open.api.santander.com.br/auth/oauth/v2/token"
        log(f"   🔗 URL do token: {url}")
        
        # Autenticação usando Basic Auth (padrão OAuth2)
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_b64 = base64.b64encode(auth_string.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "client_credentials",
            "scope": "open_banking_balances_statement"
        }
        
        log(f"   📊 Escopo solicitado: {data['scope']}")
        
        try:
            log(f"   🚀 Enviando requisição de token...")
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
                
                log(f"✅ Token obtido com sucesso (válido por {expires_in}s)")
                log(f"   Token: {self.token[:20] if self.token else 'NONE'}...")
                
                # Verificar se token tem o escopo necessário
                scope_recebido = token_data.get("scope", "")
                log(f"   📋 Escopo recebido: {scope_recebido}")
                if "account" not in scope_recebido.lower():
                    log(f"   ⚠️ AVISO: Token pode não ter permissão para accounts!")
                
                return self.token
            else:
                log(f"❌ Erro ao obter token: {response.status_code}")
                log(f"   Resposta: \n    {json.dumps(response.json(), indent=6) if response.content else 'Vazio'}")
                return None
                
        except Exception as e:
            log(f"❌ Exceção ao obter token: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def listar_contas(self):
        """Lista todas as contas bancárias do fundo"""
        token = self.obter_token_acesso()
        if not token:
            return []
        
        log(f"\n🏦 Listando contas bancárias do fundo {self.fundo_id}...")
        
        # Debug: verificar certificados
        from pathlib import Path
        cert_exists = Path(self.cert_path).exists()
        key_exists = Path(self.key_path).exists()
        if not cert_exists or not key_exists:
            log(f"⚠️  Certificado existe: {cert_exists} ({self.cert_path})")
            log(f"⚠️  Chave existe: {key_exists} ({self.key_path})")
        
        # Endpoint correto para listar contas - inclui /banks/{BANK_ID}/ no path
        url = f"https://trust-open.api.santander.com.br/bank_account_information/v1/banks/{BANK_ID}/accounts"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Application-Key": self.client_id
        }
        
        # Parâmetros corretos conforme collection
        params = {
            "_offset": "1",
            "_limit": "50"
        }
        
        # Log detalhado para debug
        log(f"   🔗 URL: {url}")
        log(f"   🗂️ Headers: X-Application-Key={self.client_id[:10]}..., X-CNPJ={self.cnpj}")
        log(f"   📊 Params: {params}")
        
        try:
            log(f"   🚀 Fazendo requisição para API...")
            response = requests.get(
                url,
                headers=headers,
                params=params,
                cert=(self.cert_path, self.key_path),
                timeout=30
            )
            
            log(f"   📡 Resposta recebida - Status: {response.status_code}")
            log(f"   📏 Tamanho da resposta: {len(response.text)} caracteres")
            
            if response.status_code == 200:
                data = response.json()
                
                # Log da resposta completa para debug
                log(f"   📋 DEBUG - Resposta completa da API:")
                log(f"   {json.dumps(data, indent=2)[:1000]}...")
                
                # Tentar diferentes estruturas de resposta
                contas = []
                
                # Estrutura 1: data.accounts (nova API)
                if "data" in data and isinstance(data["data"], dict) and "accounts" in data["data"]:
                    contas = data["data"]["accounts"]
                    log(f"   ✅ Estrutura 1 (data.accounts): {len(contas)} contas")
                
                # Estrutura 2: data como lista direta
                elif "data" in data and isinstance(data["data"], list):
                    contas = data["data"]
                    log(f"   ✅ Estrutura 2 (data lista): {len(contas)} contas")
                
                # Estrutura 3: _content (API antiga)
                elif "_content" in data:
                    contas = data["_content"]
                    log(f"   ✅ Estrutura 3 (_content): {len(contas)} contas")
                
                # Estrutura 4: accounts direto
                elif "accounts" in data:
                    contas = data["accounts"]
                    log(f"   ✅ Estrutura 4 (accounts direto): {len(contas)} contas")
                
                else:
                    log(f"   ❌ Estrutura desconhecida na resposta!")
                    log(f"   Keys disponíveis: {list(data.keys())}")
                
                log(f"✅ {len(contas)} conta(s) encontrada(s)")
                
                # Debug: mostrar resposta completa se não encontrar contas
                if len(contas) == 0:
                    log(f"   🔍 ATENÇÃO: Nenhuma conta retornada pela API!")
                    log(f"   Resposta completa: {json.dumps(data, indent=2)}")
                
                for conta in contas:
                    branch_code = conta.get('branchCode') or conta.get('agencyCode')
                    account_number = conta.get('number') or conta.get('accountNumber')
                    log(f"   • Agência: {branch_code} - Conta: {account_number}")
                    
                    # Garantir que temos os campos necessários
                    if not conta.get('branchCode') and conta.get('agencyCode'):
                        conta['branchCode'] = conta['agencyCode']
                    if not conta.get('number') and conta.get('accountNumber'):
                        conta['number'] = conta['accountNumber']
                
                return contas
            else:
                log(f"❌ Erro ao listar contas: {response.status_code}")
                log(f"   URL chamada: {url}")
                log(f"   Headers enviados: {json.dumps({k: v[:20] + '...' if len(v) > 20 else v for k, v in headers.items()}, indent=2)}")
                log(f"   Parâmetros: {params}")
                log(f"   Resposta completa: {response.text}")
                
                # ✅ FALLBACK: Se erro 401, usar contas conhecidas
                if response.status_code == 401:
                    log(f"   🔄 Tentando fallback para contas conhecidas...")
                    contas_conhecidas = self.obter_contas_conhecidas()
                    if contas_conhecidas:
                        log(f"   ✅ Usando {len(contas_conhecidas)} conta(s) conhecida(s)")
                        for conta in contas_conhecidas:
                            log(f"   • Agência: {conta['branchCode']} - Conta: {conta['number']}")
                        return contas_conhecidas
                    else:
                        log(f"   ❌ Nenhuma conta conhecida configurada para {self.fundo_nome}")
                
                # Tentar interpretar erro
                try:
                    error_data = response.json()
                    if "errors" in error_data:
                        for error in error_data["errors"]:
                            log(f"   🚨 Erro API: {error.get('title', 'N/A')} - {error.get('detail', 'N/A')}")
                except:
                    pass
                
                return []
                
        except Exception as e:
            log(f"❌ Exceção ao listar contas: {e}")
            log(f"   URL tentada: {url}")
            log(f"   Certificados: cert={self.cert_path}, key={self.key_path}")
            log(f"   Client ID: {self.client_id[:10]}...")
            log(f"   CNPJ: {self.cnpj}")
            import traceback
            traceback.print_exc()
            return []
    
    def buscar_transacoes(self, branch_code, account_number, data_inicial=None, data_final=None, limite=1000):
        """
        Busca TODAS as transações (extrato) de uma conta específica usando paginação
        
        Args:
            branch_code: Código da agência
            account_number: Número da conta
            data_inicial: Data inicial (datetime ou None para 7 dias atrás)
            data_final: Data final (datetime ou None para hoje)
            limite: Número de transações por página (padrão 1000)
        
        Returns:
            Lista de transações ou lista vazia em caso de erro
        """
        token = self.obter_token_acesso()
        if not token:
            return []
        
        # Definir período padrão se não fornecido
        if not data_final:
            data_final = datetime.now()
        if not data_inicial:
            data_inicial = data_final - timedelta(days=7)
        
        log(f"\n📊 Buscando transações da conta {branch_code}.{account_number}...")
        log(f"   Período: {data_inicial.strftime('%d/%m/%Y')} a {data_final.strftime('%d/%m/%Y')}")
        
        # Formatar account_id conforme API: AAAA.CCCCCCCCCCCC (4 dígitos agência + 12 dígitos conta)
        branch_formatted = str(branch_code).zfill(4)  # Preenche com zeros à esquerda até 4 dígitos
        account_formatted = str(account_number).zfill(12)  # Preenche com zeros à esquerda até 12 dígitos
        account_id = f"{branch_formatted}.{account_formatted}"
        
        log(f"   🔢 Account ID formatado: {account_id}")
        
        # Usar endpoint de statements com account_id no formato agencia.conta
        url = f"https://trust-open.api.santander.com.br/bank_account_information/v1/banks/{BANK_ID}/statements/{account_id}"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Application-Key": self.client_id
        }
        
        # Buscar todas as transações com paginação
        todas_transacoes = []
        offset = 0  # Índice inicial (não página)
        
        try:
            while True:
                params = {
                    "initialDate": data_inicial.strftime("%Y-%m-%d"),
                    "finalDate": data_final.strftime("%Y-%m-%d"),
                    "_limit": str(limite),
                    "_offset": str(offset)  # offset em registros, não páginas
                }
                
                log(f"   🔍 Buscando: offset={offset}, limit={limite}")
                
                response = requests.get(
                    url,
                    headers=headers,
                    params=params,
                    cert=(self.cert_path, self.key_path),
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # DEBUG: Mostrar resposta completa na primeira requisição
                    if offset == 0:
                        log(f"   📋 DEBUG - Resposta da API (offset 0):")
                        log(f"   Keys disponíveis: {list(data.keys())}")
                        log(f"   Resposta completa: {str(data)[:1000]}")
                    
                    transacoes_pagina = data.get("_content", [])
                    
                    if not transacoes_pagina:
                        # Não há mais transações
                        log(f"   ⚠️ Offset {offset} retornou 0 transações. Encerrando busca.")
                        break
                    
                    todas_transacoes.extend(transacoes_pagina)
                    pagina_num = (offset // limite) + 1
                    log(f"   Página {pagina_num} (offset {offset}): {len(transacoes_pagina)} transações | Total: {len(todas_transacoes)}")
                    
                    # DEBUG: Mostrar primeira transação
                    if offset == 0 and len(transacoes_pagina) > 0:
                        log(f"   📋 Exemplo de transação: {transacoes_pagina[0]}")
                    
                    # Verificar se há próxima página
                    links = data.get("_links", {})
                    if "next" not in links:
                        log(f"   ✅ Última página alcançada (sem link 'next')")
                        break
                    
                    # Incrementar offset pelo número de registros, não por 1
                    offset += limite
                    
                    # Segurança: evitar loop infinito
                    if offset > 100000:  # Limite de segurança: 100k transações
                        log(f"   ⚠️ Limite de segurança atingido (100k transações)")
                        break
                else:
                    log(f"❌ Erro ao buscar transações (offset {offset}): {response.status_code}")
                    log(f"   Resposta: {response.text[:500]}")
                    break
            
            log(f"✅ Total de {len(todas_transacoes)} transação(ões) encontrada(s)")
            return todas_transacoes
                
        except Exception as e:
            log(f"❌ Exceção ao buscar transações: {e}")
            import traceback
            traceback.print_exc()
            return todas_transacoes if todas_transacoes else []
    
    def buscar_saldo(self, branch_code, account_number):
        """
        Busca saldo de uma conta específica
        
        Args:
            branch_code: Código da agência
            account_number: Número da conta
        
        Returns:
            Dicionário com informações de saldo ou None
        """
        token = self.obter_token_acesso()
        if not token:
            return None
        
        log(f"\n💰 Buscando saldo da conta {branch_code}.{account_number}...")
        
        # Formatar account_id conforme API: AAAA.CCCCCCCCCCCC (4 dígitos agência + 12 dígitos conta)
        branch_formatted = str(branch_code).zfill(4)
        account_formatted = str(account_number).zfill(12)
        account_id = f"{branch_formatted}.{account_formatted}"
        
        log(f"   🔢 Account ID formatado: {account_id}")
        
        url = f"https://trust-open.api.santander.com.br/bank_account_information/v1/banks/{BANK_ID}/balances/{account_id}"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Application-Key": self.client_id
        }
        
        try:
            response = requests.get(
                url,
                headers=headers,
                cert=(self.cert_path, self.key_path),
                timeout=30
            )
            
            if response.status_code == 200:
                saldo_data = response.json()
                disponivel = float(saldo_data.get("availableAmount", 0))
                bloqueado = float(saldo_data.get("blockedAmount", 0))
                investido = float(saldo_data.get("automaticallyInvestedAmount", 0))
                
                log(f"✅ Saldo disponível: R$ {disponivel:,.2f}")
                log(f"   Bloqueado: R$ {bloqueado:,.2f}")
                log(f"   Investido automaticamente: R$ {investido:,.2f}")
                
                return saldo_data
            else:
                log(f"❌ Erro ao buscar saldo: {response.status_code}")
                log(f"   Resposta: {response.text[:500]}")
                return None
                
        except Exception as e:
            log(f"❌ Exceção ao buscar saldo: {e}")
            return None
    
    def exportar_transacoes_excel(self, transacoes, branch_code, account_number, pasta_saida=None, saldo_info=None):
        """
        Exporta transações para arquivo Excel no formato Santander IBE
        
        Args:
            transacoes: Lista de transações (pode ser vazia)
            branch_code: Código da agência
            account_number: Número da conta
            pasta_saida: Pasta para salvar (padrão: diretório atual)
            saldo_info: Informações de saldo (opcional)
        
        Returns:
            Caminho do arquivo gerado ou None
        """
        num_transacoes = len(transacoes) if transacoes else 0
        log(f"\n📝 Exportando {num_transacoes} transação(ões) para Excel...")
        
        # Definir pasta de saída
        if not pasta_saida:
            pasta_saida = os.getcwd()
        
        # Nome do arquivo no formato: exportar-Santander - Extrato DD de MMMM de YYYY-AGENCIA-CONTA.xlsx
        from datetime import datetime
        import locale
        try:
            locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
        except:
            try:
                locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
            except:
                pass
        
        data_hoje = datetime.now()
        data_formatada = data_hoje.strftime("%d de %B de %Y")
        # Incluir nome do fundo no arquivo para facilitar organização
        filename = f"exportar-Santander - Extrato {data_formatada}-{self.fundo_nome}-{branch_code}-{account_number}.xlsx"
        filepath = os.path.join(pasta_saida, filename)
        
        # Criar estrutura de dados no formato IBE
        # Linha 1: AGENCIA | codigo_agencia | CONTA | numero_conta | vazio | vazio
        # Linha 2: vazio (em todas)
        # Linha 3: Data | vazio | Histórico | Documento | Valor (R$) | Saldo (R$)
        # Linha 4+: dados das transações
        
        dados = []
        
        # Linha 1: Cabeçalho com agência e conta
        dados.append(['AGENCIA', branch_code, 'CONTA', account_number, None, None])
        
        # Linha 2: Linha em branco
        dados.append([None, None, None, None, None, None])
        
        # Linha 3: Headers das colunas
        dados.append(['Data', None, 'Histórico', 'Documento', 'Valor (R$)', 'Saldo (R$)'])
        
        # Calcular saldo inicial e processar transações
        saldo = 0
        
        # Adicionar linha de saldo anterior
        if transacoes:
            primeira_data = transacoes[0].get('transactionDate', '')
            dados.append([primeira_data, None, 'SALDO ANTERIOR', None, None, saldo])
        
        # Debug: mostrar se há transações
        log(f"📝 Processando {len(transacoes)} transações para Excel...")
        
        # Adicionar transações
        for trans in transacoes:
            data = trans.get('transactionDate', '')
            historico = trans.get('transactionName', '')
            documento = trans.get('documentNumber', '')
            valor = float(trans.get('amount', 0))
            tipo = trans.get('creditDebitType', '')
            
            # Ajustar sinal do valor (crédito positivo, débito negativo)
            if tipo == 'DEBITO':
                valor = -abs(valor)
            else:
                valor = abs(valor)
            
            saldo += valor
            
            # Formatar data (DD/MM/AAAA)
            if data and len(data) >= 10:
                try:
                    data_obj = datetime.strptime(data[:10], '%Y-%m-%d')
                    data = data_obj.strftime('%d/%m/%Y')
                except:
                    pass
            
            dados.append([data, None, historico, documento, valor, saldo])
        
        # DEBUG: Mostrar quantas linhas foram adicionadas
        log(f"📊 Total de linhas no DataFrame: {len(dados)} (incluindo 3 linhas de cabeçalho)")
        if len(dados) > 3:
            log(f"   Exemplo de linha de dados: {dados[3]}")
        
        # Criar DataFrame
        df = pd.DataFrame(dados)
        
        # Salvar em Excel
        try:
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, header=False)
                
                # Formatar células
                from openpyxl.styles import Font
                workbook = writer.book
                worksheet = writer.sheets['Sheet1']
                
                # Definir fonte vermelha para valores negativos
                red_font = Font(color="FF0000")
                
                # Formatar valores monetários (coluna E e F - índices 5 e 6)
                for row in range(4, len(dados) + 1):  # Começar da linha 4 (primeira transação)
                    # Coluna Valor (R$) - índice E (coluna 5)
                    cell_valor = worksheet.cell(row=row+1, column=5)
                    if cell_valor.value and isinstance(cell_valor.value, (int, float)):
                        cell_valor.number_format = '#,##0.00'
                        # Se valor negativo, aplicar fonte vermelha APENAS no valor
                        if cell_valor.value < 0:
                            cell_valor.font = red_font
                    
                    # Coluna Saldo (R$) - índice F (coluna 6)
                    cell_saldo = worksheet.cell(row=row+1, column=6)
                    if cell_saldo.value and isinstance(cell_saldo.value, (int, float)):
                        cell_saldo.number_format = '#,##0.00'
                        # NÃO aplicar fonte vermelha no saldo
                
                # Auto-ajustar largura das colunas
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    
                    for cell in column:
                        try:
                            if cell.value:
                                cell_length = len(str(cell.value))
                                if cell_length > max_length:
                                    max_length = cell_length
                        except:
                            pass
                    
                    # Definir largura ajustada (mínimo 10, máximo 50)
                    adjusted_width = min(max(max_length + 2, 10), 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            log(f"✅ Extrato salvo em: {filename}")
            log(f"   Caminho completo: {filepath}")
            
            # Verificar se arquivo foi criado
            if os.path.exists(filepath):
                tamanho = os.path.getsize(filepath)
                log(f"   Tamanho: {tamanho} bytes")
            else:
                log(f"   ⚠️ AVISO: Arquivo não encontrado após salvar!")
            
            return filepath
        except Exception as e:
            log(f"❌ Erro ao salvar Excel: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def gerar_pdf_extrato(self, transacoes, branch_code, account_number, pasta_saida=None, saldo_info=None, data_inicial=None, data_final=None):
        """
        Gera PDF do extrato no formato IBE (Internet Banking Empresarial) Santander
        Replica exatamente o layout do exemplo do Santander IBE
        
        Args:
            transacoes: Lista de transações (pode ser vazia)
            branch_code: Código da agência
            account_number: Número da conta
            pasta_saida: Pasta para salvar (padrão: diretório atual)
            saldo_info: Informações de saldo (opcional)
            data_inicial: Data inicial solicitada (datetime)
            data_final: Data final solicitada (datetime)
        
        Returns:
            Caminho do arquivo gerado ou None
        """
        num_transacoes = len(transacoes) if transacoes else 0
        log(f"\n📄 Gerando PDF com {num_transacoes} transação(ões)...")
        
        # Definir pasta de saída
        if not pasta_saida:
            pasta_saida = os.getcwd()
        
        # Nome do arquivo com nome do fundo: comprovante-ibe-{FUNDO}-{AGENCIA}-{CONTA}.pdf
        # REMOVER UUID para evitar duplicação - usar apenas fundo-agencia-conta
        filename = f"comprovante-ibe-{self.fundo_nome}-{branch_code}-{account_number}.pdf"
        filepath = os.path.join(pasta_saida, filename)
        
        # Verificar se arquivo já existe para evitar duplicação
        if os.path.exists(filepath):
            log(f"⚠️  PDF já existe, sobrescrevendo: {filename}")
        
        try:
            # Criar documento PDF com margens exatas do IBE (29pts = 10.23mm)
            doc = SimpleDocTemplate(filepath, pagesize=A4,
                                   rightMargin=28, leftMargin=29,
                                   topMargin=29, bottomMargin=29)
            
            elements = []
            styles = getSampleStyleSheet()
            
            # ========== CORES IBE SANTANDER ==========
            # Baseado na análise: RGB(0.933, 0.114, 0.137) = #EE1D23 (vermelho Santander)
            # Texto principal: RGB(0.255, 0.333, 0.369) = #41555E
            cor_vermelho_santander = colors.Color(0.933, 0.114, 0.137)
            cor_texto_principal = colors.Color(0.255, 0.333, 0.369)
            cor_cinza_claro = colors.Color(0.663, 0.663, 0.663)
            
            # ========== CABEÇALHO IBE ==========
            # Título com fonte 18.1pt (análise mostrou LiberationSans, usamos Helvetica como substituto)
            header_style = ParagraphStyle(
                'IBEHeader',
                parent=styles['Normal'],
                fontSize=18,
                textColor=cor_vermelho_santander,
                fontName='Helvetica',
                alignment=TA_RIGHT,
                spaceAfter=20
            )
            
            # Título "Internet Banking Empresarial"
            elements.append(Paragraph("Internet Banking Empresarial", header_style))
            
            # Linha separadora (como no exemplo - linha fina cinza)
            from reportlab.platypus import HRFlowable
            elements.append(HRFlowable(width="100%", thickness=1, color=cor_cinza_claro, spaceAfter=15))
            
            # Linha com Nome do Fundo, Agência e Conta (fonte 7pt como no exemplo)
            fund_info_style = ParagraphStyle(
                'FundInfo',
                parent=styles['Normal'],
                fontSize=7,
                fontName='Helvetica',
                textColor=cor_texto_principal,
                alignment=TA_LEFT,
                spaceAfter=10
            )
            
            # Buscar nome do fundo
            fundo_nome = SANTANDER_FUNDOS.get(self.fundo_id, {}).get('nome', self.fundo_id)
            
            # Formato exato do IBE: "FUNDO...    Agência: XXXX    Conta: XXXXXXXXX"
            fund_line = f"{fundo_nome.upper()}    Agência: {branch_code}    Conta: {account_number}"
            elements.append(Paragraph(fund_line, fund_info_style))
            
            # Linha separadora
            elements.append(HRFlowable(width="100%", thickness=1, color=cor_cinza_claro, spaceAfter=10))
            
            # Navegação (Conta Corrente > Extrato > Consultar) - fonte 8.2pt
            nav_style = ParagraphStyle(
                'Navigation',
                parent=styles['Normal'],
                fontSize=8.2,
                fontName='Helvetica',
                textColor=cor_texto_principal,
                alignment=TA_LEFT,
                spaceAfter=2
            )
            elements.append(Paragraph("Conta Corrente > Extrato >", nav_style))
            
            # "Consultar" em fonte maior (10.5pt)
            consultar_style = ParagraphStyle(
                'Consultar',
                parent=styles['Normal'],
                fontSize=10.5,
                fontName='Helvetica',
                textColor=cor_texto_principal,
                alignment=TA_LEFT,
                spaceAfter=15
            )
            elements.append(Paragraph("Consultar", consultar_style))
            
            # Opções de pesquisa e período (fonte 7pt)
            info_style = ParagraphStyle(
                'InfoLine',
                parent=styles['Normal'],
                fontSize=7,
                fontName='Helvetica',
                textColor=cor_texto_principal,
                alignment=TA_LEFT,
                leading=10
            )
            
            # Determinar período - USAR DATAS SOLICITADAS, não das transações retornadas
            import locale
            try:
                locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
            except:
                try:
                    locale.setlocale(locale.LC_TIME, 'English_United States.1252')
                except:
                    pass
            
            if data_inicial and data_final:
                # Usar datas solicitadas pelo usuário
                try:
                    periodo_inicio = data_inicial.strftime('%a %b %d 00:00:00 GMT-03:00 %Y')
                    periodo_fim = data_final.strftime('%a %b %d 23:59:59 GMT-03:00 %Y')
                except:
                    periodo_inicio = data_inicial.strftime('%d/%m/%Y')
                    periodo_fim = data_final.strftime('%d/%m/%Y')
            elif transacoes:
                # Fallback: usar primeira e última transação
                primeira_trans = transacoes[0].get('transactionDate', '')
                ultima_trans = transacoes[-1].get('transactionDate', '')
                
                if primeira_trans:
                    try:
                        dt_inicio = datetime.strptime(primeira_trans[:10], '%Y-%m-%d')
                        periodo_inicio = dt_inicio.strftime('%a %b %d 00:00:00 GMT-03:00 %Y')
                    except:
                        periodo_inicio = primeira_trans
                else:
                    periodo_inicio = "N/A"
                    
                if ultima_trans:
                    try:
                        dt_fim = datetime.strptime(ultima_trans[:10], '%Y-%m-%d')
                        periodo_fim = dt_fim.strftime('%a %b %d 23:59:59 GMT-03:00 %Y')
                    except:
                        periodo_fim = ultima_trans
                else:
                    periodo_fim = "N/A"
            else:
                periodo_inicio = periodo_fim = "N/A"
            
            data_hora_agora = datetime.now().strftime('%d/%m/%Y às %Hh%M')
            
            elements.append(Paragraph(f"<b>Opção de Pesquisa:</b> Todos", info_style))
            elements.append(Paragraph(f"<b>Períodos:</b> {periodo_inicio} a {periodo_fim}", info_style))
            elements.append(Paragraph(f"<b>Data/Hora:</b> {data_hora_agora}", info_style))
            elements.append(Spacer(1, 10))
            
            # ========== TABELA DE TRANSAÇÕES ==========
            # Baseado na análise: tabela com 6 colunas, fonte 7pt
            table_data = []
            
            # Cabeçalho (com coluna vazia após Data)
            table_data.append(['Data', '', 'Histórico', 'Documento', 'Valor (R$)', 'Saldo (R$)'])
            
            # Calcular saldo
            saldo = 0
            saldo_fmt = "0,00"  # Inicializar com valor padrão para evitar erro quando não há transações
            
            # Se há informações de saldo da API, usar como saldo inicial
            if saldo_info and 'availableAmount' in saldo_info:
                saldo = float(saldo_info.get('availableAmount', 0))
                saldo_fmt = f"{abs(saldo):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                if saldo < 0:
                    saldo_fmt = f"-{saldo_fmt}"
            
            # Saldo anterior
            if transacoes and len(transacoes) > 0:
                primeira_data = transacoes[0].get('transactionDate', '')
                if primeira_data and len(primeira_data) >= 10:
                    try:
                        data_obj = datetime.strptime(primeira_data[:10], '%Y-%m-%d')
                        primeira_data = data_obj.strftime('%d/%m/%Y')
                    except:
                        pass
                # 6 colunas com coluna vazia
                table_data.append([primeira_data, '', 'SALDO ANTERIOR', '', '', saldo_fmt])
            else:
                # Se não há transações, mostrar saldo atual na data de hoje
                data_hoje = datetime.now().strftime('%d/%m/%Y')
                table_data.append([data_hoje, '', 'SALDO ATUAL', '', '', saldo_fmt])
            
            # Transações
            for trans in transacoes:
                data = trans.get('transactionDate', '')
                historico = trans.get('transactionName', '')
                documento = trans.get('documentNumber', '')
                valor = float(trans.get('amount', 0))
                tipo = trans.get('creditDebitType', '')
                
                # DEBUG na primeira transação
                if len(table_data) == 2:  # Logo após cabeçalho e saldo anterior
                    log(f"   📋 DEBUG PDF - Primeira transação:")
                    log(f"      Data: {data}, Histórico: {historico}, Valor: {valor}, Tipo: {tipo}")
                
                # Ajustar sinal
                if tipo == 'DEBITO':
                    valor = -abs(valor)
                else:
                    valor = abs(valor)
                
                saldo += valor
                
                # Formatar data
                if data and len(data) >= 10:
                    try:
                        data_obj = datetime.strptime(data[:10], '%Y-%m-%d')
                        data = data_obj.strftime('%d/%m/%Y')
                    except:
                        pass
                
                # Formatar valores
                valor_fmt = f"{abs(valor):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                if valor < 0:
                    valor_fmt = f"-{valor_fmt}"
                
                saldo_fmt = f"{abs(saldo):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                if saldo < 0:
                    saldo_fmt = f"-{saldo_fmt}"
                
                # 6 colunas (Data, vazio, Histórico, Documento, Valor, Saldo)
                table_data.append([data, '', historico, documento or '', valor_fmt, saldo_fmt])
            
            # Criar tabela com larguras baseadas na análise do PDF (em pts)
            # Análise mostrou: cols muito pequenas no início e fim, maior no meio
            # Largura útil: 538pts (567-29), dividido em: 54, 13, 276, 56, 58, 56 ≈ 513pts
            table = Table(table_data, colWidths=[54, 13, 276, 56, 58, 56])
            
            # Estilo da tabela IBE (simples, linhas finas)
            table.setStyle(TableStyle([
                # Cabeçalho
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 7),
                ('TEXTCOLOR', (0, 0), (-1, 0), cor_texto_principal),
                ('ALIGN', (0, 0), (1, 0), 'LEFT'),
                ('ALIGN', (2, 0), (3, 0), 'LEFT'),
                ('ALIGN', (4, 0), (5, 0), 'RIGHT'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('TOPPADDING', (0, 0), (-1, 0), 6),
                
                # Corpo
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('TEXTCOLOR', (0, 1), (-1, -1), cor_texto_principal),
                ('ALIGN', (0, 1), (1, -1), 'LEFT'),
                ('ALIGN', (2, 1), (3, -1), 'LEFT'),
                ('ALIGN', (4, 1), (5, -1), 'RIGHT'),
                
                # Bordas externas
                ('BOX', (0, 0), (-1, -1), 0.5, cor_cinza_claro),
                # Linhas internas horizontais
                ('LINEBELOW', (0, 0), (-1, -2), 0.25, cor_cinza_claro),
                # Linhas internas verticais
                ('LINEAFTER', (0, 0), (-2, -1), 0.25, cor_cinza_claro),
                
                # Padding
                ('TOPPADDING', (0, 1), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 3),
                ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 10))
            
            # ========== LEGENDA ==========
            legend_style = ParagraphStyle(
                'Legend',
                parent=styles['Normal'],
                fontSize=7,
                fontName='Helvetica',
                textColor=cor_texto_principal,
                alignment=TA_LEFT,
                leading=10
            )
            
            elements.append(Paragraph(
                "<b>a</b> = Bloqueio Dia / ADM    Entenda a composição do seu saldo no quadro abaixo.",
                legend_style
            ))
            elements.append(Paragraph("<b>b</b> = Bloqueado", legend_style))
            elements.append(Paragraph("<b>p</b> = Lançamento Provisionado", legend_style))
            elements.append(Spacer(1, 8))
            
            # ========== QUADRO DE SALDO ==========
            # Usar saldo_info se disponível, senão usar saldo calculado
            if saldo_info and 'availableAmount' in saldo_info:
                saldo_disponivel = float(saldo_info.get('availableAmount', 0))
                saldo_bloqueado = float(saldo_info.get('blockedAmount', 0))
                saldo_conta = saldo_disponivel + saldo_bloqueado
                
                saldo_conta_fmt = f"{abs(saldo_conta):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                saldo_bloqueado_fmt = f"{abs(saldo_bloqueado):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                saldo_disponivel_fmt = f"{abs(saldo_disponivel):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                
                if saldo_conta < 0:
                    saldo_conta_fmt = f"-{saldo_conta_fmt}"
                if saldo_bloqueado < 0:
                    saldo_bloqueado_fmt = f"-{saldo_bloqueado_fmt}"
                if saldo_disponivel < 0:
                    saldo_disponivel_fmt = f"-{saldo_disponivel_fmt}"
            else:
                # Usar saldo calculado das transações
                saldo_conta_fmt = saldo_fmt
                saldo_bloqueado_fmt = "0,00"
                saldo_disponivel_fmt = saldo_fmt
            
            # Baseado na análise: formato exato do IBE
            saldo_data = [
                ['', 'Saldo', 'Valor (R$)', ''],
                ['', f'Posição em:{datetime.now().strftime("%d/%m/%Y")}', '', ''],
                ['', '', '', ''],
                ['', 'Saldo', 'Valor (R$)', ''],
                ['', 'A - Saldo de Conta Corrente', saldo_conta_fmt, ''],
                ['', 'B - Saldo Bloqueado', saldo_bloqueado_fmt, ''],
                ['', '    Desbloqueio em 1 dia', '0,00', ''],
                ['', '    Desbloqueio em 2 dias', '0,00', ''],
                ['', '    Desbloqueio em mais de 2 dias', '0,00', ''],
                ['C - Saldo Disponível em Conta Corrente (A - B) ' + saldo_disponivel_fmt, '', '', ''],
            ]
            
            # Larguras aproximadas da tabela de saldo
            saldo_table = Table(saldo_data, colWidths=[10, 370, 80, 10])
            saldo_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 7),
                ('TEXTCOLOR', (0, 0), (-1, -1), cor_texto_principal),
                ('FONTNAME', (1, 0), (2, 0), 'Helvetica-Bold'),
                ('FONTNAME', (1, 3), (2, 3), 'Helvetica-Bold'),
                ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOX', (0, 0), (-1, -1), 0.5, cor_cinza_claro),
                ('LINEBELOW', (0, 0), (-1, 0), 0.5, cor_cinza_claro),
                ('LINEBELOW', (0, 3), (-1, 3), 0.5, cor_cinza_claro),
                ('LINEAFTER', (0, 0), (-2, -1), 0.25, cor_cinza_claro),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ]))
            
            elements.append(saldo_table)
            elements.append(Spacer(1, 15))
            
            # ========== RODAPÉ COM CONTATOS ==========
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=7,
                fontName='Helvetica',
                textColor=cor_texto_principal,
                alignment=TA_LEFT,
                leading=9
            )
            
            contatos = [
                "<b>Central de Atendimento Santander Empresarial</b> - Das 8h às 20h, de segunda a sexta-feira",
                "4004-2125 (Capitais e Regiões Metropolitanas)",
                "0800 702 2125 (Demais Localidades)",
                "",
                "<b>Central de Atendimento Getnet</b> - Atendimento 24h por dia, todos os dias",
                "4002-4000 (Capitais e Regiões Metropolitanas)",
                "4003-4000 (Capitais e Regiões Metropolitanas)",
                "0800 648 8000 (Demais Localidades)",
                "",
                "<b>Central de Vendas PJ</b> - Das 8h às 20h, de segunda a sexta-feira, exceto feriados.",
                "0800 013 7333",
                "",
                "<b>SAC</b> - Atendimento 24h por dia, todos os dias.",
                "Reclamações cancelamentos e informações:",
                "0800 762 7777",
                "",
                "<b>Ouvidoria</b> - Disponível das 9h às 18h, de segunda a sexta-feira, exceto feriados.",
                "Se não ficar satisfeito com a solução apresentada:",
                "0800 726 0322",
                "55 (11) 3012 0322 (No exterior, ligue a cobrar)"
            ]
            
            for linha in contatos:
                elements.append(Paragraph(linha, footer_style))
            
            # Gerar PDF
            doc.build(elements)
            
            log(f"✅ PDF gerado: {filename}")
            log(f"   Caminho completo: {filepath}")
            
            # Verificar se arquivo foi criado
            if os.path.exists(filepath):
                tamanho = os.path.getsize(filepath)
                log(f"   Tamanho: {tamanho} bytes")
            else:
                log(f"   ⚠️ AVISO: Arquivo não encontrado após salvar!")
            
            return filepath
            
        except Exception as e:
            log(f"❌ Erro ao gerar PDF: {e}")
            import traceback
            traceback.print_exc()
            return None


def main(fundos=None, data_inicial=None, data_final=None, pasta_saida=None, gerar_pdf=False):
    """
    Função principal para buscar extratos de múltiplos fundos
    
    Args:
        fundos: Lista de IDs de fundos (None = todos configurados)
        data_inicial: Data inicial (datetime ou None)
        data_final: Data final (datetime ou None)
        pasta_saida: Pasta para salvar arquivos
        gerar_pdf: Se True, gera também PDF do extrato
    """
    log("="*80)
    log("BUSCA DE EXTRATOS BANCÁRIOS SANTANDER")
    log("="*80)
    
    # 🧹 LIMPEZA DE CACHE: Remover tokens antigos
    log("\n🧹 Limpando cache de tokens...")
    import glob
    tokens_removidos = 0
    try:
        # Buscar arquivos de token no diretório config
        config_dir = os.path.join(os.path.dirname(__file__), 'config')
        if os.path.exists(config_dir):
            token_files = glob.glob(os.path.join(config_dir, 'santander_token_*.json'))
            for token_file in token_files:
                try:
                    os.remove(token_file)
                    tokens_removidos += 1
                except Exception as e:
                    log(f"⚠️ Não foi possível remover {os.path.basename(token_file)}: {e}")
    except Exception as e:
        log(f"⚠️ Erro ao limpar cache: {e}")
    
    if tokens_removidos > 0:
        log(f"✅ {tokens_removidos} token(s) de cache removido(s)")
    else:
        log("✅ Nenhum token de cache encontrado")
    
    # Determinar quais fundos processar
    if not fundos:
        # Listar apenas fundos que têm credenciais configuradas
        fundos = [fid for fid, creds in SANTANDER_FUNDOS.items() 
                  if creds.get("client_id") and creds.get("client_secret")]
    
    log(f"\n📋 Fundos a processar: {', '.join(fundos)}")
    
    # Rastreamento de resultados
    fundos_com_transacoes = []
    fundos_sem_transacoes = []
    fundos_com_erro = []
    
    # Processar cada fundo
    for fundo_id in fundos:
        log(f"\n{'='*80}")
        log(f"PROCESSANDO FUNDO: {fundo_id}")
        log(f"{'='*80}")
        
        try:
            log(f"\n🔧 Criando cliente para fundo {fundo_id}...")
            # Criar cliente
            cliente = SantanderExtratosBancarios(fundo_id)
            log(f"✅ Cliente criado com sucesso")
            
            log(f"🏦 Iniciando listagem de contas...")
            # Listar contas
            contas = cliente.listar_contas()
            log(f"📊 Resultado da listagem: {len(contas) if contas else 0} contas")
            
            if not contas:
                log(f"⚠️  Nenhuma conta encontrada para o fundo {fundo_id}")
                log(f"   Isso pode indicar:")
                log(f"   - Token obtido mas sem permissão para listar contas")
                log(f"   - Endpoint /accounts retornou estrutura vazia")
                log(f"   - CNPJ {cliente.cnpj} não possui contas no Santander")
                log(f"   - Credenciais incorretas ou expiradas")
                log(f"   - Problema na API de listagem de contas")
                fundos_com_erro.append(fundo_id)
                continue
            
            log(f"📊 Total de contas encontradas: {len(contas)}")
            if len(contas) > 1:
                log(f"   🔍 ATENÇÃO: Fundo com MÚLTIPLAS CONTAS detectado!")
                for i, c in enumerate(contas, 1):
                    branch = c.get('branchCode') or c.get('agencyCode')
                    account = c.get('number') or c.get('accountNumber')
                    log(f"      Conta {i}: {branch}.{account}")
            
            # Flag para rastrear se o fundo teve alguma transação
            fundo_teve_transacoes = False
            arquivos_gerados = 0
            
            # Processar cada conta
            for i, conta in enumerate(contas, 1):
                branch_code = conta.get('branchCode') or conta.get('agencyCode')
                account_number = conta.get('number') or conta.get('accountNumber')
                
                if not branch_code or not account_number:
                    log(f"❌ Conta {i}: Dados incompletos - Branch: {branch_code}, Account: {account_number}")
                    continue
                
                log(f"\n{'-'*80}")
                log(f"Processando Conta {i}/{len(contas)}: {branch_code}.{account_number}")
                log(f"{'-'*80}")
                
                # Buscar saldo
                saldo = cliente.buscar_saldo(branch_code, account_number)
                log(f"💰 Saldo obtido: {saldo}")
                
                # Buscar transações
                transacoes = cliente.buscar_transacoes(
                    branch_code, 
                    account_number,
                    data_inicial=data_inicial,
                    data_final=data_final
                )
                
                log(f"📊 Transações recebidas da API: {len(transacoes) if transacoes else 0}")
                if transacoes and len(transacoes) > 0:
                    log(f"   Primeira transação: {transacoes[0]}")
                    fundo_teve_transacoes = True
                
                # SEMPRE exportar Excel, mesmo sem transações (mostra saldo)
                # Se não houver transações, criar lista vazia para incluir apenas saldo
                transacoes_para_export = transacoes if transacoes else []
                
                arquivo_excel = cliente.exportar_transacoes_excel(
                    transacoes_para_export,
                    branch_code,
                    account_number,
                    pasta_saida=pasta_saida,
                    saldo_info=saldo  # Passar info de saldo
                )
                
                if arquivo_excel:
                    arquivos_gerados += 1
                    log(f"   ✅ Excel gerado: {os.path.basename(arquivo_excel)}")
                
                # Gerar PDF se solicitado (mesmo sem transações)
                if gerar_pdf:
                    arquivo_pdf = cliente.gerar_pdf_extrato(
                        transacoes_para_export,
                        branch_code,
                        account_number,
                        pasta_saida=pasta_saida,
                        saldo_info=saldo,  # Passar info de saldo
                        data_inicial=data_inicial,  # Passar data solicitada
                        data_final=data_final  # Passar data solicitada
                    )
                    
                    if arquivo_pdf:
                        arquivos_gerados += 1
                        log(f"   ✅ PDF gerado: {os.path.basename(arquivo_pdf)}")
            
            # Relatório final do fundo
            log(f"\n📈 FUNDO {fundo_id} - PROCESSAMENTO CONCLUÍDO:")
            log(f"   📊 Contas processadas: {len(contas)}")
            log(f"   📄 Arquivos gerados: {arquivos_gerados}")
            log(f"   💰 Teve transações: {'✅ SIM' if fundo_teve_transacoes else '❌ NÃO'}")
            
            # Adicionar fundo na lista apropriada
            if fundo_teve_transacoes:
                fundos_com_transacoes.append(fundo_id)
            else:
                fundos_sem_transacoes.append(fundo_id)
        
        except Exception as e:
            log(f"\n❌ Erro ao processar fundo {fundo_id}: {e}")
            fundos_com_erro.append(fundo_id)
            import traceback
            traceback.print_exc()
    
    log("\n" + "="*80)
    log("PROCESSAMENTO CONCLUÍDO")
    log("="*80)
    
    # Relatório final
    log("\n📊 RESUMO DO PROCESSAMENTO")
    log("-"*80)
    
    if fundos_com_transacoes:
        log(f"\n✅ Fundos COM transações no período ({len(fundos_com_transacoes)}):")
        for fundo in fundos_com_transacoes:
            fundo_nome = SANTANDER_FUNDOS.get(fundo, {}).get('nome', fundo)
            log(f"   • {fundo_nome}")
    
    if fundos_sem_transacoes:
        log(f"\n⚠️  Fundos SEM transações no período ({len(fundos_sem_transacoes)}):")
        for fundo in fundos_sem_transacoes:
            fundo_nome = SANTANDER_FUNDOS.get(fundo, {}).get('nome', fundo)
            log(f"   • {fundo_nome}")
        log("\n   💡 Arquivos foram gerados mostrando apenas os saldos atuais")
    
    if fundos_com_erro:
        log(f"\n❌ Fundos com ERRO ({len(fundos_com_erro)}):")
        for fundo in fundos_com_erro:
            fundo_nome = SANTANDER_FUNDOS.get(fundo, {}).get('nome', fundo)
            log(f"   • {fundo_nome}")
    
    log("\n" + "="*80)


if __name__ == "__main__":
    # Exemplo de uso: buscar extratos dos últimos 7 dias
    main()
