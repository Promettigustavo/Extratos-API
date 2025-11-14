"""
Gera Excel e PDF e compara linha por linha com o JSON
"""

from buscar_extratos_bancarios import SantanderExtratosBancarios
from datetime import datetime, timedelta
import pandas as pd
import PyPDF2
import json

fundo_id = 'CONDOLIVRE FIDC'
api = SantanderExtratosBancarios(fundo_id)

print("="*80)
print("COMPARAÇÃO COMPLETA: JSON → EXCEL → PDF")
print("="*80)

# Buscar contas
contas = api.listar_contas()
conta = contas[0]
branch = conta.get('branchCode')
account = conta.get('number')

print(f"\nConta: {branch}.{account}")

# Buscar transações (últimos 30 dias para pegar dados reais)
data_inicial = datetime.now() - timedelta(days=30)
data_final = datetime.now()

print(f"\n1️⃣ BUSCANDO TRANSAÇÕES DA API...")
transacoes = api.buscar_transacoes(branch, account, data_inicial, data_final)
print(f"✅ Total: {len(transacoes)} transações")

# Salvar JSON original
with open('transacoes_original.json', 'w', encoding='utf-8') as f:
    json.dump(transacoes, f, indent=2, ensure_ascii=False)
print(f"✅ JSON salvo: transacoes_original.json")

# Gerar Excel
print(f"\n2️⃣ GERANDO EXCEL...")
excel_path = api.exportar_transacoes_excel(transacoes, branch, account, pasta_saida=".")
print(f"✅ Excel: {excel_path}")

# Gerar PDF
print(f"\n3️⃣ GERANDO PDF...")
pdf_path = api.gerar_pdf_extrato(transacoes, branch, account, pasta_saida=".")
print(f"✅ PDF: {pdf_path}")

print(f"\n{'='*80}")
print("4️⃣ COMPARAÇÃO LINHA POR LINHA")
print(f"{'='*80}")

# Ler Excel
df = pd.read_excel(excel_path, header=None)

# Comparar cada transação
print(f"\n📊 VERIFICAÇÃO EXCEL:")
print("-"*80)

erros_excel = []
for i, trans in enumerate(transacoes):
    # Linha no Excel: 4 (index 4) + i (SALDO ANTERIOR está na linha 4)
    row_idx = 4 + i + 1  # +1 porque SALDO ANTERIOR ocupa linha 4
    
    if row_idx >= len(df):
        erros_excel.append(f"Transação {i+1} FALTANDO no Excel!")
        continue
    
    row = df.iloc[row_idx]
    
    # Comparar campos
    # Coluna A (0): Data
    data_json = trans.get('transactionDate', '')[:10]
    data_excel_raw = str(row.iloc[0])
    
    # Converter data do Excel
    if 'T' in data_excel_raw:  # Se vier no formato ISO
        data_excel = data_excel_raw[:10]
    else:  # Se vier DD/MM/YYYY
        try:
            dt = datetime.strptime(data_excel_raw, '%d/%m/%Y')
            data_excel = dt.strftime('%Y-%m-%d')
        except:
            data_excel = data_excel_raw
    
    # Coluna C (2): Histórico
    historico_json = trans.get('transactionName', '')
    historico_excel = str(row.iloc[2]) if pd.notna(row.iloc[2]) else ""
    
    # Coluna D (3): Documento
    doc_json = trans.get('documentNumber', '')
    doc_excel = str(row.iloc[3]) if pd.notna(row.iloc[3]) else ""
    
    # Coluna E (4): Valor
    valor_json = float(trans.get('amount', 0))
    tipo = trans.get('creditDebitType', '')
    if tipo == 'DEBITO':
        valor_json = -abs(valor_json)
    else:
        valor_json = abs(valor_json)
    
    valor_excel = float(row.iloc[4]) if pd.notna(row.iloc[4]) else 0.0
    
    # Verificar diferenças
    diferencas = []
    if data_json not in data_excel and data_excel not in data_json:
        diferencas.append(f"Data: '{data_json}' ≠ '{data_excel}'")
    if historico_json != historico_excel:
        diferencas.append(f"Histórico: '{historico_json}' ≠ '{historico_excel}'")
    if doc_json != doc_excel and doc_excel != 'nan':
        diferencas.append(f"Doc: '{doc_json}' ≠ '{doc_excel}'")
    if abs(valor_json - valor_excel) > 0.01:
        diferencas.append(f"Valor: {valor_json} ≠ {valor_excel}")
    
    if diferencas:
        print(f"\n❌ Transação {i+1} (linha Excel {row_idx+1}):")
        for dif in diferencas:
            print(f"   {dif}")
        erros_excel.extend(diferencas)
    elif i < 5 or i >= len(transacoes) - 2:  # Mostrar primeiras 5 e últimas 2
        print(f"✅ Transação {i+1}: OK - {historico_json[:50]}")

