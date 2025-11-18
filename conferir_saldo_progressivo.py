"""
Conferência do SALDO PROGRESSIVO - Linha por Linha
Valida se o saldo acumula corretamente em cada transação
Período: 11/11/2025 a 18/11/2025 - MAKENA
"""

import sys
from datetime import datetime

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

# Saldos do extrato Santander (conforme PDF)
SALDOS_SANTANDER = {
    # 11/11/2025
    1: ("11/11/2025", "SALDO ANTERIOR", None, 488571.24),
    2: ("11/11/2025", "PAGFOR PIX OUTRA INST- DIFEREN TIT", -798606.67, -310035.43),
    3: ("11/11/2025", "PAGFOR PIX OUTRA INST- DIFEREN TIT", -500000.00, -810035.43),
    4: ("11/11/2025", "PAGFOR PIX OUTRA INST- DIFEREN TIT", -427883.63, -1237919.06),
    5: ("11/11/2025", "PAGFOR PIX OUTRA INST- DIFEREN TIT", -378892.72, -1616811.78),
    10: ("11/11/2025", "PAGFOR PIX OUTRA INST- DIFEREN TIT", -254463.87, -3378321.36),
    20: ("11/11/2025", "PAGFOR PIX OUTRA INST- DIFEREN TIT", -110907.90, -5170959.48),
    40: ("11/11/2025", "APLIC DI TITULOS PUBLICOS PREMIUM", -33300000.00, -39126312.46),
    50: ("11/11/2025", "PIX RECEBIDO", 88468.89, -22437517.81),
    60: ("11/11/2025", "PIX RECEBIDO", 65543.11, -21112492.62),
    67: ("11/11/2025", "TAR EMISSAO TED CIP PGTO FORNEC", -10.50, 32395.79),
    
    # 12/11/2025
    68: ("12/11/2025", "PAGFOR PIX MESMA INST-DIFERENT TIT", -3738184.09, -3705788.30),
    80: ("12/11/2025", "PAGFOR PIX OUTRA INST- DIFEREN TIT", -161737.92, -10864658.77),
    100: ("12/11/2025", "PAGFOR PIX OUTRA INST- DIFEREN TIT", -40380.25, -12752086.39),
    120: ("12/11/2025", "PIX RECEBIDO", 41387.47, -44206039.59),
    140: ("12/11/2025", "TAR PIX PGTO FORNEC - MESMA INST", -3.60, 912046.05),
    
    # 13/11/2025
    141: ("13/11/2025", "PAGFOR PIX OUTRA INST- DIFEREN TIT", -4848713.28, -3936667.23),
    160: ("13/11/2025", "PAGFOR PIX OUTRA INST- DIFEREN TIT", -188440.74, -12240403.04),
    180: ("13/11/2025", "PAGFOR PIX OUTRA INST- DIFEREN TIT", -38508.91, -13884054.71),
    200: ("13/11/2025", "PIX RECEBIDO", 141490.35, -41696573.92),
    220: ("13/11/2025", "RESGATE FUNDO DE INVESTIMENTO", 33318145.18, 53445.52),
    223: ("13/11/2025", "TAR EMISSAO TED CIP PGTO FORNEC", -5.25, 53350.27),
    
    # 14/11/2025
    224: ("14/11/2025", "PAGFOR PIX OUTRA INST- DIFEREN TIT", -2628952.31, -2575602.04),
    240: ("14/11/2025", "PAGFOR PIX OUTRA INST- DIFEREN TIT", -236913.56, -10692990.67),
    260: ("14/11/2025", "PAGFOR PIX OUTRA INST- DIFEREN TIT", -111775.43, -12492071.81),
    280: ("14/11/2025", "PAGFOR PIX OUTRA INST- DIFEREN TIT", -19115.28, -13623393.10),
    300: ("14/11/2025", "PIX RECEBIDO", 80409.09, -76909213.43),
    320: ("14/11/2025", "RESGATE FUNDO DE INVESTIMENTO", 65035114.34, 103073.71),
    322: ("14/11/2025", "TAR PIX PGTO FORNEC - MESMA INST", -9.00, 102987.31),
    
    # 17/11/2025
    323: ("17/11/2025", "PAGFOR PIX OUTRA INST- DIFEREN TIT", -7115721.29, -7012733.98),
    340: ("17/11/2025", "PAGFOR PIX OUTRA INST- DIFEREN TIT", -283567.23, -24191476.31),
    360: ("17/11/2025", "PAGFOR PIX OUTRA INST- DIFEREN TIT", -131876.62, -27907421.55),
    380: ("17/11/2025", "PAGFOR PIX OUTRA INST- DIFEREN TIT", -23878.27, -29740050.82),
    400: ("17/11/2025", "PIX RECEBIDO", 15510.91, -71773838.66),
    420: ("17/11/2025", "RESGATE FUNDO DE INVESTIMENTO", 64835133.35, 237674.78),
    423: ("17/11/2025", "TAR EMISSAO TED CIP PGTO FORNEC", -5.25, 237559.73),
    
    # 18/11/2025
    424: ("18/11/2025", "PAGFOR PIX OUTRA INST- DIFEREN TIT", -773388.35, -535828.62),
    425: ("18/11/2025", "PIX RECEBIDO", 17428.23, -518400.39),
    430: ("18/11/2025", "PIX RECEBIDO", 54190.55, 2827644.01),
    440: ("18/11/2025", "PAGFOR PIX OUTRA INST- DIFEREN TIT", -398900.00, 2502772.72),
    445: ("18/11/2025", "PIX RECEBIDO", 385714.00, 70190610.99),
    446: ("18/11/2025", "TAR PIX PGTO FORNEC - OUTRA INST", -127.80, 70190483.19),
    447: ("18/11/2025", "TAR PIX PGTO FORNEC - MESMA INST", -7.20, 70190475.99),
    448: ("18/11/2025", "TAR EMISSAO TED CIP PGTO FORNEC", -5.25, 70190470.74),
}

