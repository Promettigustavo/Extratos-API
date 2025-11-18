"""
Teste de Validação de Saldos - Dados Reais da API
Busca extratos do MAKENA e valida cálculos de saldo
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

print("=" * 100)
print("VALIDAÇÃO DE CÁLCULO DE SALDOS - MAKENA")
print("=" * 100)

# Criar cliente
client = SantanderExtratosBancarios(FUNDO_ID)

# Período: últimos 7 dias (mais rápido para teste)
data_final = datetime.now()
data_inicial = data_final - timedelta(days=7)

print(f"\n📅 Período: {data_inicial.strftime('%d/%m/%Y')} a {data_final.strftime('%d/%m/%Y')}")
print(f"\n🔄 Buscando transações e saldo...\n")

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
    
    print(f"✅ {len(transacoes)} transações encontradas")
    print(f"✅ Saldo obtido da API\n")
    
    if not transacoes:
        print("⚠️  Nenhuma transação encontrada")
        sys.exit(0)
    
    # ========== ANÁLISE DO SALDO DA API ==========
    print("=" * 100)
    print("1. SALDO DA API:")
    print("=" * 100)
    
    saldo_atual = float(saldo_info.get('availableAmount', 0))
    saldo_bloqueado = float(saldo_info.get('blockedAmount', 0))
    
    print(f"\n💰 Saldo Disponível (availableAmount): R$ {saldo_atual:,.2f}")
    print(f"🔒 Saldo Bloqueado (blockedAmount): R$ {saldo_bloqueado:,.2f}")
    print(f"📊 Saldo Total: R$ {saldo_atual + saldo_bloqueado:,.2f}")
    
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
    
    # ========== CALCULAR TOTAL DO PERÍODO ==========
    print("\n" + "=" * 100)
    print("2. TOTAL DE TRANSAÇÕES DO PERÍODO:")
    print("=" * 100)
    
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
    
    print(f"\n💚 Total Créditos: R$ {total_creditos:,.2f}")
    print(f"❤️  Total Débitos: R$ {total_debitos:,.2f}")
    print(f"📊 Total Líquido: R$ {total_transacoes:,.2f}")
    
    # ========== CALCULAR SALDO ANTERIOR ==========
    print("\n" + "=" * 100)
    print("3. CÁLCULO DO SALDO ANTERIOR:")
    print("=" * 100)
    
    saldo_anterior = saldo_atual - total_transacoes
    
    print(f"\nFórmula: Saldo Anterior = Saldo Atual - Total Transações")
    print(f"         Saldo Anterior = {saldo_atual:,.2f} - {total_transacoes:,.2f}")
    print(f"         Saldo Anterior = R$ {saldo_anterior:,.2f}")
    
    # ========== VALIDAR SALDO PROGRESSIVO ==========
    print("\n" + "=" * 100)
    print("4. VALIDAÇÃO DO SALDO PROGRESSIVO:")
    print("=" * 100)
    
    print(f"\nMostrando primeiras 10 transações com cálculo de saldo:")
    print("-" * 100)
    print(f"{'Data':<12} | {'Histórico':<40} | {'Valor (R$)':>15} | {'Saldo (R$)':>15}")
    print("-" * 100)
    
    # Linha de saldo anterior
    primeira_data = transacoes_ordenadas[0].get('transactionDate', '')
    print(f"{primeira_data:<12} | {'SALDO ANTERIOR':<40} | {'':<15} | {saldo_anterior:>15,.2f}")
    
    # Calcular saldo progressivo
    saldo = saldo_anterior
    for i, trans in enumerate(transacoes_ordenadas[:10], 1):
        data = trans.get('transactionDate', '')
        historico = trans.get('transactionName', '')[:40]
        valor = float(trans.get('amount', 0))
        tipo = trans.get('creditDebitType', '')
        
        # Aplicar sinal
        if tipo == 'DEBITO':
            valor_com_sinal = -abs(valor)
        else:
            valor_com_sinal = abs(valor)
        
        saldo += valor_com_sinal
        
        print(f"{data:<12} | {historico:<40} | {valor_com_sinal:>15,.2f} | {saldo:>15,.2f}")
    
    if len(transacoes_ordenadas) > 10:
        print(f"\n... ({len(transacoes_ordenadas) - 10} transações omitidas) ...")
        
        # Mostrar últimas 5
        print("\nÚltimas 5 transações:")
        print("-" * 100)
        print(f"{'Data':<12} | {'Histórico':<40} | {'Valor (R$)':>15} | {'Saldo (R$)':>15}")
        print("-" * 100)
        
        # Recalcular saldo até o final
        saldo = saldo_anterior
        for trans in transacoes_ordenadas:
            valor = float(trans.get('amount', 0))
            tipo = trans.get('creditDebitType', '')
            if tipo == 'DEBITO':
                saldo -= abs(valor)
            else:
                saldo += abs(valor)
        
        # Mostrar últimas 5
        saldo_temp = saldo_anterior
        for trans in transacoes_ordenadas[:-5]:
            valor = float(trans.get('amount', 0))
            tipo = trans.get('creditDebitType', '')
            if tipo == 'DEBITO':
                saldo_temp -= abs(valor)
            else:
                saldo_temp += abs(valor)
        
        for trans in transacoes_ordenadas[-5:]:
            data = trans.get('transactionDate', '')
            historico = trans.get('transactionName', '')[:40]
            valor = float(trans.get('amount', 0))
            tipo = trans.get('creditDebitType', '')
            
            if tipo == 'DEBITO':
                valor_com_sinal = -abs(valor)
            else:
                valor_com_sinal = abs(valor)
            
            saldo_temp += valor_com_sinal
            print(f"{data:<12} | {historico:<40} | {valor_com_sinal:>15,.2f} | {saldo_temp:>15,.2f}")
    
    # ========== VALIDAÇÃO FINAL ==========
    print("\n" + "=" * 100)
    print("5. VALIDAÇÃO FINAL:")
    print("=" * 100)
    
    saldo_final_calculado = saldo_anterior + total_transacoes
    
    print(f"\n✅ Saldo Anterior: R$ {saldo_anterior:,.2f}")
    print(f"✅ Total do Período: R$ {total_transacoes:,.2f}")
    print(f"✅ Saldo Final (calculado): R$ {saldo_final_calculado:,.2f}")
    print(f"✅ Saldo Atual (API): R$ {saldo_atual:,.2f}")
    
    diferenca = abs(saldo_final_calculado - saldo_atual)
    
    if diferenca < 0.01:
        print(f"\n🎯 SUCESSO! Saldos conferem (diferença: R$ {diferenca:.2f})")
    else:
        print(f"\n⚠️  ATENÇÃO! Diferença encontrada: R$ {diferenca:,.2f}")
        print(f"   Isso pode indicar:")
        print(f"   - Transações fora do período não consideradas")
        print(f"   - Erro no cálculo de débito/crédito")
        print(f"   - Saldo bloqueado não considerado")
    
    print("\n" + "=" * 100)
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