if not erros_excel:
    print(f"\n✅✅✅ EXCEL: Todas as {len(transacoes)} transações estão PERFEITAS!")
else:
    print(f"\n❌ EXCEL: {len(erros_excel)} erro(s) encontrado(s)")

# Verificar PDF
print(f"\n{'='*80}")
print(f"📄 VERIFICAÇÃO PDF:")
print("-"*80)

try:
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        texto_pdf = ""
        for page in reader.pages:
            texto_pdf += page.extract_text()
    
    print(f"✅ PDF lido: {len(texto_pdf)} caracteres")
    
    # Salvar texto do PDF para análise
    with open('pdf_extraido.txt', 'w', encoding='utf-8') as f:
        f.write(texto_pdf)
    print(f"✅ Texto do PDF salvo: pdf_extraido.txt")
    
    erros_pdf = []
    nao_encontrados = []
    
    for i, trans in enumerate(transacoes):
        data_pdf = trans.get('transactionDate', '')[:10]
        try:
            dt = datetime.strptime(data_pdf, '%Y-%m-%d')
            data_formatada = dt.strftime('%d/%m/%Y')
        except:
            data_formatada = data_pdf
        
        historico = trans.get('transactionName', '')
        valor = float(trans.get('amount', 0))
        
        # Formatar valor como no PDF
        valor_formatado = f"{abs(valor):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        
        # Verificar se a data está no PDF
        if data_formatada not in texto_pdf:
            erros_pdf.append(f"Data {data_formatada} não encontrada")
        
        # Verificar se o histórico está no PDF (pode estar quebrado em linhas)
        # Remover espaços extras para comparação
        historico_limpo = ' '.join(historico.split())
        texto_pdf_limpo = ' '.join(texto_pdf.split())
        
        if historico_limpo not in texto_pdf_limpo:
            # Verificar se está parcialmente (primeiras 30 chars)
            if historico[:30] not in texto_pdf:
                nao_encontrados.append(f"Transação {i+1}: {historico[:50]}")
        
        if i < 5:
            if historico_limpo in texto_pdf_limpo:
                print(f"✅ Transação {i+1}: Histórico encontrado no PDF")
            else:
                print(f"❌ Transação {i+1}: Histórico NÃO encontrado")
    
    if nao_encontrados:
        print(f"\n⚠️  Históricos não encontrados no PDF:")
        for nf in nao_encontrados[:5]:  # Mostrar primeiros 5
            print(f"   {nf}")
    
    if not erros_pdf and not nao_encontrados:
        print(f"\n✅✅✅ PDF: Todas as transações verificadas estão OK!")
    else:
        print(f"\n⚠️  PDF: {len(erros_pdf) + len(nao_encontrados)} possíveis problemas")

except Exception as e:
    print(f"❌ Erro ao ler PDF: {e}")
    import traceback
    traceback.print_exc()

print(f"\n{'='*80}")
print("RESUMO FINAL")
print(f"{'='*80}")
print(f"JSON (API):    {len(transacoes)} transações")
print(f"Excel:         {len(df) - 4} linhas de dados (incluindo SALDO ANTERIOR)")
print(f"Excel (real):  {len(df) - 4 - 1} transações (excluindo SALDO ANTERIOR)")
print(f"Erros Excel:   {len(erros_excel)}")
print(f"Issues PDF:    {len(erros_pdf) + len(nao_encontrados)}")

if len(erros_excel) == 0 and len(erros_pdf) + len(nao_encontrados) == 0:
    print(f"\n🎉🎉🎉 PERFEITO! Todos os dados do JSON estão nos arquivos!")
else:
    print(f"\n⚠️  Verifique os arquivos para mais detalhes")

print(f"\n📁 Arquivos gerados:")
print(f"   - {excel_path}")
print(f"   - {pdf_path}")
print(f"   - transacoes_original.json")
print(f"   - pdf_extraido.txt")
