"""
Script para buscar comprovantes e pagamentos via API Santander
Usa autenticação mTLS + OAuth2 Client Credentials já configurada
ENDPOINT FUNCIONAL: /consult_payment_receipts/v1/payment_receipts
"""

import sys
import codecs
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

from credenciais_bancos import SantanderAuth, SANTANDER_FUNDOS
from buscar_comprovantes_santander import SantanderComprovantes
import requests
from datetime import datetime, timedelta
import json
import pandas as pd
from pathlib import Path

class SantanderPagamentos:
    """Cliente para consultar pagamentos e comprovantes via API Santander"""
    
    def __init__(self, fundo_id: str):
        """
        Inicializa cliente de pagamentos
        
        Args:
            fundo_id: ID do fundo (chave em SANTANDER_FUNDOS)
        """
        self.auth = SantanderAuth.criar_por_fundo(fundo_id)
        self.cliente_comprovantes = SantanderComprovantes(self.auth)
        self.base_url = "https://trust-open.api.santander.com.br"
        self.cnpj = self.auth.fundo_cnpj.replace(".", "").replace("/", "").replace("-", "")
        
    def listar_comprovantes_periodo(self, data_inicial: str, data_final: str):
        """
        Lista comprovantes de pagamento no período
        
        Args:
            data_inicial: Data inicial no formato YYYY-MM-DD
            data_final: Data final no formato YYYY-MM-DD (máx 30 dias)
            
        Returns:
            Dados dos comprovantes ou None se erro
        """
        print(f"\n📋 Buscando comprovantes do fundo: {self.auth.fundo_nome}")
        print(f"   CNPJ: {self.auth.fundo_cnpj}")
        print(f"   Período: {data_inicial} até {data_final}")
        
        try:
            dados = self.cliente_comprovantes.listar_comprovantes(data_inicial, data_final)
            
            if dados and 'paymentsReceipts' in dados:
                comprovantes = dados['paymentsReceipts']
                print(f"   ✅ {len(comprovantes)} comprovante(s) encontrado(s)")
                return dados
            else:
                print(f"   ⚠️ Nenhum comprovante no período")
                return None
                
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def baixar_comprovante_pdf(self, payment_id: str):
        """
        Baixa PDF de um comprovante específico
        
        Args:
            payment_id: ID do pagamento
            
        Returns:
            Caminho do arquivo PDF ou None se erro
        """
        print(f"\n📥 Baixando comprovante: {payment_id}")
        
        try:
            # Usar o método correto do SantanderComprovantes
            pdf_path = self.cliente_comprovantes.buscar_e_baixar_comprovante(payment_id)
            
            if pdf_path and Path(pdf_path).exists():
                print(f"   ✅ PDF salvo: {pdf_path}")
                return pdf_path
            else:
                print(f"   ❌ Falha ao baixar PDF")
                return None
                
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")
            return None
    
    def exportar_comprovantes_excel(self, comprovantes_data: dict, arquivo_saida: str = None):
        """
        Exporta lista de comprovantes para Excel com formatação adequada
        
        Args:
            comprovantes_data: Dados dos comprovantes retornados pela API
            arquivo_saida: Nome do arquivo (opcional)
            
        Returns:
            Caminho do arquivo gerado
        """
        if not comprovantes_data or "paymentsReceipts" not in comprovantes_data:
            print("❌ Sem dados para exportar")
            return None
        
        comprovantes = comprovantes_data["paymentsReceipts"]
        
        if not comprovantes:
            print("❌ Nenhum comprovante no período")
            return None
        
        # Normalizar dados aninhados
        dados_normalizados = []
        
        for item in comprovantes:
            payment = item.get('payment', {})
            category = item.get('category', {})
            channel = item.get('channel', {})
            
            # Extrair informações do pagamento
            payer = payment.get('payer', {}).get('person', {}).get('document', {})
            payee = payment.get('payee', {})
            amount_info = payment.get('paymentAmountInfo', {}).get('direct', {})
            
            registro = {
                'Payment ID': payment.get('paymentId', ''),
                'Número Compromisso': payment.get('commitmentNumber', ''),
                'Data Pagamento': payment.get('requestValueDate', ''),
                'Valor': float(amount_info.get('amount', 0)),
                'Beneficiário': payee.get('name', ''),
                'CNPJ/CPF Beneficiário': payee.get('person', {}).get('document', {}).get('documentNumber', ''),
                'CNPJ Pagador': payer.get('documentNumber', ''),
                'Tipo Pagador': payer.get('documentTypeCode', ''),
                'Categoria': category.get('code', ''),
                'Canal': channel.get('code', '')
            }
            
            dados_normalizados.append(registro)
        
        # Converter para DataFrame
        df = pd.DataFrame(dados_normalizados)
        
        # Formatar data (remover timezone se presente)
        if 'Data Pagamento' in df.columns:
            df['Data Pagamento'] = pd.to_datetime(df['Data Pagamento'], errors='coerce')
            df['Data'] = df['Data Pagamento'].dt.strftime('%d/%m/%Y')
            df['Hora'] = df['Data Pagamento'].dt.strftime('%H:%M:%S')
            df = df.drop('Data Pagamento', axis=1)
        
        # Reordenar colunas
        colunas_ordem = [
            'Payment ID', 'Número Compromisso', 'Data', 'Hora',
            'Beneficiário', 'CNPJ/CPF Beneficiário', 'Valor',
            'Categoria', 'Canal', 'CNPJ Pagador', 'Tipo Pagador'
        ]
        
        # Manter apenas colunas que existem
        colunas_ordem = [col for col in colunas_ordem if col in df.columns]
        df = df[colunas_ordem]
        
        # Nome do arquivo
        if not arquivo_saida:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fundo_id = self.auth.fundo_id or "santander"
            arquivo_saida = f"comprovantes_{fundo_id}_{timestamp}.xlsx"
        
        # Salvar com formatação
        with pd.ExcelWriter(arquivo_saida, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Comprovantes')
            
            # Formatar planilha
            worksheet = writer.sheets['Comprovantes']
            
            # Ajustar largura das colunas
            for idx, col in enumerate(df.columns, 1):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(col)
                ) + 2
                worksheet.column_dimensions[chr(64 + idx)].width = min(max_length, 50)
            
            # Formatar valores monetários
            from openpyxl.styles import numbers
            valor_col = df.columns.get_loc('Valor') + 1
            for row in range(2, len(df) + 2):
                cell = worksheet.cell(row=row, column=valor_col)
                cell.number_format = 'R$ #,##0.00'
        
        print(f"\n✅ Comprovantes exportados: {arquivo_saida}")
        print(f"   Total de registros: {len(df)}")
        print(f"   Valor total: R$ {df['Valor'].sum():,.2f}")
        
        return arquivo_saida


