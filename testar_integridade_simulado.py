"""
Teste de integridade com dados simulados
Verifica se todos os campos do JSON aparecem no Excel e PDF
"""

import pandas as pd
import PyPDF2
from datetime import datetime
import os
import json

def criar_transacoes_teste():
    """Cria transações de teste simulando resposta da API"""
    transacoes = [
        {
            "transactionDate": "2025-11-12T00:00:00-03:00",
            "transactionName": "TED RECEBIDA 44650156000193",
            "documentNumber": "000000",
            "amount": 202523.67,
            "creditDebitType": "CREDITO",
            "transactionId": "TEST001"
        },
        {
            "transactionDate": "2025-11-13T00:00:00-03:00",
            "transactionName": "TRANSF VALORES P/C/C MESMO TITULAR PARA: 2271.13.017871-2",
            "documentNumber": "551791",
            "amount": 202523.67,
            "creditDebitType": "DEBITO",
            "transactionId": "TEST002"
        },
        {
            "transactionDate": "2025-11-13T00:00:00-03:00",
            "transactionName": "HISTÓRICO MUITO LONGO PARA TESTAR TRUNCAMENTO - Este é um texto extremamente longo que deve ser verificado se está sendo cortado ou não nos arquivos de saída tanto no Excel quanto no PDF",
            "documentNumber": "999999",
            "amount": 1000.00,
            "creditDebitType": "CREDITO",
            "transactionId": "TEST003"
        }
    ]
    return transacoes

def testar_integridade():
    """Testa integridade dos dados"""
    
    print("="*80)
    print("TESTE DE INTEGRIDADE COM DADOS SIMULADOS")
    print("="*80)
    
    # Criar transações de teste
    transacoes = criar_transacoes_teste()
    print(f"\n✅ {len(transacoes)} transações de teste criadas")
    
    # Mostrar JSON
    print("\n📋 JSON de entrada:")
    print("-"*80)
    for i, trans in enumerate(transacoes, 1):
        print(f"\nTransação {i}:")
        print(json.dumps(trans, indent=2, ensure_ascii=False))
    print("-"*80)
    
    # Importar e testar
    from buscar_extratos_bancarios import SantanderExtratosBancarios
    
    fundo_id = "CONDOLIVRE FIDC"
    api = SantanderExtratosBancarios(fundo_id)
    
    branch_code = "2271"
    account_number = "000130163172"
    
    # Gerar Excel
    print("\n📊 Gerando Excel...")
    excel_path = api.exportar_transacoes_excel(transacoes, branch_code, account_number, pasta_saida=".")
    
    if excel_path:
        print(f"✅ Excel: {excel_path}")
        
        # Verificar Excel
        print("\n🔍 Verificando Excel...")
        df = pd.read_excel(excel_path, header=None)
        
        print(f"   Total de linhas: {len(df)}")
        print(f"   Transações esperadas: {len(transacoes)}")
        print(f"   Transações no Excel: {len(df) - 4}")  # -3 header - 1 saldo anterior
        
        print("\n   Conteúdo do Excel:")
        print(df.to_string())
        
        # Verificar campos específicos
        print("\n   Verificando campos:")
        for i, trans in enumerate(transacoes):
            row_idx = i + 4  # Linha no Excel (0-indexed + 3 header + 1 saldo anterior)
            if row_idx < len(df):
                row = df.iloc[row_idx]
                historico_excel = str(row.iloc[2]) if pd.notna(row.iloc[2]) else ""
                historico_json = trans.get('transactionName', '')
                
                if historico_json == historico_excel:
                    print(f"   ✅ Transação {i+1}: Histórico OK")
                else:
                    print(f"   ❌ Transação {i+1}: Histórico DIFERENTE!")
                    print(f"      JSON:  {historico_json}")
                    print(f"      Excel: {historico_excel}")
                    if len(historico_json) > len(historico_excel):
                        print(f"      ⚠️  TRUNCADO! {len(historico_json)} → {len(historico_excel)} chars")
    
    # Gerar PDF
    print("\n📄 Gerando PDF...")
    pdf_path = api.gerar_pdf_extrato(transacoes, branch_code, account_number, pasta_saida=".")
    
    if pdf_path:
        print(f"✅ PDF: {pdf_path}")
        
        # Verificar PDF
        print("\n🔍 Verificando PDF...")
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                page = reader.pages[0]
                texto = page.extract_text()
                
                print(f"   Total de caracteres: {len(texto)}")
                
                print("\n   Verificando campos:")
                for i, trans in enumerate(transacoes, 1):
                    historico = trans.get('transactionName', '')
                    
                    if historico in texto:
                        print(f"   ✅ Transação {i}: Histórico encontrado COMPLETO")
                    elif historico[:42] in texto:  # Verifica se foi truncado
                        print(f"   ⚠️  Transação {i}: Histórico TRUNCADO!")
                        print(f"      Original: {historico}")
                        print(f"      Truncado: {historico[:42]}...")
                    else:
                        print(f"   ❌ Transação {i}: Histórico NÃO ENCONTRADO!")
                        print(f"      Buscado: {historico}")
                
                # Mostrar texto extraído
                print("\n   Texto extraído do PDF:")
                print("-"*80)
                print(texto[:1000])  # Primeiros 1000 chars
                print("-"*80)
                
        except Exception as e:
            print(f"   ❌ Erro ao ler PDF: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print("TESTE CONCLUÍDO")
    print("="*80)

if __name__ == "__main__":
    testar_integridade()
