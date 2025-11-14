"""Script para simular um teste local (sem API) e verificar se os arquivos são criados"""

import os
import pandas as pd
from datetime import datetime
import json

# Testar se a geração de arquivo funciona localmente
print("="*80)
print("TESTE DE GERAÇÃO DE ARQUIVOS - SEM API")
print("="*80)

# Criar dados de teste (simulando resposta da API vazia)
dados_teste = {
    'fundo': 'CONDOLIVRE FIDC',
    'branch_code': '2271',
    'account_number': '130137784',
    'transacoes': [],  # Lista vazia (sem transações)
    'saldo': {
        'availableAmount': 1000000.50,
        'currency': 'BRL'
    }
}

# Testar exportação Excel (como feito no buscar_extratos_bancarios.py)
def testar_excel():
    print("\n1. Testando criação de arquivo Excel...")
    
    try:
        # Estrutura de dados como o código original
        transacoes = dados_teste['transacoes']
        saldo_info = dados_teste['saldo']
        
        # Criar DataFrame
        if transacoes:
            df = pd.DataFrame(transacoes)
        else:
            # Sem transações - apenas cabeçalhos
            df = pd.DataFrame(columns=[
                'Fundo', 'Agência', 'Conta', 'Data', 'Tipo', 'Valor', 'Descrição', 'Saldo'
            ])
            
            # Adicionar linha com saldo (como no código original)
            if saldo_info:
                saldo_valor = float(saldo_info.get('availableAmount', 0))
                saldo_fmt = f"R$ {saldo_valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                
                linha_saldo = pd.DataFrame([{
                    'Fundo': dados_teste['fundo'],
                    'Agência': dados_teste['branch_code'],
                    'Conta': dados_teste['account_number'],
                    'Data': datetime.now().strftime('%d/%m/%Y'),
                    'Tipo': 'SALDO ATUAL',
                    'Valor': saldo_fmt,
                    'Descrição': 'Saldo disponível na conta',
                    'Saldo': saldo_fmt
                }])
                
                df = pd.concat([df, linha_saldo], ignore_index=True)
        
        # Nome do arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"teste_Extrato_{dados_teste['branch_code']}_{dados_teste['account_number']}_{timestamp}.xlsx"
        filepath = os.path.join(os.getcwd(), filename)
        
        # Salvar Excel
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Extrato')
        
        print(f"✅ Arquivo Excel criado: {filename}")
        print(f"   Tamanho: {os.path.getsize(filepath)} bytes")
        print(f"   Caminho: {filepath}")
        
        # Verificar conteúdo
        df_lido = pd.read_excel(filepath)
        print(f"   Linhas no arquivo: {len(df_lido)}")
        if len(df_lido) > 0:
            print(f"   Primeira linha: {df_lido.iloc[0].to_dict()}")
            
        return filepath
        
    except Exception as e:
        print(f"❌ Erro ao criar Excel: {e}")
        import traceback
        traceback.print_exc()
        return None

# Testar criação de PDF (versão simplificada)
def testar_pdf():
    print("\n2. Testando criação de arquivo PDF...")
    
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"teste_Extrato_{dados_teste['branch_code']}_{dados_teste['account_number']}_{timestamp}.pdf"
        filepath = os.path.join(os.getcwd(), filename)
        
        # Criar PDF
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Título
        titulo = Paragraph(f"Extrato Bancário - {dados_teste['fundo']}", styles['Title'])
        story.append(titulo)
        story.append(Spacer(1, 12))
        
        # Informações da conta
        info = f"Agência: {dados_teste['branch_code']} | Conta: {dados_teste['account_number']}"
        info_para = Paragraph(info, styles['Normal'])
        story.append(info_para)
        story.append(Spacer(1, 12))
        
        # Saldo
        if dados_teste['saldo']:
            saldo_valor = float(dados_teste['saldo'].get('availableAmount', 0))
            saldo_fmt = f"R$ {saldo_valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            saldo_para = Paragraph(f"<b>Saldo Atual: {saldo_fmt}</b>", styles['Heading2'])
            story.append(saldo_para)
        
        # Transações
        if not dados_teste['transacoes']:
            sem_trans = Paragraph("Nenhuma transação encontrada no período.", styles['Normal'])
            story.append(sem_trans)
        
        doc.build(story)
        
        print(f"✅ Arquivo PDF criado: {filename}")
        print(f"   Tamanho: {os.path.getsize(filepath)} bytes")
        print(f"   Caminho: {filepath}")
        
        return filepath
        
    except Exception as e:
        print(f"❌ Erro ao criar PDF: {e}")
        import traceback
        traceback.print_exc()
        return None

# Executar testes
arquivos_criados = []

excel_path = testar_excel()
if excel_path:
    arquivos_criados.append(excel_path)

pdf_path = testar_pdf()
if pdf_path:
    arquivos_criados.append(pdf_path)

print(f"\n3. Listando arquivos no diretório atual:")
print(f"   Diretório: {os.getcwd()}")

todos_arquivos = os.listdir(os.getcwd())
arquivos_teste = [f for f in todos_arquivos if f.startswith('teste_Extrato_')]

print(f"   Arquivos de teste encontrados: {len(arquivos_teste)}")
for arquivo in arquivos_teste:
    caminho = os.path.join(os.getcwd(), arquivo)
    tamanho = os.path.getsize(caminho)
    print(f"   - {arquivo} ({tamanho} bytes)")

print("\n" + "="*80)
print("TESTE CONCLUÍDO")
print("="*80)

# Limpar arquivos de teste
print("\n🧹 Removendo arquivos de teste...")
for arquivo in arquivos_criados:
    try:
        if os.path.exists(arquivo):
            os.remove(arquivo)
            print(f"   ✅ Removido: {os.path.basename(arquivo)}")
    except:
        pass