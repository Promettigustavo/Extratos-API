"""
Script para verificar se todos os dados do JSON estão sendo incluídos no Excel e PDF
"""

import pandas as pd
import PyPDF2
from datetime import datetime, timedelta
from buscar_extratos_bancarios import SantanderExtratosBancarios

def verificar_integridade():
    """Verifica se todos os dados do JSON aparecem no Excel e PDF"""
    
    print("="*80)
    print("VERIFICAÇÃO DE INTEGRIDADE DE DADOS")
    print("="*80)
    
    # Selecionar um fundo para teste
    fundo_id = "CONDOLIVRE FIDC"
    
    print(f"\n📋 Testando com fundo: {fundo_id}")
    
    # Criar instância
    api = SantanderExtratosBancarios(fundo_id)
    
    # Buscar contas
    print("\n1️⃣ Buscando contas...")
    contas = api.listar_contas()
    
    if not contas:
        print("❌ Nenhuma conta encontrada")
        return
    
    conta = contas[0]
    branch_code = conta.get('branchCode')
    account_number = conta.get('number')
    
    print(f"✅ Conta: {branch_code}.{account_number}")
    
    # Buscar transações (últimos 7 dias)
    print("\n2️⃣ Buscando transações...")
    data_final = datetime.now()
    data_inicial = data_final - timedelta(days=7)
    
    transacoes = api.buscar_transacoes(branch_code, account_number, data_inicial, data_final)
    
    if not transacoes:
        print("❌ Nenhuma transação encontrada")
        return
    
    print(f"✅ Total de transações da API: {len(transacoes)}")
    
    # Mostrar estrutura de uma transação
    print("\n3️⃣ Estrutura da primeira transação (JSON):")
    print("-"*80)
    primeira = transacoes[0]
    for key, value in primeira.items():
        print(f"  {key}: {value}")
    print("-"*80)
    
    # Gerar Excel
    print("\n4️⃣ Gerando Excel...")
    excel_path = api.exportar_transacoes_excel(transacoes, branch_code, account_number)
    
    if excel_path:
        print(f"✅ Excel gerado: {excel_path}")
        
        # Ler Excel e verificar
        print("\n5️⃣ Verificando Excel...")
        df = pd.read_excel(excel_path, header=None)
        
        # Contar linhas de dados (excluindo header e linha vazia)
        # Linha 1: AGENCIA/CONTA
        # Linha 2: vazio
        # Linha 3: Headers
        # Linha 4+: dados (SALDO ANTERIOR + transações)
        total_linhas_dados = len(df) - 3  # Subtrair as 3 primeiras linhas
        total_transacoes_excel = total_linhas_dados - 1  # Subtrair SALDO ANTERIOR
        
        print(f"   Total de linhas no Excel: {len(df)}")
        print(f"   Total de transações no Excel: {total_transacoes_excel}")
        print(f"   Total de transações da API: {len(transacoes)}")
        
        if total_transacoes_excel == len(transacoes):
            print("   ✅ EXCEL OK - Todas as transações estão presentes!")
        else:
            print(f"   ❌ EXCEL INCONSISTENTE - Faltam {len(transacoes) - total_transacoes_excel} transações!")
        
        # Verificar campos
        print("\n   Verificando campos no Excel:")
        print(f"   Colunas: {df.shape[1]}")
        print(f"   Esperado: 6 colunas (Data, vazio, Histórico, Documento, Valor, Saldo)")
        
        # Mostrar amostra
        print("\n   Amostra de dados (primeiras 5 linhas de transações):")
        print(df.iloc[3:8].to_string())
        
        # Verificar se há truncamento de texto
        print("\n   Verificando truncamento de texto...")
        for idx, row in df.iloc[4:].iterrows():  # Pular header e SALDO ANTERIOR
            historico = str(row.iloc[2]) if pd.notna(row.iloc[2]) else ""
            if len(historico) > 100:
                print(f"   ⚠️  Linha {idx+1}: Histórico muito longo ({len(historico)} chars)")
    
    # Gerar PDF
    print("\n6️⃣ Gerando PDF...")
    pdf_path = api.gerar_pdf_extrato(transacoes, branch_code, account_number)
    
    if pdf_path:
        print(f"✅ PDF gerado: {pdf_path}")
        
        # Ler PDF e verificar
        print("\n7️⃣ Verificando PDF...")
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                page = reader.pages[0]
                texto = page.extract_text()
                
                print(f"   Total de caracteres extraídos: {len(texto)}")
                
                # Contar transações no PDF (cada linha tem uma data DD/MM/YYYY)
                import re
                datas_encontradas = re.findall(r'\d{2}/\d{2}/\d{4}', texto)
                # Subtrair datas que não são transações (cabeçalho, saldo, etc)
                total_transacoes_pdf = len([d for d in datas_encontradas if d not in texto[:200]])  # Ignorar header
                
                print(f"   Datas encontradas no PDF: {len(datas_encontradas)}")
                print(f"   Total de transações no PDF (estimado): {total_transacoes_pdf - 1}")  # -1 para SALDO ANTERIOR
                print(f"   Total de transações da API: {len(transacoes)}")
                
                # Verificar se todos os históricos aparecem
                print("\n   Verificando históricos no PDF:")
                historicos_faltantes = []
                for trans in transacoes[:5]:  # Verificar primeiras 5
                    historico = trans.get('transactionName', '')
                    if historico and historico not in texto:
                        historicos_faltantes.append(historico)
                
                if historicos_faltantes:
                    print(f"   ❌ {len(historicos_faltantes)} históricos não encontrados:")
                    for h in historicos_faltantes:
                        print(f"      - {h}")
                else:
                    print("   ✅ Históricos (amostra) encontrados no PDF!")
                
                # Verificar truncamento
                print("\n   Verificando truncamento no PDF:")
                for trans in transacoes:
                    historico = trans.get('transactionName', '')
                    if len(historico) > 45:
                        print(f"   ⚠️  Histórico longo ({len(historico)} chars): {historico[:50]}...")
                        # Verificar se foi truncado
                        if historico[:42] in texto:
                            print(f"      → Aparece truncado no PDF: {historico[:42]}...")
                        elif historico in texto:
                            print(f"      → Aparece completo no PDF!")
                        else:
                            print(f"      → ❌ NÃO ENCONTRADO no PDF!")
                
        except Exception as e:
            print(f"   ❌ Erro ao ler PDF: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print("VERIFICAÇÃO CONCLUÍDA")
    print("="*80)

if __name__ == "__main__":
    verificar_integridade()