def main():
    """Função principal - exemplo de uso"""
    
    print("="*80)
    print("💳 CONSULTA DE COMPROVANTES DE PAGAMENTO - API SANTANDER")
    print("="*80)
    
    # Listar fundos disponíveis
    print("\n📋 Fundos disponíveis:")
    for idx, (fundo_id, config) in enumerate(SANTANDER_FUNDOS.items(), 1):
        if config.get("client_id"):  # Apenas fundos com credenciais
            print(f"{idx:2d}. {fundo_id:20s} - {config['nome'][:60]}")
    
    # Selecionar fundo para teste (usando o primeiro disponível)
    # Você pode alterar aqui para testar outro fundo
    FUNDO_TESTE = "911_BANK"  # ← ALTERE AQUI para outro fundo se necessário
    
    print(f"\n🎯 Usando fundo: {FUNDO_TESTE}")
    
    try:
        # Criar cliente
        cliente = SantanderPagamentos(FUNDO_TESTE)
        
        # 1. LISTAR COMPROVANTES
        print("\n" + "="*80)
        print("PASSO 1: LISTANDO COMPROVANTES DE PAGAMENTO")
        print("="*80)
        
        # Calcular datas (últimos 30 dias)
        data_final = datetime.now()
        data_inicial = data_final - timedelta(days=30)
        
        data_inicial_str = data_inicial.strftime("%Y-%m-%d")
        data_final_str = data_final.strftime("%Y-%m-%d")
        
        comprovantes = cliente.listar_comprovantes_periodo(data_inicial_str, data_final_str)
        
        if comprovantes and 'paymentsReceipts' in comprovantes:
            receipts = comprovantes['paymentsReceipts']
            
            print(f"\n📄 Comprovantes encontrados ({len(receipts)}):")
            print("="*80)
            
            for idx, receipt in enumerate(receipts[:5], 1):  # Mostrar primeiros 5
                print(f"\n   Comprovante {idx}:")
                print(f"      Payment ID: {receipt.get('paymentId', 'N/A')}")
                print(f"      Data: {receipt.get('paymentDate', 'N/A')}")
                print(f"      Valor: R$ {receipt.get('amount', 0):.2f}")
                print(f"      Beneficiário: {receipt.get('beneficiaryName', 'N/A')}")
                print(f"      CNPJ/CPF: {receipt.get('beneficiaryCnpjCpf', 'N/A')}")
            
            if len(receipts) > 5:
                print(f"\n   ... e mais {len(receipts) - 5} comprovante(s)")
            
            # 2. BAIXAR PDFs DOS COMPROVANTES
            print("\n" + "="*80)
            print("PASSO 2: BAIXANDO PDFs DOS COMPROVANTES")
            print("="*80)
            
            baixados = 0
            erros = 0
            
            for idx, receipt in enumerate(receipts, 1):
                payment = receipt.get('payment', {})
                payment_id = payment.get('paymentId')
                beneficiario = payment.get('payee', {}).get('name', 'N/A')
                
                if payment_id:
                    print(f"\n[{idx}/{len(receipts)}] Baixando: {beneficiario} (ID: {payment_id})")
                    try:
                        # Usar o método da classe SantanderPagamentos
                        pdf_path = cliente.baixar_comprovante_pdf(payment_id)
                        if pdf_path:
                            print(f"   ✅ Salvo em: {pdf_path}")
                            baixados += 1
                        else:
                            erros += 1
                    except Exception as e:
                        print(f"   ❌ Erro: {e}")
                        erros += 1

            
            print(f"\n📊 Resumo de downloads:")
            print(f"   ✅ Baixados: {baixados}")
            print(f"   ❌ Erros: {erros}")
            print(f"   📁 Diretório: Comprovantes/{cliente.auth.fundo_id}/")
            
            # 3. EXPORTAR PARA EXCEL
            print("\n" + "="*80)
            print("PASSO 3: EXPORTANDO LISTA DE COMPROVANTES PARA EXCEL")
            print("="*80)
            
            arquivo = cliente.exportar_comprovantes_excel(comprovantes)
            
            if arquivo:
                print(f"\n🎉 Arquivo Excel gerado: {arquivo}")
        
        print("\n" + "="*80)
        print("✅ PROCESSO CONCLUÍDO")
        print("="*80)
        
    except ValueError as e:
        print(f"\n❌ Erro de configuração: {str(e)}")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