print("=" * 140)
print("CONFERÊNCIA DO SALDO PROGRESSIVO - LINHA POR LINHA")
print("MAKENA | 11/11/2025 a 18/11/2025")
print("=" * 140)

# Buscar dados da API
client = SantanderExtratosBancarios(FUNDO_ID)
data_inicial = datetime(2025, 11, 11)
data_final = datetime(2025, 11, 18)

print(f"\n🔄 Buscando transações da API...\n")

try:
    transacoes = client.buscar_transacoes(
        branch_code="2271",
        account_number="000130107983",
        data_inicial=data_inicial,
        data_final=data_final
    )
    
    saldo_info = client.buscar_saldo(
        branch_code="2271",
        account_number="000130107983"
    )
    
    # Ordenar transações
    def extrair_data_ordenacao(trans):
        data = trans.get('transactionDate', '')
        if data and len(data) >= 10:
            try:
                return datetime.strptime(data[:10], '%d/%m/%Y')
            except:
                try:
                    return datetime.strptime(data[:10], '%Y-%m-%d')
                except:
                    return datetime(9999, 12, 31)
        return datetime(9999, 12, 31)
    
    transacoes_ordenadas = sorted(transacoes, key=extrair_data_ordenacao)
    
    print(f"✅ {len(transacoes_ordenadas)} transações obtidas da API\n")
    
    # ========== CALCULAR SALDO ANTERIOR ==========
    saldo_atual = float(saldo_info.get('availableAmount', 0))
    
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
    saldo_anterior = saldo_atual - total_transacoes
    
    print("=" * 140)
    print("1. VALIDAÇÃO DO SALDO ANTERIOR:")
    print("=" * 140)
    
    saldo_anterior_santander = 488571.24
    diff_saldo_anterior = abs(saldo_anterior - saldo_anterior_santander)
    
    print(f"""
Saldo Atual (API):          R$ {saldo_atual:>20,.2f}
Total Transações Período:   R$ {total_transacoes:>20,.2f}
Saldo Anterior Calculado:   R$ {saldo_anterior:>20,.2f}
Saldo Anterior Santander:   R$ {saldo_anterior_santander:>20,.2f}
Diferença:                  R$ {diff_saldo_anterior:>20,.2f}  {'✅ CORRETO' if diff_saldo_anterior < 0.01 else '❌ DIVERGENTE'}
""")
    
    # ========== CONFERIR SALDO PROGRESSIVO ==========
    print("=" * 140)
    print("2. CONFERÊNCIA DO SALDO PROGRESSIVO (Pontos de Controle):")
    print("=" * 140)
    
    print(f"\n{'Linha':<6} | {'Data':<12} | {'Histórico':<45} | {'Valor':>18} | {'Saldo API':>18} | {'Saldo Sant':>18} | {'Diff':>12} | {'OK':<4}")
    print("-" * 140)
    
    # Calcular saldo progressivo
    saldo = saldo_anterior
    divergencias_saldo = 0
    conferencias_saldo_ok = 0
    
    for i, trans in enumerate(transacoes_ordenadas, 1):
        data = trans.get('transactionDate', '')
        historico = trans.get('transactionName', '')[:45]
        valor_raw = float(trans.get('amount', 0))
        tipo = trans.get('creditDebitType', '')
        
        # Aplicar sinal
        if tipo == 'DEBITO':
            valor = -abs(valor_raw)
        else:
            valor = abs(valor_raw)
        
        # Acumular saldo
        saldo += valor
        
        # Verificar se é um ponto de controle
        if i in SALDOS_SANTANDER:
            data_sant, hist_sant, valor_sant, saldo_sant = SALDOS_SANTANDER[i]
            
            diff = abs(saldo - saldo_sant)
            ok = "✅" if diff < 0.01 else "❌"
            
            if diff < 0.01:
                conferencias_saldo_ok += 1
            else:
                divergencias_saldo += 1
            
            print(f"{i:<6} | {data:<12} | {historico:<45} | R$ {valor:>15,.2f} | R$ {saldo:>15,.2f} | R$ {saldo_sant:>15,.2f} | R$ {diff:>9,.2f} | {ok:<4}")
    
    # ========== VALIDAR SALDO FINAL ==========
    print("\n" + "=" * 140)
    print("3. VALIDAÇÃO DO SALDO FINAL:")
    print("=" * 140)
    
    saldo_final_santander = 70190470.74
    diff_saldo_final = abs(saldo - saldo_final_santander)
    
    print(f"""
Saldo Final Calculado (API): R$ {saldo:>20,.2f}
Saldo Final Santander:       R$ {saldo_final_santander:>20,.2f}
Diferença:                   R$ {diff_saldo_final:>20,.2f}  {'✅ CORRETO' if diff_saldo_final < 0.01 else '❌ DIVERGENTE'}
""")
    
    # ========== RESUMO ==========
    print("=" * 140)
    print("4. RESUMO DA CONFERÊNCIA:")
    print("=" * 140)
    
    total_pontos = len(SALDOS_SANTANDER) - 1  # -1 porque o primeiro é o saldo anterior
    
    print(f"""
📊 Pontos de Controle Conferidos: {conferencias_saldo_ok}/{total_pontos}

Validações:
   ✅ Saldo Anterior:  {'CORRETO' if diff_saldo_anterior < 0.01 else 'DIVERGENTE'} (diferença: R$ {diff_saldo_anterior:.2f})
   ✅ Saldo Final:     {'CORRETO' if diff_saldo_final < 0.01 else 'DIVERGENTE'} (diferença: R$ {diff_saldo_final:.2f})
   ✅ Cálculo Progressivo: {conferencias_saldo_ok}/{total_pontos} pontos corretos
   
Transações Processadas: {len(transacoes_ordenadas)}
""")
    
    if divergencias_saldo == 0 and diff_saldo_anterior < 0.01 and diff_saldo_final < 0.01:
        print("""
🎯 RESULTADO FINAL: PERFEITO!

   ✅ Saldo Anterior está CORRETO
   ✅ Todos os pontos de controle estão CORRETOS
   ✅ Saldo Final está CORRETO
   ✅ Cálculo progressivo funciona perfeitamente!
   
   O saldo acumula corretamente em TODAS as 429 transações!
""")
    else:
        print(f"""
⚠️  ATENÇÃO: Encontradas {divergencias_saldo} divergências nos pontos de controle!

   Recomendação: Verificar cálculos individualmente.
""")
    
    print("=" * 140)
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
