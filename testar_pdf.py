"""
Teste para verificar problema no PDF
"""

import traceback
from buscar_extratos_bancarios import SantanderExtratosBancarios
from datetime import datetime, timedelta

# Configurar ambiente sem verbose
import buscar_extratos_bancarios
buscar_extratos_bancarios.VERBOSE = True

print("Testando geracao de PDF...")

try:
    # Usar fundo que sabemos que funciona  
    fundo_id = "911_BANK"  # Primeiro da lista, geralmente configurado
    branch_code = "2271"  
    account_number = "130137784"
    
    # Período pequeno para teste
    data_final = datetime.now()
    data_inicial = data_final - timedelta(days=3)
    
    print(f"Fundo: {fundo_id}")
    print(f"Periodo: {data_inicial.strftime('%d/%m/%Y')} a {data_final.strftime('%d/%m/%Y')}")
    print()
    
    cliente = SantanderExtratosBancarios(fundo_id)
    
    # Buscar transações
    print("Buscando transacoes...")
    resultado = cliente.buscar_transacoes(
        branch_code=branch_code,
        account_number=account_number,
        data_inicial=data_inicial,
        data_final=data_final
    )
    
    if not resultado or 'transacoes' not in resultado:
        print("AVISO: Nenhuma transacao da API, usando dados mock para testar PDF...")
        # Criar dados mock para testar se PDF funciona
        transacoes = [
            {
                'transactionDate': '2025-11-17',
                'transactionName': 'PIX RECEBIDO TESTE',
                'documentNumber': '000001',
                'amount': 100.50,
                'creditDebitType': 'CREDITO'
            },
            {
                'transactionDate': '2025-11-16', 
                'transactionName': 'TARIFA TESTE',
                'documentNumber': '000002',
                'amount': 5.00,
                'creditDebitType': 'DEBITO'
            }
        ]
        saldo_info = {'availableAmount': 1000.00}
    else:
        transacoes = resultado['transacoes']
        saldo_info = resultado.get('saldo_info')
    
    print(f"Transacoes encontradas: {len(transacoes)}")
    
    # Testar geração do PDF
    print("Gerando PDF...")
    pdf_path = cliente.gerar_pdf_extrato(
        transacoes=transacoes,
        branch_code=branch_code,
        account_number=account_number,
        saldo_info=saldo_info,
        data_inicial=data_inicial,
        data_final=data_final
    )
    
    if pdf_path:
        print(f"PDF gerado com sucesso: {pdf_path}")
    else:
        print("ERRO: PDF nao foi gerado")
        
except Exception as e:
    print(f"ERRO: {e}")
    traceback.print_exc()