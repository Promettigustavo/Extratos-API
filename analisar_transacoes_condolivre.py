"""Análise detalhada das transações da conta 130176356 no período 07-14/nov"""

import pandas as pd
from datetime import datetime

print("="*80)
print("ANÁLISE: CONDOLIVRE CONTA 130176356 - PERÍODO 07-14 NOV 2025")
print("="*80)

arquivo = "exportar-Santander - Extrato 14 de novembro de 2025-2271-130176356 (1).xls"

try:
    df = pd.read_excel(arquivo, header=None)
    
    print(f"📄 Arquivo: {arquivo}")
    print(f"📊 Total de linhas: {len(df)}")
    
    print(f"\n📋 Estrutura do arquivo:")
    for i, row in df.iterrows():
        valores = [str(v) if pd.notna(v) else '' for v in row]
        print(f"   L{i+1}: {valores}")
    
    print(f"\n🔍 ANÁLISE DAS TRANSAÇÕES:")
    print("-"*60)
    
    # Analisar linha por linha para encontrar transações
    transacoes_encontradas = []
    
    for i, row in df.iterrows():
        linha = [str(v) if pd.notna(v) else '' for v in row]
        
        # Verificar se é linha de transação (tem data)
        if len(linha) > 0 and linha[0]:
            try:
                # Tentar converter para data
                if '/' in str(linha[0]):
                    data_str = str(linha[0])
                    data = datetime.strptime(data_str, '%d/%m/%Y')
                    
                    transacao = {
                        'linha': i + 1,
                        'data': data,
                        'data_str': data_str,
                        'historico': linha[2] if len(linha) > 2 else '',
                        'documento': linha[3] if len(linha) > 3 else '',
                        'valor': linha[4] if len(linha) > 4 else '',
                        'saldo': linha[5] if len(linha) > 5 else ''
                    }
                    transacoes_encontradas.append(transacao)
                    
            except ValueError:
                # Não é data válida
                pass
    
    print(f"💰 Total de transações encontradas: {len(transacoes_encontradas)}")
    
    # Filtrar por período 07-14 novembro 2025
    periodo_inicio = datetime(2025, 11, 7)
    periodo_fim = datetime(2025, 11, 14)
    
    transacoes_periodo = []
    for t in transacoes_encontradas:
        if periodo_inicio <= t['data'] <= periodo_fim:
            transacoes_periodo.append(t)
    
    print(f"📅 Transações no período 07-14/nov/2025: {len(transacoes_periodo)}")
    
    if transacoes_periodo:
        print(f"\n✅ TRANSAÇÕES ENCONTRADAS NO PERÍODO:")
        print("="*60)
        
        for i, t in enumerate(transacoes_periodo, 1):
            print(f"\n🔹 Transação {i}:")
            print(f"   📅 Data: {t['data_str']}")
            print(f"   📝 Histórico: {t['historico'][:50]}...")
            print(f"   🧾 Documento: {t['documento']}")
            print(f"   💰 Valor: R$ {t['valor']}")
            print(f"   💳 Saldo: R$ {t['saldo']}")
            
            # Verificar tipo de transação
            historico = t['historico'].upper()
            if 'TED' in historico:
                tipo = "🔽 TED Recebida" if '-' not in str(t['valor']) else "🔼 TED Enviada"
            elif 'TRANSF' in historico:
                tipo = "↔️ Transferência"
            elif 'SALDO' in historico:
                tipo = "💰 Saldo"
            else:
                tipo = "❓ Outro"
            
            print(f"   🏷️ Tipo: {tipo}")
    
    else:
        print(f"\n❌ Nenhuma transação encontrada no período 07-14/nov/2025")
        
        print(f"\n📅 Transações fora do período:")
        for t in transacoes_encontradas:
            status = "⚠️ Anterior" if t['data'] < periodo_inicio else "⚠️ Posterior"
            print(f"   {status} {t['data_str']}: {t['historico'][:30]}... (R$ {t['valor']})")
    
    # Análise de saldo
    print(f"\n💰 ANÁLISE DE SALDO:")
    print("-"*40)
    
    saldos = []
    for t in transacoes_encontradas:
        if t['saldo'] and t['saldo'] != '':
            try:
                saldo_num = float(str(t['saldo']).replace(',', ''))
                saldos.append((t['data_str'], saldo_num))
            except:
                pass
    
    if saldos:
        print(f"   📊 Evolução do saldo:")
        for data, saldo in saldos:
            print(f"      {data}: R$ {saldo:,.2f}")
        
        saldo_inicial = saldos[0][1] if saldos else 0
        saldo_final = saldos[-1][1] if saldos else 0
        print(f"\n   📈 Saldo inicial: R$ {saldo_inicial:,.2f}")
        print(f"   📉 Saldo final: R$ {saldo_final:,.2f}")
        print(f"   🔄 Variação: R$ {saldo_final - saldo_inicial:,.2f}")

except Exception as e:
    print(f"❌ Erro ao processar arquivo: {e}")
    import traceback
    traceback.print_exc()

print(f"\n" + "="*80)
print("CONCLUSÃO")
print("="*80)
print("Esta análise mostra exatamente quais transações")
print("estão disponíveis para a conta 130176356 do CONDOLIVRE")
print("e se elas se enquadram no período de busca 07-14/nov.")
print("="*80)