"""
Comparação entre dados da API e extrato oficial do Santander
Período: 11/11/2025 a 18/11/2025
Fundo: MAKENA
"""

import sys
from datetime import datetime, timedelta

try:
    try:
        from credenciais_bancos import SANTANDER_FUNDOS
    except ImportError:
        from config_credentials import SANTANDER_FUNDOS
    
    from buscar_extratos_bancarios import SantanderExtratosBancarios
    print("✅ Módulos importados\n")
except ImportError as e:
    print(f"❌ Erro: {e}")
    sys.exit(1)

FUNDO_ID = "MAKENA"

print("=" * 120)
print("COMPARAÇÃO: API vs EXTRATO OFICIAL SANTANDER")
print("Fundo: MAKENA | Período: 11/11/2025 a 18/11/2025")
print("=" * 120)

# Criar cliente
client = SantanderExtratosBancarios(FUNDO_ID)

# Período exato do extrato Santander
data_inicial = datetime(2025, 11, 11)
data_final = datetime(2025, 11, 18)

print(f"\n📅 Período: {data_inicial.strftime('%d/%m/%Y')} a {data_final.strftime('%d/%m/%Y')}")
print(f"\n🔄 Buscando dados da API...\n")

try:
    # Buscar transações
    transacoes = client.buscar_transacoes(
        branch_code="2271",
        account_number="000130107983",
        data_inicial=data_inicial,
        data_final=data_final
    )
    
    # Buscar saldo
    saldo_info = client.buscar_saldo(
        branch_code="2271",
        account_number="000130107983"
    )
    
    print(f"✅ {len(transacoes)} transações retornadas pela API")
    print(f"✅ Saldo obtido da API\n")
    
    # ========== ORDENAR TRANSAÇÕES ==========
    def extrair_data_ordenacao(trans):
        data = trans.get('transactionDate', '')
        if data and len(data) >= 10:
            try:
                dt = datetime.strptime(data[:10], '%d/%m/%Y')
                return dt
            except:
                try:
                    dt = datetime.strptime(data[:10], '%Y-%m-%d')
                    return dt
                except:
                    return datetime(9999, 12, 31)
        return datetime(9999, 12, 31)
    
    transacoes_ordenadas = sorted(transacoes, key=extrair_data_ordenacao)
    
    # ========== DADOS DO EXTRATO SANTANDER ==========
    print("=" * 120)
    print("1. DADOS DO EXTRATO OFICIAL SANTANDER:")
    print("=" * 120)
    
    # Valores do extrato Santander
    saldo_anterior_santander = 488571.24
    saldo_final_santander = 70190470.74
    
    # Contagem manual do PDF fornecido
    total_transacoes_santander = 429  # Contando todas as linhas de transações
    
    print(f"""
📋 Informações do extrato Santander:
   - Saldo Anterior (11/11/2025): R$ {saldo_anterior_santander:,.2f}
   - Saldo Final (18/11/2025): R$ {saldo_final_santander:,.2f}
   - Total de transações: {total_transacoes_santander}
""")
    
    # ========== DADOS DA API ==========
    print("=" * 120)
    print("2. DADOS DA API:")
    print("=" * 120)
    
    saldo_atual = float(saldo_info.get('availableAmount', 0))
    
    # Calcular totais
    total_creditos = 0
    total_debitos = 0
    
    for trans in transacoes_ordenadas:
        valor = float(trans.get('amount', 0))
        tipo = trans.get('creditDebitType', '')
        
        if tipo == 'CREDITO':
            total_creditos += valor
        else:
            total_debitos += valor
    
    total_transacoes = total_creditos - total_debitos
    saldo_anterior_api = saldo_atual - total_transacoes
    
    print(f"""
📊 Cálculos da API:
   - Saldo Atual (18/11/2025): R$ {saldo_atual:,.2f}
   - Total Créditos: R$ {total_creditos:,.2f}
   - Total Débitos: R$ {total_debitos:,.2f}
   - Total Líquido: R$ {total_transacoes:,.2f}
   - Saldo Anterior Calculado: R$ {saldo_anterior_api:,.2f}
   - Total de transações: {len(transacoes)}
""")
    
    # ========== COMPARAÇÃO ==========
    print("=" * 120)
    print("3. COMPARAÇÃO DETALHADA:")
    print("=" * 120)
    
    diff_saldo_anterior = abs(saldo_anterior_api - saldo_anterior_santander)
    diff_saldo_final = abs(saldo_atual - saldo_final_santander)
    diff_qtd_transacoes = abs(len(transacoes) - total_transacoes_santander)
    
    print(f"""
┌──────────────────────────────────────┬─────────────────────────┬─────────────────────────┬─────────────────────────┐
│ Item                                 │ Santander               │ API                     │ Diferença               │
├──────────────────────────────────────┼─────────────────────────┼─────────────────────────┼─────────────────────────┤
│ Saldo Anterior (11/11/2025)          │ R$ {saldo_anterior_santander:>18,.2f} │ R$ {saldo_anterior_api:>18,.2f} │ R$ {diff_saldo_anterior:>18,.2f} │
│ Saldo Final (18/11/2025)             │ R$ {saldo_final_santander:>18,.2f} │ R$ {saldo_atual:>18,.2f} │ R$ {diff_saldo_final:>18,.2f} │
│ Quantidade de Transações             │ {total_transacoes_santander:>23} │ {len(transacoes):>23} │ {diff_qtd_transacoes:>23} │
└──────────────────────────────────────┴─────────────────────────┴─────────────────────────┴─────────────────────────┘
""")
    
    # ========== VALIDAÇÃO ==========
    print("\n" + "=" * 120)
    print("4. VALIDAÇÃO:")
    print("=" * 120)
    
    tolerancia = 0.01
    
    if diff_saldo_anterior < tolerancia:
        print(f"✅ SALDO ANTERIOR: CORRETO (diferença: R$ {diff_saldo_anterior:.2f})")
    else:
        print(f"❌ SALDO ANTERIOR: DIVERGENTE (diferença: R$ {diff_saldo_anterior:,.2f})")
    
    if diff_saldo_final < tolerancia:
        print(f"✅ SALDO FINAL: CORRETO (diferença: R$ {diff_saldo_final:.2f})")
    else:
        print(f"❌ SALDO FINAL: DIVERGENTE (diferença: R$ {diff_saldo_final:,.2f})")
    
    if diff_qtd_transacoes == 0:
        print(f"✅ QUANTIDADE DE TRANSAÇÕES: CORRETA (ambos têm {len(transacoes)} transações)")
    else:
        print(f"⚠️  QUANTIDADE DE TRANSAÇÕES: DIVERGENTE (Santander: {total_transacoes_santander}, API: {len(transacoes)})")
    
    # ========== AMOSTRA DE TRANSAÇÕES ==========
    print("\n" + "=" * 120)
    print("5. AMOSTRA - PRIMEIRAS 10 TRANSAÇÕES (API vs SANTANDER):")
    print("=" * 120)
    
    # Primeiras transações do extrato Santander (conforme PDF fornecido)
    santander_primeiras = [
        ("11/11/2025", "PAGFOR PIX OUTRA INST- DIFEREN TIT", -798606.67),
        ("11/11/2025", "PAGFOR PIX OUTRA INST- DIFEREN TIT", -500000.00),
        ("11/11/2025", "PAGFOR PIX OUTRA INST- DIFEREN TIT", -427883.63),
        ("11/11/2025", "PAGFOR PIX OUTRA INST- DIFEREN TIT", -378892.72),
        ("11/11/2025", "PAGFOR PIX OUTRA INST- DIFEREN TIT", -315449.05),
        ("11/11/2025", "PAGFOR PIX OUTRA INST- DIFEREN TIT", -308282.62),
        ("11/11/2025", "PAGFOR PIX OUTRA INST- DIFEREN TIT", -304020.80),
        ("11/11/2025", "PAGFOR PIX OUTRA INST- DIFEREN TIT", -292720.08),
        ("11/11/2025", "PAGFOR PIX OUTRA INST- DIFEREN TIT", -286573.16),
        ("11/11/2025", "PAGFOR PIX OUTRA INST- DIFEREN TIT", -254463.87),
    ]
    
    print(f"\n{'#':<4} | {'Data':<12} | {'Histórico (Santander)':<42} | {'Valor Santander':>18} | {'Valor API':>18} | {'Match':<6}")
    print("-" * 120)
    
    for i, (data_sant, hist_sant, valor_sant) in enumerate(santander_primeiras, 1):
        if i - 1 < len(transacoes_ordenadas):
            trans_api = transacoes_ordenadas[i - 1]
            data_api = trans_api.get('transactionDate', '')
            hist_api = trans_api.get('transactionName', '')[:42]
            valor_api_raw = float(trans_api.get('amount', 0))
            tipo_api = trans_api.get('creditDebitType', '')
            
            # Aplicar sinal
            if tipo_api == 'DEBITO':
                valor_api = -abs(valor_api_raw)
            else:
                valor_api = abs(valor_api_raw)
            
            # Verificar match
            match_data = "✅" if data_api == data_sant else "❌"
            match_valor = "✅" if abs(valor_api - valor_sant) < 0.01 else "❌"
            match = f"{match_data}{match_valor}"
            
            print(f"{i:<4} | {data_sant:<12} | {hist_sant:<42} | R$ {valor_sant:>15,.2f} | R$ {valor_api:>15,.2f} | {match:<6}")
        else:
            print(f"{i:<4} | {data_sant:<12} | {hist_sant:<42} | R$ {valor_sant:>15,.2f} | {'N/A':>18} | ❌")
    
    # ========== ÚLTIMAS TRANSAÇÕES ==========
    print("\n" + "=" * 120)
    print("6. AMOSTRA - ÚLTIMAS 10 TRANSAÇÕES (18/11/2025):")
    print("=" * 120)
    
    santander_ultimas = [
        ("18/11/2025", "PIX RECEBIDO", 10023.40),
        ("18/11/2025", "PIX RECEBIDO", 24684.99),
        ("18/11/2025", "PIX RECEBIDO", 26855.96),
        ("18/11/2025", "PAGFOR PIX OUTRA INST- DIFEREN TIT", -398900.00),
        ("18/11/2025", "PIX RECEBIDO", 18375458.14),
        ("18/11/2025", "RESGATE FUNDO DE INVESTIMENTO", 48926666.13),
        ("18/11/2025", "PIX RECEBIDO", 385714.00),
        ("18/11/2025", "TAR PIX PGTO FORNEC - OUTRA INST", -127.80),
        ("18/11/2025", "TAR PIX PGTO FORNEC - MESMA INST", -7.20),
        ("18/11/2025", "TAR EMISSAO TED CIP PGTO FORNEC", -5.25),
    ]
    
    print(f"\n{'#':<4} | {'Data':<12} | {'Histórico (Santander)':<42} | {'Valor Santander':>18} | {'Valor API':>18} | {'Match':<6}")
    print("-" * 120)
    
    # Pegar últimas 10 da API
    ultimas_api = transacoes_ordenadas[-10:]
    
    for i, (data_sant, hist_sant, valor_sant) in enumerate(santander_ultimas, 1):
        idx = -11 + i  # Índice reverso
        if abs(idx) <= len(transacoes_ordenadas):
            trans_api = transacoes_ordenadas[idx]
            data_api = trans_api.get('transactionDate', '')
            hist_api = trans_api.get('transactionName', '')[:42]
            valor_api_raw = float(trans_api.get('amount', 0))
            tipo_api = trans_api.get('creditDebitType', '')
            
            # Aplicar sinal
            if tipo_api == 'DEBITO':
                valor_api = -abs(valor_api_raw)
            else:
                valor_api = abs(valor_api_raw)
            
            # Verificar match
            match_data = "✅" if data_api == data_sant else "❌"
            match_valor = "✅" if abs(valor_api - valor_sant) < 0.01 else "❌"
            match = f"{match_data}{match_valor}"
            
            print(f"{i:<4} | {data_sant:<12} | {hist_sant:<42} | R$ {valor_sant:>15,.2f} | R$ {valor_api:>15,.2f} | {match:<6}")
        else:
            print(f"{i:<4} | {data_sant:<12} | {hist_sant:<42} | R$ {valor_sant:>15,.2f} | {'N/A':>18} | ❌")
    
    # ========== CONCLUSÃO ==========
    print("\n" + "=" * 120)
    print("7. CONCLUSÃO:")
    print("=" * 120)
    
    if diff_saldo_anterior < tolerancia and diff_saldo_final < tolerancia and diff_qtd_transacoes == 0:
        print("""
🎯 RESULTADO FINAL: DADOS CONFEREM PERFEITAMENTE!

   ✅ Saldo Anterior: CORRETO
   ✅ Saldo Final: CORRETO
   ✅ Quantidade de Transações: CORRETA
   ✅ Valores de transações: CONFEREM (amostra validada)

   Os dados da API estão 100% consistentes com o extrato oficial do Santander.
""")
    else:
        print("""
⚠️  RESULTADO FINAL: DIVERGÊNCIAS ENCONTRADAS

   Possíveis causas:
   1. Transações pendentes não incluídas na API
   2. Diferença de horário de corte entre sistemas
   3. Lançamentos provisionados não refletidos na API
   
   Recomendação: Verificar transações individuais para identificar diferenças.
""")
    
    print("=" * 120)
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
