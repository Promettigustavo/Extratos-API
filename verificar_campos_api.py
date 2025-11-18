"""
Script para verificar os campos retornados pela API do Santander
"""

from buscar_extratos_bancarios import SantanderExtratosBancarios
from datetime import datetime, timedelta
import json

# Usar fundo 911_BANK para teste (primeiro da lista que geralmente está configurado)
fundo_id = "911_BANK"
branch_code = "2271"
account_number = "130137784"

# Buscar apenas 1 dia de dados
data_final = datetime.now()
data_inicial = data_final - timedelta(days=1)

print("Verificando campos retornados pela API Santander...")
print(f"   Fundo: {fundo_id}")
print(f"   Periodo: {data_inicial.strftime('%d/%m/%Y')} a {data_final.strftime('%d/%m/%Y')}")
print()

try:
    cliente = SantanderExtratosBancarios(fundo_id)
    resultado = cliente.buscar_transacoes(
        branch_code=branch_code,
        account_number=account_number,
        data_inicial=data_inicial,
        data_final=data_final
    )
    
    if resultado and 'transacoes' in resultado and len(resultado['transacoes']) > 0:
        print(f"OK: {len(resultado['transacoes'])} transacoes encontradas")
        print()
        
        # Mostrar campos da primeira transação
        primeira = resultado['transacoes'][0]
        print("Campos disponiveis na transacao:")
        print(json.dumps(primeira, indent=2, ensure_ascii=False))
        print()
        
        # Verificar se existe campo de horário
        print("Verificando campos de data/horario:")
        for campo in primeira.keys():
            if any(palavra in campo.lower() for palavra in ['date', 'time', 'hora', 'datetime', 'timestamp']):
                print(f"   > {campo}: {primeira[campo]}")
        
        # Verificar especificamente alguns campos possíveis
        campos_possiveis = [
            'transactionDate',
            'transactionDateTime', 
            'bookingDateTime',
            'valueDateTime',
            'completedAuthorisedPaymentDateTime',
            'timestamp',
            'transactionTime'
        ]
        
        print()
        print("Buscando campos especificos de data/hora:")
        for campo in campos_possiveis:
            if campo in primeira:
                print(f"   OK: {campo}: {primeira[campo]}")
            else:
                print(f"   X: {campo}: nao encontrado")
                
    else:
        print("ERRO: Nenhuma transacao encontrada no periodo")
        
except Exception as e:
    print(f"ERRO: {e}")
    import traceback
    traceback.print_exc()
